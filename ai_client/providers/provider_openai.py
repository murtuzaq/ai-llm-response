
import os, time
from typing import Tuple
from ..provider_base import BaseProvider

class OpenAIProvider(BaseProvider):
    def __init__(self):
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment")
        self.__client = OpenAI(api_key=api_key)

    def generate(self, system, user, model, temperature, max_tokens) -> Tuple[str, int, int, int]:
        t0 = time.time()
        r = self.__client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system or ""},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        text = r.choices[0].message.content or ""
        usage = getattr(r, "usage", None)
        prompt_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
        completion_tokens = getattr(usage, "completion_tokens", 0) if usage else len(text)
        dur = int((time.time() - t0) * 1000)
        return text, dur, prompt_tokens, completion_tokens
