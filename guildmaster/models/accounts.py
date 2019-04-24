import dataclasses
import uuid

from concurrency import fields
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


@dataclasses.dataclass(frozen=True)
class Service:
    name: str
    description: str
    authorization_url: str
    token_url: str
    scopes: tuple
    verification_url: str = None
    revocation_url: str = None
    http_basic_auth: bool = False


class Account(models.Model):
    key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = fields.AutoIncVersionField(verbose_name=_('entity version'))
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, verbose_name=_('users'), related_name='accounts', related_query_name='account'
    )
    created = models.DateTimeField(verbose_name=_('created at'), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_('updated at'), auto_now=True)

    services = []  # service registry

    def __init_subclass__(cls, **kwargs) -> None:
        name = cls.service.name
        for other in [x for x in cls.services if x.service.name == name]:
            raise AttributeError(f"'{name}' label is already in use by '{other.service.name}'")
        else:
            cls.services.append(cls)
        super().__init_subclass__(**kwargs)

    @classmethod
    def get_service_choices(cls):
        return [(x.service.name, x.service.description) for x in cls.services]


class DiscordAccount(Account):
    id = models.CharField(max_length=20, primary_key=True)
    username = models.CharField(verbose_name=_('username'), max_length=32)
    discriminator = models.CharField(verbose_name=_('discriminator'), max_length=4)
    email = models.EmailField(verbose_name=_('email'))
    verified = models.BooleanField(verbose_name=_('verified'), default=False)
    mfa_enabled = models.BooleanField(verbose_name=_('MFA enabled'), default=False)
    avatar = models.CharField(verbose_name=_('avatar'), max_length=64, blank=True, default='')

    service = Service(
        name='discord',
        description='Discord',
        authorization_url='https://discordapp.com/api/oauth2/authorize',
        token_url='https://discordapp.com/api/oauth2/token',
        revocation_url='https://discordapp.com/api/oauth2/token/revoke',
        scopes=('identify', 'email'),
    )

    class Meta:
        ordering = ('username', 'discriminator')

    def __str__(self):
        return f"{self.username}#{self.discriminator}"
