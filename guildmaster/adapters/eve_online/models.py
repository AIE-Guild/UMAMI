from django.db import models

from guildmaster.models.clients import Client, ClientAdapterControl


class EveOnlineClientManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(adapter=Client.EVE)


class EveOnlineClient(Client):
    _control = ClientAdapterControl(
        id=Client.EVE,
        authorization_url='https://login.eveonline.com/oauth/authorize',
        token_url='https://login.eveonline.com/oauth/token',
        revocation_url='https://login.eveonline.com/oauth/revoke',
        resource_url='https://esi.evetech.net/verify/',
        resource_key='CharacterID'
    )

    objects = EveOnlineClientManager()

    class Meta:
        proxy = True
