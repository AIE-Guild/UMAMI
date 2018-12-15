import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from oauth2 import drivers


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.CharField(verbose_name=_('driver'), max_length=50)
    name = models.CharField(verbose_name=_('name'), unique=True, max_length=50)
    enabled = models.BooleanField(verbose_name=_('enabled'), default=True)
    client_id = models.CharField(verbose_name=_('client id'), max_length=191)
    client_secret = models.CharField(verbose_name=_('client secret'), max_length=191)
    scope_override = models.TextField(verbose_name=_('scope override'))

    @property
    def scopes(self) -> tuple:
        driver = drivers.ClientDriver.create(self.driver)
        if self.scope_override:
            return tuple(self.scope_override.split())
        else:
            return driver.scopes


class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE)
    client = models.ForeignKey('Client', verbose_name=_('client'), on_delete=models.CASCADE)
    token_type = models.CharField(verbose_name=_('token type'), max_length=50, default='bearer')
    access_token = models.TextField(verbose_name=_('access token'))
    refresh_token = models.TextField(verbose_name=_('refresh token'), blank=True)
    expiry = models.DateTimeField(verbose_name=_('expiry'), blank=True, null=True)
