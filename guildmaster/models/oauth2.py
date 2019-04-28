import datetime as dt
import logging
import uuid
from typing import Optional
import secrets
from urllib import parse

import requests
from django import http
from django.conf import settings
from django.db import models
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from guildmaster import exceptions, utils
from guildmaster.core import TokenData

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

PROVIDERS = {
    'discord': {
        'description': 'Discord',
        'authorization_url': 'https://discordapp.com/api/oauth2/authorize',
        'token_url': 'https://discordapp.com/api/oauth2/token',
        'revocation_url': 'https://discordapp.com/api/oauth2/token/revoke',
        'default_scopes': ('identify', 'email'),
    }
}


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.SlugField(verbose_name=_('name'), unique=True, max_length=64)
    service = models.CharField(
        verbose_name=_('service'), max_length=64, choices=[(k, PROVIDERS[k]['description']) for k in PROVIDERS]
    )
    enabled = models.BooleanField(verbose_name=_('enabled'), default=True)
    client_id = models.CharField(verbose_name=_('client id'), max_length=191)
    client_secret = models.CharField(verbose_name=_('client secret'), max_length=191)
    scope_override = models.TextField(verbose_name=_('scope override'), blank=True, default='')

    def __str__(self):
        return self.name

    def __getattr__(self, item):
        defaults = {
            'description': None,
            'authorization_url': None,
            'token_url': None,
            'verification_url': None,
            'revocation_url': None,
            'default_scopes': (),
            'http_basic_auth': False,
        }
        if item in defaults:
            return PROVIDERS[self.service].get(item, defaults[item])
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    @classmethod
    def get_providers(cls):
        return [x for x in PROVIDERS]

    @property
    def callback(self) -> Optional[str]:
        try:
            return reverse('guildmaster:token', kwargs={'client_name': self.name})
        except NoReverseMatch:
            return None

    def redirect_url(self, request: http.HttpRequest) -> Optional[str]:
        return utils.exposed_url(request, path=self.callback)

    @property
    def scopes(self) -> Optional[tuple]:
        if self.scope_override:
            return tuple(self.scope_override.split())
        else:
            return self.default_scopes

    def get_authorization_url(self, request: http.HttpRequest, return_url: Optional[str] = None) -> str:
        """Build the OAuth2 authorization redirect URL.

        Args:
            request: The received user request.
            return_url: The URL to redirect to when the OAuth2 authorization code workflow is complete.

        Returns:
            The fully parametrized URL to redirect the user to for authorization.

        """
        target = parse.urlsplit(self.authorization_url)
        state = secrets.token_urlsafe(settings.GUILDMASTER_STATE_BYTES)
        if return_url is None:
            return_url = settings.GUILDMASTER_RETURN_URL
        args = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_url(request),
            'scope': ' '.join(self.scopes),
            'state': state,
        }
        target = target._replace(query=parse.urlencode(args, quote_via=parse.quote))
        result = parse.urlunsplit(target)
        logger.debug("built authorization URL: %s", result)
        request.session[settings.GUILDMASTER_SESSION_STATE_KEY] = state
        request.session[settings.GUILDMASTER_SESSION_RETURN_KEY] = return_url
        logger.debug("stored session state for user %s: state=%s, return_url=%s", request.user, state, return_url)
        return result


class Token(models.Model):
    REFRESH_COEFFICIENT = 0.5

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey('Client', verbose_name=_('client'), on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('users'), on_delete=models.CASCADE)
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
