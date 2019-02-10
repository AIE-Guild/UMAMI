import datetime as dt
import secrets

import pytest

from oauth2 import core


@pytest.fixture(scope='session')
def token_response():
    return {
        'access_token': secrets.token_urlsafe(64),
        'token_type': 'Bearer',
        'refresh_token': secrets.token_urlsafe(64),
        'expires_in': 3600,
        'comment': 'This is a test token.',
    }


def test_token_data_from_response(response_factory, token_response, tf_datestr, tf_date):
    response = response_factory(token_response, date=tf_datestr)
    token_data = core.TokenData.from_response(response=response)
    assert all(
        [
            getattr(token_data, k) == token_response.get(k)
            for k in ['access_token', 'token_type', 'refresh_token', 'expires_in']
        ]
    )
    assert token_data.timestamp == tf_date
    assert token_data.expiry == tf_date + dt.timedelta(seconds=token_data.expires_in)


def test_token_data_non_expiring(response_factory, token_response, tf_datestr, tf_date):
    token_response = {k: v for k, v in token_response.items() if k != 'expires_in'}
    response = response_factory(token_response, date=tf_datestr)
    token_data = core.TokenData.from_response(response=response)
    assert all(
        [
            getattr(token_data, k) == token_response.get(k)
            for k in ['access_token', 'token_type', 'refresh_token', 'expires_in']
        ]
    )
    assert token_data.timestamp == tf_date
    assert token_data.expiry is None
