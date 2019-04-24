import logging
import secrets
from typing import Optional
from urllib import parse

import requests
from django import http
from django.conf import settings

from oauth2 import exceptions
from oauth2.core import TokenData
from oauth2.models import Client, Token

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class AuthorizationCodeWorkflow:
    session = requests.Session()
    grant_params = {'authorization_code': ['code', 'redirect_uri'], 'refresh_token': ['refresh_token', 'redirect_uri']}

    def __init__(self, client_name: str) -> None:
        try:
            self.client = Client.objects.get(name=client_name)
        except Client.DoesNotExist:
            logger.error("No client found: %s", client_name)
            raise ValueError(f"No client found: {client_name}")

    @property
    def verbose_name(self):
        return self.client.description

    def get_authorization_url(self, request: http.HttpRequest, return_url: Optional[str] = None) -> str:
        """Build the OAuth2 authorization redirect URL.

        Args:
            request: The received user request.
            return_url: The URL to redirect to when the OAuth2 authorization code workflow is complete.

        Returns:
            The fully parametrized URL to redirect the user to for authorization.

        """
        target = parse.urlsplit(self.client.authorization_url)
        state = secrets.token_urlsafe(settings.OAUTH2_STATE_BYTES)
        if return_url is None:
            return_url = settings.OAUTH2_RETURN_URL
        args = {
            'response_type': 'code',
            'client_id': self.client.client_id,
            'redirect_uri': self.client.redirect_url(request),
            'scope': ' '.join(self.client.scopes),
            'state': state,
        }
        target = target._replace(query=parse.urlencode(args, quote_via=parse.quote))
        result = parse.urlunsplit(target)
        logger.debug("built authorization URL: %s", result)
        request.session[settings.OAUTH2_SESSION_STATE_KEY] = state
        request.session[settings.OAUTH2_SESSION_RETURN_KEY] = return_url
        logger.debug("stored session state for user %s: state=%s, return_url=%s", request.user, state, return_url)
        return result

    def get_access_token(self, request: http.HttpRequest) -> Token:
        token_data = self._fetch_access_token(request)
        token, __ = Token.objects.update_or_create(
            client=self.client,
            user=request.user,
            defaults={
                k: getattr(token_data, k)
                for k in ['timestamp', 'access_token', 'token_type', 'refresh_token', 'scope', 'redirect_uri']
                if getattr(token_data, k) is not None
            },
        )
        logger.info("%s token %s obtained for user %s", self.client.description, token, request.user)
        return token

    def _fetch_access_token(self, request: http.HttpRequest) -> TokenData:
        auth = None
        payload = {
            'grant_type': 'authorization_code',
            'code': request.GET['code'],
            'redirect_uri': self.client.redirect_url(request),
            'scope': ' '.join(self.client.scopes),
        }
        if self.client.http_basic_auth:
            auth = (self.client.client_id, self.client.client_secret)
        else:
            payload.update({'client_id': self.client.client_id, 'client_secret': self.client.client_secret})

        logger.debug("sending token request to %s", self.client.token_url)
        try:
            response = self.session.post(self.client.token_url, data=payload, auth=auth)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("failed to fetch access token: %s", exc)
            raise IOError(f"Failed to fetch access token from {self.client.service}.")
        token = TokenData.from_response(response)
        token.redirect_uri = payload['redirect_uri']
        return token

    @classmethod
    def validate_state(cls, request: http.HttpRequest) -> None:
        state = request.session.get(settings.OAUTH2_SESSION_STATE_KEY)
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

    @classmethod
    def get_return_url(cls, request: http.HttpRequest) -> str:
        return request.session.get(settings.OAUTH2_SESSION_RETURN_KEY, settings.OAUTH2_RETURN_URL)
