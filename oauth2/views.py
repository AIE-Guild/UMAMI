import logging

from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import base

from oauth2 import exceptions, models, workflows

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class AuthorizationView(LoginRequiredMixin, base.View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        name = kwargs.get('client_name')
        try:
            client = models.Client.objects.get(name=name)
        except models.Client.DoesNotExist:
            logger.error('No client found: %s', name)
            return http.HttpResponseServerError()
        return_url = request.GET.get(settings.OAUTH2_RETURN_FIELD_NAME)
        url = workflows.get_authorization_url(request, client, return_url)
        logger.info('Redirecting to: %s', url)
        return http.HttpResponseRedirect(url)


class TokenView(LoginRequiredMixin, base.View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        name = kwargs.get('client_name')
        try:
            client = models.Client.objects.get(name=name)
        except models.Client.DoesNotExist:
            logger.error('No client found: %s', name)
            return http.HttpResponseServerError()

        try:
            workflows.validate_authorization_response(request, client)
        except ValueError as exc:
            logger.error(exc)
            return http.HttpResponseForbidden(exc)
        except exceptions.OAuth2Error as exc:
            logger.warning(exc)
            return http.HttpResponseForbidden(exc)

        try:
            workflows.fetch_tokens(request, client)
        except IOError:
            return http.HttpResponse(f'An error occurred while communicating with {client.description}', status=503)
        messages.success(request, f'Authorization obtained from {client.description}')
        return_url = workflows.get_return_url(request)
        return http.HttpResponseRedirect(return_url)
