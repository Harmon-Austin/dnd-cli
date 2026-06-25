from typing import Annotated, List, cast
import typer

from . import roller, spell as spell_lookup, printer, monster as monster_lookup

app = typer.Typer()

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
    Looks up the information about the provided spell.
    """
    full_query = " ".join(query)
    result = spell_lookup.spell_lookup(full_query)

    if result == None:
        print(f"Could not find a spell with the name {query}")
        return
    
    # result is either a dict or None, already checked for None
    # Doing this to supress editor warnings
    result = cast(dict, result)

    if result["match_score"] < 100:
        printer.rich_print(f"[dim]Closest match: '{result['name']}' ({result['match_score']:.0f}% match)[/dim]\n")

    printer.print_spell(result)

@app.command()
def monster(query: Annotated[List[str], typer.Argument(help="Name of the monster to lookup. Can fuzzy match.")], 
            list: Annotated[bool, typer.Argument(help="List the top 10 results of the query without printing information.")] = False):
    """
    Looks up the queried stat block.
    """
    full_query = " ".join(query)
    result = monster_lookup.monster_lookup(full_query)

    if result == None:
        print(f"Could not find a stat block with the name {full_query}")
        return
    
    # result is either a dict or None, already checked for None
    # Doing this to supress editor warnings
    result = cast(dict, result)

    if result["match_score"] < 100:
        printer.rich_print(f"[dim]Closest match: '{result['name']}' ({result['match_score']:.0f}% match)[/dim]\n")

    printer.print_monster(result)

if __name__ == "__main__":
    app()