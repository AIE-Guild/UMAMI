from guildmaster.adapters.base import Adapter


class OAuth2Adapter(Adapter):
    authorization_url = '/authorize',
    token_url = '/token',
    revocation_url = '/revoke',
