from concurrency.admin import ConcurrentModelAdmin
from django.contrib import admin

from guildmaster import models


@admin.register(models.Client)
class ClientAdmin(ConcurrentModelAdmin):
    list_display = ('name', 'adapter', 'slug', 'client_id', 'is_enabled')
    list_display_links = ('name',)
    fieldsets = (
        (None, {
            'fields': ('adapter', ('name', 'slug', 'version'))
        }),
        (('OAuth2 Options', {
            'fields': ('client_id', 'client_secret', 'scopes')
        })),
        ('Advanced Options', {
            'classes': ('collapse',),
            'fields': ('options',)
        })
    )
    prepopulated_fields = {'slug': ['name']}
    filter_horizontal = ('scopes',)


@admin.register(models.ClientScope)
class ClientScopeAdmin(ConcurrentModelAdmin):
    list_display = ('adapter', 'name')
    list_display_links = ('name',)
