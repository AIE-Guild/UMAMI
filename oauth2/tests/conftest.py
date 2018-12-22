import collections.abc as collections
import datetime as dt
import secrets

import pytest
import pytz
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory
from django.utils import timezone

from oauth2 import drivers, models


@pytest.fixture(scope='session', params=drivers.ClientDriver.get_drivers())
def service(request):
    return request.param


@pytest.fixture()
def rf(rf):
    class UserSessionRequestFactory(RequestFactory):
        def generic(self, method, path, data='', content_type='application/octet-stream', secure=False, **extra):
            username = extra.get('username')
            headers = extra.get('headers')
            request = super().generic(method, path, data, content_type, secure, **extra)
            try:
                request.user = User.objects.get(username=username)
            except User.DoesNotExist:
                request.user = AnonymousUser()
            if headers is not None:
                for key in headers:
                    request.META[key] = headers[key]
            middleware = SessionMiddleware()
            middleware.process_request(request)
            middleware = MessageMiddleware()
            middleware.process_request(request)
            request.session.save()
            return request

    return UserSessionRequestFactory()


@pytest.fixture(scope='session')
def response_factory():
    class Response:
        class Headers(collections.MutableMapping):
            def __init__(self, data=None, **kwargs):
                self._store = dict()
                if data is None:
                    data = {}
                self.update(data, **kwargs)

            def __setitem__(self, key, value):
                self._store[key.lower()] = (key, value)

            def __getitem__(self, key):
                return self._store[key.lower()][1]

            def __delitem__(self, key):
                del self._store[key.lower()]

            def __iter__(self):
                return (casedkey for casedkey, mappedvalue in self._store.values())

            def __len__(self):
                return len(self._store)

        def __init__(self, data, date=None):
            if date is None:
                date = timezone.now().strftime('%a, %d %b %Y %H:%M:%S %Z')
            self.headers = self.Headers({'Date': date})
            self.data = data

        def json(self):
            return self.data

    def factory(data, date=None):
        return Response(data, date=date)

    return factory


@pytest.fixture(scope='session')
def sample_datestr():
    return 'Sun, 12 Jan 1997 12:00:00 UTC'


@pytest.fixture(scope='session')
def sample_date():
    date = dt.datetime(1997, 1, 12, 12, 00, 00, 0)
    return pytz.timezone(timezone.get_default_timezone_name()).localize(date)


@pytest.fixture()
def sample_user():
    user, __ = User.objects.get_or_create(username='ralff', email='ralff@aie-guild.org')
    return user


@pytest.fixture(params=drivers.ClientDriver.get_driver_names())
def sample_client(request):
    return models.Client.objects.create(
        service=request.param,
        name='test_client',
        client_id=secrets.token_hex(16),
        client_secret=secrets.token_urlsafe(16)
    )
