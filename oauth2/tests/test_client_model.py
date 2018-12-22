import base64
import secrets

import pytest

from oauth2 import exceptions, models


@pytest.fixture()
def client(service):
    return models.Client.objects.create(
        service=service.name,
        name='test_client',
        client_id=secrets.token_hex(16),
        client_secret=secrets.token_urlsafe(16)
    )


def test_name(client):
    assert client.name == 'test_client'


def test_driver(client):
    driver = client.driver
    assert client.service == driver.name


def test_scopes(client):
    driver = client.driver
    assert client.scopes == driver.scopes


def test_scope_override(client):
    client.scope_override = 'foo bar   baz '
    client.save()
    assert client.scopes == ('foo', 'bar', 'baz')
