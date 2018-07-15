import pytest

from guildmaster import models


@pytest.fixture(params=models.Client._adapter_classes, ids=lambda x: x.adapter_id)
def adapter(request):
    return request.param
