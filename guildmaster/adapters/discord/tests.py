from guildmaster.models import Client
from guildmaster.adapters.discord.models import DiscordClient


def test_load():
    assert Client._adapter_class(DiscordClient._control.id) == DiscordClient


def test_manager():
    assert all([isinstance(DiscordClient, x) for x in DiscordClient.objects.all()])
