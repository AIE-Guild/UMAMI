from typing import Optional


class OAuth2Error(Exception):
    """OAuth2 workflow errors."""

    def __init__(self, error: str, description: Optional[str] = None, uri: Optional[str] = None) -> None:
        super().__init__(error)
        self.error = error
        self.description = description
        self.uri = uri

    def __str__(self):
        text = super().__str__()
        if self.description:
            text += f': {self.description}'
        if self.uri:
            text += f' ({self.uri})'
        return text
