import secrets

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode

from oauth2 import drivers, models, views


@pytest.fixture()
def user():
    user, __ = User.objects.get_or_create(username='henry', email='henry@aie-guild.org')
    return user


@pytest.fixture(params=drivers.ClientDriver.get_driver_names())
def client_obj(request):
    return models.Client.objects.create(
        service=request.param,
        name='test_client',
        client_id=secrets.token_hex(16),
        client_secret=secrets.token_urlsafe(16)
    )


def test_authorization(rf, user, client_obj):
    request = rf.get(reverse('oauth2:authorization', kwargs={'client_name': client_obj.name}), username=user.username)
    response = views.AuthorizationView.as_view()(request, client_name=client_obj.name)
    assert response.status_code == 302
    assert response.url.startswith(client_obj.driver.authorization_url)


def test_authorization_state(rf, user, client_obj, settings):
    request = rf.get(reverse('oauth2:authorization', kwargs={'client_name': client_obj.name}), username=user.username)
    response = views.AuthorizationView.as_view()(request, client_name=client_obj.name)
    assert request.session[settings.OAUTH2_SESSION_STATE_KEY] in response.url


def test_authorization_return_url(rf, user, client_obj, settings):
    request = rf.get(reverse('oauth2:authorization', kwargs={'client_name': client_obj.name}), username=user.username)
    response = views.AuthorizationView.as_view()(request, client_name=client_obj.name)
    assert request.session[settings.OAUTH2_SESSION_RETURN_KEY] == settings.OAUTH2_RETURN_URL

    request = rf.get('{}?{}'.format(
        reverse('oauth2:authorization', kwargs={'client_name': client_obj.name}),
        urlencode({f'{settings.OAUTH2_RETURN_FIELD_NAME}': '/other'})
    ), username=user.username)
    response = views.AuthorizationView.as_view()(request, client_name=client_obj.name)
    assert request.session[settings.OAUTH2_SESSION_RETURN_KEY] == '/other'


def test_token(rf, settings, user, client_obj, requests_mock):
    expected = {
        'access_token': secrets.token_urlsafe(64),
        'refresh_token': secrets.token_urlsafe(64),
        'token_type': 'bearer',
        'expires_in': 3600,
    }
    resource = {
        'id': secrets.token_hex(16),
        'battletag': 'User#1234',
        'username': 'User',
        'discriminator': '1234'
    }
    requests_mock.post(
        client_obj.driver.token_url,
        json=expected,
        headers={'Date': timezone.now().strftime('%a, %d %b %Y %H:%M:%S %Z')})
    requests_mock.get(client_obj.driver.resource_url, json=resource)
    code = secrets.token_urlsafe(64)
    state = secrets.token_urlsafe(64)
    request = rf.get(
        reverse('oauth2:token', kwargs={'client_name': client_obj.name}),
        {'code': code, 'state': state}, username=user.username
    )
    request.user = user
    request.session[settings.OAUTH2_SESSION_STATE_KEY] = state
    response = views.TokenView.as_view()(request, client_name=client_obj.name)
    assert response.status_code == 302
    assert requests_mock.called
    assert requests_mock.call_count == 2
    assert requests_mock.request_history[0].method == 'POST'
    assert requests_mock.request_history[0].url == client_obj.driver.token_url
    assert requests_mock.request_history[1].method == 'GET'
    assert requests_mock.request_history[1].url == client_obj.driver.resource_url


def test_token_error(rf, settings, user, client_obj):
    code = secrets.token_urlsafe(64)
    state = secrets.token_urlsafe(64)
    request = rf.get(
        reverse('oauth2:token', kwargs={'client_name': client_obj.name}),
        {'error': 'access_denied', 'state': state}, username=user.username
    )
    request.session[settings.OAUTH2_SESSION_STATE_KEY] = state
    response = views.TokenView.as_view()(request, client_name=client_obj.name)
    assert response.status_code == 403


def test_token_bogus(rf, settings, user, client_obj):
    code = secrets.token_urlsafe(64)
    state = secrets.token_urlsafe(64)
    request = rf.get(
        reverse('oauth2:token', kwargs={'client_name': client_obj.name}),
        {'code': code, 'state': state}, username=user.username
    )
    request.session[settings.OAUTH2_SESSION_STATE_KEY] = secrets.token_urlsafe(64)
    response = views.TokenView.as_view()(request, client_name=client_obj.name)
    assert response.status_code == 403
