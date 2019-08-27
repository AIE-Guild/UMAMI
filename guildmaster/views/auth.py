import logging

from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import base

from guildmaster import exceptions, models

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class AuthorizationView(LoginRequiredMixin, base.View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        # pylint: disable=no-self-use
        client_name = kwargs.get('client_name')
        try:
            client = models.Client.objects.get(name=client_name)
        except models.Client.DoesNotExist:
            return http.HttpResponseServerError(f"Invalid client: {client_name}")
        return_url = request.GET.get(settings.GUILDMASTER_RETURN_FIELD_NAME)
        url = client.get_authorization_url(request, return_url)
        logger.info('Redirecting to: %s', url)
        return http.HttpResponseRedirect(url)


class TokenView(LoginRequiredMixin, base.View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        # pylint: disable=no-self-use
        client_name = kwargs.get('client_name')
        try:
            client = models.Client.objects.get(name=client_name)
        except models.Client.DoesNotExist:
            return http.HttpResponseServerError(f"Invalid client: {client_name}")

        try:
            client.validate_state(request)
            client.validate_authorization_response(request)
        except ValueError as exc:
            logger.error(exc)
            return http.HttpResponseForbidden(exc)
        except exceptions.OAuth2Error as exc:
            logger.warning(exc)
            return http.HttpResponseForbidden(exc)

        try:
            client.get_access_token(request)
        except IOError as exc:
            return http.HttpResponse(exc, status=503)
        messages.success(request, f'Authorization obtained from {client}')
        return_url = client.get_return_url(request)
        return http.HttpResponseRedirect(return_url)
