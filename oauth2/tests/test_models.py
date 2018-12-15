import secrets

from oauth2 import drivers, models


def test_clients(driver_data):
    client = models.Client.objects.create(
        driver=driver_data['name'],
        name='test_client',
        client_id=secrets.token_hex(16),
        client_secret=secrets.token_urlsafe(16)
    )
    driver = drivers.ClientDriver.create(driver_data['name'])
    assert client.driver == driver.name
    assert client.name == 'test_client'
    assert client.scopes == driver.scopes


def test_clients_scope_override(driver_data):
    client = models.Client.objects.create(
        driver=driver_data['name'],
        name='test_client',
        client_id=secrets.token_hex(16),
        client_secret=secrets.token_urlsafe(16),
        scope_override='foo bar   baz '
    )
    driver = drivers.ClientDriver.create(driver_data['name'])
    assert client.driver == driver.name
    assert client.name == 'test_client'
    assert client.scopes == ('foo', 'bar', 'baz')
