"""Day 6: Custom Customs.

Parse once into groups, each group a list of per-person letter sets, then
part1 sums each group's union size ("anyone answered yes") and part2 sums
each group's intersection size ("everyone answered yes").  The whole puzzle
is that one word swap: "anyone" is |, "everyone" is &.

day06_opt.py and day06_mtl.py are earlier takes that parse separately per
part; this is the maintained one.
"""

import re
from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day06.txt"


def parse_input(raw: str) -> list[list[set[str]]]:
    # Groups separated by blank lines; each person's line -> a set of letters.
    groups = []
    for block in re.split(r"\n\s*\n", raw.strip()):
        # splitlines() with a per-line strip, not split("\n"): on a CRLF input
        # the latter leaves a trailing \r in every line, and set() then counts
        # it as a 27th question everybody answered yes to.
        people = [set(line.strip()) for line in block.splitlines() if line.strip()]
        groups.append(people)
    return groups


def group_anyone(people: list[set[str]]) -> int:
    # Union has identity (empty set), so fold from an empty set.
    return len(set().union(*people))


def group_everyone(people: list[set[str]]) -> int:
    # Intersection has no identity; seed with the first person.
    return len(people[0].intersection(*people[1:]))


def part1(groups: list[list[set[str]]]) -> int:
    return sum(group_anyone(g) for g in groups)


def part2(groups: list[list[set[str]]]) -> int:
    return sum(group_everyone(g) for g in groups)


def solve(raw: str) -> tuple[int, int]:
    groups = parse_input(raw)
    return part1(groups), part2(groups)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
