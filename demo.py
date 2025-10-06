
import os, argparse
from ai_client.client import AIClient
from ai_client.models import AIRequest

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--provider", default=os.getenv("AI_PROVIDER", "mock"), choices=["mock","openai"])
    p.add_argument("--model", default=os.getenv("AI_MODEL", "mock-1"))
    p.add_argument("--system", default="You are a culinary assistant that always returns valid JSON for a recipe")
    p.add_argument("--user", default="Generate a recipe JSON for a spiced gram flour snack")
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--max_tokens", type=int, default=512)
    args = p.parse_args()

    client = AIClient(provider=args.provider, model=args.model)
    req = AIRequest(model=args.model, system=args.system, user=args.user, temperature=args.temperature, max_tokens=args.max_tokens)
    res = client.generate(req)

    print("=== INPUT PROMPT ===")
    print("System:", args.system)
    print("User:", args.user)
    print()
    print("=== OUTPUT ===")
    print("Provider:", args.provider)
    print("Model:", res.model)
    print("Latency (ms):", res.latency_ms)
    print("Tokens in:", res.tokens_in, "Tokens out:", res.tokens_out)
    print("JSON:")
    print(res.text)

if __name__ == "__main__":
    main()
