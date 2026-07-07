"""Day 7: Handy Haversacks — canonical reference for the Prolog solution.

The rules are a directed, edge-weighted graph over bag colours. Mirrors
src/day07.pl: parse once into rules[colour] = [(count, child), ...], then

  - part1: reverse the edges and take the transitive closure of shiny
    gold's parents (every colour that can eventually contain it),
  - part2: recursive weighted descendant count of one shiny gold bag.

Re-confirms part1=370 / part2=29547.
"""

import re

TARGET = "shiny gold"


def parse_input(raw: str) -> dict[str, list[tuple[int, str]]]:
    rules = {}
    for line in raw.strip().splitlines():
        colour, rest = line.split(" bags contain ")
        rest = rest.rstrip(".")
        if rest == "no other bags":
            rules[colour] = []
            continue
        children = []
        for item in rest.split(", "):
            m = re.match(r"(\d+) (.+) bags?$", item)
            children.append((int(m.group(1)), m.group(2)))
        rules[colour] = children
    return rules


def part1(rules: dict[str, list[tuple[int, str]]]) -> int:
    # Invert to child -> {parents}, then BFS the closure of TARGET's parents.
    parents: dict[str, set[str]] = {}
    for colour, children in rules.items():
        for _count, child in children:
            parents.setdefault(child, set()).add(colour)

    seen: set[str] = set()
    queue = list(parents.get(TARGET, set()))
    while queue:
        c = queue.pop()
        if c in seen:
            continue
        seen.add(c)
        queue.extend(parents.get(c, set()))
    return len(seen)


def contained_count(rules: dict[str, list[tuple[int, str]]], colour: str) -> int:
    return sum(n * (1 + contained_count(rules, child)) for n, child in rules[colour])


def part2(rules: dict[str, list[tuple[int, str]]]) -> int:
    return contained_count(rules, TARGET)


def solve(raw: str) -> tuple[int, int]:
    rules = parse_input(raw)
    return part1(rules), part2(rules)


if __name__ == "__main__":
    from pathlib import Path

    raw = Path("inputs/day07.txt").read_text()
    p1, p2 = solve(raw)
    print(f"part1={p1} part2={p2}")
