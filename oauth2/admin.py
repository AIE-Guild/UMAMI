from django.contrib import admin

from oauth2.models import Client, Resource, Token


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'service', 'enabled', 'client_id', 'callback')
    list_display_links = ('name',)
    list_editable = ('enabled',)
    fields = ('name', 'service', 'enabled', 'callback', 'client_id', 'client_secret', 'scopes', 'scope_override')
    readonly_fields = ('callback', 'scopes')
    save_on_top = True


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'user', 'key', 'tag')
    list_display_links = ('id',)
    fields = ('id', 'client', 'user', ('key', 'tag'))
    readonly_fields = ('id', 'client', 'user', 'key', 'tag')
    list_filter = ('client', 'user')
    search_fields = ('client', 'user')
    save_on_top = True


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'user', 'resource', 'token_type', 'expiry')
    list_display_links = ('id',)
    fields = ('id', 'client', 'user', 'resource', 'token_type', 'access_token', 'refresh_token', 'expiry')
    readonly_fields = ('id', 'client', 'user', 'resource', 'token_type', 'access_token', 'refresh_token', 'expiry')
    search_fields = ('client', 'user')
    save_on_top = True

    def has_add_permission(self, request, obj=None):
        # pylint: disable=arguments-differ
        return False
