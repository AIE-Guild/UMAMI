from django.contrib import admin

from oauth2.models import Client, Token


@admin.register(Client)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ('name', 'service', 'enabled', 'client_id', 'callback')
    list_display_links = ('name',)
    list_editable = ('enabled',)
    fields = ('name', 'service', 'enabled', 'callback', 'client_id', 'client_secret', 'scopes', 'scope_override')
    readonly_fields = ('callback', 'scopes')
    save_on_top = True


@admin.register(Token)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'client', 'resource_id', 'resource_tag', 'token_type', 'expiry')
    list_display_links = ('id',)
    fields = ('id', 'user', 'client', 'resource_id', 'resource_tag', 'token_type', 'access_token', 'refresh_token',
              'expiry')
    readonly_fields = ('id', 'user', 'client', 'resource_id', 'resource_tag', 'token_type', 'access_token',
                       'refresh_token', 'expiry')
    save_on_top = True

    def has_add_permission(self, request, obj=None):
        return False
