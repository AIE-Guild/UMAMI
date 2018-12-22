import datetime as dt
import secrets

import pytest
import requests

from oauth2 import exceptions, workflows, models


@pytest.fixture(scope='session')
def token_response():
    return {
        'access_token': secrets.token_urlsafe(64),
        'token_type': 'Bearer',
        'refresh_token': secrets.token_urlsafe(64),
        'expires_in': 3600,
        'comment': 'This is a test token.'
    }


def test_token_data_from_response(response_factory, token_response, sample_user, sample_client, sample_datestr,
                                  sample_date):
    response = response_factory(token_response, date=sample_datestr)
    token_data = workflows.TokenData.from_response(user=sample_user, client=sample_client, response=response)
    assert token_data.user == sample_user
    assert token_data.client == sample_client
    assert all([getattr(token_data, k) == token_response.get(k) for k in
                ['access_token', 'token_type', 'refresh_token', 'expires_in']])
    assert token_data.timestamp == sample_date
    assert token_data.expiry == sample_date + dt.timedelta(seconds=token_data.expires_in)


def test_token_data_non_expiring(response_factory, token_response, sample_user, sample_client, sample_datestr,
                                 sample_date):
    token_response = {k: v for k, v in token_response.items() if k != 'expires_in'}
    response = response_factory(token_response, date=sample_datestr)
    token_data = workflows.TokenData.from_response(user=sample_user, client=sample_client, response=response)
    assert token_data.user == sample_user
    assert token_data.client == sample_client
    assert all([getattr(token_data, k) == token_response.get(k) for k in
                ['access_token', 'token_type', 'refresh_token', 'expires_in']])
    assert token_data.timestamp == sample_date
    assert token_data.expiry is None


def test_get_authorization_url(sample_client, rf, settings):
    driver = sample_client.driver
    request = rf.get('/')
    url = workflows.get_authorization_url(request, sample_client)
    assert url.startswith(driver.authorization_url)
    assert 'response_type=code' in url
    assert f'client_id={sample_client.client_id}' in url
    assert f"state={request.session[settings.OAUTH2_SESSION_STATE_KEY]}" in url
    assert request.session[settings.OAUTH2_SESSION_RETURN_KEY] == settings.OAUTH2_RETURN_URL

    url = workflows.get_authorization_url(request, sample_client, return_url='/foo')
    assert url.startswith(driver.authorization_url)
    assert 'response_type=code' in url
    assert f'client_id={sample_client.client_id}' in url
    assert f"state={request.session[settings.OAUTH2_SESSION_STATE_KEY]}" in url
    assert request.session[settings.OAUTH2_SESSION_RETURN_KEY] == '/foo'


def test_authorization_response_state(rf, sample_client, settings):
    data = {
        'code': secrets.token_urlsafe(16),
        'state': secrets.token_urlsafe(16)
    }
    request = rf.get('/auth/token', data=data)
    request.session[settings.OAUTH2_SESSION_STATE_KEY] = data['state']
    workflows.validate_authorization_response(request, sample_client)
    request.session[settings.OAUTH2_SESSION_STATE_KEY] = secrets.token_hex(16)
    with pytest.raises(ValueError):
        workflows.validate_authorization_response(request, sample_client)


def test_authorization_response_error(rf, sample_client, settings):
    data = {
        'error': 'temporarily_unavailable',
        'error_description': 'server offline for maintenance',
        'error_uri': 'https://tools.ietf.org/html/rfc6749#section-4.1.2',
        'state': secrets.token_urlsafe(16)
    }
    request = rf.get('/auth/token', data=data)
    request.session[settings.OAUTH2_SESSION_STATE_KEY] = None
    with pytest.raises(ValueError):
        workflows.validate_authorization_response(request, sample_client)
    request.session[settings.OAUTH2_SESSION_STATE_KEY] = data['state']
    with pytest.raises(exceptions.OAuth2Error) as exc:
        workflows.validate_authorization_response(request, sample_client)
    assert str(exc.value) == ('temporarily_unavailable: server offline for maintenance '
                              '(https://tools.ietf.org/html/rfc6749#section-4.1.2)')
    assert exc.value.error == data['error']
    assert exc.value.description == data['error_description']
    assert exc.value.uri == data['error_uri']


def test_fetch_tokens(rf, sample_client, requests_mock, token_response, sample_datestr, sample_user):
    requests_mock.post(sample_client.driver.token_url, json=token_response, headers={'Date': sample_datestr})
    data = {
        'code': secrets.token_urlsafe(16),
        'state': secrets.token_urlsafe(16)
    }
    request = rf.get('/auth/token', username=sample_user, data=data)
    token = workflows.fetch_tokens(request, sample_client)
    assert isinstance(token, models.Token)
    assert token.access_token == token_response['access_token']


def test_fetch_tokens_failure(rf, sample_client, requests_mock, token_response, sample_datestr, sample_user):
    requests_mock.post(sample_client.driver.token_url, exc=requests.ConnectionError())
    data = {
        'code': secrets.token_urlsafe(16),
        'state': secrets.token_urlsafe(16)
    }
    request = rf.get('/auth/token', username=sample_user, data=data)
    with pytest.raises(IOError):
        workflows.fetch_tokens(request, sample_client)
