from django.contrib import admin

from guildmaster.models import Client, Resource, Token, DiscordAccount


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('service', 'name', 'enabled', 'client_id', 'callback')
    list_display_links = ('name',)
    list_editable = ('enabled',)
    fields = ('service', 'name', 'enabled', 'callback', 'client_id', 'client_secret', 'scopes', 'scope_override')
    readonly_fields = ('callback', 'scopes')
    prepopulated_fields = {'name': ('service',)}
    save_on_top = True


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'key', 'tag', 'created', 'updated')
    list_display_links = ('id',)
    fields = ('id', 'client', ('key', 'tag'), 'users', 'created', 'updated')
    readonly_fields = ('id', 'client', 'key', 'tag', 'users', 'created', 'updated')
    list_filter = ('client',)
    search_fields = ('client', 'users')
    save_on_top = True


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'resource', 'token_type', 'scope', 'timestamp')
    list_display_links = ('id',)
    fields = (
        'id',
        'client',
        'resource',
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
        'resource',
        'token_type',
        'scope',
        'access_token',
        'refresh_token',
        'timestamp',
        'expires_in',
        'expiry',
        'redirect_uri',
    )
    search_fields = ('client', 'resource__users')
    save_on_top = True

    def has_add_permission(self, request, obj=None):
        # pylint: disable=arguments-differ
        return False


@admin.register(DiscordAccount)
class DiscordAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'id', 'username', 'discriminator', 'email', 'verified', 'mfa_enabled')
    list_display_links = ('id', 'username')
    fields = ('user', 'id', 'username', 'discriminator', 'email', 'verified', 'mfa_enabled', 'avatar', 'resource')
    readonly_fields = (
        'user',
        'id',
        'username',
        'discriminator',
        'email',
        'verified',
        'mfa_enabled',
        'avatar',
        'resource',
    )
    save_on_top = True
