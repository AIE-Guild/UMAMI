import pytest

from oauth2 import drivers


def test_driver(services):
    driver = drivers.ClientDriver.create(services['name'])
    assert driver.name == services['name']
    assert driver.description == services['description']
    assert driver.authorization_url == services['authorization_url']
    assert driver.token_url == services['token_url']
    assert driver.revocation_url == services['revocation_url']
    assert driver.scopes == services['scopes']


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
