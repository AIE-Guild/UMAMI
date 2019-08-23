import abc


class Provider(abc.ABC):
    """Base class for provider classes that provides a registry."""

    registry = {}

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.name in cls.registry:
            raise AttributeError(f"{cls.name} already in use by {cls.registry[cls.name]}")
        cls.registry[cls.name] = cls

    def __str__(self):
        return self.name

    @property
    @abc.abstractmethod
    def name(self):
        pass

    @property
    @abc.abstractmethod
    def description(self):
        pass

    @property
    @abc.abstractmethod
    def base_url(self):
        pass

    @property
    @abc.abstractmethod
    def authorization_url(self):
        pass

    @property
    @abc.abstractmethod
    def token_url(self):
        pass

    @property
    @abc.abstractmethod
    def revocation_url(self):
        pass

    @property
    @abc.abstractmethod
    def verification_url(self):
        pass

    @property
    @abc.abstractmethod
    def default_scopes(self):
        pass

    @property
    @abc.abstractmethod
    def http_basic_auth(self):
        pass

    @classmethod
    def choices(cls):
        return [(k, v.description) for k, v in cls.registry.items()]


class DiscordProvider(Provider):
    """A provider for Discord, https://discordapp.com/ ."""

    name = 'discord'
    description = 'Discord'
    base_url = 'https://discordapp.com/api'
    authorization_url = 'https://discordapp.com/api/oauth2/authorize'
    token_url = 'https://discordapp.com/api/oauth2/token'
    revocation_url = 'https://discordapp.com/api/oauth2/token/revoke'
    verification_url = None
    default_scopes = ('identify', 'email')
    http_basic_auth = False
