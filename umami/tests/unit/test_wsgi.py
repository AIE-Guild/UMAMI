# -*- coding: utf-8 -*-
from django.utils.module_loading import import_string

from umami.wsgi import application

def test_wsgi_app(settings):
    assert application == import_string(settings.WSGI_APPLICATION)
