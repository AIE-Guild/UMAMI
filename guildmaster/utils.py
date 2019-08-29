import datetime as dt
import email.utils as eut
from typing import Optional
from urllib import parse

import pytz
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.utils import timezone


def exposed_url(request: HttpRequest, path: Optional[str] = '/') -> str:
    target = parse.urlsplit(request.build_absolute_uri(path))
    try:
        target = target._replace(scheme=request.META['HTTP_X_FORWARDED_PROTO'])
    except KeyError:
        pass
    return parse.urlunsplit(target)


def parse_http_date(text):
    date = dt.datetime(*eut.parsedate(text)[:6])
    return pytz.timezone(timezone.get_default_timezone_name()).localize(date)


def reverse(viewname, urlconf=None, args=None, kwargs=None, current_app=None, query=None):
    """Wrapper for Django's reverse that applies an optional query string."""
    url = reverse_lazy(viewname, urlconf=urlconf, args=args, kwargs=kwargs, current_app=current_app)
    if query is not None:
        target = parse.urlsplit(str(url))
        target = target._replace(query=parse.urlencode(query, quote_via=parse.quote))
        url = parse.urlunsplit(target)
    return url
