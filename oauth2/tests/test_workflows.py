import datetime as dt
import secrets

import pytest

from oauth2 import workflows


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
