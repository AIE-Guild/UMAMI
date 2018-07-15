from typing import Any, Dict, Union

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenBinding:
    pdu: Dict[str, Union[str, int, float]]
    user: Any
    client: Any
