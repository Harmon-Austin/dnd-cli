from typing import Annotated, List
import typer

from . import roller

app = typer.Typer()

@app.command()
def roll(
        times: Annotated[int, typer.Option(help="How many times to perform the operation")] = 1,
        full: Annotated[bool, typer.Option(help="Displays each die roll")] = False,
        dice: Annotated[List[str], typer.Argument(help="Dice to roll. Can add a modifier. (Spaces allowed)")] = "1d20"
        ):
    """
    Rolls dice using D&D notation.
    """
    full_dice = "".join(dice)
    try:
        result = roller.roll(full_dice, times, full)
        print(f'Total: {result}')
    except ValueError as e:
        print(e)

@app.command()
def spell(query: str):
    """
    Looks up the information about the provided spell. UNFINISHED.
    """
    print("Unfinished")

if __name__ == "__main__":
    app()