from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from guildmaster.models import mixins


class BaseAccount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE)
    resource = models.ForeignKey(
        'guildmaster.Resource', verbose_name=_('oauth2 resource'), null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        abstract = True


class DiscordAccount(mixins.TimestampMixin, BaseAccount):
    id = models.CharField(max_length=20, primary_key=True)
    username = models.CharField(verbose_name=_('username'), max_length=32)
    discriminator = models.CharField(verbose_name=_('dsicriminator'), max_length=4)
    email = models.EmailField(verbose_name=_('email'))
    verified = models.BooleanField(verbose_name=_('verified'), default=False)
    mfa_enabled = models.BooleanField(verbose_name=_('MFA enabled'), default=False)
    avatar = models.CharField(verbose_name=_('avatar'), max_length=64, blank=True, default='')

    class Meta:
        ordering = ('username', 'discriminator')

    def __str__(self):
        return f"{self.username}#{self.discriminator}"
