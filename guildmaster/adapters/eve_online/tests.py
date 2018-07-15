from guildmaster.models import Client
from guildmaster.adapters.eve_online.models import EveOnlineClient


def test_load():
    assert Client._adapter_class(EveOnlineClient._control.id) == EveOnlineClient


def test_manager():
    assert all([isinstance(EveOnlineClient, x) for x in EveOnlineClient.objects.all()])
