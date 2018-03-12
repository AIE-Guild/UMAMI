# -*- coding: utf-8 -*-
from django.conf import settings
from appconf import AppConf


class UMAMIConf(AppConf):
    SOCIALAUTH_TRUST_PROVIDER = False

    class Meta:
        prefix = 'umami'
