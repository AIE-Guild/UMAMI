import requests
from requests.auth import AuthBase
from requests.status_codes import codes
from django.contrib.auth.models import AbstractBaseUser

from oauth2.models import Client, Token
from oauth2.exceptions import AuthorizationRequired


class BearerTokenAuth(AuthBase):
    def __init__(self, user: AbstractBaseUser, client: Client) -> None:
        """Authentication class to apply Oauth2 token.

        Args:
            user: A Django user.
            client: An OAuth2 client.

        """
        self.user = user
        self.client = client

    def _handle_response(self, response: requests.Response, **kwargs) -> requests.Response:
        """Response handler.

        Args:
            response: A Response object.
            **kwargs: Keyword arguments passed to the original request.

        Returns:
            A Response object.

        Raises:
            AuthorizationRequired: Authentication token was missing or invalid.

        """
        if response.status_code in (codes.UNAUTHORIZED, codes.FORBIDDEN):
            raise AuthorizationRequired(f"{self.client} authorization token failed for user {self.user}")
        return response

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Authentication wrapper for requests.

        Args:
            request: A PreparedRequest object.

        Returns:
            The request with authentication headers applied.

        """
        request.register_hook('response', self._handle_response)
        try:
            token = Token.objects.get(user=self.user, client=self.client)
        except Token.DoesNotExist:
            raise AuthorizationRequired(f"{self.client} authorization required for user {self.user}")
        request.headers['Authorization'] = token.authorization
        return request
