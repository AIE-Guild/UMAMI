# -*- coding: utf-8 -*-
from concurrency.admin import ConcurrentModelAdmin
from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from umami.models import Bulletin


@admin.register(Bulletin)
class BulletinAdmin(ConcurrentModelAdmin, MarkdownxModelAdmin):
    list_display = ('title', 'public', 'published')
    fields = ('title', 'version', 'publish', 'public', 'body', 'created', 'published', 'modified')
    readonly_fields = ('created', 'published', 'modified')
