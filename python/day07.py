"""Day 7: Handy Haversacks.

The rules are a directed, edge-weighted graph over bag colours.  Parse once
into rules[colour] = [(count, child), ...], then walk it in both directions:

  - part1: reverse the edges and take the transitive closure of shiny
    gold's parents -- every colour that can eventually contain it,
  - part2: recursive weighted descendant count of one shiny gold bag.

Part 1 must be done on the reversed graph.  Asking "can this colour reach
shiny gold?" once per colour re-walks the same subgraphs over and over and
goes exponential; inverting the edges and doing one traversal outward from
shiny gold is O(V + E).
"""

import re
from pathlib import Path

TARGET = "shiny gold"

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day07.txt"


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


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
