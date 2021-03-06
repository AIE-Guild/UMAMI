import datetime as dt
import logging
import secrets
from typing import Optional
from urllib import parse

import requests
from django import http
from django.conf import settings
from django.db import models
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from requests.auth import AuthBase
from requests.status_codes import codes

from guildmaster import exceptions, utils
from guildmaster.core import TokenData
from guildmaster.exceptions import AuthorizationRequiredError
from guildmaster.models import providers

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Client(models.Model):
    name = models.SlugField(verbose_name=_('name'), unique=True, max_length=64)
    provider_id = models.CharField(
        verbose_name=_('providers'), max_length=64, unique=True, choices=providers.Provider.choices()
    )
    enabled = models.BooleanField(verbose_name=_('enabled'), default=True)
    client_id = models.CharField(verbose_name=_('client id'), max_length=191)
    client_secret = models.CharField(verbose_name=_('client secret'), max_length=191)
    scope_override = models.TextField(verbose_name=_('scope override'), blank=True, default='')

    session = requests.Session()

    def __str__(self):
        return self.name

    def __getattr__(self, attr):
        return getattr(self.provider, attr)

    @property
    def provider(self):
        return providers.Provider.registry[self.provider_id]

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
            try:
                return self.provider.default_scopes
            except KeyError:
                return None

    def get_authorization_url(self, request: http.HttpRequest, return_url: Optional[str] = None) -> str:
        """Build the OAuth2 authorization redirect URL.

        Args:
            request: The received user request.
            return_url: The URL to redirect to when the OAuth2 authorization code workflow is complete.

        Returns:
            The fully parametrized URL to redirect the user to for authorization.

        """
        target = parse.urlsplit(self.provider.authorization_url)
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

    def get_access_token(self, request: http.HttpRequest) -> 'Token':
        token_data = self._fetch_token_data(request)
        token, __ = Token.objects.update_or_create(
            client=self,
            user=request.user,
            defaults={
                k: getattr(token_data, k)
                for k in ['timestamp', 'access_token', 'token_type', 'refresh_token', 'scope', 'redirect_uri']
                if getattr(token_data, k) is not None
            },
        )
        logger.info("%s token %s obtained for user %s", self.provider.description, token, request.user)

        try:
            response = self.session.get(self.provider.userinfo_url, auth=token.auth)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("failed to fetch user info: %s", exc)
            raise IOError(f"Failed to fetch user info from {self.provider}.")

        tag = self.provider.resource(response.json())
        Token.objects.filter(user=request.user, resource=tag).delete()
        token.resource = tag
        token.save()

        logger.info("%s token %s obtained for user %s", self.provider.description, token, request.user)

        return token

    def _fetch_token_data(self, request: http.HttpRequest) -> TokenData:
        auth = None
        payload = {
            'grant_type': 'authorization_code',
            'code': request.GET['code'],
            'redirect_uri': self.redirect_url(request),
            'scope': ' '.join(self.scopes),
        }
        if self.provider.http_basic_auth:
            auth = (self.client_id, self.client_secret)
        else:
            payload.update({'client_id': self.client_id, 'client_secret': self.client_secret})

        logger.debug("sending token request to %s", self.provider.token_url)
        try:
            response = self.session.post(self.provider.token_url, data=payload, auth=auth)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("failed to fetch access token: %s", exc)
            raise IOError(f"Failed to fetch access token from {self.provider}.")
        token = TokenData.from_response(response)
        token.redirect_uri = payload['redirect_uri']
        return token

    @classmethod
    def validate_state(cls, request: http.HttpRequest) -> None:
        state = request.session.get(settings.GUILDMASTER_SESSION_STATE_KEY)
        logger.debug("fetched session state for user %s: state=%s", request.user, state)
        if request.GET['state'] != state:
            logger.error("state mismatch: %s received, %s expected.", request.GET['state'], state)
            raise ValueError("Authorization state mismatch.")

    @classmethod
    def validate_authorization_response(cls, request: http.HttpRequest) -> None:
        if 'error' in request.GET:
            exc = exceptions.OAuth2Error(
                error=request.GET['error'],
                description=request.GET.get('error_description'),
                uri=request.GET.get('error_uri'),
            )
            logger.error("Authorization request error: %s", exc)
            raise exc

    def get_return_url(cls, request: http.HttpRequest) -> str:
        return request.session.get(settings.GUILDMASTER_SESSION_RETURN_KEY, settings.GUILDMASTER_RETURN_URL)


class Token(models.Model):
    REFRESH_COEFFICIENT = 0.5

    client = models.ForeignKey('Client', verbose_name=_('client'), on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('users'), on_delete=models.CASCADE)
    timestamp = models.DateTimeField(verbose_name=_('timestamp'), auto_now_add=True)
    token_type = models.CharField(verbose_name=_('token type'), max_length=64, default='bearer')
    access_token = models.TextField(verbose_name=_('access token'))
    refresh_token = models.TextField(verbose_name=_('refresh token'), blank=True, default='')
    expires_in = models.PositiveIntegerField(verbose_name=_('expires in'), blank=True, null=True)
    scope = models.TextField(verbose_name=_('scope'), blank=True, default='')
    redirect_uri = models.URLField(verbose_name=_('redirect URI'), blank=True, default='')
    resource = models.CharField(verbose_name=_('resource tag'), max_length=64, unique=True, null=True, blank=True)

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
            raise IOError(f"Failed to fetch access token from {self.client.provider}.")
        data = TokenData.from_response(response)
        self.timestamp = data.timestamp
        self.access_token = data.access_token
        self.refresh_token = data.refresh_token
        self.expires_in = data.expires_in
        self.scope = data.scope
        self.save()

    @property
    def auth(self):
        return TokenAuth(self)


class TokenAuth(AuthBase):
    def __init__(self, token: 'Token') -> None:
        """Authentication class to apply Oauth2 token.

        Args:
            token: An OAuth2 Token object.

        """
        self.token = token

    def _handle_response(self, response: requests.Response, **kwargs) -> requests.Response:
        """Response handler.

        Args:
            response: A Response object.
            **kwargs: Keyword arguments passed to the original request.

        Returns:
            A Response object.

        Raises:
            AuthorizationRequired: Authentication token was missing or invalid.

        """
        if response.status_code in (codes.UNAUTHORIZED, codes.FORBIDDEN):
            raise AuthorizationRequiredError(
                f"{self.token.client} authorization token failed for user {self.token.user}"
            )
        return response

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Authentication wrapper for requests.

        Args:
            request: A PreparedRequest object.

        Returns:
            The request with authentication headers applied.

        """
        request.register_hook('response', self._handle_response)
        if self.token.is_stale:
            self.token.refresh()
        request.headers['Authorization'] = self.token.authorization
        return request
