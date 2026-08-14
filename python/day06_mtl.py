import re


def parse_input1(raw: str) -> list[dict[str, str]]:
    groups = []

    for block in re.split(r"\n\s*\n", raw.strip()):
        questions = []
        for char in block:
            if char != "\n" and char != " " and char != "":
                if char not in questions:
                    questions.append(char)
        groups.append(questions)
    return groups


def parse_input2(raw: str) -> list[dict[str, str]]:
    groups = []

    for block in re.split(r"\n\s*\n", raw.strip()):
        questions = []
        common = set()
        first = True
        for line in block.split("\n"):
            if first:
                common = set(line)
                first = False
            else:
                common &= set(line)
            if line != "\n" and line != " " and line != "":
                if line not in questions:
                    questions.append(line)
        groups.append(common)
    return groups


def part1(data: list[dict[str, str]]) -> int:
    sum = 0
    for group in data:
        sum += len(group)
    return sum


def part2(data: list[dict[str, str]]) -> int:
    sum = 0
    for group in data:
        sum += len(group)
    return sum


def solve(data1: list[dict[str, str]], data2: list[dict[str, str]]) -> tuple[int, int]:
    p1 = part1(data1)
    p2 = part2(data2)
    return p1, p2


if __name__ == "__main__":
    from pathlib import Path

    raw = Path("inputs/day06.txt").read_text()
    data1 = parse_input1(raw)
    data2 = parse_input2(raw)
    p1, p2 = solve(data1, data2)
    print(f"part1={p1} part2={p2}")
