import abc


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


class DiscordDriver(ClientDriver):
    name = 'discord'
    description = 'Discord'
    authorization_url = 'https://discordapp.com/api/oauth2/authorize'
    token_url = 'https://discordapp.com/api/oauth2/token'
    revocation_url = 'https://discordapp.com/api/oauth2/token/revoke'
    scopes = ('identity', 'email')


class BattleNetDriver(ClientDriver):
    name = 'battle_net'
    description = 'Battle.net'
    authorization_url = 'https://us.battle.net/oauth/authorize'
    token_url = 'https://us.battle.net/oauth/token'
    verification_url = 'https://us.battle.net/oauth/check_token'
    revocation_url = None
    scopes = ('wow.profile', 'sc2.profile')
