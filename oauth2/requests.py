from requests.auth import AuthBase
from django.contrib.auth.models import AbstractBaseUser

from oauth2.models import Client, Token
from oauth2.exceptions import AuthorizationRequired


class BearerTokenAuth(AuthBase):
    def __init__(self, user: AbstractBaseUser, client: Client) -> None:
        self.user = user
        self.client = client

    def __call__(self, request):
        try:
            token = Token.objects.get(user=self.user, client=self.client)
        except Token.DoesNotExist:
            raise AuthorizationRequired(f"{self.client} authorization required for user {self.user}")
        request.headers['Authorization'] = token.authorization
        return request
