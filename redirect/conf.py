# -*- coding: utf-8 -*-
from appconf import AppConf
from django.conf import settings


class RedirectAppConf(AppConf):
    SECURE = True

    class Meta:
        prefix = 'redirect'
        required = ['HOST']
