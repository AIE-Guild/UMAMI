import datetime as dt
import email.utils as eut
from typing import Optional

import pytz
from django.http import HttpRequest
from django.utils import timezone
from furl import furl


def exposed_url(request: HttpRequest, path: Optional[str] = '/') -> str:
    target = furl(request.build_absolute_uri(path))
    try:
        target.scheme = request.META['HTTP_X_FORWARDED_PROTO']
    except KeyError:
        pass
    return target.url


def parse_http_date(text):
    date = dt.datetime(*eut.parsedate(text)[:6])
    return pytz.timezone(timezone.get_default_timezone_name()).localize(date)
