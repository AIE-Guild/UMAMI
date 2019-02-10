import datetime as dt
import logging
import uuid
from typing import Dict, Optional

import requests
from django import http
from django.conf import settings
from django.db import models
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from oauth2 import drivers, exceptions, utils
from oauth2.core import TokenData

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.SlugField(verbose_name=_('name'), unique=True, max_length=64)
    service = models.CharField(verbose_name=_('service'), max_length=64, choices=drivers.ClientDriver.get_choices())
    enabled = models.BooleanField(verbose_name=_('enabled'), default=True)
    client_id = models.CharField(verbose_name=_('client id'), max_length=191)
    client_secret = models.CharField(verbose_name=_('client secret'), max_length=191)
    scope_override = models.TextField(verbose_name=_('scope override'), blank=True, default='')

    def __str__(self):
        return self.name

    @property
    def callback(self) -> Optional[str]:
        try:
            return reverse('oauth2:token', kwargs={'client_name': self.name})
        except NoReverseMatch:
            return None

    def redirect_url(self, request: http.HttpRequest) -> Optional[str]:
        return utils.exposed_url(request, path=self.callback)

    def get_resource_key(self, data: Dict) -> Optional[str]:
        return self.driver.get_resource_key(data)

    def get_resource_tag(self, data: Dict) -> Optional[str]:
        return self.driver.get_resource_tag(data)

    @property
    def driver(self) -> drivers.ClientDriver:
        return drivers.ClientDriver.factory(self.service)

    @property
    def http_basic_auth(self) -> bool:
        return self.driver.http_basic_auth

    @property
    def scopes(self) -> Optional[tuple]:
        if self.scope_override:
            return tuple(self.scope_override.split())
        else:
            return self.driver.scopes

    @property
    def description(self):
        return self.driver.description

    @property
    def authorization_url(self) -> str:
        return self.driver.authorization_url

    @property
    def token_url(self) -> str:
        return self.driver.token_url

    @property
    def verification_url(self) -> str:
        return self.driver.verification_url

    @property
    def revocation_url(self) -> str:
        return self.driver.revocation_url

    @property
    def resource_url(self) -> str:
        return self.driver.resource_url


class Resource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, verbose_name=_('users'), related_name='resources', related_query_name='resource'
    )
    client = models.ForeignKey('Client', verbose_name=_('client'), on_delete=models.PROTECT)
    key = models.CharField(verbose_name=_('key'), max_length=64)
    tag = models.CharField(verbose_name=_('tag'), max_length=64, blank=True, default='')

    class Meta:
        unique_together = ('client', 'key')

    def __str__(self):
        return f"{self.key} ({self.tag})"


class Token(models.Model):
    REFRESH_COEFFICIENT = 0.5

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resource = models.OneToOneField('Resource', verbose_name=_('resource'), on_delete=models.CASCADE)
    timestamp = models.DateTimeField(verbose_name=_('timestamp'), auto_now_add=True)
    token_type = models.CharField(verbose_name=_('token type'), max_length=64, default='bearer')
    access_token = models.TextField(verbose_name=_('access token'))
    refresh_token = models.TextField(verbose_name=_('refresh token'), blank=True, default='')
    expires_in = models.PositiveIntegerField(verbose_name=_('expires in'), blank=True, null=True)
    scope = models.TextField(verbose_name=_('scope'), blank=True, default='')
    redirect_uri = models.URLField(verbose_name=_('redirect URI'), blank=True, default='')

    def __str__(self):
        return str(self.id)

    @property
    def expiry(self) -> Optional[dt.datetime]:
        if self.expires_in is None:
            return None
        result = self.timestamp + dt.timedelta(seconds=self.expires_in)
        logger.debug("calculated expiry=%s from timestamp=%s + expires_in=%s", result, self.timestamp, self.expires_in)
        return result

    @property
    def is_stale(self):
        if self.expires_in is None:
            return False
        return timezone.now() > self.timestamp + (self.REFRESH_COEFFICIENT * dt.timedelta(seconds=self.expires_in))

    @property
    def client(self):
        return self.resource.client

    @property
    def authorization(self):
        return f'{self.token_type.title()} {self.access_token}'

    def refresh(self) -> None:
        if not self.refresh_token:
            raise exceptions.TokenRefreshError(f"No authorization client found.")
        auth = None
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
        }
        if self.client.http_basic_auth:
            auth = (self.client.client_id, self.client.client_secret)
        else:
            payload.update({'client_id': self.client.client_id, 'client_secret': self.client.client_secret})

        logger.debug("sending token request to %s", self.client.token_url)
        try:
            response = requests.post(self.client.token_url, data=payload, auth=auth)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("failed to fetch access token: %s", exc)
            raise IOError(f"Failed to fetch access token from {self.client.service}.")
        data = TokenData.from_response(response)
        self.timestamp = data.timestamp
        self.access_token = data.access_token
        self.refresh_token = data.refresh_token
        self.expires_in = data.expires_in
        self.scope = data.scope
        self.save()
