# -*- coding: utf-8 -*-
from appconf import AppConf
from django.conf import settings


class UMAMIConf(AppConf):
    class Meta:
        prefix = 'umami'
