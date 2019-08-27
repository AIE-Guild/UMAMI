from concurrency.admin import ConcurrentModelAdmin
from django.contrib import admin

from guildmaster.models import Client, DiscordAccount, Token


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('provider_id', 'name', 'enabled', 'client_id', 'callback')
    list_display_links = ('name',)
    list_editable = ('enabled',)
    fields = ('provider_id', 'name', 'enabled', 'callback', 'client_id', 'client_secret', 'scopes', 'scope_override')
    readonly_fields = ('callback', 'scopes')
    prepopulated_fields = {'name': ('provider_id',)}
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


@admin.register(DiscordAccount)
class DiscordAccountAdmin(ConcurrentModelAdmin):
    list_display = ('__str__', 'id', 'email', 'verified', 'mfa_enabled')
    list_display_links = ('__str__',)
    list_filter = ('verified', 'mfa_enabled')
    fieldsets = (
        ('Local', {'fields': ('users', 'version')}),
        ('Remote', {'fields': ('id', 'username', 'discriminator', 'email', 'verified', 'mfa_enabled')}),
    )
    readonly_fields = ('id', 'username', 'discriminator', 'users', 'email', 'verified', 'mfa_enabled')
    search_fields = ('username', 'discriminator', 'email', 'users__username', 'users__email')
