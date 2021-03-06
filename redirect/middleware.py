# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.template.response import TemplateResponse

from redirect.models import Redirect

logger = logging.getLogger('umami.redirect')


class RedirectServiceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            host = request.META['HTTP_HOST']
        except KeyError:
            logger.debug("Redirect service skipped for missing Host header.")
            return self.get_response(request)
        if host == settings.REDIRECT_HOST:
            logger.debug("Redirect service activated for '%s'.", host)
            try:
                redirect = Redirect.objects.get(path=request.path_info)
            except Redirect.DoesNotExist:
                logger.warning("No redirect configured for '%s'.", request.path_info)
                return TemplateResponse(request, 'redirect/404.html', status=404)
            logger.info("Redirecting '%s' to '%s'.", request.path_info, redirect.location)
            return HttpResponseRedirect(redirect.location)
        else:
            logger.debug("Redirect service skipped for '%s'.", host)
            return self.get_response(request)
