from django.conf import settings
from appconf import AppConf


class GuildmasterAppConf(AppConf):
    class Meta:
        prefix = 'guildmaster'

    def ready(self):
        import guildmaster.conf  # noqa
