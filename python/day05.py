"""Day 5: Binary Boarding.

Each boarding pass is
a 10-bit binary number: F/L = 0 (lower half), B/R = 1 (upper half). Read
whole, the pass equals its seat ID (Row*8 + Col). Part 1 is the highest
ID; part 2 is the one interior gap whose neighbours are both occupied.
"""

from pathlib import Path

BITS = str.maketrans("FBLR", "0101")


def seat_id(boarding_pass: str) -> int:
    return int(boarding_pass.translate(BITS), 2)


INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day05.txt"


def parse_input(raw: str) -> list[int]:
    return [seat_id(line.strip()) for line in raw.splitlines() if line.strip()]


def part1(ids: list[int]) -> int:
    return max(ids)


def part2(ids: list[int]) -> int:
    occupied = sorted(ids)
    for lo, hi in zip(occupied, occupied[1:]):
        if hi == lo + 2:
            return lo + 1
    raise ValueError("no missing seat found")


def solve(raw: str) -> tuple[int, int]:
    ids = parse_input(raw)
    return part1(ids), part2(ids)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
