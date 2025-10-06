
import json, sys
from .ai_request import AIRequest
from .ai_response import AIResponse
from .providers.provider_mock import MockProvider
from .providers.provider_openai import OpenAIProvider
from .validation import validate_recipe
from .recipe_schema import schema_description

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
        text, latency_ms, tokens_in, tokens_out = self.__provider.generate(req.system or "", req.user, req.model or self.__model, req.temperature, req.max_tokens)
        _debug_print("RAW AI RESPONSE", text)
        _debug_print("USAGE", f"latency_ms={latency_ms}, tokens_in={tokens_in}, tokens_out={tokens_out}")
        parsed = self.__parse_json_or_none(text)
        if parsed is not None:
            errs = validate_recipe(parsed)
            if not errs:
                return AIResponse(text=text, parsed_json=parsed, model=req.model or self.__model, latency_ms=latency_ms, tokens_in=tokens_in, tokens_out=tokens_out)

        # Repair loop
        schema_text = json.dumps(schema_description(), ensure_ascii=False)
        repair_prompt = (
            "Your last output did not match the schema. "
            "Fix it to VALID JSON ONLY. Follow this schema strictly: "
            + schema_text
            + "\nHere is your last output to repair:\n"
            + (text if isinstance(text, str) else json.dumps(text, ensure_ascii=False))
        )
        _debug_print("REPAIR_PROMPT", repair_prompt[:1000] + ("..." if len(repair_prompt) > 1000 else ""))
        text2, latency_ms2, tokens_in2, tokens_out2 = self.__provider.generate(req.system or "", repair_prompt, req.model or self.__model, req.temperature, req.max_tokens)
        _debug_print("RAW AI RESPONSE (REPAIR)", text2)
        _debug_print("USAGE (REPAIR)", f"latency_ms={latency_ms2}, tokens_in={tokens_in2}, tokens_out={tokens_out2}")
        parsed2 = self.__parse_json_or_none(text2)
        if parsed2 is not None:
            errs2 = validate_recipe(parsed2)
            if not errs2:
                return AIResponse(text=text2, parsed_json=parsed2, model=req.model or self.__model, latency_ms=latency_ms+latency_ms2, tokens_in=tokens_in+tokens_in2, tokens_out=tokens_out+tokens_out2)
            raise ValueError("schema_error_after_repair: " + ";".join(errs2))
        raise ValueError("json_parse_error_after_repair")

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
