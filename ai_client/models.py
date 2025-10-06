
from dataclasses import dataclass
from typing import Optional, Any, Dict

@dataclass
class AIRequest:
    model: str
    system: Optional[str]
    user: str
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

@dataclass
class AIResponse:
    text: str
    parsed_json: Optional[Dict[str, Any]]
    model: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
