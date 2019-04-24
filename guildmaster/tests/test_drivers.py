import pytest

from guildmaster import drivers


def test_driver(service):
    driver = drivers.ClientDriver.factory(service.name)
    assert driver.name == service.name
    assert driver.description == service.description
    assert driver.authorization_url == service.authorization_url
    assert driver.token_url == service.token_url
    assert driver.revocation_url == service.revocation_url
    assert driver.scopes == service.scopes


def test_registry_conflict():
    # pylint: disable=unused-variable
    class Foo(drivers.ClientDriver):
        name = 'foo'
        description = 'Foo'
        authorization_url = 'https://example.com/api/oauth2/authorize'
        token_url = 'https://example.com/api/oauth2/token'
        revocation_url = 'https://example.com/api/oauth2/revoke'
        scopes = ('test',)
        resource_url = 'https://example.com/api/userinfo'

        def get_resource_key(self, data):
            return data['userid']

        def get_resource_tag(self, data):
            return data['username']

    with pytest.raises(AttributeError):

        class Bar(drivers.ClientDriver):
            name = 'foo'
            description = 'Foo'
            authorization_url = 'https://example.com/api/oauth2/authorize'
            token_url = 'https://example.com/api/oauth2/token'
            revocation_url = 'https://example.com/api/oauth2/revoke'
            scopes = ('test',)
            resource_url = 'https://example.com/api/userinfo'

            def get_resource_key(self, data):
                return data['userid']

            def get_resource_tag(self, data):
                return data['username']
