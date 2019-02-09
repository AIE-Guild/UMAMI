# -*- coding: utf-8 -*-
import re
import uuid
from urllib.parse import urljoin

from concurrency.fields import AutoIncVersionField
from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _

from redirect.conf import settings


class URLPathValidator(validators.RegexValidator):
    pchar_re = r'[\w\-_\.!~\*\'\(\)%:@&=\+\$,]'
    regex = re.compile(r'^/?{0}*(?:;{0}*)?(?:/{0}*(?:;{0}*)?)*$'.format(pchar_re))
    message = _('Enter a valid URL path.')
    code = 'invalid_path'


class Redirect(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = AutoIncVersionField()
    path = models.CharField(max_length=32, unique=True, validators=[URLPathValidator()])
    location = models.URLField(max_length=2048)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.path = urljoin('/', self.path)
        super().save(*args, **kwargs)

    @property
    def url(self):
        scheme = 'https' if settings.REDIRECT_SECURE else 'http'
        return '{0}://{1}{2}'.format(scheme, settings.REDIRECT_HOST, self.path)
