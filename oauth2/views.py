import logging

from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import base

from oauth2 import exceptions, models
from oauth2.workflows import AuthorizationCodeWorkflow

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class AuthorizationView(LoginRequiredMixin, base.View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        client_name = kwargs.get('client_name')
        try:
            flow = AuthorizationCodeWorkflow(client_name)
        except ValueError as exc:
            return http.HttpResponseServerError(exc)
        return_url = request.GET.get(settings.OAUTH2_RETURN_FIELD_NAME)
        url = flow.get_authorization_url(request, return_url)
        logger.info('Redirecting to: %s', url)
        return http.HttpResponseRedirect(url)


class TokenView(LoginRequiredMixin, base.View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        client_name = kwargs.get('client_name')
        try:
            flow = AuthorizationCodeWorkflow(client_name)
        except ValueError as exc:
            return http.HttpResponseServerError(exc)

        try:
            flow.validate_state(request)
            flow.validate_authorization_response(request)
        except ValueError as exc:
            logger.error(exc)
            return http.HttpResponseForbidden(exc)
        except exceptions.OAuth2Error as exc:
            logger.warning(exc)
            return http.HttpResponseForbidden(exc)

        try:
            flow.get_access_token(request)
        except IOError as exc:
            return http.HttpResponse(exc, status=503)
        messages.success(request, f'Authorization obtained from {flow.verbose_name}')
        return_url = flow.get_return_url(request)
        return http.HttpResponseRedirect(return_url)


class ClientDumpView(LoginRequiredMixin, base.TemplateView):
    template_name = 'client_dump.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resources = models.Resource.objects.filter(user=self.request.user)
        context['resources'] = {}
        for client in models.Client.objects.filter(enabled=True):
            try:
                resource = resources.get(client=client)
            except models.Resource.DoesNotExist:
                context['resources'][client.name] = ""
            else:
                context['resources'][client.name] = str(resource)
        return context
