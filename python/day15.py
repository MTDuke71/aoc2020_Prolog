def parse_input(raw: str) -> list[str]:
    return [line.strip() for line in raw.splitlines() if line.strip()]


def part1(data: list[str]) -> int:
    return len(data)


def part2(data: list[str]) -> int:
    return len(data)


def solve(raw: str) -> tuple[int, int]:
    data = parse_input(raw)
    return part1(data), part2(data)
