from typing import Annotated, List, cast
import typer
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text

from . import roller
from . import spell as spell_lookup

app = typer.Typer()

console = Console()

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
    console.print(result["description"] or "", markup=False)

    # At higher levels
    if result["higher_levels"]:
        console.print("\n[bold cyan]At Higher Levels.[/bold cyan]", end=" ")
        console.print(result["higher_levels"], markup=False)

@app.command()
def roll(
        times: Annotated[int, typer.Option(help="How many times to perform the operation")] = 1,
        detail: Annotated[bool, typer.Option(help="Displays each die roll")] = False,
        dice: Annotated[List[str], typer.Argument(help="Dice to roll. Can add a modifier. (Spaces allowed)")] = ["1d20"]
        ):
    """
    Rolls dice using D&D notation.
    """
    full_dice = "".join(dice)
    try:
        result = roller.roll(full_dice, times, detail)
        print(f'Total: {result}')
    except ValueError as e:
        print(e)

@app.command()
def spell(query: Annotated[List[str], typer.Argument(help="Name of the spell to lookup. Can fuzzy match.")]):
    """
    Looks up the information about the provided spell. UNFINISHED.
    """
    full_query = " ".join(query)
    result = spell_lookup.spell_lookup(full_query)

    if result == None:
        print(f"Could not find a spell with the name {query}")
    
    # result is either a dict or None, already checked for None
    # Doing this to supress editor warnings
    result = cast(dict, result)

    if result["match_score"] < 100:
        console.print(f"[dim]Closest match: '{result['name']}' ({result['match_score']:.0f}% match)[/dim]\n")

    print_spell(result)

if __name__ == "__main__":
    app()