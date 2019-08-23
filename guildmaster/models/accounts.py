import uuid

from concurrency import fields
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Account(models.Model):
    key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = fields.AutoIncVersionField(verbose_name=_('entity version'))
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, verbose_name=_('users'), related_name='accounts', related_query_name='account'
    )
    created = models.DateTimeField(verbose_name=_('created at'), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_('updated at'), auto_now=True)


class DiscordAccount(Account):
    id = models.CharField(max_length=20, primary_key=True)
    username = models.CharField(verbose_name=_('username'), max_length=32)
    discriminator = models.CharField(verbose_name=_('discriminator'), max_length=4)
    email = models.EmailField(verbose_name=_('email'))
    verified = models.BooleanField(verbose_name=_('verified'), default=False)
    mfa_enabled = models.BooleanField(verbose_name=_('MFA enabled'), default=False)
    avatar = models.CharField(verbose_name=_('avatar'), max_length=64, blank=True, default='')

    class Meta:
        ordering = ('username', 'discriminator')

    def __str__(self):
        return f"{self.username}#{self.discriminator}"
