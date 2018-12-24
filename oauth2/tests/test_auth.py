import secrets

import pytest
import requests

from oauth2.auth import TokenAuth
from oauth2.models import Token


@pytest.fixture()
def tf_token(tf_user, tf_client):
    token = Token.objects.create(
        user=tf_user,
        client=tf_client,
        resource_id='012345',
        resource_tag='Test#1234',
        access_token=secrets.token_urlsafe(64),
        token_type='bearer'
    )
    return token


def test_token_auth(tf_token, requests_mock):
    requests_mock.get('https://test.aie-guild.org', text='fert!')
    auth = TokenAuth(tf_token)
    response = requests.get('https://test.aie-guild.org', auth=auth)
    assert response.request.headers['Authorization'] == f'Bearer {tf_token.access_token}'
