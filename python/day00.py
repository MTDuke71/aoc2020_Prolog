"""Day 0: The Tyranny of the Rocket Equation (tutorial dry run).

Python algorithm reference mirroring src/day00.pl. Input is one integer
module mass per line.
"""


def parse_input(raw: str) -> list[int]:
    return [int(line) for line in raw.splitlines() if line.strip()]


def fuel(mass: int) -> int:
    """Base equation: floor(mass / 3) - 2."""
    return mass // 3 - 2


def total_fuel(mass: int) -> int:
    """Part 2: fuel for the fuel, recursively, until a step is <= 0."""
    total = 0
    f = fuel(mass)
    while f > 0:
        total += f
        f = fuel(f)
    return total


def part1(data: list[int]) -> int:
    return sum(fuel(m) for m in data)


def part2(data: list[int]) -> int:
    return sum(total_fuel(m) for m in data)


def solve(raw: str) -> tuple[int, int]:
    data = parse_input(raw)
    return part1(data), part2(data)


if __name__ == "__main__":
    from pathlib import Path

    raw = Path("inputs/day00.txt").read_text()
    p1, p2 = solve(raw)
    print(f"part1={p1} part2={p2}")
