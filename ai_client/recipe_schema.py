
RECIPE_SCHEMA_KEYS = [
    "title",
    "servings",
    "difficulty",
    "time",
    "ingredients",
    "steps"
]

def schema_description():
    return {
        "title": "str",
        "servings": "int",
        "difficulty": "str",
        "time": {"prep_min": "int", "cook_min": "int", "total_min": "int"},
        "ingredients": [{"name":"str","quantity":"float|null","unit":"str|null","notes":"str|null"}],
        "steps": [{"number":"int","instruction":"str","duration_min":"int|null","equipment":[{"name":"str","usage":"str|null"}],"notes":"str|null"}]
    }
