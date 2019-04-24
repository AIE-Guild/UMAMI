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
            # pylint: disable=too-many-arguments
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


@pytest.fixture()
def tf_token_response():
    return {
        'token_type': 'Bearer',
        'access_token': secrets.token_urlsafe(64),
        'refresh_token': secrets.token_urlsafe(64),
        'expires_in': 3600,
        'scope': 'foo bar baz',
        'comment': 'This is a sample response.',
    }


@pytest.fixture(scope='session')
def tf_datestr():
    return 'Sun, 12 Jan 1997 12:00:00 UTC'


@pytest.fixture(scope='session')
def tf_date():
    date = dt.datetime(1997, 1, 12, 12, 00, 00, 0)
    return pytz.timezone(timezone.get_default_timezone_name()).localize(date)


@pytest.fixture()
def tf_user():
    user, __ = User.objects.get_or_create(username='ralff', email='ralff@aie-guild.org')
    return user


@pytest.fixture(params=drivers.ClientDriver.get_driver_names())
def tf_client(request):
    return models.Client.objects.create(
        service=request.param,
        name='test_client',
        client_id=secrets.token_hex(16),
        client_secret=secrets.token_urlsafe(16),
    )


@pytest.fixture()
def tf_token(tf_user, tf_client):
    obj = models.Token.objects.create(
        client=tf_client,
        user=tf_user,
        token_type='bearer',
        access_token=secrets.token_urlsafe(64),
        refresh_token=secrets.token_urlsafe(64),
        timestamp=timezone.now(),
        expires_in=3600,
        scope='email identify',
        redirect_uri='https://test.aie-guild.org/auth/token',
    )
    return obj


@pytest.fixture()
def tf_resource_response():
    return {
        'id': secrets.token_hex(16),
        'battletag': 'User#1234',
        'username': 'User',
        'discriminator': '1234',
        'CharacterID': 95465499,
        'CharacterName': 'CCP Bartender',
    }


@pytest.fixture()
def tf_error_response():
    return {
        "error": "invalid_request",
        "error_description": "Request was missing the 'redirect_uri' parameter.",
        "error_uri": "See the full API docs at https://example.com/docs/access_token",
    }
