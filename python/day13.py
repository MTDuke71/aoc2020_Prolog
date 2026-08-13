"""Day 13: Shuttle Search -- canonical reference for the Prolog solution.

Bus N departs at every timestamp divisible by N.  Both parts are modular
arithmetic on the same notes:

  Part 1: the wait for bus `id` at minute `earliest` is (-earliest) % id;
          minimise over the buses and report id * wait.
  Part 2: bus `id` at list offset `off` must depart at t + off, i.e.
          t == -off (mod id).  That is a simultaneous congruence system,
          solved by the Chinese Remainder Theorem.  The IDs are distinct
          primes, so a unique solution exists modulo their product.

The CRT is done here as an incremental sieve: keep (t, step) meaning "the
solutions so far are t, t+step, t+2*step, ...", walk that progression until
it also satisfies the next bus, then multiply step by that bus ID.  Fewer
than `id` strides per bus, so a handful of thousands of steps for an answer
near 10^15.

Python's % is floored like Prolog's (unlike C/Rust), so (-earliest) % id
lands in 0..id-1 with no correction.
"""


def parse_input(raw: str) -> tuple[int, list[tuple[int, int]]]:
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    earliest = int(lines[0])
    buses = [
        (offset, int(field))
        for offset, field in enumerate(lines[1].split(","))
        if field != "x"
    ]
    return earliest, buses


def part1(notes: tuple[int, list[tuple[int, int]]]) -> int:
    earliest, buses = notes
    wait, bus = min(((-earliest) % bus, bus) for _offset, bus in buses)
    return bus * wait


def part2(notes: tuple[int, list[tuple[int, int]]]) -> int:
    _earliest, buses = notes
    t, step = 0, 1
    for offset, bus in buses:
        while (t + offset) % bus:
            t += step
        step *= bus
    return t


def solve(raw: str) -> tuple[int, int]:
    notes = parse_input(raw)
    return part1(notes), part2(notes)


if __name__ == "__main__":
    from pathlib import Path

    raw = Path("inputs/day13.txt").read_text()
    p1, p2 = solve(raw)
    print(f"part1={p1} part2={p2}")
