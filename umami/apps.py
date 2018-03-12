# -*- coding: utf-8 -*-
from django.apps import AppConfig


class UMAMIConfig(AppConfig):
    name = 'umami'

    def ready(self):
        import umami.conf  # noqa
