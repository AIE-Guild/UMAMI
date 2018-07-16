import uuid
from typing import TypeVar, Dict, Any
import time
import datetime as dt

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from concurrency.fields import AutoIncVersionField

C = TypeVar('C', bound='Client')
T = TypeVar('T', bound='Token')
U = TypeVar('U', bound=get_user_model())


class TokenManager(models.Manager):

    def create_token(self, data: Dict[str, Any], user: U, client: C, timestamp: float = None) -> T:
        if timestamp is None:
            timestamp = time.time()
        offset = int(data['expires_in'])
        expiry = dt.datetime.fromtimestamp(timestamp + offset, tz=timezone.get_default_timezone())
        return self.create(
            user=user,
            client=client,
            access_token=data['access_token'],
            token_type=data['token_type'],
            refresh_token=data.get('refresh_token', ''),
            expiry=expiry
        )


class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = AutoIncVersionField()
    created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_('modified'), auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE)
    client = models.ForeignKey('Client', verbose_name=_('client'), on_delete=models.CASCADE)
    token_type = models.CharField(verbose_name=_('token type'), max_length=50, default='bearer')
    access_token = models.TextField(verbose_name=_('access token'))
    refresh_token = models.TextField(verbose_name=_('refresh token'), blank=True)
    expiry = models.DateTimeField(verbose_name=('expires at'), blank=True, null=True)
    resource = models.CharField(verbose_name=_('resource'), max_length=191, blank=True,
                                help_text='An optional resource tag.')

    objects = TokenManager()

    class Meta:
        verbose_name = _('token')
        verbose_name_plural = _('tokens')
