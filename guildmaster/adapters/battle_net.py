from guildmaster.adapters.oauth2 import OAuth2Adapter


class BattleNetAdapter(OAuth2Adapter):
    id = 'battle_net'
    name = 'Battle.net'
    authorization_url = 'https://us.battle.net/oauth/authorize',
    token_url = 'https://us.battle.net/oauth/token',
    verification_url = 'https://us.battle.net/oauth/check_token',
    resource_url = 'https://us.api.battle.net/account/user',
    resource_key = 'battletag'
