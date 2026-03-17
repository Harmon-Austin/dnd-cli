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
