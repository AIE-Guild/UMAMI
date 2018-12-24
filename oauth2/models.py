import logging
import uuid
from typing import Dict, Optional

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models, transaction
from django.urls import NoReverseMatch, reverse
from django.utils.translation import ugettext_lazy as _

from oauth2 import drivers

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.SlugField(verbose_name=_('name'), unique=True, max_length=64)
    service = models.CharField(verbose_name=_('service'), max_length=64, choices=drivers.ClientDriver.get_choices())
    enabled = models.BooleanField(verbose_name=_('enabled'), default=True)
    client_id = models.CharField(verbose_name=_('client id'), max_length=191)
    client_secret = models.CharField(verbose_name=_('client secret'), max_length=191)
    scope_override = models.TextField(verbose_name=_('scope override'), blank=True, default='')

    def __str__(self):
        return self.name

    @property
    def scopes(self) -> Optional[tuple]:
        driver = drivers.ClientDriver.create(self.service)
        if driver is None:
            return
        if self.scope_override:
            return tuple(self.scope_override.split())
        else:
            return driver.scopes

    @property
    def description(self):
        return self.driver.description

    @property
    def driver(self) -> drivers.ClientDriver:
        return drivers.ClientDriver.create(self.service)

    @property
    def callback(self):
        try:
            return reverse('oauth2:token', kwargs={'client_name': self.name})
        except NoReverseMatch:
            return


class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE)
    client = models.ForeignKey('Client', verbose_name=_('client'), on_delete=models.CASCADE)
    resource_id = models.CharField(verbose_name=_('resource ID'), max_length=64, blank=True, default='')
    resource_tag = models.CharField(verbose_name=_('resource tag'), max_length=64, blank=True, default='')
    token_type = models.CharField(verbose_name=_('token type'), max_length=64, default='bearer')
    access_token = models.TextField(verbose_name=_('access token'))
    refresh_token = models.TextField(verbose_name=_('refresh token'), blank=True, default='')
    expiry = models.DateTimeField(verbose_name=_('expiry'), blank=True, null=True)

    class Meta:
        unique_together = ('user', 'client', 'resource_id')

    def __str__(self):
        return str(self.id)

    @property
    def authorization(self):
        return f'{self.token_type.title()} {self.access_token}'
