"""Day 6: Custom Customs — a refactor of day06_mtl.py.

Same architecture as the _mtl original: one parse per part (part 1 builds
each group's union, part 2 its intersection), and part1/part2 that just
count set sizes. What changed in the refactor:

  - parse_input1's manual "char not in questions" dedup loop becomes a set
    union (|=) — same result, no O(n^2) membership scan, and now it mirrors
    parse_input2's intersection (&=): "anyone" = |, "everyone" = &.
  - parse_input2's unused `questions` bookkeeping is deleted.
  - part1/part2 use sum(...) over a generator instead of a `sum` accumulator
    variable (which shadowed the builtin).
"""

import re


def parse_input1(raw: str) -> list[set[str]]:
    # Part 1: questions ANYONE answered — union of the group's people.
    groups = []
    for block in re.split(r"\n\s*\n", raw.strip()):
        anyone = set()
        for person in block.split():
            anyone |= set(person)
        groups.append(anyone)
    return groups


def parse_input2(raw: str) -> list[set[str]]:
    # Part 2: questions EVERYONE answered — intersection of the group.
    # Union has an identity (the empty set) so part 1 can start empty;
    # intersection does not, so we must seed with the first person.
    groups = []
    for block in re.split(r"\n\s*\n", raw.strip()):
        everyone = None
        for person in block.split():
            if everyone is None:
                everyone = set(person)
            else:
                everyone &= set(person)
        groups.append(everyone)
    return groups


def part1(data: list[set[str]]) -> int:
    return sum(len(group) for group in data)


def part2(data: list[set[str]]) -> int:
    return sum(len(group) for group in data)


def solve(data1: list[set[str]], data2: list[set[str]]) -> tuple[int, int]:
    return part1(data1), part2(data2)


if __name__ == "__main__":
    from pathlib import Path

    raw = Path("inputs/day06.txt").read_text()
    data1 = parse_input1(raw)
    data2 = parse_input2(raw)
    p1, p2 = solve(data1, data2)
    print(f"part1={p1} part2={p2}")
