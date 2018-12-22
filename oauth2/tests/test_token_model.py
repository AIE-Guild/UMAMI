import datetime as dt
import secrets

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from oauth2 import models, utils


@pytest.fixture()
def user():
    return User.objects.create(username='ralff', email='ralff@aie-guild.org')


@pytest.fixture()
def client(service):
    return models.Client.objects.create(
        service=service.name,
        name='test_client',
        client_id=secrets.token_hex(16),
        client_secret=secrets.token_urlsafe(16)
    )


@pytest.fixture()
def token_data():
    return {
        'token_type': 'bearer',
        'access_token': secrets.token_urlsafe(64),
        'refresh_token': secrets.token_urlsafe(64),
        'expires_in': 3600,
        'example_parameter': 'example_value'
    }


def test_create(user, client):
    token = models.Token.objects.create(
        user=user,
        client=client,
        token_type='bearer',
        access_token=secrets.token_urlsafe(64),
        refresh_token=secrets.token_urlsafe(64),
        expiry=timezone.now() + dt.timedelta(seconds=3600)
    )
    assert isinstance(token, models.Token)


def test_extract(user, client, token_data, response_factory):
    response = response_factory(token_data)
    ts = utils.parse_http_date(response.headers['Date'])
    token = models.Token.objects.extract(user, client, response)
    assert token.user == user
    assert token.client == client
    diff = token.expiry - ts
    assert diff == dt.timedelta(seconds=int(token_data['expires_in']))
