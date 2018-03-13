# -*- coding: utf-8 -*-
from django.contrib import admin
from concurrency.admin import ConcurrentModelAdmin
from markdownx.admin import MarkdownxModelAdmin

from umami.models import Bulletin


@admin.register(Bulletin)
class BulletinAdmin(ConcurrentModelAdmin, MarkdownxModelAdmin):
    list_display = ('title', 'publish', 'published')
    fields = ('title', 'version', 'publish', 'body', 'created', 'published', 'modified')
    readonly_fields = ('created', 'published', 'modified')
    save_on_top = True
