# -*- coding: utf-8 -*-
import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from concurrency.fields import AutoIncVersionField
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class BulletinManager(models.Manager):
    def get_published(self, group_size=None):
        """

        Args:
            group_size (optional): Active bulletins will be returned as a list of group_size arity tuples.

        Returns:
            list: Either a list of bulletins or a list of bulletin tuples.

        """
        publist = [x for x in self.get_queryset().filter(publish=True)]
        if group_size is None:
            return publist
        else:
            return [tuple(publist[i:i + group_size]) for i in range(0, len(publist), group_size)]


class Bulletin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = AutoIncVersionField()
    publish = models.BooleanField(default=False)
    title = models.CharField(max_length=250)
    body = MarkdownxField()
    published = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = BulletinManager()

    class Meta:
        verbose_name = _('bulletin')
        verbose_name_plural = _('bulletins')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.publish and self.published is None:
            self.published = timezone.now()
        super().save(*args, **kwargs)

    @property
    def as_html(self):
        return markdownify(self.body)
