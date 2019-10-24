import datetime as dt

import pytest
import requests

from guildmaster.exceptions import AuthorizationRequiredError
from guildmaster.models import Token


def test_token_auth(tf_token, requests_mock):
    requests_mock.get('https://test.aie-guild.org', text='fert!')
    requests.get('https://test.aie-guild.org', auth=tf_token.auth)
    assert requests_mock.request_history[0].headers['Authorization'] == f'Bearer {tf_token.access_token}'


def test_token_auth_refresh(tf_client, tf_token, requests_mock, tf_token_response, tf_datestr):
    tf_token.timestamp = tf_token.timestamp - dt.timedelta(seconds=tf_token.expires_in * Token.REFRESH_COEFFICIENT + 1)
    requests_mock.get('https://test.aie-guild.org', text='fert!')
    requests_mock.post(tf_client.token_url, json=tf_token_response, headers={'Date': tf_datestr})
    requests.get('https://test.aie-guild.org', auth=tf_token.auth)
    assert requests_mock.request_history[1].headers['Authorization'] == f"Bearer {tf_token_response['access_token']}"
    assert requests_mock.request_history[0].method == 'POST'


def test_token_fail(tf_token, requests_mock):
    requests_mock.get('https://test.aie-guild.org', status_code=403)
    with pytest.raises(AuthorizationRequiredError):
        requests.get('https://test.aie-guild.org', auth=tf_token.auth)
