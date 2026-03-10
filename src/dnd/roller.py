import re
import random

def roll(dice: str, times: int, full: bool) -> int:
    clean_dice = dice.replace(" ", "").lower()
    PATTERN = re.compile(r"(\d+)[dD](\d+)([+-]\d+)?$")
    if not re.fullmatch(PATTERN, clean_dice):
        raise ValueError(f"Invalid dice format '{dice}'. Expected format: XdY+Z")
    
    values = re.split(r"[d+-]+", clean_dice)
    if re.search(r"[-]+", clean_dice):
        values[2] = int(values[2]) * -1

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
        if full:
            roll_history = ", ".join(roll_history)
            print(f"Rolled {num_of_die}d{sides}: {roll_history}")
        result += sum

    return result + modifier