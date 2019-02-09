from django.apps import AppConfig


class OAuth2Config(AppConfig):
    name = 'oauth2'
    verbose_name = 'OAuth2 Client'

    def ready(self) -> None:
        import oauth2.conf  # pylint: disable=unused-import
