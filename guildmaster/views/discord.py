import logging

import requests
from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import DeleteView

from guildmaster import exceptions
from guildmaster.models import Client, DiscordAccount, DiscordProvider, Token
from guildmaster.requests import TokenAuth
from guildmaster.utils import reverse

logger = logging.getLogger(__name__)


class DiscordAccountSync(LoginRequiredMixin, View):
    provider = DiscordProvider
    client = None
    token = None
    userinfo = {}

    def dispatch(self, request, *args, **kwargs):
        try:
            self.client = Client.objects.get(provider_id=self.provider.name)
        except Client.DoesNotExist:
            logger.error(f"no client configured for {self.provider.description}")
            messages.error(request, f"No client configured for {self.provider.description}")
            return http.HttpResponseRedirect(reverse('guildmaster:discord-list'))

        try:
            self.token = Token.objects.get(client=self.client, user=request.user)
        except Token.DoesNotExist:
            auth_url = reverse(
                'guildmaster:authorization',
                kwargs={'client_name': self.provider.name},
                query={settings.GUILDMASTER_RETURN_FIELD_NAME: reverse('guildmaster:discord-sync')},
            )
            return http.HttpResponseRedirect(auth_url)

        auth = TokenAuth(self.token)
        try:
            r = requests.get(self.client.provider.base_url + '/users/@me', auth=auth)
            r.raise_for_status()
        except exceptions.AuthorizationRequiredError as exc:
            logger.error("unable to access requested resource: %s", exc)
            self.token.delete()
            messages.error(request, f"Cannot access {self.provider.description} user data; please try again")
            return http.HttpResponseRedirect(reverse('guildmaster:discord-list'))
        except requests.RequestException as exc:
            logger.error("communication error: %s", exc)
            messages.error(request, f"Cannot communicate with {self.provider.description}: {exc}")
            return http.HttpResponseRedirect(reverse('guildmaster:discord-list'))
        self.userinfo = r.json()

        if request.method == 'GET':
            return self.get(request)
        elif request.method == 'POST':
            return self.post(request)
        return self.http_method_not_allowed()

    def get(self, request):
        return render(request, "guildmaster/discordaccount_sync.html", context=self.userinfo)

    def post(self, request):
        data = {
            k: v
            for k, v in self.userinfo.items()
            if k in ['id', 'username', 'discriminator', 'email', 'verified', 'mfa_enabled', 'avatar']
        }
        try:
            account, ok = DiscordAccount.objects.update_or_create(id=data['id'], defaults=data)
        except Exception as exc:
            messages.error(request, f"Cannot synchronize {self.provider.description} account {data['id']}: {exc}")
            return http.HttpResponseRedirect(reverse('guildmaster:discord-list'))
        account.users.add(request.user)

        messages.success(request, f"Synchronized {self.provider.description} account: {account}")
        return http.HttpResponseRedirect(reverse('guildmaster:discord-list'))


class DiscordAccountList(LoginRequiredMixin, ListView):
    model = DiscordAccount

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(users=self.request.user)


class DiscordAccountDelete(LoginRequiredMixin, DeleteView):
    model = DiscordAccount
    success_url = reverse('guildmaster:discord-list')
