from django.apps import AppConfig


class GuildmasterConfig(AppConfig):
    name = 'guildmaster'
    verbose_name = 'Guildmaster OAuth2 Client'

    def ready(self) -> None:
        import guildmaster.conf  # pylint: disable=unused-import
