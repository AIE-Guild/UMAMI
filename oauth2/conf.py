from appconf import AppConf
from django.conf import settings


class OAuth2AppConf(AppConf):
    SECURE: bool = True
    STATE_BYTES: int = 32
    SESSION_STATE_KEY: str = '_oauth2_state'

    class Meta:
        prefix = 'oauth2'
