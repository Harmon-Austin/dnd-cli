import re
import random

def roll(dice: str, times: int, detail: bool) -> int:
    # Clean text input to be read by the regex check for formatting
    clean_dice = dice.replace(" ", "").lower()
    PATTERN = re.compile(r"(\d+)[dD](\d+)([+-]\d+)?$")
    if not re.fullmatch(PATTERN, clean_dice):
        raise ValueError(f"Invalid dice format '{dice}'. Expected format: XdY+Z")
    
    # Determine if modifier is positive or negative
    values = re.split(r"[d+-]+", clean_dice)
    if re.search(r"[-]+", clean_dice):
        values[2] = int(values[2]) * -1

    # Roll the dice according to the parsed values and flags
    result = 0
    num_of_die = int(values[0])
    sides = int(values[1])
    modifier = 0
    if len(values) == 3:
        modifier = int(values[2])

    for x in range(0, times):
        sum = 0
        roll_history = []
        for y in range(0, num_of_die):
            die_roll = random.randint(1, sides)
            sum += die_roll
            roll_history.append(str(die_roll))
        if detail:
            roll_history = ", ".join(roll_history)
            print(f"Rolled {num_of_die}d{sides}: {roll_history}")
        result += sum

    return result + modifier