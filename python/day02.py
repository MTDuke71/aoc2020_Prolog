"""Day 2: Password Philosophy.

Python algorithm reference mirroring src/day02.pl. Each line pairs a
policy with a password: "Lo-Hi L: password". Part 1 counts passwords
where L occurs between Lo and Hi times (inclusive); part 2 counts
passwords where exactly one of the 1-indexed positions Lo and Hi holds L.
"""

import re
from typing import NamedTuple


class Entry(NamedTuple):
    lo: int
    hi: int
    letter: str
    password: str


LINE = re.compile(r"(\d+)-(\d+) (\S): (\S+)")


def parse_input(raw: str) -> list[Entry]:
    entries = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        m = LINE.fullmatch(line)
        if m is None:
            raise ValueError(f"bad line: {line!r}")
        lo, hi, letter, password = m.groups()
        entries.append(Entry(int(lo), int(hi), letter, password))
    return entries


def valid_count(e: Entry) -> bool:
    return e.lo <= e.password.count(e.letter) <= e.hi


def valid_position(e: Entry) -> bool:
    return (e.password[e.lo - 1] == e.letter) != (e.password[e.hi - 1] == e.letter)


def part1(entries: list[Entry]) -> int:
    return sum(map(valid_count, entries))


def part2(entries: list[Entry]) -> int:
    return sum(map(valid_position, entries))


def solve(raw: str) -> tuple[int, int]:
    entries = parse_input(raw)
    return part1(entries), part2(entries)


if __name__ == "__main__":
    from pathlib import Path

    raw = Path("inputs/day02.txt").read_text()
    p1, p2 = solve(raw)
    print(f"part1={p1} part2={p2}")
