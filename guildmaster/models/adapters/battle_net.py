from django.db import models

from guildmaster.models.clients import Client, ClientAdapterControl


class BattleNetClientManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(adapter=Client.BATTLE_NET)


class BattleNetClient(Client):
    _control = ClientAdapterControl(
        id=Client.BATTLE_NET,
        authorization_url='https://us.battle.net/oauth/authorize',
        token_url='https://us.battle.net/oauth/token',
        verification_url='https://us.battle.net/oauth/check_token',
        resource_url='https://us.api.battle.net/account/user',
        resource_key='battletag'
    )

    objects = BattleNetClientManager()

    class Meta:
        proxy = True
