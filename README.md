
# AI Connector — Stage 2 (OpenAI adapter)

This stage adds a real OpenAI provider behind the same interface.

## Setup
1. Create and activate a Python 3.10+ venv.
2. Install deps:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your API key:
   ```bash
   export OPENAI_API_KEY=sk-...
   ```
   On Windows PowerShell:
   ```powershell
   setx OPENAI_API_KEY "sk-..."
   ```

## Run (mock provider)
```bash
python demo.py --provider mock
```

## Run (OpenAI)
Pick a JSON-friendly model (e.g., `gpt-4o-mini`):
```bash
python demo.py --provider openai --model gpt-4o-mini --system "Return ONLY valid JSON matching the recipe schema." --user "Generate a Punjabi kadhi pakora recipe JSON"
```

The output is validated against the recipe schema. If it isn't valid JSON or fails schema checks, the client raises a `ValueError`.
