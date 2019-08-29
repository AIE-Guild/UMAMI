import pytest


def test_providers(tf_provider):
    if tf_provider.name == 'discord':
        assert tf_provider.description == 'Discord'
    elif tf_provider.name == 'battle-net':
        assert tf_provider.description == 'Battle.net'
    else:
        pytest.fail(f"unknown provider: {tf_provider.name}")


def test_provider_registry_error():
    from guildmaster.models import Provider

    class Foo(Provider):
        name = 'example'
        description = 'Foo'
        authorization_url = 'https://example.com/api/oauth2/authorize'
        token_url = 'https://example.com/api/oauth2/token'
        revocation_url = 'https://example.com/api/oauth2/token/revoke'
        verification_url = 'https://example.com/api/oauth2/token/verify'
        default_scopes = ('identify', 'email')
        http_basic_auth = False

    with pytest.raises(AttributeError):
        class Bar(Provider):
            name = 'example'
            description = 'Bar'
            authorization_url = 'https://example.com/api/oauth2/authorize'
            token_url = 'https://example.com/api/oauth2/token'
            revocation_url = 'https://example.com/api/oauth2/token/revoke'
            verification_url = 'https://example.com/api/oauth2/token/verify'
            default_scopes = ('identify', 'email')
            http_basic_auth = False
