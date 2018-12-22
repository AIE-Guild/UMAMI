import datetime as dt
import secrets

import pytest
import pytz
from django.utils import timezone

from oauth2 import workflows


@pytest.fixture(scope='session')
def sample_datestr():
    return 'Sun, 12 Jan 1997 12:00:00 UTC'


@pytest.fixture(scope='session')
def sample_date():
    date = dt.datetime(1997, 1, 12, 12, 00, 00, 0)
    return pytz.timezone(timezone.get_default_timezone_name()).localize(date)


@pytest.fixture(scope='session')
def token_response():
    return {
        'access_token': secrets.token_urlsafe(64),
        'token_type': 'Bearer',
        'refresh_token': secrets.token_urlsafe(64),
        'expires_in': 3600,
        'comment': 'This is a test token.'
    }


def test_parse_http_date(sample_datestr, sample_date):
    assert workflows.parse_http_date(sample_datestr) == sample_date


def test_token_data_from_response(response_factory, token_response, sample_user, sample_client, sample_date):
    response = response_factory(token_response, date=sample_date)
    token_data = workflows.TokenData.from_response(user=sample_user, client=sample_client, response=response)
    assert token_data.user == sample_user
    assert token_data.client == sample_client
    assert all([getattr(token_data, k) == token_response.get(k) for k in
                ['access_token', 'token_type', 'refresh_token', 'expires_in']])
    assert token_data.timestamp == sample_date
    assert token_data.expiry == sample_date + dt.timedelta(seconds=token_data.expires_in)


def test_token_data_non_expiring(response_factory, token_response, sample_user, sample_client, sample_date):
    token_response = {k: v for k, v in token_response.items() if k != 'expires_in'}
    response = response_factory(token_response, date=sample_date)
    token_data = workflows.TokenData.from_response(user=sample_user, client=sample_client, response=response)
    assert token_data.user == sample_user
    assert token_data.client == sample_client
    assert all([getattr(token_data, k) == token_response.get(k) for k in
                ['access_token', 'token_type', 'refresh_token', 'expires_in']])
    assert token_data.timestamp == sample_date
    assert token_data.expiry is None
