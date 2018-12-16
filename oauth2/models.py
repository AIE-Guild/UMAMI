import secrets
import logging
import uuid
from typing import Optional, Tuple, Dict

import requests
from django.conf import settings
from django.db import models
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from furl import furl

from oauth2 import drivers, utils, exceptions

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.CharField(verbose_name=_('service'), max_length=50)
    name = models.CharField(verbose_name=_('name'), unique=True, max_length=50)
    enabled = models.BooleanField(verbose_name=_('enabled'), default=True)
    client_id = models.CharField(verbose_name=_('client id'), max_length=191)
    client_secret = models.CharField(verbose_name=_('client secret'), max_length=191)
    scope_override = models.TextField(verbose_name=_('scope override'))

    @property
    def scopes(self) -> tuple:
        driver = drivers.ClientDriver.create(self.service)
        if self.scope_override:
            return tuple(self.scope_override.split())
        else:
            return driver.scopes

    @property
    def driver(self) -> drivers.ClientDriver:
        return drivers.ClientDriver.create(self.service)

    def get_authorization_request(self, request: HttpRequest, state: Optional[str] = None) -> Tuple[str, str]:
        target = furl(self.driver.authorization_url)
        if state is None:
            state = secrets.token_urlsafe(settings.OAUTH2_STATE_BYTES)
        target.args['response_type'] = 'code'
        target.args['client_id'] = self.client_id
        target.args['redirect_uri'] = utils.exposed_url(request, path=reverse('oauth2:token'))
        target.args['scope'] = ' '.join(self.scopes)
        target.args['state'] = state
        return target.url, state

    def validate_authorization_response(self, request: HttpRequest, state: Optional[str] = None) -> None:
        if 'error' in request.GET:
            error = request.GET['error']
            logger.error(f'Oauth2 authorization error: {error}')
            raise exceptions.OAuth2Error(
                error=error,
                description=request.GET.get('error_description'),
                uri=request.GET.get('error_uri')
            )
        if state is not None:
            if state != request.GET['state']:
                msg = f"state mismatch: '{request.GET['state']}' received, '{state}' expected."
                logger.error(msg)
                raise ValueError(msg)

    def get_token_request(self, request: HttpRequest) -> requests.PreparedRequest:
        data = {
            'grant_type': 'authorization_code',
            'code': request.GET['code'],
            'redirect_uri': utils.exposed_url(request, path=reverse('oauth2:token')),
            'client_id': self.client_id
        }
        if self.driver.http_basic_auth:
            auth = (self.client_id, self.client_secret)
        else:
            auth = None
            data['client_secret'] = self.client_secret
        r = requests.Request('POST', self.driver.token_url, data=data, auth=auth)
        return r.prepare()


class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE)
    client = models.ForeignKey('Client', verbose_name=_('client'), on_delete=models.CASCADE)
    token_type = models.CharField(verbose_name=_('token type'), max_length=50, default='bearer')
    access_token = models.TextField(verbose_name=_('access token'))
    refresh_token = models.TextField(verbose_name=_('refresh token'), blank=True)
    expiry = models.DateTimeField(verbose_name=_('expiry'), blank=True, null=True)
