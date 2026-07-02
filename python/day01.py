"""Day 1: Report Repair.

Python algorithm reference mirroring src/day01.pl. Input is one integer
expense entry per line; find the 2 (part 1) / 3 (part 2) entries summing
to 2020 and multiply them.
"""

import math
from typing import Iterator


def parse_input(raw: str) -> list[int]:
    return [int(line) for line in raw.splitlines() if line.strip()]


def k_sum(k: int, target: int, entries: list[int], start: int = 0) -> Iterator[list[int]]:
    """Yield every k-element combination of entries[start:] summing to target.

    Mirrors the Prolog k_sum/4: entries must be ascending and non-negative
    so the `x <= target` guard prunes doomed branches.
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


if __name__ == "__main__":
    from pathlib import Path

    raw = Path("inputs/day01.txt").read_text()
    p1, p2 = solve(raw)
    print(f"part1={p1} part2={p2}")
