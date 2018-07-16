from typing import Any, Dict, Union
import time

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TokenBinding:
    pdu: Dict[str, Union[str, int, float]]
    user: Any
    client: Any
    timestamp: float = field(default_factory=time.time)
