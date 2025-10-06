
from dataclasses import dataclass
from typing import Optional, Any, Dict

@dataclass
class AIResponse:
    text: str
    parsed_json: Optional[Dict[str, Any]]
    model: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
