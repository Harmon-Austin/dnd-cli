import sqlite3
from rapidfuzz import process, fuzz
from importlib.resources import files

def _get_db_path() -> str:
    return str(files("dnd_cli").joinpath("data/dnd2024.db"))

def get_connection() -> sqlite3.Connection:
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Allows dict-style column access
    return conn

def spell_lookup(query: str, cutoff: int = 70) -> dict | None:
    with get_connection() as conn:
        # Get all spells to fuzzy match from
        cur = conn.cursor()
        rows = cur.execute("SELECT * FROM spells")

    # Build a name -> row mapping
    name_map = {row["name"]: row for row in rows}
    names = list(name_map.keys())

    # Find the closest matching spell name
    match = process.extractOne(
        query,
        names,
        scorer=fuzz.WRatio,
        score_cutoff=cutoff
    )

    if not match:
        return None

    best_name, score, _ = match
    row = name_map[best_name]

    return {
        "id":           row["id"],
        "name":         row["name"],
        "level":        row["level"],
        "school":       row["school"],
        "casting_time": row["casting_time"],
        "range":        row["range"],
        "components":   row["components"],
        "duration":     row["duration"],
        "description":  row["description"],
        "higher_levels":row["higher_levels"],
        "classes":      row["classes"],
        "match_score":  score,
    }
    
    

