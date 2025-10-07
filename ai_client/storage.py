
from __future__ import annotations
import os, sqlite3, uuid, json, datetime
from typing import Optional, List, Dict, Any, Tuple

INIT_SQL = """
CREATE TABLE IF NOT EXISTS recipes (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  title TEXT NOT NULL,
  servings INTEGER,
  difficulty TEXT,
  time_prep_min INTEGER,
  time_cook_min INTEGER,
  time_total_min INTEGER,
  json TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_recipes_user_title ON recipes (user_id, title);
""".strip()

class RecipeStore:
    def save(self, recipe: Dict[str, Any], user_id: Optional[str] = None) -> str: ...
    def get(self, recipe_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]: ...
    def list(self, user_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]: ...
    def search(self, q: str, user_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]: ...
    def delete(self, recipe_id: str, user_id: Optional[str] = None) -> bool: ...

class SQLiteRecipeStore(RecipeStore):
    def __init__(self, db_path: str = "./recipes.db"):
        self.db_path = db_path
        self._ensure_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_db(self):
        with self._connect() as con:
            con.executescript(INIT_SQL)

    def _extract_columns(self, recipe: Dict[str, Any]) -> Tuple[str, int, str, int, int, int]:
        title = recipe.get("title", "")
        servings = int(recipe.get("servings") or 0)
        difficulty = str(recipe.get("difficulty") or "")
        t = recipe.get("time") or {}
        prep = int(t.get("prep_min") or 0)
        cook = int(t.get("cook_min") or 0)
        total = int(t.get("total_min") or (prep + cook))
        return title, servings, difficulty, prep, cook, total

    def save(self, recipe: Dict[str, Any], user_id: Optional[str] = None) -> str:
        rid = uuid.uuid4().hex
        title, servings, difficulty, prep, cook, total = self._extract_columns(recipe)
        now = datetime.datetime.utcnow().isoformat(timespec="seconds")
        blob = json.dumps(recipe, ensure_ascii=False)
        with self._connect() as con:
            con.execute(
                "INSERT INTO recipes (id, user_id, title, servings, difficulty, time_prep_min, time_cook_min, time_total_min, json, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (rid, user_id, title, servings, difficulty, prep, cook, total, blob, now, now),
            )
        return rid

    def get(self, recipe_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        with self._connect() as con:
            if user_id:
                row = con.execute("SELECT * FROM recipes WHERE id=? AND (user_id IS ? OR user_id=?)", (recipe_id, None, user_id)).fetchone()
            else:
                row = con.execute("SELECT * FROM recipes WHERE id=?", (recipe_id,)).fetchone()
        return dict(row) if row else None

    def list(self, user_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        with self._connect() as con:
            if user_id:
                rows = con.execute(
                    "SELECT * FROM recipes WHERE user_id IS ? OR user_id=? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (None, user_id, limit, offset),
                ).fetchall()
            else:
                rows = con.execute(
                    "SELECT * FROM recipes ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (limit, offset),
                ).fetchall()
        return [dict(r) for r in rows]

    def search(self, q: str, user_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        pattern = f"%{q.lower()}%"
        with self._connect() as con:
            if user_id:
                rows = con.execute(
                    "SELECT * FROM recipes WHERE (user_id IS ? OR user_id=?) AND lower(title) LIKE ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (None, user_id, pattern, limit, offset),
                ).fetchall()
            else:
                rows = con.execute(
                    "SELECT * FROM recipes WHERE lower(title) LIKE ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (pattern, limit, offset),
                ).fetchall()
        return [dict(r) for r in rows]

    def delete(self, recipe_id: str, user_id: Optional[str] = None) -> bool:
        with self._connect() as con:
            if user_id:
                cur = con.execute("DELETE FROM recipes WHERE id=? AND (user_id IS ? OR user_id=?)", (recipe_id, None, user_id))
            else:
                cur = con.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
        return cur.rowcount > 0

def get_store() -> SQLiteRecipeStore:
    db_path = os.getenv("RECIPE_DB_PATH", "./recipes.db")
    return SQLiteRecipeStore(db_path)
