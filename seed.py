# Seeds the DB that gets shipped with the package
import sqlite3
import re
import csv

db_path = "/Users/user/Desktop/Projects/dnd-cli/src/dnd_cli/data/dnd2024.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Allows dict-style column access
    return conn

def init_db(conn: sqlite3.Connection):
    """Create tables if they don't already exist."""
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS spells (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            level       INTEGER,
            school      TEXT,
            casting_time TEXT,
            range       TEXT,
            components  TEXT,       -- JSON array e.g. ["V", "S", "M (a pinch of sand)"]
            duration    TEXT,
            description TEXT,
            higher_levels TEXT,
            classes     TEXT        -- JSON array e.g. ["Wizard", "Sorcerer"]
        );
    """)

def make_id(name: str) -> str:
    slug = name.strip().lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)  # Remove special characters
    slug = re.sub(r"\s+", "-", slug)          # Replace spaces with hyphens
    return slug

def parse_level(value: str) -> int | None:
    value = value.strip().lower()
    if value == "Cantrip" or value == "cantrip":
        return 0
    try:
        value = value[0]
        return int(value)
    except ValueError:
        return None
    
def clean_description(text: str) -> str:
    """
    Inserts newlines where periods followed by uppercase letters indicate
    a missing newline in the CSV data.
    """
    if not text:
        return text
    return re.sub(r'\.(?=[A-Z])', '.\n\n', text)

def seed_from_csv(csv_path: str, reset: bool = False):
    """
    Read spells from a CSV file and insert them into the database.

    Expected columns:
        Name, Source, Page, Level, Casting Time, Duration,
        School, Range, Components, Classes, Text, At Higher Levels
    """
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        with get_connection() as conn:
            if reset:
                conn.executescript("""
                    DROP TABLE IF EXISTS spells
                """)
            init_db(conn)
            cursor = conn.cursor()

            inserted = 0
            skipped = 0

            for row in reader:
                name = row.get("Name", "").strip()
                if not name:
                    skipped += 1
                    continue

                cursor.execute("""
                    INSERT OR REPLACE INTO spells
                        (id, name, level, casting_time, duration,
                         school, range, components, classes, description, higher_levels)
                    VALUES
                        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    make_id(name),
                    name,
                    parse_level(row.get("Level", "")),
                    row.get("Casting Time", "").strip(),
                    row.get("Duration", "").strip(),
                    row.get("School", "").strip(),
                    row.get("Range", "").strip(),
                    row.get("Components", "").strip(),
                    row.get("Classes", "").strip(),
                    clean_description(row.get("Text", "").strip()),
                    clean_description(row.get("At Higher Levels", "").strip()),
                ))
                inserted += 1

            print(f"Done. {inserted} spells inserted, {skipped} rows skipped.")

if __name__ == "__main__":
    import sys

    reset = "--reset" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--reset"]

    if len(args) != 1:
        print("Usage: python seed.py <spells.csv> [--reset]")
        sys.exit(1)

    seed_from_csv(csv_path=args[0], reset=reset)