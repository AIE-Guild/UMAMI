import datetime as dt
import secrets

import pytest
import requests

from oauth2 import exceptions, models, workflows


@pytest.fixture(scope='session')
def token_response():
    return {
        'access_token': secrets.token_urlsafe(64),
        'token_type': 'Bearer',
        'refresh_token': secrets.token_urlsafe(64),
        'expires_in': 3600,
        'comment': 'This is a test token.'
    }


@pytest.fixture(scope='session')
def resource_response():
    return {
        'id': secrets.token_hex(16),
        'battletag': 'User#1234',
        'username': 'User',
        'discriminator': '1234'
    }


def test_token_data_from_response(response_factory, token_response, tf_user, tf_client, tf_datestr,
                                  tf_date):
    response = response_factory(token_response, date=tf_datestr)
    token_data = workflows.TokenData.from_response(user=tf_user, client=tf_client, response=response)
    assert token_data.user == tf_user
    assert token_data.client == tf_client
    assert all([getattr(token_data, k) == token_response.get(k) for k in
                ['access_token', 'token_type', 'refresh_token', 'expires_in']])
    assert token_data.timestamp == tf_date
    assert token_data.expiry == tf_date + dt.timedelta(seconds=token_data.expires_in)


def test_token_data_non_expiring(response_factory, token_response, tf_user, tf_client, tf_datestr,
                                 tf_date):
    token_response = {k: v for k, v in token_response.items() if k != 'expires_in'}
    response = response_factory(token_response, date=tf_datestr)
    token_data = workflows.TokenData.from_response(user=tf_user, client=tf_client, response=response)
    assert token_data.user == tf_user
    assert token_data.client == tf_client
    assert all([getattr(token_data, k) == token_response.get(k) for k in
                ['access_token', 'token_type', 'refresh_token', 'expires_in']])
    assert token_data.timestamp == tf_date
    assert token_data.expiry is None


def test_get_authorization_url(tf_client, rf, settings):
    driver = tf_client.driver
    request = rf.get('/')
    url = workflows.get_authorization_url(request, tf_client)
    assert url.startswith(driver.authorization_url)
    assert 'response_type=code' in url
    assert f'client_id={tf_client.client_id}' in url
    assert f"state={request.session[settings.OAUTH2_SESSION_STATE_KEY]}" in url
    assert request.session[settings.OAUTH2_SESSION_RETURN_KEY] == settings.OAUTH2_RETURN_URL

    url = workflows.get_authorization_url(request, tf_client, return_url='/foo')
    assert url.startswith(driver.authorization_url)
    assert 'response_type=code' in url
    assert f'client_id={tf_client.client_id}' in url
    assert f"state={request.session[settings.OAUTH2_SESSION_STATE_KEY]}" in url
    assert request.session[settings.OAUTH2_SESSION_RETURN_KEY] == '/foo'


def test_authorization_response_state(rf, tf_client, settings):
    data = {
        'code': secrets.token_urlsafe(16),
        'state': secrets.token_urlsafe(16)
    }
    request = rf.get('/auth/token', data=data)
    request.session[settings.OAUTH2_SESSION_STATE_KEY] = data['state']
    workflows.validate_authorization_response(request, tf_client)
    request.session[settings.OAUTH2_SESSION_STATE_KEY] = secrets.token_hex(16)
    with pytest.raises(ValueError):
        workflows.validate_authorization_response(request, tf_client)


def test_authorization_response_error(rf, tf_client, settings):
    data = {
        'error': 'temporarily_unavailable',
        'error_description': 'server offline for maintenance',
        'error_uri': 'https://tools.ietf.org/html/rfc6749#section-4.1.2',
        'state': secrets.token_urlsafe(16)
    }
    request = rf.get('/auth/token', data=data)
    request.session[settings.OAUTH2_SESSION_STATE_KEY] = None
    with pytest.raises(ValueError):
        workflows.validate_authorization_response(request, tf_client)
    request.session[settings.OAUTH2_SESSION_STATE_KEY] = data['state']
    with pytest.raises(exceptions.OAuth2Error) as exc:
        workflows.validate_authorization_response(request, tf_client)
    assert str(exc.value) == ('temporarily_unavailable: server offline for maintenance '
                              '(https://tools.ietf.org/html/rfc6749#section-4.1.2)')
    assert exc.value.error == data['error']
    assert exc.value.description == data['error_description']
    assert exc.value.uri == data['error_uri']


def test_fetch_tokens(rf, tf_client, requests_mock, token_response, resource_response, tf_datestr, tf_user):
    requests_mock.post(tf_client.driver.token_url, json=token_response, headers={'Date': tf_datestr})
    requests_mock.get(tf_client.driver.resource_url, json=resource_response)
    data = {
        'code': secrets.token_urlsafe(16),
        'state': secrets.token_urlsafe(16)
    }
    request = rf.get('/auth/token', username=tf_user, data=data)
    token = workflows.fetch_tokens(request, tf_client)
    assert isinstance(token, models.Token)
    assert token.access_token == token_response['access_token']


def test_fetch_tokens_token_failure(rf, tf_client, requests_mock, token_response, tf_datestr, tf_user):
    requests_mock.post(tf_client.driver.token_url, exc=requests.ConnectionError())
    data = {
        'code': secrets.token_urlsafe(16),
        'state': secrets.token_urlsafe(16)
    }
    request = rf.get('/auth/token', username=tf_user, data=data)
    with pytest.raises(IOError):
        workflows.fetch_tokens(request, tf_client)


def test_fetch_tokens_resource_failure(rf, tf_client, requests_mock, token_response, resource_response, tf_datestr,
                                       tf_user):
    requests_mock.post(tf_client.driver.token_url, json=token_response, headers={'Date': tf_datestr})
    requests_mock.get(tf_client.driver.resource_url, exc=requests.ConnectionError())
    data = {
        'code': secrets.token_urlsafe(16),
        'state': secrets.token_urlsafe(16)
    }
    request = rf.get('/auth/token', username=tf_user, data=data)
    with pytest.raises(IOError):
        workflows.fetch_tokens(request, tf_client)
