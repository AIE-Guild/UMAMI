from django.db import models

from guildmaster.models.clients import Client


class DiscordClientManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(adapter=Client.DISCORD)


class DiscordClient(Client):
    adapter_id = Client.DISCORD
    authorization_url = 'https://discordapp.com/api/oauth2/authorize'
    token_url = 'https://discordapp.com/api/oauth2/token'
    revocation_url = 'https://discordapp.com/api/oauth2/token/revoke'
    resource_url = 'https://discordapp.com/api/users/@me'
    resource_key = 'id'

    objects = DiscordClientManager()

    class Meta:
        proxy = True
