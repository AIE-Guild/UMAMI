from concurrency.admin import ConcurrentModelAdmin
from django.contrib import admin

from guildmaster import forms, models


@admin.register(models.Client)
class ClientAdmin(ConcurrentModelAdmin):
    form = forms.ClientForm
    list_display = ('name', 'adapter', 'slug', 'client_id', 'is_enabled')
    list_display_links = ('name',)
    fieldsets = (
        (None, {
            'fields': ('adapter', ('name', 'slug', 'version'), 'is_enabled')
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
