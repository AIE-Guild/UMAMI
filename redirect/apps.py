# -*- coding: utf-8 -*-
from django.apps import AppConfig


class RedirectConfig(AppConfig):
    name = 'redirect'

    def ready(self):
        import redirect.conf
