from guildmaster.adapters.oauth2 import OAuth2Adapter


class DiscordAdapter(OAuth2Adapter):
    id = 'discord'
    name = 'Discord'
    authorization_url = 'https://discordapp.com/api/oauth2/authorize',
    token_url = 'https://discordapp.com/api/oauth2/token',
    revocation_url = 'https://discordapp.com/api/oauth2/token/revoke',
    scope = ('identity', 'email')
    resource_url = 'https://discordapp.com/api/users/@me',
    resource_key = 'id'
