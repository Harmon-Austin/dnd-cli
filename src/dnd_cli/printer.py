from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text
from rich.highlighter import RegexHighlighter
from rich.theme import Theme

class SpellHighlighter(RegexHighlighter):
    base_style = "spell."
    highlights = [
        r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)",
        r"(?P<dice>\d+d\d+)",
        r"(?P<number>(?<![d\d])\d+(?![d\d]))", #Any number not involved with nds format for dice
        r"(?P<elemental_damage>Fire|Acid|Lightning|Thunder|Cold)",
        r"(?P<physical_damage>Bludgeoning|Slashing|Piercing)",
        r"(?P<special_damage>Radiant|Necrotic|Force|Poison|Psychic)"
    ]

custom_theme = Theme({
    "spell.ability" : "bold yellow",
    "spell.dice" : "bold cyan",
    "spell.number" : "bold green",
    "spell.elemental_damage" : "bold red",
    "spell.physical_damage" : "bold white",
    "spell.special_damage" : "bold magenta",
})

console = Console(theme=custom_theme)

def rich_print(text: str):
    '''
    Prints provided text using the rich console.print command.
    '''
    console.print(text)

def print_spell(result: dict):
    # Header
    level = "Cantrip" if result["level"] == 0 else f"Level {result['level']}"
    header = Text()
    header.append(result["name"], style="bold magenta")
    header.append(f"  {level} {result['school']}", style="dim")
    console.print(header)
    console.rule(style="magenta")

    # Stats table
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column(style="bold cyan", no_wrap=True)
    table.add_column()

    table.add_row("Casting Time", result["casting_time"] or "—")
    table.add_row("Range",        result["range"] or "—")
    table.add_row("Components",   result["components"] or "—")
    table.add_row("Duration",     result["duration"] or "—")
    table.add_row("Classes",      result["classes"] or "—")

    console.print(table)

    # Description
    highlighter = SpellHighlighter()

    console.print(highlighter(result["description"] or ""), markup=False)

    # At higher levels
    if result["higher_levels"]:
        console.print("\n[bold cyan]At Higher Levels.[/bold cyan]", end=" ")
        console.print(highlighter(result["higher_levels"]), markup=False)


def calc_modifier(score: int) -> str:
    mod = (score - 10) // 2
    return f"+{mod}" if mod >= 0 else str(mod)


def print_section(title: str, text: str):
    """Prints a titled section with highlighted text, only if text is non-empty."""
    if not text or not text.strip():
        return
    highlighter = SpellHighlighter()
    console.print(f"\n[bold red]{title}[/bold red]")
    console.rule(style="red")
    console.print(highlighter(str(text)), markup=False)


def print_monster(result: dict):
    highlighter = SpellHighlighter()

    # -------------------------------------------------------------------------
    # Header
    # -------------------------------------------------------------------------
    header = Text()
    header.append(result["name"], style="bold red")
    size  = result.get("size") or ""
    mtype = result.get("type") or ""
    if size or mtype:
        header.append(f"  {size} {mtype}".rstrip(), style="dim")
    console.print(header)
    console.rule(style="red")

    # -------------------------------------------------------------------------
    # Core stats (AC, HP, CR)
    # -------------------------------------------------------------------------
    core_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    core_table.add_column(style="bold red", no_wrap=True)
    core_table.add_column()

    for key, label in [("ac", "Armor Class"), ("hp", "Hit Points"), ("cr", "Challenge"),
                       ("senses", "Senses"), ("languages", "Languages"), ("environment", "Environment")]:
        if result.get(key):
            core_table.add_row(label, highlighter(str(result[key])))

    console.print(core_table)

    # -------------------------------------------------------------------------
    # Ability scores
    # -------------------------------------------------------------------------
    console.rule(style="red")
    ability_table = Table(box=box.SIMPLE, show_header=True, padding=(0, 2))

    abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    labels    = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]

    for label in labels:
        ability_table.add_column(label, style="bold red", justify="center")

    scores = []
    for ability in abilities:
        raw = result.get(ability)
        if raw is not None:
            try:
                score = int(str(raw).strip())
                scores.append(f"{score} ({calc_modifier(score)})")
            except ValueError:
                scores.append(str(raw))
        else:
            scores.append("—")

    ability_table.add_row(*scores)
    console.print(ability_table)
    console.rule(style="red")

    # -------------------------------------------------------------------------
    # Saving throws, skills, and defenses
    # -------------------------------------------------------------------------
    defense_fields = [
        ("saving_throws",        "Saving Throws"),
        ("skills",               "Skills"),
        ("vulnerabilities",      "Damage Vulnerabilities"),
        ("resistances",          "Damage Resistances"),
        ("damage_immunities",    "Damage Immunities"),
        ("condition_immunities", "Condition Immunities"),
    ]

    defense_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    defense_table.add_column(style="bold red", no_wrap=True)
    defense_table.add_column()

    has_defense_rows = False
    for key, label in defense_fields:
        value = result.get(key)
        if value and str(value).strip():
            defense_table.add_row(label, Text(str(value)))
            has_defense_rows = True

    if has_defense_rows:
        console.print(defense_table)

    # -------------------------------------------------------------------------
    # Traits, actions, and optional sections
    # -------------------------------------------------------------------------
    for title, key in [
        ("TRAITS",            "traits"),
        ("ACTIONS",           "actions"),
        ("BONUS ACTIONS",     "bonus_actions"),
        ("REACTIONS",         "reactions"),
        ("LEGENDARY ACTIONS", "legendary_actions"),
        ("MYTHIC ACTIONS",    "mythic_actions"),
        ("LAIR ACTIONS",      "lair_actions"),
        ("REGIONAL EFFECTS",  "regional_effects"),
        ("TREASURE",          "treasure"),
    ]:
        print_section(title, result.get(key) or "")

    console.print()