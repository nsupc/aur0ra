import os

from typing import List


def get_old_pop(path: str) -> List[str] | None:
    if os.path.exists(path):
        with open(path, "r") as in_file:
            return in_file.read().splitlines()
    else:
        return None


def write_old_pop(path: str, pop: List[str]):
    with open(path, "w") as out_file:
        out_file.write("\n".join(pop))


def format_pings(input: List[str]) -> str:
    nations = [f"[nation]{nation}[/nation]" for nation in input]

    if len(nations) == 1:
        return nations[0]
    elif len(nations) == 2:
        return " and ".join(nations)
    else:
        return ", ".join(nations[:-1]) + ", and " + nations[-1]
