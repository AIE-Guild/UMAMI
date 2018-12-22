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


def test_authorization_response_state(client, rf):
    data = {
        'code': secrets.token_urlsafe(16),
        'state': secrets.token_urlsafe(16)
    }
    request = rf.get('/auth/token', data=data)
    client.validate_authorization_response(request, state=data['state'])
    with pytest.raises(ValueError):
        client.validate_authorization_response(request, state='deadbeef')


def test_authorization_response_error(client, rf):
    data = {
        'error': 'temporarily_unavailable',
        'error_description': 'server offline for maintenance',
        'error_uri': 'https://tools.ietf.org/html/rfc6749#section-4.1.2',
        'state': secrets.token_urlsafe(16)
    }
    request = rf.get('/auth/token', data=data)
    with pytest.raises(ValueError):
        client.validate_authorization_response(request, state='deadbeef')
    with pytest.raises(exceptions.OAuth2Error) as exc:
        client.validate_authorization_response(request, state=data['state'])
    assert str(exc.value) == ('temporarily_unavailable: server offline for maintenance '
                              '(https://tools.ietf.org/html/rfc6749#section-4.1.2)')
    assert exc.value.error == data['error']
    assert exc.value.description == data['error_description']
    assert exc.value.uri == data['error_uri']


def test_token_request(client, service, rf):
    data = {
        'code': secrets.token_urlsafe(16),
        'state': secrets.token_urlsafe(16)
    }
    request = rf.get('/auth/token', data=data)
    token_request = client.get_token_request(request)
    assert token_request.url == service.token_url
    if client.driver.http_basic_auth:
        assert token_request.headers['Authorization'] == 'Basic {}'.format(
            base64.b64encode(f'{client.client_id}:{client.client_secret}'.encode()).decode()
        )
        assert 'client_secret=' not in token_request.body
    else:
        assert f'client_secret={client.client_secret}' in token_request.body
    assert 'grant_type=' in token_request.body
    assert 'code=' in token_request.body
    assert 'redirect_uri=' in token_request.body
    assert f'client_id={client.client_id}' in token_request.body


def test_token_request_noauth(client, service, rf):
    data = {
        'code': secrets.token_urlsafe(16),
        'state': secrets.token_urlsafe(16)
    }
    request = rf.get('/auth/token', data=data)
    token_request = client.get_token_request(request)
    assert token_request.url == service.token_url
    if client.driver.http_basic_auth:
        assert token_request.headers['Authorization'] == 'Basic {}'.format(
            base64.b64encode(f'{client.client_id}:{client.client_secret}'.encode()).decode()
        )
        assert 'client_secret' not in token_request.body
    else:
        assert 'Authorization' not in token_request.headers
        assert 'client_secret' in token_request.body
    assert 'grant_type' in token_request.body
    assert 'code' in token_request.body
    assert 'redirect_uri' in token_request.body
    assert 'client_id' in token_request.body
