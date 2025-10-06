import json, sys
from .ai_request import AIRequest
from .ai_response import AIResponse
from .providers.provider_mock import MockProvider
from .providers.provider_openai import OpenAIProvider
from .validation import validate_recipe
from .json_repair import repair_json_structure

def _debug_print(header: str, payload: str):
    try:
        print(f"\n=== {header} ===", flush=True)
        print(payload, flush=True)
    except Exception:
        pass

class AIClient:
    def __init__(self, provider: str = "mock", model: str = "mock-1"):
        self.__provider_name = provider
        self.__model = model
        self.__provider = self.__select_provider(provider)

    def generate(self, req: AIRequest) -> AIResponse:
        # 1) Call provider
        text, latency_ms, tokens_in, tokens_out = self.__provider.generate(
            req.system or "",
            req.user,
            req.model or self.__model,
            req.temperature,
            req.max_tokens
        )
        _debug_print("RAW AI RESPONSE", text)
        _debug_print("USAGE", f"latency_ms={latency_ms}, tokens_in={tokens_in}, tokens_out={tokens_out}")

        # 2) Try direct parse + schema
        parsed = self.__parse_json_or_none(text)
        if parsed is not None:
            errs = validate_recipe(parsed)
            if not errs:
                return AIResponse(
                    text=text,
                    parsed_json=parsed,
                    model=req.model or self.__model,
                    latency_ms=latency_ms,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                )

        # 3) Structural repair (no extra tokens / no retry)
        repaired = repair_json_structure(text)
        if repaired and repaired != text:
            _debug_print("STRUCTURAL REPAIR (LOCAL)", repaired)
            parsed_local = self.__parse_json_or_none(repaired)
            if parsed_local is not None:
                errs_local = validate_recipe(parsed_local)
                if not errs_local:
                    return AIResponse(
                        text=repaired,
                        parsed_json=parsed_local,
                        model=req.model or self.__model,
                        latency_ms=latency_ms,
                        tokens_in=tokens_in,
                        tokens_out=tokens_out,
                    )

        # 4) If we get here, still bad → raise specific error
        if parsed is None:
            raise ValueError("json_parse_error_after_structural_repair")
        else:
            # parsed existed but schema errors remained after repair attempt
            raise ValueError("schema_error_after_structural_repair: " + ";".join(validate_recipe(parsed)))

    def __select_provider(self, name: str):
        if name == "mock":
            return MockProvider()
        if name == "openai":
            return OpenAIProvider()
        raise ValueError("unknown provider")

    def __parse_json_or_none(self, text: str):
        try:
            return json.loads(text)
        except Exception:
            return None
