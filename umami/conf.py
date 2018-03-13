# -*- coding: utf-8 -*-
from django.conf import settings
from appconf import AppConf


class UMAMIConf(AppConf):
    class Meta:
        prefix = 'umami'
