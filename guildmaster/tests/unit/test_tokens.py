import time

import pytest
from django.contrib.auth.models import User

from guildmaster import models


@pytest.fixture()
def user():
    return User.objects.create(username='hoots')


@pytest.fixture()
def client(test_db):
    return models.Client.objects.first()


def test_token_create(user, client):
    data = {
        'access_token': '8ACOHlt9RpUBkRxRdAn5HVHioHx-YWAmFiWwbsCNaBw',
        'token_type': 'bearer',
        'refresh_token': '3bwccDOiorq2xfoMpCtRrn3meY8oEUdIiki2SLuFCJA',
        'expires_in': 3600
    }
    token = models.Token.objects.create_token(data, user, client, timestamp=1000000000)
    assert token.user == user
    assert token.client == client
    assert token.access_token == '8ACOHlt9RpUBkRxRdAn5HVHioHx-YWAmFiWwbsCNaBw'
    assert token.token_type == 'bearer'
    assert token.refresh_token == '3bwccDOiorq2xfoMpCtRrn3meY8oEUdIiki2SLuFCJA'
    assert token.expiry.timestamp() == 1000003600


def test_token_create_partial(user, client):
    data = {
        'access_token': '8ACOHlt9RpUBkRxRdAn5HVHioHx-YWAmFiWwbsCNaBw',
        'token_type': 'bearer',
        'expires_in': 3600
    }
    token = models.Token.objects.create_token(data, user, client, timestamp=1000000000)
    assert token.user == user
    assert token.client == client
    assert token.access_token == '8ACOHlt9RpUBkRxRdAn5HVHioHx-YWAmFiWwbsCNaBw'
    assert token.token_type == 'bearer'
    assert token.refresh_token == ''
    assert token.expiry.timestamp() == 1000003600


def test_token_create_no_date(monkeypatch, user, client):
    monkeypatch.setattr(time, 'time', lambda: 1000000000)
    data = {
        'access_token': '8ACOHlt9RpUBkRxRdAn5HVHioHx-YWAmFiWwbsCNaBw',
        'token_type': 'bearer',
        'refresh_token': '3bwccDOiorq2xfoMpCtRrn3meY8oEUdIiki2SLuFCJA',
        'expires_in': 3600
    }
    token = models.Token.objects.create_token(data, user, client)
    assert token.user == user
    assert token.client == client
    assert token.access_token == '8ACOHlt9RpUBkRxRdAn5HVHioHx-YWAmFiWwbsCNaBw'
    assert token.token_type == 'bearer'
    assert token.refresh_token == '3bwccDOiorq2xfoMpCtRrn3meY8oEUdIiki2SLuFCJA'
    assert token.expiry.timestamp() == 1000003600
