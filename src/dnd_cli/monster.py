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

def monster_lookup(query: str, cutoff: int = 70) -> dict | None:
    with get_connection() as conn:
        cur = conn.cursor()
        rows = cur.execute("SELECT * FROM monsters").fetchall()
 
    # Build a name -> row mapping
    name_map = {row["name"]: row for row in rows}
    names = list(name_map.keys())
 
    # Find the closest matching monster name
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
        "id":                   row["id"],
        "name":                 row["name"],
        "size":                 row["size"],
        "type":                 row["type"],
        "ac":                   row["ac"],
        "hp":                   row["hp"],
        "strength":             row["strength"],
        "dexterity":            row["dexterity"],
        "constitution":         row["constitution"],
        "intelligence":         row["intelligence"],
        "wisdom":               row["wisdom"],
        "charisma":             row["charisma"],
        "saving_throws":        row["saving_throws"],
        "skills":               row["skills"],
        "vulnerabilities":      row["vulnerabilities"],
        "resistances":          row["resistances"],
        "damage_immunities":    row["damage_immunities"],
        "condition_immunities": row["condition_immunities"],
        "senses":               row["senses"],
        "languages":            row["languages"],
        "cr":                   row["cr"],
        "traits":               row["traits"],
        "actions":              row["actions"],
        "bonus_actions":        row["bonus_actions"],
        "reactions":            row["reactions"],
        "legendary_actions":    row["legendary_actions"],
        "mythic_actions":       row["mythic_actions"],
        "lair_actions":         row["lair_actions"],
        "regional_effects":     row["regional_effects"],
        "environment":          row["environment"],
        "treasure":             row["treasure"],
        "match_score":          score,
    }