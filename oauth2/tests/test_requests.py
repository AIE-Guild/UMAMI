import secrets

import pytest
import requests

from oauth2.exceptions import AuthorizationRequired
from oauth2.models import Token
from oauth2.requests import TokenAuth


@pytest.fixture()
def tf_token(tf_user, tf_resource):
    token = Token.objects.create(
        user=tf_user, resource=tf_resource, access_token=secrets.token_urlsafe(64), token_type='bearer'
    )
    return token


def test_token_auth(tf_token, requests_mock):
    requests_mock.get('https://test.aie-guild.org', text='fert!')
    auth = TokenAuth(tf_token)
    requests.get('https://test.aie-guild.org', auth=auth)
    assert requests_mock.request_history[0].headers['Authorization'] == f'Bearer {tf_token.access_token}'


def test_token_fail(tf_token, requests_mock):
    requests_mock.get('https://test.aie-guild.org', status_code=403)
    auth = TokenAuth(tf_token)
    with pytest.raises(AuthorizationRequired):
        requests.get('https://test.aie-guild.org', auth=auth)
