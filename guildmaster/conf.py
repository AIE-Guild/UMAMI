from appconf import AppConf
from django.conf import settings  # pylint: disable=unused-import


class GuildmasterAppConf(AppConf):
    SECURE: bool = True
    STATE_BYTES: int = 32
    RETURN_FIELD_NAME = 'next'
    RETURN_URL = '/'
    SESSION_STATE_KEY: str = '_guildmaster_state'
    SESSION_RETURN_KEY: str = '_guildmaster_return'

    class Meta:
        prefix = 'guildmaster'
