"""Day 4: Passport Processing.

Python algorithm reference mirroring src/day04.pl. Passports are
blank-line-separated blocks of key:value fields. Part 1 counts
passports with all seven required fields (cid optional); part 2
additionally validates every field's value.
"""

import re

REQUIRED = ["byr", "iyr", "eyr", "hgt", "hcl", "ecl", "pid"]
EYE_COLORS = {"amb", "blu", "brn", "gry", "grn", "hzl", "oth"}


def parse_input(raw: str) -> list[dict[str, str]]:
    passports = []
    for block in re.split(r"\n\s*\n", raw.strip()):
        fields = dict(token.split(":", 1) for token in block.split())
        passports.append(fields)
    return passports


def has_required_fields(passport: dict[str, str]) -> bool:
    return all(key in passport for key in REQUIRED)


def valid_year(value: str, lo: int, hi: int) -> bool:
    return re.fullmatch(r"\d{4}", value) is not None and lo <= int(value) <= hi


def valid_field(key: str, value: str) -> bool:
    if key == "byr":
        return valid_year(value, 1920, 2002)
    if key == "iyr":
        return valid_year(value, 2010, 2020)
    if key == "eyr":
        return valid_year(value, 2020, 2030)
    if key == "hgt":
        m = re.fullmatch(r"(\d+)(cm|in)", value)
        if m is None:
            return False
        height, unit = int(m.group(1)), m.group(2)
        return 150 <= height <= 193 if unit == "cm" else 59 <= height <= 76
    if key == "hcl":
        return re.fullmatch(r"#[0-9a-f]{6}", value) is not None
    if key == "ecl":
        return value in EYE_COLORS
    if key == "pid":
        return re.fullmatch(r"\d{9}", value) is not None
    return key == "cid"  # cid: always fine; unknown keys: invalid


def valid_passport(passport: dict[str, str]) -> bool:
    return has_required_fields(passport) and all(
        valid_field(key, value) for key, value in passport.items()
    )


def part1(passports: list[dict[str, str]]) -> int:
    return sum(map(has_required_fields, passports))


def part2(passports: list[dict[str, str]]) -> int:
    return sum(map(valid_passport, passports))


def solve(raw: str) -> tuple[int, int]:
    passports = parse_input(raw)
    return part1(passports), part2(passports)


if __name__ == "__main__":
    from pathlib import Path

    raw = Path("inputs/day04.txt").read_text()
    p1, p2 = solve(raw)
    print(f"part1={p1} part2={p2}")
