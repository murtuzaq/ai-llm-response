
from typing import Any, Dict, List

def validate_recipe(obj: Dict[str, Any]) -> List[str]:
    errs = []
    if not isinstance(obj, dict):
        return ["root not object"]
    keys = ["title","description","servings","time","ingredients","equipment","steps","nutrition","tags","source","version"]
    for k in keys:
        if k not in obj:
            errs.append(f"missing {k}")
    if "title" in obj and not isinstance(obj["title"], str):
        errs.append("title type")
    if "description" in obj and not isinstance(obj["description"], str):
        errs.append("description type")
    if "servings" in obj and not isinstance(obj["servings"], int):
        errs.append("servings type")
    if "version" in obj and not isinstance(obj["version"], int):
        errs.append("version type")
    if "time" in obj:
        t = obj["time"]
        if not isinstance(t, dict):
            errs.append("time type")
        else:
            for k in ["prep_min","cook_min","total_min"]:
                if k not in t or not isinstance(t[k], int):
                    errs.append(f"time.{k} type")
    if "ingredients" in obj:
        if not isinstance(obj["ingredients"], list):
            errs.append("ingredients type")
        else:
            for i,ing in enumerate(obj["ingredients"]):
                if not isinstance(ing, dict):
                    errs.append(f"ingredients[{i}] type")
                    continue
                if "name" not in ing or not isinstance(ing["name"], str):
                    errs.append(f"ingredients[{i}].name type")
                if "quantity" in ing and ing["quantity"] is not None and not isinstance(ing["quantity"], (int,float)):
                    errs.append(f"ingredients[{i}].quantity type")
                if "unit" in ing and ing["unit"] is not None and not isinstance(ing["unit"], str):
                    errs.append(f"ingredients[{i}].unit type")
    if "equipment" in obj:
        if not isinstance(obj["equipment"], list):
            errs.append("equipment type")
        else:
            for i,eq in enumerate(obj["equipment"]):
                if not isinstance(eq, dict):
                    errs.append(f"equipment[{i}] type")
                    continue
                if "name" not in eq or not isinstance(eq["name"], str):
                    errs.append(f"equipment[{i}].name type")
    if "steps" in obj:
        if not isinstance(obj["steps"], list):
            errs.append("steps type")
        else:
            for i,st in enumerate(obj["steps"]):
                if not isinstance(st, dict):
                    errs.append(f"steps[{i}] type")
                    continue
                if "number" not in st or not isinstance(st["number"], int):
                    errs.append(f"steps[{i}].number type")
                if "instruction" not in st or not isinstance(st["instruction"], str):
                    errs.append(f"steps[{i}].instruction type")
                if "equipment" in st and not isinstance(st["equipment"], list):
                    errs.append(f"steps[{i}].equipment type")
                if "duration_min" in st and st["duration_min"] is not None and not isinstance(st["duration_min"], int):
                    errs.append(f"steps[{i}].duration_min type")
    if "nutrition" in obj:
        n = obj["nutrition"]
        if not isinstance(n, dict):
            errs.append("nutrition type")
        else:
            for k,t in {"calories":int,"protein_g":(int,float),"fat_g":(int,float),"carbs_g":(int,float)}.items():
                if k in n and n[k] is not None and not isinstance(n[k], t):
                    errs.append(f"nutrition.{k} type")
    if "tags" in obj and not isinstance(obj["tags"], list):
        errs.append("tags type")
    if "source" in obj:
        s = obj["source"]
        if not isinstance(s, dict):
            errs.append("source type")
        else:
            if "author" in s and s["author"] is not None and not isinstance(s["author"], str):
                errs.append("source.author type")
            if "url" in s and s["url"] is not None and not isinstance(s["url"], str):
                errs.append("source.url type")
    return errs
