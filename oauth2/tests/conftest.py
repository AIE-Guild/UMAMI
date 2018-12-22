import collections.abc as collections

import pytest
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory
from django.utils import timezone

from oauth2 import drivers


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
            request.session.save()
            return request

    return UserSessionRequestFactory()


@pytest.fixture()
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

        def __init__(self, data):
            self.headers = self.Headers({'Date': timezone.now().strftime('%a, %d %b %Y %H:%M:%S GMT')})
            self.data = data

        def json(self):
            return self.data

    def factory(data):
        return Response(data)

    return factory
