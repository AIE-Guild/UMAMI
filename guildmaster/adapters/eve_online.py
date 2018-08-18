from guildmaster.adapters.oauth2 import OAuth2Adapter


class EveOnlineAdapter(OAuth2Adapter):
    id = 'eve_online'
    name = 'EVE Online'
    authorization_url = 'https://login.eveonline.com/oauth/authorize',
    token_url = 'https://login.eveonline.com/oauth/token',
    revocation_url = 'https://login.eveonline.com/oauth/revoke',
    resource_url = 'https://esi.evetech.net/verify/',
    resource_key = 'CharacterID'
