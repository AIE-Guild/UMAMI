from appconf import AppConf
from django.conf import settings


class OAuth2AppConf(AppConf):
    SECURE = True

    class Meta:
        prefix = 'oauth2'
