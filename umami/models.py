# -*- coding: utf-8 -*-
import uuid

from concurrency.fields import AutoIncVersionField
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class Bulletin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = AutoIncVersionField()
    publish = models.BooleanField(default=False)
    public = models.BooleanField(default=False)
    title = models.CharField(max_length=250)
    body = MarkdownxField()
    published = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('bulletin')
        verbose_name_plural = _('bulletins')
        ordering = ['-published']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.publish and self.published is None:
            self.published = timezone.now()
        super().save(*args, **kwargs)

    @property
    def as_html(self):
        return markdownify(self.body)
