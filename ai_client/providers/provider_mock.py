
import json, time, hashlib, random
from typing import Tuple
from ..provider_base import BaseProvider

class MockProvider(BaseProvider):
    def generate(self, system, user, model, temperature, max_tokens) -> Tuple[str, int, int, int]:
        t0 = time.time()
        seed = int(hashlib.sha256(((system or "") + "|" + user).encode()).hexdigest(), 16) % (10**8)
        rnd = random.Random(seed)
        title = "Mock Recipe " + str(abs(seed) % 1000)
        servings = 2 + rnd.randint(0, 4)
        difficulty = rnd.choice(["easy","medium","hard"])
        prep = 5 + rnd.randint(0, 15)
        cook = 10 + rnd.randint(0, 25)
        total = prep + cook
        ingredients = []
        for i in range(1, 6):
            ingredients.append({"name": f"Item {i}", "quantity": float(rnd.randint(1, 3)), "unit": "cup" if i % 2 == 0 else "tbsp", "notes": None})
        steps = []
        for i in range(1, 5):
            equip = [{"name": "Bowl", "usage": "mix"}] if i == 1 else ([{"name":"Pan","usage":"saute"}] if i==3 else [])
            steps.append({"number": i, "instruction": f"Do step {i}", "duration_min": rnd.randint(1, 10), "equipment": equip, "notes": None})
        recipe = {
            "title": title,
            "servings": servings,
            "difficulty": difficulty,
            "time": {"prep_min": prep, "cook_min": cook, "total_min": total},
            "ingredients": ingredients,
            "steps": steps
        }
        text = json.dumps(recipe, ensure_ascii=False)
        dur = int((time.time() - t0) * 1000)
        return text, dur, 200, len(text)
