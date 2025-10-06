
import json
from typing import Optional
from .models import AIRequest, AIResponse
from .provider_mock import MockProvider
from .validation import validate_recipe

class AIClient:
    def __init__(self, provider: str = "mock", model: str = "mock-1"):
        self.__provider_name = provider
        self.__model = model
        self.__provider = self.__select_provider(provider)

    def generate(self, req: AIRequest) -> AIResponse:
        text, latency_ms, tokens_in, tokens_out = self.__provider.generate(req.system or "", req.user, req.model or self.__model, req.temperature, req.max_tokens)
        parsed = self.__parse_json_or_none(text)
        if parsed is not None:
            errs = validate_recipe(parsed)
            if errs:
                raise ValueError("schema_error: " + ";".join(errs))
        return AIResponse(text=text, parsed_json=parsed, model=req.model or self.__model, latency_ms=latency_ms, tokens_in=tokens_in, tokens_out=tokens_out)

    def __select_provider(self, name: str):
        if name == "mock":
            return MockProvider()
        raise ValueError("unknown provider")

    def __parse_json_or_none(self, text: str):
        try:
            return json.loads(text)
        except Exception:
            return None
