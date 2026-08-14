"""Day 1: Report Repair.

Input is one integer expense entry per line; find the 2 (part 1) / 3
(part 2) entries summing to 2020 and multiply them.  This is k-SUM, done
as a depth-first take/skip walk rather than itertools.combinations, so the
ascending-order bound can prune whole subtrees.
"""

import math
from pathlib import Path
from typing import Iterator

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day01.txt"


def parse_input(raw: str) -> list[int]:
    return [int(line) for line in raw.splitlines() if line.strip()]


def k_sum(k: int, target: int, entries: list[int], start: int = 0) -> Iterator[list[int]]:
    """Yield every k-element combination of entries[start:] summing to target.

    Entries must be sorted ascending and non-negative: that is what makes
    the `x > target` break sound.  Once one candidate overshoots, every
    later one does too, so the rest of the level can be abandoned.
    """
    if k == 0:
        if target == 0:
            yield []
        return
    for i in range(start, len(entries)):
        x = entries[i]
        if x > target:
            break  # ascending: everything after is too big as well
        for combo in k_sum(k - 1, target - x, entries, i + 1):
            yield [x, *combo]


def entry_product(k: int, entries: list[int]) -> int:
    combo = next(k_sum(k, 2020, sorted(entries)))
    return math.prod(combo)


def part1(entries: list[int]) -> int:
    return entry_product(2, entries)


def part2(entries: list[int]) -> int:
    return entry_product(3, entries)


def solve(raw: str) -> tuple[int, int]:
    entries = parse_input(raw)
    return part1(entries), part2(entries)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
