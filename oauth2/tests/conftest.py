import pytest

from oauth2 import drivers


@pytest.fixture(scope='session', params=drivers.ClientDriver.get_drivers())
def service(request):
    return request.param
