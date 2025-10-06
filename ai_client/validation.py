
from typing import Any, Dict, List

def validate_recipe(obj: Dict[str, Any]) -> List[str]:
    errs = []
    if not isinstance(obj, dict):
        return ["root not object"]
    for k in ["title", "servings", "difficulty", "time", "ingredients", "steps"]:
        if k not in obj:
            errs.append(f"missing {k}")

    if "title" in obj and not isinstance(obj["title"], str):
        errs.append("title type")
    if "servings" in obj and not isinstance(obj["servings"], int):
        errs.append("servings type")
    if "difficulty" in obj and not isinstance(obj["difficulty"], str):
        errs.append("difficulty type")

    if "time" in obj:
        t = obj["time"]
        if not isinstance(t, dict):
            errs.append("time type")
        else:
            for key in ["prep_min", "cook_min", "total_min"]:
                if key not in t or not isinstance(t[key], int):
                    errs.append(f"time.{key} type")

    if "ingredients" in obj:
        if not isinstance(obj["ingredients"], list):
            errs.append("ingredients type")
        else:
            for i, ing in enumerate(obj["ingredients"]):
                if not isinstance(ing, dict):
                    errs.append(f"ingredients[{i}] type")
                    continue
                if "name" not in ing or not isinstance(ing["name"], str):
                    errs.append(f"ingredients[{i}].name type")
                if "quantity" in ing and ing["quantity"] is not None and not isinstance(ing["quantity"], (int, float)):
                    errs.append(f"ingredients[{i}].quantity type")
                if "unit" in ing and ing["unit"] is not None and not isinstance(ing["unit"], str):
                    errs.append(f"ingredients[{i}].unit type")
                if "notes" in ing and ing["notes"] is not None and not isinstance(ing["notes"], str):
                    errs.append(f"ingredients[{i}].notes type")

    if "steps" in obj:
        if not isinstance(obj["steps"], list):
            errs.append("steps type")
        else:
            for i, st in enumerate(obj["steps"]):
                if not isinstance(st, dict):
                    errs.append(f"steps[{i}] type")
                    continue
                if "number" not in st or not isinstance(st["number"], int):
                    errs.append(f"steps[{i}].number type")
                if "instruction" not in st or not isinstance(st["instruction"], str):
                    errs.append(f"steps[{i}].instruction type")
                if "duration_min" in st and st["duration_min"] is not None and not isinstance(st["duration_min"], int):
                    errs.append(f"steps[{i}].duration_min type")
                if "equipment" in st:
                    if not isinstance(st["equipment"], list):
                        errs.append(f"steps[{i}].equipment type")
                    else:
                        for j, eq in enumerate(st["equipment"]):
                            if not isinstance(eq, dict):
                                errs.append(f"steps[{i}].equipment[{j}] type")
                                continue
                            if "name" not in eq or not isinstance(eq["name"], str):
                                errs.append(f"steps[{i}].equipment[{j}].name type")
                            if "usage" in eq and eq["usage"] is not None and not isinstance(eq["usage"], str):
                                errs.append(f"steps[{i}].equipment[{j}].usage type")
                if "notes" in st and st["notes"] is not None and not isinstance(st["notes"], str):
                    errs.append(f"steps[{i}].notes type")

    return errs
