import secrets

import pytest
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils.http import urlencode

from oauth2 import models
from oauth2 import views


@pytest.fixture()
def client_obj(services):
    return models.Client.objects.create(
        service=services['name'],
        name='test_client',
        client_id=secrets.token_hex(16),
        client_secret=secrets.token_urlsafe(16)
    )


@pytest.fixture()
def add_rf_session():
    def wrapper(request):
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        return request

    return wrapper


def test_authorization(rf, add_rf_session, client_obj):
    request = rf.get(reverse('oauth2:authorization', kwargs={'client_name': client_obj.name}))
    request = add_rf_session(request)
    response = views.AuthorizationView.as_view()(request, client_name=client_obj.name)
    assert response.status_code == 302
    assert response.url.startswith(client_obj.driver.authorization_url)


def test_authorization_state(rf, add_rf_session, client_obj, settings):
    request = rf.get(reverse('oauth2:authorization', kwargs={'client_name': client_obj.name}))
    request = add_rf_session(request)
    response = views.AuthorizationView.as_view()(request, client_name=client_obj.name)
    assert request.session[settings.OAUTH2_SESSION_STATE_KEY] in response.url


def test_authorization_return_url(rf, add_rf_session, client_obj, settings):
    request = rf.get(reverse('oauth2:authorization', kwargs={'client_name': client_obj.name}))
    request = add_rf_session(request)
    response = views.AuthorizationView.as_view()(request, client_name=client_obj.name)
    assert request.session[settings.OAUTH2_SESSION_RETURN_KEY] == settings.OAUTH2_RETURN_URL

    request = rf.get('{}?{}'.format(
        reverse('oauth2:authorization', kwargs={'client_name': client_obj.name}),
        urlencode({f'{settings.OAUTH2_RETURN_FIELD_NAME}': '/other'})
    ))
    request = add_rf_session(request)
    response = views.AuthorizationView.as_view()(request, client_name=client_obj.name)
    assert request.session[settings.OAUTH2_SESSION_RETURN_KEY] == '/other'


@pytest.mark.xfail()
def test_token(rf, add_rf_session, client_obj):
    request = rf.get(reverse('oauth2:token', kwargs={'client_name': 'test'}))
    request = add_rf_session(request)
    response = views.TokenView.as_view()(request)
    assert response.status_code == 302
