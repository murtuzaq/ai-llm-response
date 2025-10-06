
from ai_client.client import AIClient
from ai_client.models import AIRequest

def main():
    client = AIClient(provider="mock", model="mock-1")
    system = "You are a culinary assistant that always returns valid JSON for a recipe"
    user = "Make a quick snack using gram flour and chili flakes"
    req = AIRequest(model="mock-1", system=system, user=user, temperature=0.2, max_tokens=512)
    res = client.generate(req)

    print("=== INPUT PROMPT ===")
    print("System:", system)
    print("User:", user)
    print()
    print("=== OUTPUT ===")
    print("Model:", res.model)
    print("Latency (ms):", res.latency_ms)
    print("Tokens in:", res.tokens_in, "Tokens out:", res.tokens_out)
    print("JSON:")
    print(res.text)

if __name__ == "__main__":
    main()
