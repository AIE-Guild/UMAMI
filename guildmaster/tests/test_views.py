import http
import secrets

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode

from guildmaster import views
from guildmaster.utils import reverse


@pytest.fixture()
def user():
    user, __ = User.objects.get_or_create(username='henry', email='henry@aie-guild.org')
    return user


def test_authorization(rf, user, tf_client):
    request = rf.get(
        reverse('guildmaster:authorization', kwargs={'client_name': tf_client.name}), username=user.username
    )
    response = views.AuthorizationView.as_view()(request, client_name=tf_client.name)
    assert response.status_code == 302
    assert response.url.startswith(tf_client.authorization_url)


def test_authorization_state(rf, user, tf_client, settings):
    request = rf.get(
        reverse('guildmaster:authorization', kwargs={'client_name': tf_client.name}), username=user.username
    )
    response = views.AuthorizationView.as_view()(request, client_name=tf_client.name)
    assert request.session[settings.GUILDMASTER_SESSION_STATE_KEY] in response.url


def test_authorization_return_url(rf, user, tf_client, settings):
    request = rf.get(
        reverse('guildmaster:authorization', kwargs={'client_name': tf_client.name}), username=user.username
    )
    views.AuthorizationView.as_view()(request, client_name=tf_client.name)
    assert request.session[settings.GUILDMASTER_SESSION_RETURN_KEY] == settings.GUILDMASTER_RETURN_URL

    request = rf.get(
        '{}?{}'.format(
            reverse('guildmaster:authorization', kwargs={'client_name': tf_client.name}),
            urlencode({f'{settings.GUILDMASTER_RETURN_FIELD_NAME}': '/other'}),
        ),
        username=user.username,
    )
    views.AuthorizationView.as_view()(request, client_name=tf_client.name)
    assert request.session[settings.GUILDMASTER_SESSION_RETURN_KEY] == '/other'


def test_token(rf, settings, user, tf_client, requests_mock):
    expected = {
        'access_token': secrets.token_urlsafe(64),
        'refresh_token': secrets.token_urlsafe(64),
        'token_type': 'bearer',
        'expires_in': 3600,
    }
    requests_mock.post(
        tf_client.token_url, json=expected, headers={'Date': timezone.now().strftime('%a, %d %b %Y %H:%M:%S %Z')}
    )
    userinfo = {'username': 'henry', 'discriminator': '1234', 'battletag': 'henry#1234'}
    requests_mock.get(tf_client.userinfo_url, json=userinfo)
    code = secrets.token_urlsafe(64)
    state = secrets.token_urlsafe(64)
    request = rf.get(
        reverse('guildmaster:token', kwargs={'client_name': tf_client.name}),
        {'code': code, 'state': state},
        username=user.username,
    )
    request.user = user
    request.session[settings.GUILDMASTER_SESSION_STATE_KEY] = state
    response = views.TokenView.as_view()(request, client_name=tf_client.name)
    assert response.status_code == 302
    assert requests_mock.called
    assert requests_mock.call_count == 2
    assert requests_mock.request_history[0].method == 'POST'
    assert requests_mock.request_history[0].url == tf_client.token_url
    assert requests_mock.request_history[1].method == 'GET'
    assert requests_mock.request_history[1].url == tf_client.userinfo_url


def test_token_error(rf, settings, user, tf_client):
    secrets.token_urlsafe(64)
    state = secrets.token_urlsafe(64)
    request = rf.get(
        reverse('guildmaster:token', kwargs={'client_name': tf_client.name}),
        {'error': 'access_denied', 'state': state},
        username=user.username,
    )
    request.session[settings.GUILDMASTER_SESSION_STATE_KEY] = state
    response = views.TokenView.as_view()(request, client_name=tf_client.name)
    assert response.status_code == 403


def test_token_bogus(rf, settings, user, tf_client):
    code = secrets.token_urlsafe(64)
    state = secrets.token_urlsafe(64)
    request = rf.get(
        reverse('guildmaster:token', kwargs={'client_name': tf_client.name}),
        {'code': code, 'state': state},
        username=user.username,
    )
    request.session[settings.GUILDMASTER_SESSION_STATE_KEY] = secrets.token_urlsafe(64)
    response = views.TokenView.as_view()(request, client_name=tf_client.name)
    assert response.status_code == 403


def test_discord_list(settings, client, user):
    client.force_login(user)
    response = client.get(reverse('guildmaster:discord-list'))
    assert response.status_code == http.HTTPStatus.OK
