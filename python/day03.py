"""Day 3: Toboggan Trajectory.

The map of open
squares (.) and trees (#) repeats infinitely to the right; count trees
hit descending at a fixed slope. Part 1: right 3, down 1. Part 2:
product of tree counts over five fixed slopes.
"""

import math
from pathlib import Path

SLOPES = [(1, 1), (3, 1), (5, 1), (7, 1), (1, 2)]

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day03.txt"


def parse_input(raw: str) -> list[str]:
    return [line.strip() for line in raw.splitlines() if line.strip()]


def slope_trees(rows: list[str], right: int, down: int) -> int:
    return sum(row[(i * right) % len(row)] == "#" for i, row in enumerate(rows[::down]))


def part1(rows: list[str]) -> int:
    return slope_trees(rows, 3, 1)


def part2(rows: list[str]) -> int:
    return math.prod(slope_trees(rows, r, d) for r, d in SLOPES)


def solve(raw: str) -> tuple[int, int]:
    rows = parse_input(raw)
    return part1(rows), part2(rows)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
