
def get_supported_models(provider: str) -> list[str]:
    if provider == "mock":
        return ["mock-1"]
    if provider == "openai":
        return ["gpt-4o-mini", "gpt-4o"]
    return []
