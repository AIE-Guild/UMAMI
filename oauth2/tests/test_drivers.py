import pytest

from oauth2 import drivers


def test_driver(service):
    driver = drivers.ClientDriver.create(service.name)
    assert driver.name == service.name
    assert driver.description == service.description
    assert driver.authorization_url == service.authorization_url
    assert driver.token_url == service.token_url
    assert driver.revocation_url == service.revocation_url
    assert driver.scopes == service.scopes


def test_registry_conflict():
    class Foo(drivers.ClientDriver):
        name = 'foo'
        description = 'Foo'
        authorization_url = 'https://example.com/api/oauth2/authorize'
        token_url = 'https://example.com/api/oauth2/token'
        revocation_url = 'https://example.com/api/oauth2/revoke'
        scopes = ('test',)

    with pytest.raises(AttributeError):
        class Bar(drivers.ClientDriver):
            name = 'foo'
            description = 'Foo'
            authorization_url = 'https://example.com/api/oauth2/authorize'
            token_url = 'https://example.com/api/oauth2/token'
            revocation_url = 'https://example.com/api/oauth2/revoke'
            scopes = ('test',)
