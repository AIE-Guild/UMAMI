from concurrency import fields
from django.db import models
from django.utils.translation import ugettext_lazy as _


class ConcurrencyMixin(models.Model):
    """A mixin to add optimistic concurrency control to a model."""

    version = fields.AutoIncVersionField(verbose_name=_('entity version'))

    class Meta:
        abstract = True


class TimestampMixin(models.Model):
    """A mixin to add creation and update timestamps to a model."""

    created = models.DateTimeField(verbose_name=_('created at'), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_('updated at'), auto_now_add=True)

    class Meta:
        abstract = True
