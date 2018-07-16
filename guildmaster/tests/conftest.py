import pytest
from django.core.management import call_command

from guildmaster import models


@pytest.fixture(params=models.Client._adapter_classes, ids=lambda x: x.adapter_id)
def adapter(request):
    return request.param


@pytest.fixture()
def test_db(db, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'test.json')
