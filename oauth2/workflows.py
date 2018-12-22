from dataclasses import dataclass, field
import datetime as dt
import logging
import email.utils as eut
from typing import Optional

import pytz
import requests
from django.contrib.auth.models import User
from django.utils import timezone

from oauth2.models import Client

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def parse_http_date(text: str) -> dt.datetime:
    date = dt.datetime(*eut.parsedate(text)[:6])
    return pytz.timezone(timezone.get_default_timezone_name()).localize(date)


@dataclass()
class TokenData:
    user: User
    client: Client
    access_token: str
    token_type: str = 'Bearer'
    refresh_token: str = None
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
        ts = response.headers['Date']
        whitelist = ('access_token', 'token_type', 'refresh_token', 'expires_in')
        args = {k: v for k, v in response.json().items() if k in whitelist}
        return cls(user, client, timestamp=ts, **args)
