import pytest

DRIVER_DATA = [
    {
        'name': 'discord',
        'description': 'Discord',
        'authorization_url': 'https://discordapp.com/api/oauth2/authorize',
        'token_url': 'https://discordapp.com/api/oauth2/token',
        'revocation_url': 'https://discordapp.com/api/oauth2/token/revoke',
        'scopes': ('identity', 'email')
    }
]


@pytest.fixture(scope='session', params=DRIVER_DATA, ids=lambda x: x['name'])
def driver_data(request):
    return request.param
