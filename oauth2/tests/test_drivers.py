import pytest

from oauth2 import drivers


def test_driver(driver_data):
    driver = drivers.ClientDriver.create(driver_data['name'])
    assert driver.name == driver_data['name']
    assert driver.description == driver_data['description']
    assert driver.authorization_url == driver_data['authorization_url']
    assert driver.token_url == driver_data['token_url']
    assert driver.revocation_url == driver_data['revocation_url']
    assert driver.scopes == driver_data['scopes']


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
