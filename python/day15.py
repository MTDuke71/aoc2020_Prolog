"""Day 15: Rambunctious Recitation.

The Elves' memory game (Van Eck's sequence, to the OEIS): after the
starting numbers, each turn speaks the age of the previous number -- how
many turns ago it was last said before this -- or 0 if it was new.

Both parts are the same game stopped at different turns: 2,020 for part 1
and 30,000,000 for part 2.  There is no closed form and no known shortcut;
the sequence has to be walked turn by turn.  The whole solution is
therefore one engine, `play`, and the parts differ only in the turn they
pass it.

The engine keeps a single table, `last_seen[number] = turn it was most
recently spoken`, plus the current number *outside* the table.  That split
is the trick that makes each turn O(1): when `current` was spoken on the
previous turn, the table still holds its *earlier* occurrence, so the age
is one lookup -- no per-number history lists.  Only then is the table
updated and the next number computed.

Concretely, for 0,3,6 at the start of turn 5: current=0 (spoken on turn
4), and the table says 0 was last seen on turn 1.  Age = 4 - 1 = 3, so
turn 5 speaks 3, and only now does the table advance to last_seen[0]=4.

Part 2 is pure throughput: 30 million iterations of that loop.  The dict
is the readable shipping version; the function guide's sidebar shows a
flat-array variant (the table is really a direct-mapped store indexed by
number, since every spoken number is an age < final turn) that trades a
little clarity for a faster inner loop.
"""

from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day15.txt"

PART1_TURNS = 2_020
PART2_TURNS = 30_000_000


def parse_input(raw: str) -> list[int]:
    """One line of comma-separated starting numbers."""
    return [int(field) for field in raw.strip().split(",")]


def play(starting: list[int], final_turn: int) -> int:
    """Return the number spoken on turn `final_turn` (1-based).

    `last_seen` maps a number to the turn it was most recently spoken,
    deliberately *excluding* the current number's latest occurrence: at the
    top of the loop, `current` was spoken on turn `turn` but the table
    still points at the time before that, which is exactly what "how many
    turns apart" needs.  The table is then brought up to date and the next
    number derived, preserving the invariant for the next iteration.
    """
    if final_turn <= len(starting):
        return starting[final_turn - 1]

    last_seen = {number: turn for turn, number in enumerate(starting[:-1], start=1)}
    current = starting[-1]
    for turn in range(len(starting), final_turn):
        previous = last_seen.get(current)
        last_seen[current] = turn
        current = 0 if previous is None else turn - previous
    return current


def part1(starting: list[int]) -> int:
    return play(starting, PART1_TURNS)


def part2(starting: list[int]) -> int:
    return play(starting, PART2_TURNS)


def solve(raw: str) -> tuple[int, int]:
    starting = parse_input(raw)
    return part1(starting), part2(starting)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
