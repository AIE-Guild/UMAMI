import datetime as dt
import logging
import secrets
from typing import Optional
from urllib import parse

import requests
from django import http
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

from dataclasses import dataclass, field
from oauth2 import exceptions, utils
from oauth2.models import Client, Token

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@dataclass()
class TokenData:
    user: User
    client: Client
    access_token: str
    token_type: str = 'Bearer'
    refresh_token: str = ''
    expires_in: int = None
    timestamp: dt.datetime = field(default_factory=timezone.now)
    resource_id: str = None
    resource_tag: str = None

    @property
    def expiry(self) -> Optional[dt.datetime]:
        if self.expires_in is None:
            return
        result = self.timestamp + dt.timedelta(seconds=self.expires_in)
        logger.debug(f'calculated expiry=%s from timestamp=%s + expires_in=%s', result, self.timestamp, self.expires_in)
        return result

    @classmethod
    def from_response(cls, user: User, client: Client, response: requests.Response) -> 'TokenData':
        ts = utils.parse_http_date(response.headers['Date'])
        whitelist = ('access_token', 'token_type', 'refresh_token', 'expires_in')
        args = {k: v for k, v in response.json().items() if k in whitelist}
        return cls(user, client, timestamp=ts, **args)


def get_authorization_url(request: http.HttpRequest, client: Client, return_url: Optional[str] = None) -> str:
    """Build the OAuth2 authorization redirect URL.

    Args:
        request: The received user request.
        client: An OAuth2 client.
        return_url: The URL to redirect to when the OAuth2 authorization code workflow is complete.

    Returns:
        The fully parametrized URL to redirect the user to for authorization.

    """
    target = parse.urlsplit(client.driver.authorization_url)
    state = secrets.token_urlsafe(settings.OAUTH2_STATE_BYTES)
    if return_url is None:
        return_url = settings.OAUTH2_RETURN_URL
    args = {
        'response_type': 'code',
        'client_id': client.client_id,
        'redirect_uri': utils.exposed_url(request, path=client.callback),
        'scope': ' '.join(client.scopes),
        'state': state
    }
    target = target._replace(query=parse.urlencode(args, quote_via=parse.quote))
    result = parse.urlunsplit(target)
    logger.debug('built authorization URL: %s', result)
    request.session[settings.OAUTH2_SESSION_STATE_KEY] = state
    request.session[settings.OAUTH2_SESSION_RETURN_KEY] = return_url
    logger.debug('stored session state for user %s: state=%s, return_url=%s', request.user, state, return_url)
    return result


def validate_authorization_response(request: http.HttpRequest, client: Client) -> None:
    state = request.session.get(settings.OAUTH2_SESSION_STATE_KEY)
    logger.debug('fetched session state for user %s: state=%s', request.user, state)
    if request.GET['state'] != state:
        logger.error('state mismatch: %s received, %s expected.', request.GET['state'], state)
        raise ValueError('Authorization state mismatch.')
    if 'error' in request.GET:
        exc = exceptions.OAuth2Error(
            error=request.GET['error'],
            description=request.GET.get('error_description'),
            uri=request.GET.get('error_uri')
        )
        logger.error(f'Authorization error: {exc}')
        raise exc


def fetch_tokens(request: http.HttpRequest, client: Client) -> Token:
    data = {
        'grant_type': 'authorization_code',
        'code': request.GET['code'],
        'redirect_uri': utils.exposed_url(request, path=client.callback),
        'client_id': client.client_id
    }
    if client.driver.http_basic_auth:
        auth = (client.client_id, client.client_secret)
    else:  # pragma: no cover
        auth = None
        data['client_secret'] = client.client_secret

    session = requests.Session()
    try:
        logger.debug('sending token request to %s', client.driver.token_url)
        response = session.post(client.driver.token_url, data=data, auth=auth)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error(exc)
        raise IOError(exc)
    token_data = TokenData.from_response(request.user, client, response)
    attrs = {k: getattr(token_data, k) for k in ['access_token', 'token_type', 'refresh_token', 'expiry'] if
             getattr(token_data, k) is not None}
    token, created = Token.objects.update_or_create(user=request.user, client=client, defaults=attrs)
    logger.info('%s token %s obtained for user %s', client.driver.description, token, request.user)
    return token


def get_return_url(request: http.HttpRequest) -> str:
    return request.session.get(settings.OAUTH2_SESSION_RETURN_KEY, settings.OAUTH2_RETURN_URL)
