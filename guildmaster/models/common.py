from typing import Type

from django.db.models import Model

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenBinding:
    pdu: str
    user: Type[Model]
    client: Type[Model]
