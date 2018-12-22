import logging

import requests
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

        state = request.session.get(settings.OAUTH2_SESSION_STATE_KEY)
        return_url = request.session.get(settings.OAUTH2_SESSION_RETURN_KEY, settings.OAUTH2_RETURN_URL)
        logger.debug(f'fetched from session: state={state}, return_url={return_url}')

        try:
            workflows.validate_authorization_response(request, client)
        except ValueError as exc:
            logger.error(exc)
            return http.HttpResponseForbidden(exc)
        except exceptions.OAuth2Error as exc:
            logger.warning(exc)
            return http.HttpResponseForbidden(exc)

        s = requests.Session()
        try:
            token_request = client.get_token_request(request)
            logger.info(f'Sending token request to {token_request.url} for user {request.user}')
            response = s.send(token_request)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error(exc)
            messages.error(request, f'Error communicating with {client.driver.description}')
        else:
            token = models.Token.objects.extract(request.user, client, response)
            logger.info(f'{client.driver.description} token {token} obtained for user {request.user}')
            messages.success(request, f'Obtained token from {client.driver.description}')

        return http.HttpResponseRedirect(return_url)
