import abc
from collections import namedtuple
from typing import Mapping

APIResource = namedtuple('APIResource', 'key tag')


class ClientDriver(metaclass=abc.ABCMeta):
    _registry = {}
    http_basic_auth = True

    def __init_subclass__(cls, **kwargs) -> None:
        if cls.name in cls._registry:
            raise AttributeError(f"'{cls.name}' label is already in use by '{cls._registry[cls.name]}'")
        else:
            cls._registry[cls.name] = cls
        super().__init_subclass__(**kwargs)

    @classmethod
    def create(cls, name) -> 'ClientDriver':
        try:
            return cls._registry[name]()
        except KeyError:
            return

    @classmethod
    def get_driver_names(cls):
        return [x for x in cls._registry]

    @classmethod
    def get_drivers(cls):
        return cls._registry.values()

    @classmethod
    def get_choices(cls):
        return [(x.name, x.description) for x in cls.get_drivers()]

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """A unique name for the driver class."""

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """The driver description."""

    @property
    @abc.abstractmethod
    def authorization_url(self) -> str:
        """OAuth2 authorization endpoint."""

    @property
    @abc.abstractmethod
    def token_url(self) -> str:
        """OAuth2 token endpoint."""

    @property
    @abc.abstractmethod
    def revocation_url(self) -> str:
        """OAuth2 revocation endpoint."""

    @property
    @abc.abstractmethod
    def scopes(self) -> tuple:
        """Default OAuth2 scopes."""

    @property
    @abc.abstractmethod
    def resource_url(self) -> str:
        """API resource info endpoint."""

    @abc.abstractmethod
    def get_resource_ids(self, data: Mapping[str, str]) -> APIResource:
        """Method to extract resource identifiers from an API resource response."""


class DiscordDriver(ClientDriver):
    """
    Discord API - https://discordapp.com/developers/docs/intro
    """

    http_basic_auth = False
    name = 'discord'
    description = 'Discord'
    authorization_url = 'https://discordapp.com/api/oauth2/authorize'
    token_url = 'https://discordapp.com/api/oauth2/token'
    verification_url = None
    revocation_url = 'https://discordapp.com/api/oauth2/token/revoke'
    scopes = ('identify', 'email')
    resource_url = 'https://discordapp.com/api/v6/users/@me'

    def get_resource_ids(self, data: Mapping[str, str]) -> APIResource:
        return APIResource(key=data['id'], tag=f"{data['username']}#{data['discriminator']}")


class BattleNetDriver(ClientDriver):
    """
    Battle.net API - https://develop.battle.net/documentation
    """

    http_basic_auth = False
    name = 'battle_net_us'
    description = 'Battle.net US'
    authorization_url = 'https://us.battle.net/oauth/authorize'
    token_url = 'https://us.battle.net/oauth/token'
    verification_url = 'https://us.battle.net/oauth/check_token'
    revocation_url = None
    scopes = ('wow.profile', 'sc2.profile')
    resource_url = 'https://us.battle.net/oauth/userinfo'

    def get_resource_ids(self, data: Mapping[str, str]) -> APIResource:
        return APIResource(key=data['id'], tag=data['battletag'])


class EVEOnlineDriver(ClientDriver):
    """
    EVE Online ESI - https://docs.esi.evetech.net/
    """

    http_basic_auth = False
    name = 'eve_online'
    description = 'EVE Online'
    authorization_url = 'https://login.eveonline.com/oauth/authorize'
    token_url = 'https://login.eveonline.com/oauth/token'
    verification_url = 'https://us.battle.net/oauth/check_token'
    revocation_url = 'https://login.eveonline.com/oauth/revoke'
    scopes = ('wow.profile', 'sc2.profile')
    resource_url = 'https://esi.evetech.net/verify/'

    def get_resource_ids(self, data: Mapping[str, str]) -> APIResource:
        return APIResource(key=str(data['CharacterID']), tag=data['CharacterName'])
