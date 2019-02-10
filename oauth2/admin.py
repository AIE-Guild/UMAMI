from django.contrib import admin

from oauth2.models import Client, Resource, Token


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'service', 'enabled', 'client_id', 'callback')
    list_display_links = ('name',)
    list_editable = ('enabled',)
    fields = ('name', 'service', 'enabled', 'callback', 'client_id', 'client_secret', 'scopes', 'scope_override')
    readonly_fields = ('callback', 'scopes')
    prepopulated_fields = {'name': ('service',)}
    save_on_top = True


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'key', 'tag')
    list_display_links = ('id',)
    fields = ('id', 'client', ('key', 'tag'), 'users')
    readonly_fields = ('id', 'client', 'key', 'tag', 'users')
    list_filter = ('client',)
    search_fields = ('client', 'users')
    save_on_top = True


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'resource', 'token_type', 'scope', 'expiry')
    list_display_links = ('id',)
    fields = (
        'id',
        'client',
        'resource',
        'token_type',
        'scope',
        'access_token',
        'refresh_token',
        'expiry',
        'redirect_uri',
    )
    readonly_fields = (
        'id',
        'client',
        'resource',
        'token_type',
        'scope',
        'access_token',
        'refresh_token',
        'expiry',
        'redirect_uri',
    )
    search_fields = ('client', 'resource__users')
    save_on_top = True

    def has_add_permission(self, request, obj=None):
        # pylint: disable=arguments-differ
        return False
