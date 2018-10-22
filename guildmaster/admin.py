from concurrency.admin import ConcurrentModelAdmin
from django.contrib import admin

from guildmaster import models


@admin.register(models.Client)
class ClientAdmin(ConcurrentModelAdmin):
    list_display = ('name', 'adapter', 'slug', 'client_id', 'is_enabled')
    list_display_links = ('name',)
    fieldsets = (
        (None, {
            'fields': ('adapter', ('name', 'slug', 'version'), 'is_enabled')
        }),
        (('OAuth2 Options', {
            'fields': ('client_id', 'client_secret', 'scope')
        })),
        ('Advanced Options', {
            'classes': ('collapse',),
            'fields': ('options',)
        })
    )
    readonly_fields = ('scope',)
    prepopulated_fields = {'slug': ['adapter']}
