import secrets

import pytest

from oauth2 import models


@pytest.fixture()
def client(services):
    return models.Client.objects.create(
        service=services['name'],
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


def test_authorization_request(client, rf):
    driver = client.driver
    request = rf.get('/')
    url, state = client.get_authorization_request(request)
    assert url.startswith(driver.authorization_url)
    assert 'response_type=code' in url
    assert f'client_id={client.client_id}' in url
    assert f'state={state}' in url

    url, state = client.get_authorization_request(request, 'foobar')
    assert f'state=foobar' in url
