import pytest

SERVICE_DATA = [
    {
        'name': 'discord',
        'description': 'Discord',
        'authorization_url': 'https://discordapp.com/api/oauth2/authorize',
        'token_url': 'https://discordapp.com/api/oauth2/token',
        'revocation_url': 'https://discordapp.com/api/oauth2/token/revoke',
        'scopes': ('identity', 'email')
    }
]


@pytest.fixture(scope='session', params=SERVICE_DATA, ids=lambda x: x['name'])
def services(request):
    return request.param
