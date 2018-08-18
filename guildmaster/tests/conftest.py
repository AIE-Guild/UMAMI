import pytest
from django.core.management import call_command

from guildmaster.adapters import Adapter


@pytest.fixture(params=Adapter.adapters, ids=lambda x: x.id)
def adapter(request):
    return request.param


@pytest.fixture()
def test_db(db, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'test.json')
