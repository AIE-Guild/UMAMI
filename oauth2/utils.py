from typing import Optional

from django.http import HttpRequest
from furl import furl


def exposed_url(request: HttpRequest, path: Optional[str] = '/') -> str:
    target = furl(request.build_absolute_uri(path))
    try:
        target.scheme = request.META['HTTP_X_FORWARDED_PROTO']
    except KeyError:
        pass
    return target.url
