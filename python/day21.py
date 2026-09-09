"""Day 21: Allergen Assessment.

Each line of the input is a food: an ingredients list in a language I cannot
read, then (usually) a parenthesised list of allergens in one I can.  Two
rules make the puzzle solvable.  Each allergen lives in exactly one
ingredient, and when a food lists an allergen, the ingredient holding it is
somewhere in that food's ingredients list.  Allergens are not always listed,
so a food *not* naming an allergen says nothing at all.

Put together, the ingredient holding allergen A must appear in *every* food
that lists A -- so A's candidates are the intersection of those foods'
ingredient sets.  On the statement's four foods:

    dairy: food 1 ∩ food 2 = {mxmxvkd}
    fish:  food 1 ∩ food 4 = {mxmxvkd, sqjhc}
    soy:   food 3          = {sqjhc, fvjkl}

Part 1 counts the appearances of every ingredient in *no* candidate set --
those cannot possibly carry an allergen (kfcds, nhms, sbzzf, trh: five
appearances).  Part 2 resolves the candidates to one ingredient per allergen
by elimination, day 16's move again: dairy is forced to mxmxvkd, striking it
leaves fish = {sqjhc}, striking that leaves soy = {fvjkl}.  The answer is
those ingredients sorted by allergen name and joined with commas, a string
rather than a number: `mxmxvkd,sqjhc,fvjkl`.
"""

from pathlib import Path
from typing import NamedTuple

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day21.txt"


class Food(NamedTuple):
    ingredients: tuple[str, ...]  # as written, so repeated appearances count
    allergens: tuple[str, ...]  # empty when the food carries no "(contains ...)"


def parse_input(raw: str) -> list[Food]:
    """One `Food` per non-blank line.

    `splitlines()` plus a per-line `.strip()` drops a Windows `\r` before
    the closing `)` is trimmed; otherwise the last allergen on every line
    would be `wheat)\r` and no two lines would agree on any allergen.
    """
    foods = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        head, tagged, tail = line.partition(" (contains ")
        ingredients = tuple(head.split())
        allergens = tuple(tail.removesuffix(")").split(", ")) if tagged else ()
        foods.append(Food(ingredients, allergens))
    return foods


def candidates(foods: list[Food]) -> dict[str, set[str]]:
    """Per allergen, the ingredients that appear in every food listing it.

    That intersection is the whole of what the statement's two rules say:
    the ingredient holding an allergen is in each ingredients list that
    names the allergen, and a food that does not name it is no evidence.
    """
    possible: dict[str, set[str]] = {}
    for food in foods:
        present = set(food.ingredients)
        for allergen in food.allergens:
            if allergen in possible:
                possible[allergen] &= present
            else:
                possible[allergen] = set(present)
    return possible


def assign(possible: dict[str, set[str]]) -> dict[str, str]:
    """Resolve candidate sets to one ingredient per allergen, by elimination.

    Repeatedly take every allergen with exactly one candidate left, give it
    that ingredient, and strike the ingredient from the other allergens'
    sets.  Sound because a single candidate is forced whatever else is
    true; complete only when every round forces at least one allergen,
    which is how the puzzle inputs are built.  If a round forces nothing
    the sets admit more than one matching, so raise rather than guess.
    """
    remaining = {allergen: set(ingredients) for allergen, ingredients in possible.items()}
    holder: dict[str, str] = {}

    while remaining:
        forced = {allergen for allergen, options in remaining.items() if len(options) == 1}
        if not forced:
            raise ValueError("allergen assignment is not forced by elimination alone")
        for allergen in forced:
            (holder[allergen],) = remaining.pop(allergen)
        taken = {holder[allergen] for allergen in forced}
        for options in remaining.values():
            options -= taken

    if len(set(holder.values())) != len(holder):
        raise ValueError("two allergens were forced to the same ingredient")
    return holder


def part1(foods: list[Food]) -> int:
    """How many times ingredients that cannot hold any allergen appear, over all foods."""
    suspect = set().union(*candidates(foods).values())
    return sum(ingredient not in suspect for food in foods for ingredient in food.ingredients)


def part2(foods: list[Food]) -> str:
    """The canonical dangerous ingredient list: holders sorted by allergen, comma-joined."""
    holder = assign(candidates(foods))
    return ",".join(holder[allergen] for allergen in sorted(holder))


def solve(raw: str) -> tuple[int, str]:
    foods = parse_input(raw)
    return part1(foods), part2(foods)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
