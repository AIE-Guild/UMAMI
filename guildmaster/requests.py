import requests
from requests.auth import AuthBase
from requests.status_codes import codes

from guildmaster.exceptions import AuthorizationRequiredError
from guildmaster.models import Token


class TokenAuth(AuthBase):
    def __init__(self, token: Token) -> None:
        """Authentication class to apply Oauth2 token.

        Args:
            token: An OAuth2 Token object.

        """
        self.token = token

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
            raise AuthorizationRequiredError(
                f"{self.token.client} authorization token failed for user {self.token.user}"
            )
        return response

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Authentication wrapper for requests.

        Args:
            request: A PreparedRequest object.

        Returns:
            The request with authentication headers applied.

        """
        request.register_hook('response', self._handle_response)
        if self.token.is_stale:
            self.token.refresh()
        request.headers['Authorization'] = self.token.authorization
        return request
