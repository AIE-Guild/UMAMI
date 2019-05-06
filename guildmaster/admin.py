from django.contrib import admin

from guildmaster.models import Client, Token


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('provider', 'name', 'enabled', 'client_id', 'callback')
    list_display_links = ('name',)
    list_editable = ('enabled',)
    fields = ('provider', 'name', 'enabled', 'callback', 'client_id', 'client_secret', 'scopes', 'scope_override')
    readonly_fields = ('callback', 'scopes')
    prepopulated_fields = {'name': ('provider',)}
    save_on_top = True


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'user', 'token_type', 'scope', 'timestamp')
    list_display_links = ('id',)
    fields = (
        'id',
        'client',
        'user',
        'token_type',
        'scope',
        'access_token',
        'refresh_token',
        'timestamp',
        'expires_in',
        'expiry',
        'redirect_uri',
    )
    readonly_fields = (
        'id',
        'client',
        'user',
        'token_type',
        'scope',
        'access_token',
        'refresh_token',
        'timestamp',
        'expires_in',
        'expiry',
        'redirect_uri',
    )
    search_fields = ('client', 'user')
    save_on_top = True

    def has_add_permission(self, request, obj=None):
        # pylint: disable=arguments-differ
        return False
