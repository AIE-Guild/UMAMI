from appconf import AppConf
from django.conf import settings


class GuildmasterAppConf(AppConf):
    STATE_KEY = 'guildmaster_state'

    class Meta:
        prefix = 'guildmaster'

    def ready(self):
        import guildmaster.conf  # pragma: no cover noqa
