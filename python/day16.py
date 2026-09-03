"""Day 16: Ticket Translation.

The notes hold three things: a rule per field (a name and two inclusive
ranges, `class: 1-3 or 5-7`), my ticket, and a stack of nearby tickets.
Every ticket is the same list of numbers in the same unknown column order.

The two parts are two filters in series.  Part 1 looks at each value on
its own: a value that no field's ranges accept cannot belong anywhere, and
the "ticket scanning error rate" is the sum of those.  Part 2 throws away
every ticket that carried one, then asks which field lives in which
column.  The only evidence is the values themselves: field F can be in
column c only if F's ranges accept *every* surviving value in column c.

That gives one candidate set per column, and the puzzle is built so they
resolve by elimination.  On the real input the twenty sets are nested like
a staircase -- one column has 1 candidate, one has 2, ... one has all 20 --
so the 1-candidate column is forced, removing its field forces the
2-candidate column, and so on down.  Concretely, with the statement's own
Part Two example (fields class/row/seat, three valid tickets):

    column 0 accepts {row}              -> row   (forced)
    column 1 accepts {class, row}       -> minus row   = class
    column 2 accepts {class, row, seat} -> minus row, class = seat

The answer is the product of my ticket's values in the six columns whose
field name starts with "departure".

The machine framing that makes this cheap: values are small (0..999), so a
rule is really a 1000-entry lookup table, and "which fields accept this
value" is one table read.  The shipping code keeps the ranges as ranges
because that is what the statement says; the function guide's sidebar
shows the table version.
"""

from math import prod
from pathlib import Path
from typing import NamedTuple

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day16.txt"

Ranges = tuple[tuple[int, int], ...]


class Notes(NamedTuple):
    rules: dict[str, Ranges]  # field name -> inclusive (lo, hi) spans, in input order
    mine: list[int]
    nearby: list[list[int]]


def parse_input(raw: str) -> Notes:
    """Three blank-line-separated blocks: rules, "your ticket:", "nearby tickets:".

    Rejoining `splitlines()` normalises CRLF before the block split, so a
    Windows download's `\\r\\n\\r\\n` separators land as `\\n\\n` (the day 6
    lesson: a surviving `\\r` would otherwise ride along on the last field of
    every ticket line).
    """
    rules_block, mine_block, nearby_block = "\n".join(raw.splitlines()).strip().split("\n\n")

    rules: dict[str, Ranges] = {}
    for line in rules_block.splitlines():
        name, spec = line.split(": ")
        rules[name] = tuple(_span(text) for text in spec.split(" or "))

    return Notes(
        rules=rules,
        mine=_ticket(mine_block.splitlines()[1]),
        nearby=[_ticket(line) for line in nearby_block.splitlines()[1:]],
    )


def _span(text: str) -> tuple[int, int]:
    lo, hi = text.split("-")
    return int(lo), int(hi)


def _ticket(line: str) -> list[int]:
    return [int(value) for value in line.split(",")]


def accepts(ranges: Ranges, value: int) -> bool:
    """True when `value` lies inside one of the field's inclusive spans."""
    return any(lo <= value <= hi for lo, hi in ranges)


def invalid_values(ticket: list[int], rules: dict[str, Ranges]) -> list[int]:
    """The values on `ticket` that no field at all would accept.

    Empty means the ticket is valid.  This is the one predicate both parts
    share: part 1 sums these, part 2 keeps the tickets for which the list
    is empty.
    """
    return [value for value in ticket if not any(accepts(ranges, value) for ranges in rules.values())]


def part1(notes: Notes) -> int:
    """Ticket scanning error rate: the sum of every invalid value on nearby tickets."""
    return sum(sum(invalid_values(ticket, notes.rules)) for ticket in notes.nearby)


def candidate_fields(rules: dict[str, Ranges], tickets: list[list[int]]) -> list[set[str]]:
    """Per column, the set of field names whose ranges accept every value in it."""
    columns = list(zip(*tickets))
    return [
        {name for name, ranges in rules.items() if all(accepts(ranges, value) for value in column)}
        for column in columns
    ]


def assign_fields(rules: dict[str, Ranges], tickets: list[list[int]]) -> list[str]:
    """Return the field name of each column, deduced by elimination.

    Repeatedly take every column that has exactly one candidate left, give
    it that field, and strike the field from the other columns' sets.  This
    terminates with a full assignment whenever the candidate sets are nested
    (a chain), which is how the puzzle inputs are built; if a round finds no
    forced column the sets are not a chain and a real matching search would
    be needed, so raise rather than guess.
    """
    candidates = candidate_fields(rules, tickets)
    names: list[str | None] = [None] * len(candidates)
    unresolved = set(range(len(candidates)))

    while unresolved:
        forced = {column for column in unresolved if len(candidates[column]) == 1}
        if not forced:
            raise ValueError("field order is not forced by elimination alone")
        for column in forced:
            (names[column],) = candidates[column]
        unresolved -= forced
        taken = {names[column] for column in forced}
        for column in unresolved:
            candidates[column] -= taken

    if len(set(names)) != len(names):
        raise ValueError("two columns were forced to the same field")
    return names


def part2(notes: Notes) -> int:
    """Product of my ticket's values in the columns whose field starts with "departure"."""
    valid = [ticket for ticket in notes.nearby if not invalid_values(ticket, notes.rules)]
    order = assign_fields(notes.rules, valid)
    return prod(value for name, value in zip(order, notes.mine) if name.startswith("departure"))


def solve(raw: str) -> tuple[int, int]:
    notes = parse_input(raw)
    return part1(notes), part2(notes)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
