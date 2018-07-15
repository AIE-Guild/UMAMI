from django.apps import AppConfig


class GuildmasterConfig(AppConfig):
    name = 'guildmaster'

    def ready(self):
        import guildmaster.conf  # noqa
