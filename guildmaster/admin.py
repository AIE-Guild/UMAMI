from concurrency.admin import ConcurrentModelAdmin
from django.contrib import admin

from guildmaster import forms, models


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
    filter_horizontal = ('scopes',)


@admin.register(models.ClientScope)
class ClientScopeAdmin(ConcurrentModelAdmin):
    list_display = ('adapter', 'name')
    list_display_links = ('name',)


@admin.register(models.BattleNetClient)
class BattleNetClientAdmin(ClientAdmin):
    pass

@admin.register(models.DiscordClient)
class DiscordClientAdmin(ClientAdmin):
    pass

@admin.register(models.EveOnlineClient)
class EveOnlineClientAdmin(ClientAdmin):
    pass