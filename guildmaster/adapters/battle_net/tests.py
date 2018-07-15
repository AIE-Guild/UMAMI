from guildmaster.models import Client
from guildmaster.adapters.battle_net.models import BattleNetClient


def test_load():
    assert Client._adapter_class(BattleNetClient._control.id) == BattleNetClient


def test_manager():
    assert all([isinstance(BattleNetClient, x) for x in BattleNetClient.objects.all()])
