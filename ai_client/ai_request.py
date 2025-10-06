
from dataclasses import dataclass
from typing import Optional

@dataclass
class AIRequest:
    model: str
    system: Optional[str]
    user: str
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
