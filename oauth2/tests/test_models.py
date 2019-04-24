import datetime as dt
import secrets

import pytest
from django.utils import timezone

from oauth2 import exceptions, models


def test_name(tf_client):
    assert tf_client.name == 'test_client'


def test_driver(tf_client):
    driver = tf_client.driver
    assert tf_client.service == driver.name


def test_scopes(tf_client):
    driver = tf_client.driver
    assert tf_client.scopes == driver.scopes


def test_scope_override(tf_client):
    tf_client.scope_override = 'foo bar   baz '
    tf_client.save()
    assert tf_client.scopes == ('foo', 'bar', 'baz')


def test_create_token(tf_user, tf_client):
    # pylint: disable=duplicate-code
    token = models.Token.objects.create(
        client=tf_client,
        user=tf_user,
        token_type='bearer',
        access_token=secrets.token_urlsafe(64),
        refresh_token=secrets.token_urlsafe(64),
        timestamp=timezone.now(),
        expires_in=3600,
        scope='email identify',
        redirect_uri='https://test.aie-guild.org/auth/token',
    )
    assert isinstance(token, models.Token)


def test_token_not_state(tf_token):
    assert not tf_token.is_stale


def test_token_is_state(tf_token):
    tf_token.timestamp = tf_token.timestamp - dt.timedelta(seconds=tf_token.expires_in)
    tf_token.save()
    assert tf_token.is_stale


def test_token_no_expiry(tf_token):
    tf_token.expires_in = None
    tf_token.save()


def test_refresh_token(requests_mock, tf_client, tf_token, tf_datestr, tf_token_response):
    requests_mock.post(tf_client.token_url, json=tf_token_response, headers={'Date': tf_datestr})
    tf_token.refresh()
    assert requests_mock.request_history[0].method == 'POST'
    assert requests_mock.request_history[0].url == tf_client.token_url
    assert tf_token.access_token == tf_token_response['access_token']
    assert tf_token.refresh_token == tf_token_response['refresh_token']
    assert tf_token.scope == tf_token_response['scope']


def test_refresh_token_error(requests_mock, tf_client, tf_token, tf_error_response):
    requests_mock.post(tf_client.token_url, json=tf_error_response)
    with pytest.raises(exceptions.OAuth2Error) as exc:
        tf_token.refresh()
    assert exc.value.error == tf_error_response['error']


def test_refresh_token_fail(requests_mock, tf_client, tf_token, tf_error_response):
    requests_mock.post(tf_client.token_url, status_code=500)
    with pytest.raises(IOError) as exc:
        tf_token.refresh()
    assert 'Failed to fetch access token' in str(exc.value)


def test_refresh_token_not_supported(tf_client, tf_token, tf_datestr):
    tf_token.refresh_token = ''
    tf_token.save()
    with pytest.raises(exceptions.TokenRefreshError) as exc:
        tf_token.refresh()
    assert 'No authorization client found.' in str(exc.value)
