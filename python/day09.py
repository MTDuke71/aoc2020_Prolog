"""Day 9: Encoding Error.

After a 25-number preamble, each number must be the sum of two different
values from the preceding 25 numbers. Part 1 finds the first invalid number;
Part 2 finds a contiguous range before it and returns min(range)+max(range).

The optional preamble argument is useful for the statement's five-number
example and defaults to the real puzzle size of 25.
"""

from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day09.txt"


def parse_input(raw: str) -> list[int]:
    return [int(line) for line in raw.splitlines() if line.strip()]


def has_valid_sum(target: int, window: list[int]) -> bool:
    # Different values are required, so a lone 25 cannot make 50 valid.
    return any(a != b and a + b == target for i, a in enumerate(window) for b in window[i + 1 :])


def find_invalid(numbers: list[int], preamble: int = 25) -> tuple[int, int]:
    for i in range(preamble, len(numbers)):
        window = numbers[i - preamble : i]
        if not has_valid_sum(numbers[i], window):
            return i, numbers[i]
    raise ValueError("no invalid number")


def part1(numbers: list[int], preamble: int = 25) -> int:
    return find_invalid(numbers, preamble)[1]


def contiguous_range(numbers: list[int], target: int) -> list[int]:
    # All puzzle values are positive, so a growing window can stop on an
    # overshoot. Start each candidate range at every position.
    for start in range(len(numbers)):
        total = numbers[start]
        for end in range(start + 1, len(numbers)):
            total += numbers[end]
            if total == target:
                return numbers[start : end + 1]
            if total > target:
                break
    raise ValueError("no contiguous range")


def part2(numbers: list[int], preamble: int = 25) -> int:
    invalid_index, invalid = find_invalid(numbers, preamble)
    values = contiguous_range(numbers[:invalid_index], invalid)
    return min(values) + max(values)


def solve(raw: str) -> tuple[int, int]:
    numbers = parse_input(raw)
    return part1(numbers), part2(numbers)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
