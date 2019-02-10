import datetime as dt
import logging
from typing import Optional

import requests
from django.utils import timezone

from dataclasses import dataclass, field
from oauth2 import exceptions, utils

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@dataclass()
class TokenData:
    access_token: str
    token_type: str = 'Bearer'
    refresh_token: str = ''
    expires_in: int = None
    timestamp: dt.datetime = field(default_factory=timezone.now)
    scope: str = ''
    redirect_uri: str = ''

    @property
    def expiry(self) -> Optional[dt.datetime]:
        if self.expires_in is None:
            return None
        result = self.timestamp + dt.timedelta(seconds=self.expires_in)
        logger.debug("calculated expiry=%s from timestamp=%s + expires_in=%s", result, self.timestamp, self.expires_in)
        return result

    @property
    def authorization(self):
        return f'{self.token_type.title()} {self.access_token}'

    @classmethod
    def from_response(cls, response: requests.Response) -> 'TokenData':
        cls.validate_token_response(response)
        ts = utils.parse_http_date(response.headers['Date'])
        whitelist = ('access_token', 'token_type', 'refresh_token', 'expires_in', 'scope')
        args = {k: v for k, v in response.json().items() if k in whitelist}
        return cls(timestamp=ts, **args)

    @classmethod
    def validate_token_response(cls, response: requests.Response) -> None:
        data = response.json()
        if 'error' in data:
            exc = exceptions.OAuth2Error(
                error=data['error'], description=data.get('error_description'), uri=data.get('error_uri')
            )
            logger.error("Token request error: %s", exc)
            raise exc
