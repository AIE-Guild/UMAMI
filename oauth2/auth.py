import requests
from requests.auth import AuthBase

from oauth2.models import Token


class TokenAuth(AuthBase):
    """Uses the access token obtained from the OAuth2 authorization code flow."""

    def __init__(self, token: Token) -> None:
        self.token = token

    def __call__(self, request: requests.Request) -> requests.Request:
        request.headers['Authorization'] = self.token.authorization
        return request
