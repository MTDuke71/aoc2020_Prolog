"""Day 6: Custom Customs — canonical reference for the Prolog solution.

Mirrors src/day06.pl's architecture: parse ONCE into groups (each group a
list of per-person letter sets), then part1 sums each group's union size
("anyone answered yes") and part2 sums each group's intersection size
("everyone answered yes"). "Anyone" = |, "everyone" = &.

python/day06_opt.py and python/day06_mtl.py keep the earlier per-part-parse
shape; this file is the one that lines up predicate-for-predicate with the
Prolog and re-confirms part1=6683 / part2=3122.
"""

import re


def parse_input(raw: str) -> list[list[set[str]]]:
    # Groups separated by blank lines; each person's line -> a set of letters.
    groups = []
    for block in re.split(r"\n\s*\n", raw.strip()):
        people = [set(line) for line in block.split("\n") if line.strip()]
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


if __name__ == "__main__":
    from pathlib import Path

    raw = Path("inputs/day06.txt").read_text()
    p1, p2 = solve(raw)
    print(f"part1={p1} part2={p2}")
