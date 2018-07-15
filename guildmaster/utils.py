import secrets
from email.utils import parsedate_tz, mktime_tz
from typing import Type
import logging

import requests

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def generate_state() -> str:
    """Generate a state string to be used for anti-CSRF.
    Returns:
        str: A URL-safe pseudorandom string.
    """
    return secrets.token_urlsafe(settings.OAUTH_STATE_BYTES)


def parse_http_date(response: Type[requests.Response]) -> int:
    header = None
    try:
        header = response.headers['Date']
        timestamp = mktime_tz(parsedate_tz(header))
    except KeyError:
        timestamp = timezone.now().timestamp()
    logger.debug('parsed HTTP Date: %s -> %s', header, timestamp)
    return timestamp
