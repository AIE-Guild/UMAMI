import logging

import requests
from django import http
from django.conf import settings
from django.views.generic import base

from oauth2 import exceptions, models

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class AuthorizationView(base.View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        name = kwargs.get('client_name')
        return_url = request.GET.get(settings.OAUTH2_RETURN_FIELD_NAME, settings.OAUTH2_RETURN_URL)
        try:
            client = models.Client.objects.get(name=name)
        except models.Client.DoesNotExist:
            logger.error(f'No client found: {name}')
            return http.HttpResponseServerError()
        url, state = client.get_authorization_request(request)
        logger.debug(f'storing to session: state={state}, return_url={return_url}')
        request.session[settings.OAUTH2_SESSION_STATE_KEY] = state
        request.session[settings.OAUTH2_SESSION_RETURN_KEY] = return_url
        logger.debug(f'Redirecting to: {url}')
        return http.HttpResponseRedirect(url)


class TokenView(base.View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        name = kwargs.get('client_name')
        try:
            client = models.Client.objects.get(name=name)
        except models.Client.DoesNotExist:
            logger.error(f'No client found: {name}')
            return http.HttpResponseServerError()

        state = request.session.get(settings.OAUTH2_SESSION_STATE_KEY)
        return_url = request.session.get(settings.OAUTH2_SESSION_RETURN_KEY)
        logger.debug(f'fetched from session: state={state}, return_url={return_url}')

        try:
            client.validate_authorization_response(request, state=state)
        except ValueError as exc:
            logger.error(exc)
            return http.HttpResponseForbidden(exc)
        except exceptions.OAuth2Error as exc:
            logger.warning(exc)
            return http.HttpResponseForbidden(exc)

        s = requests.Session()
        response = s.send(client.get_token_request(request))

        return http.HttpResponseRedirect(return_url)
