# -*- coding: utf-8 -*-
from concurrency.admin import ConcurrentModelAdmin
from django.contrib import admin

from redirect.models import Redirect


@admin.register(Redirect)
class RedirectAdmin(ConcurrentModelAdmin):
    list_display = ('path', 'url', 'location')
    list_display_links = ('path',)
    fields = ('version', 'path', 'url', 'location', 'created', 'modified')
    readonly_fields = ('url', 'created', 'modified')
    save_on_top = True
