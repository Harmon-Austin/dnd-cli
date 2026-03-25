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
            components  TEXT,       
            duration    TEXT,
            description TEXT,
            higher_levels TEXT,
            classes     TEXT        
        );
    """)

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS monsters(
            id          TEXT PRIMARY KEY,
            name        TEXT,
            size        TEXT,
            type        TEXT,
            ac          TEXT,
            hp          TEXT,
            strength    TEXT,
            dexterity   TEXT,
            constitution TEXT,
            intelligence TEXT,
            wisdom      TEXT,
            charisma    TEXT,
            saving_throws TEXT,
            skills      TEXT,
            vulnerabilities TEXT,
            resistances TEXT,
            damage_immunities TEXT,
            condition_immunities TEXT,
            senses      TEXT,
            languages   TEXT,
            cr          TEXT,
            traits      TEXT,
            actions     TEXT,
            bonus_actions TEXT,
            reactions   TEXT,
            legendary_actions TEXT,
            mythic_actions TEXT,
            lair_actions TEXT,
            regional_effects TEXT,
            environment TEXT,
            treasure    TEXT
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

def seed_spells_from_csv(csv_path: str, reset: bool = False):
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

def seed_monsters_from_csv(csv_path: str, reset: bool = False):
    """
    Read monster stat blocks from CSV and insert them into the database.

    Expected columns:
        Name, Size, Type, HP, AC, Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma
        Saving Throws, Skills, Vulnerabilities, Resistances, Damage Immunities, Condition Immunities,
        Senses, Languages, Challenge Rating, Traits, Actions, Bonus Actions, Reactions, Legendary Actions,
        Mythic Actions, Lair Actions, Regional Effects, Environment, Treasure
    """
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        with get_connection() as conn:
            if reset:
                conn.executescript("""
                    DROP TABLE IF EXISTS monsters
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
                    INSERT OR REPLACE INTO monsters
                        (id, name, size, type, hp, ac, strength, dexterity, constitution, intelligence, wisdom, charisma,
                        saving_throws, skills, vulnerabilities, resistances, damage_immunities, condition_immunities,
                        senses, languages, cr, traits, actions, bonus_actions, reactions, legendary_actions, mythic_actions,
                        lair_actions, regional_effects, environment, treasure)
                    VALUES (?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?, ?,
                            ?)
                """, (
                    make_id(name),
                    name,
                    row.get("Size", "").strip(),
                    row.get("Type", "").strip(),
                    row.get("HP", "").strip(),
                    row.get("AC", "").strip(),
                    row.get("Strength", "").strip(),      # was "STR"
                    row.get("Dexterity", "").strip(),     # was "DEX"
                    row.get("Constitution", "").strip(),  # was "CON"
                    row.get("Intelligence", "").strip(),  # was "INT"
                    row.get("Wisdom", "").strip(),        # was "WIS"
                    row.get("Charisma", "").strip(),      # was "CHA"
                    row.get("Saving Throws", "").strip(),
                    row.get("Skills", "").strip(),
                    row.get("Damage Vulnerabilities", "").strip(),  # was "Vulnerabilities"
                    row.get("Damage Resistances", "").strip(),      # was "Resistances"
                    row.get("Damage Immunities", "").strip(),
                    row.get("Condition Immunities", "").strip(),
                    row.get("Senses", "").strip(),
                    row.get("Languages", "").strip(),
                    row.get("CR", "").strip(),
                    clean_description(row.get("Traits", "").strip()),
                    clean_description(row.get("Actions", "").strip()),
                    clean_description(row.get("Bonus Actions", "").strip()),
                    clean_description(row.get("Reactions", "").strip()),
                    clean_description(row.get("Legendary Actions", "").strip()),
                    clean_description(row.get("Mythic Actions", "").strip()),
                    clean_description(row.get("Lair Actions", "").strip()),
                    clean_description(row.get("Regional Effects", "").strip()),
                    row.get("Environment", "").strip(),
                    row.get("Treasure", "").strip())
                )
                inserted += 1
            
            print(f"Done. {inserted} monsters inserted, {skipped} rows skipped.")

if __name__ == "__main__":
    import sys

    reset = "--reset" in sys.argv
    monsters = "--monsters" in sys.argv
    args = []
    for a in sys.argv[1:]:
        if (a != "--reset") and (a != "--monsters"):
            args.append(a)

    if len(args) != 1:
        print("Usage: python seed.py <.csv path> [--reset] [--monsters]")
        print(args)
        sys.exit(1)

    if monsters:
        seed_monsters_from_csv(csv_path=args[0], reset=reset)
    else:
        seed_spells_from_csv(csv_path=args[0], reset=reset)