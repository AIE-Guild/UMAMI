import datetime as dt
import logging
import secrets
import uuid
from typing import Optional, Tuple

import requests
from django import http
from django.conf import settings
from django.db import models, transaction
from django.urls import reverse, NoReverseMatch
from django.utils.translation import ugettext_lazy as _
from furl import furl

from oauth2 import drivers, exceptions, utils

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.SlugField(verbose_name=_('name'), unique=True, max_length=50)
    service = models.CharField(verbose_name=_('service'), max_length=50, choices=drivers.ClientDriver.get_choices())
    enabled = models.BooleanField(verbose_name=_('enabled'), default=True)
    client_id = models.CharField(verbose_name=_('client id'), max_length=191)
    client_secret = models.CharField(verbose_name=_('client secret'), max_length=191)
    scope_override = models.TextField(verbose_name=_('scope override'), blank=True, default='')

    @property
    def scopes(self) -> tuple:
        driver = drivers.ClientDriver.create(self.service)
        if driver is None:
            return
        if self.scope_override:
            return tuple(self.scope_override.split())
        else:
            return driver.scopes

    @property
    def driver(self) -> drivers.ClientDriver:
        return drivers.ClientDriver.create(self.service)

    @property
    def callback(self):
        try:
            return reverse('oauth2:token', kwargs={'client_name': self.name})
        except NoReverseMatch:
            return

    def get_authorization_request(self, request: http.HttpRequest, state: Optional[str] = None) -> Tuple[str, str]:
        target = furl(self.driver.authorization_url)
        if state is None:
            state = secrets.token_urlsafe(settings.OAUTH2_STATE_BYTES)
        target.args['response_type'] = 'code'
        target.args['client_id'] = self.client_id
        target.args['redirect_uri'] = utils.exposed_url(request, path=self.callback)
        target.args['scope'] = ' '.join(self.scopes)
        target.args['state'] = state
        return target.url, state

    def validate_authorization_response(self, request: http.HttpRequest, state: str) -> None:
        if state != request.GET['state']:
            msg = f"state mismatch: '{request.GET['state']}' received, '{state}' expected."
            logger.error(msg)
            raise ValueError(msg)
        if 'error' in request.GET:
            error = request.GET['error']
            logger.error(f'Oauth2 authorization error: {error}')
            raise exceptions.OAuth2Error(
                error=error,
                description=request.GET.get('error_description'),
                uri=request.GET.get('error_uri')
            )

    def get_token_request(self, request: http.HttpRequest) -> requests.PreparedRequest:
        data = {
            'grant_type': 'authorization_code',
            'code': request.GET['code'],
            'redirect_uri': utils.exposed_url(request, path=reverse('oauth2:token', kwargs={'client_name': self.name})),
            'client_id': self.client_id
        }
        if self.driver.http_basic_auth:
            auth = (self.client_id, self.client_secret)
        else:  # pragma: no cover
            auth = None
            data['client_secret'] = self.client_secret
        r = requests.Request('POST', self.driver.token_url, data=data, auth=auth)
        return r.prepare()


class TokenManager(models.Manager):
    def extract(self, user, client, response: requests.Response) -> 'Token':
        def expiry(date_header, expires_in=None):
            current = utils.parse_http_date(date_header)
            if expires_in is None:
                return
            target = current + dt.timedelta(seconds=int(expires_in))
            logger.debug(f'calculating expiry: current={current}, target={target}')
            return target

        data = response.json()
        attrs = {
            'token_type': data['token_type'],
            'access_token': data['access_token'],
            'refresh_token': data.get('refresh_token'),
            'expiry': expiry(response.headers['Date'], data.get('expires_in'))
        }
        with transaction.atomic():
            token, created = self.get_or_create(user=user, client=client, defaults=attrs)
            if created:
                for key in attrs:
                    setattr(token, key, attrs[key])
                token.save()
        return token


class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE)
    client = models.ForeignKey('Client', verbose_name=_('client'), on_delete=models.CASCADE)
    token_type = models.CharField(verbose_name=_('token type'), max_length=50, default='bearer')
    access_token = models.TextField(verbose_name=_('access token'))
    refresh_token = models.TextField(verbose_name=_('refresh token'), blank=True)
    expiry = models.DateTimeField(verbose_name=_('expiry'), blank=True, null=True)

    objects = TokenManager()

    class Meta:
        unique_together = ('user', 'client')
