import secrets

import pytest
import requests

from guildmaster import exceptions, models


def test_get_authorization_url(tf_client, rf, settings):
    request = rf.get('/')
    url = tf_client.get_authorization_url(request)
    assert url.startswith(tf_client.authorization_url)
    assert 'response_type=code' in url
    assert f'client_id={tf_client.client_id}' in url
    assert f"state={request.session[settings.GUILDMASTER_SESSION_STATE_KEY]}" in url
    assert request.session[settings.GUILDMASTER_SESSION_RETURN_KEY] == settings.GUILDMASTER_RETURN_URL

    url = tf_client.get_authorization_url(request, return_url='/foo')
    assert url.startswith(tf_client.authorization_url)
    assert 'response_type=code' in url
    assert f'client_id={tf_client.client_id}' in url
    assert f"state={request.session[settings.GUILDMASTER_SESSION_STATE_KEY]}" in url
    assert request.session[settings.GUILDMASTER_SESSION_RETURN_KEY] == '/foo'


def test_authorization_response_state(rf, tf_client, settings):
    data = {'code': secrets.token_urlsafe(16), 'state': secrets.token_urlsafe(16)}
    request = rf.get('/auth/token', data=data)
    request.session[settings.GUILDMASTER_SESSION_STATE_KEY] = data['state']
    tf_client.validate_state(request)
    request.session[settings.GUILDMASTER_SESSION_STATE_KEY] = secrets.token_hex(16)
    with pytest.raises(ValueError):
        tf_client.validate_state(request)


def test_authorization_response_error(rf, tf_client, settings):
    data = {
        'error': 'temporarily_unavailable',
        'error_description': 'server offline for maintenance',
        'error_uri': 'https://tools.ietf.org/html/rfc6749#section-4.1.2',
        'state': secrets.token_urlsafe(16),
    }
    request = rf.get('/auth/token', data=data)
    request.session[settings.GUILDMASTER_SESSION_STATE_KEY] = data['state']
    with pytest.raises(exceptions.OAuth2Error) as exc:
        tf_client.validate_authorization_response(request)
    assert str(exc.value) == (
        'temporarily_unavailable: server offline for maintenance ' '(https://tools.ietf.org/html/rfc6749#section-4.1.2)'
    )
    assert exc.value.error == data['error']
    assert exc.value.description == data['error_description']
    assert exc.value.uri == data['error_uri']


def test_fetch_token(rf, tf_client, requests_mock, tf_token_response, tf_datestr, tf_user):
    userinfo = {'username': 'henry', 'discriminator': '1234', 'battletag': 'henry#1234'}
    requests_mock.post(tf_client.token_url, json=tf_token_response, headers={'Date': tf_datestr})
    requests_mock.get(tf_client.userinfo_url, json=userinfo)
    data = {'code': secrets.token_urlsafe(16), 'state': secrets.token_urlsafe(16)}
    request = rf.get('/auth/token', username=tf_user, data=data)
    token = tf_client.get_access_token(request)
    assert isinstance(token, models.Token)
    assert token.access_token == tf_token_response['access_token']


def test_fetch_token_auth_error(rf, tf_client, requests_mock, tf_token_response, tf_datestr, tf_user):
    error = {
        'error': 'temporarily_unavailable',
        'error_description': 'server offline for maintenance',
        'error_uri': 'https://tools.ietf.org/html/rfc6749#section-4.1.2',
        'state': secrets.token_urlsafe(16),
    }
    requests_mock.post(tf_client.token_url, json=error)
    data = {'code': secrets.token_urlsafe(16), 'state': secrets.token_urlsafe(16)}
    request = rf.get('/auth/token', username=tf_user, data=data)
    with pytest.raises(exceptions.OAuth2Error) as exc:
        tf_client.get_access_token(request)
    assert str(exc.value) == (
        'temporarily_unavailable: server offline for maintenance ' '(https://tools.ietf.org/html/rfc6749#section-4.1.2)'
    )
    assert exc.value.error == error['error']
    assert exc.value.description == error['error_description']
    assert exc.value.uri == error['error_uri']


def test_fetch_token_auth_failure(rf, tf_client, requests_mock, tf_token_response, tf_datestr, tf_user):
    requests_mock.post(tf_client.token_url, exc=requests.ConnectionError())
    data = {'code': secrets.token_urlsafe(16), 'state': secrets.token_urlsafe(16)}
    request = rf.get('/auth/token', username=tf_user, data=data)
    with pytest.raises(IOError):
        tf_client.get_access_token(request)
