# -*- coding: utf-8 -*-
from django.conf import settings
from appconf import AppConf


class RedirectAppConf(AppConf):
    SECURE = True

    class Meta:
        prefix = 'redirect'
        required = ['HOST']
