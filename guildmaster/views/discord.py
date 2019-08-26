import logging

from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.http import urlencode
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import DeleteView
from django.shortcuts import render
import requests

from guildmaster.models import Client, DiscordAccount, DiscordProvider, Token
from guildmaster.requests import TokenAuth

logger = logging.getLogger(__name__)


class DiscordAccountSync(LoginRequiredMixin, View):
    provider = DiscordProvider

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = None
        self.token = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.client = Client.objects.get(provider_id=self.provider.name)
        except Client.DoesNotExist:
            messages.error(request, f"No client configured for {self.provider.description}")
            return http.HttpResponseRedirect(reverse_lazy('guildmaster:discord-list'))

        try:
            self.token = Token.objects.get(client=self.client, user=request.user)
        except Token.DoesNotExist:
            auth_url = '{}?{}'.format(
                reverse_lazy('guildmaster:authorization', kwargs={'client_name': self.provider.name}),
                urlencode({settings.GUILDMASTER_RETURN_FIELD_NAME: reverse_lazy('guildmaster:discord-sync')}),
            )
            return http.HttpResponseRedirect(auth_url)

        if request.method == 'GET':
            return self.get(request)
        elif request.method == 'POST':
            return self.post(request)
        return self.http_method_not_allowed()

    def get(self, request):
        auth = TokenAuth(self.token)
        try:
            r = requests.get(self.client.provider.base_url + '/users/@me', auth=auth)
            r.raise_for_status()
        except requests.RequestException as exc:
            logger.error("communication error: %s", exc)
            messages.error(request, f"Cannot communicate with {self.provider.description}: {exc}")
            return http.HttpResponseRedirect(reverse_lazy('guildmaster:discord-list'))

        c = r.json()
        return render(request, "guildmaster/discordaccount_sync.html", context=c)

    def post(self, request):
        auth = TokenAuth(self.token)
        try:
            r = requests.get(self.client.provider.base_url + '/users/@me', auth=auth)
            r.raise_for_status()
        except requests.RequestException as exc:
            logger.error("communication error: %s", exc)
            messages.error(request, f"Cannot communicate with {self.provider.description}: {exc}")
            return http.HttpResponseRedirect(reverse_lazy('guildmaster:discord-list'))

        data = {
            k: v
            for k, v in r.json().items()
            if k in ['id', 'username', 'discriminator', 'email', 'verified', 'mfa_enabled', 'avatar']
        }
        try:
            account, ok = DiscordAccount.objects.update_or_create(id=data['id'], defaults=data)
        except Exception as exc:
            messages.error(request, f"Cannot synchronize {self.provider.description} account {data['id']}: {exc}")
            return http.HttpResponseRedirect(reverse_lazy('guildmaster:discord-list'))
        account.users.add(request.user)

        messages.success(request, f"Synchronized {self.provider.description} account: {account}")
        return http.HttpResponseRedirect(reverse_lazy('guildmaster:discord-list'))


class DiscordAccountList(LoginRequiredMixin, ListView):
    model = DiscordAccount

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(users=self.request.user)


class DiscordAccountDelete(LoginRequiredMixin, DeleteView):
    model = DiscordAccount
    success_url = reverse_lazy('guildmaster:discord-list')
