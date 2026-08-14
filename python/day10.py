"""Day 10: Adapter Array.

Every adapter must be used and each accepts an input 1-3 jolts below its
rating, so sorting the ratings fixes the single chain that uses them all.
Part 1 multiplies the number of 1-jolt steps by the number of 3-jolt steps.
Part 2 counts the distinct sub-chains that still connect outlet to device --
a linear DP where ways[v] = ways[v-1] + ways[v-2] + ways[v-3].
"""

from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day10.txt"


def parse_input(raw: str) -> list[int]:
    return [int(line) for line in raw.splitlines() if line.strip()]


def full_chain(ratings: list[int]) -> list[int]:
    # Outlet at 0, adapters ascending, device at highest + 3.
    ordered = sorted(ratings)
    return [0, *ordered, ordered[-1] + 3]


def differences(chain: list[int]) -> list[int]:
    return [hi - lo for lo, hi in zip(chain, chain[1:])]


def part1(ratings: list[int]) -> int:
    diffs = differences(full_chain(ratings))
    return diffs.count(1) * diffs.count(3)


def arrangements(chain: list[int]) -> int:
    # ways[v] = number of chains from the outlet that end at link v.
    ways = {chain[0]: 1}
    for value in chain[1:]:
        ways[value] = sum(ways.get(value - gap, 0) for gap in (1, 2, 3))
    return ways[chain[-1]]


def part2(ratings: list[int]) -> int:
    return arrangements(full_chain(ratings))


def solve(raw: str) -> tuple[int, int]:
    ratings = parse_input(raw)
    chain = full_chain(ratings)
    diffs = differences(chain)
    return diffs.count(1) * diffs.count(3), arrangements(chain)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
