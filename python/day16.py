"""Day 16: Ticket Translation.

The input is a block-structured notes file: field rules, the player's ticket,
then a set of nearby tickets.  The rules are inclusive ranges, and the main
work is to separate invalid tickets from valid ones, then infer which field
name sits in each column.
"""

from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day16.txt"


def parse_input(raw: str) -> dict[str, object]:
    """Parse the field rules and both ticket lists.

    The returned structure is intentionally plain: it keeps the rules in a
    dict, and stores the player's ticket plus the nearby tickets as lists of
    ints.  That makes the validation and deduction logic linear and easy to
    read without introducing a custom class.
    """
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    rules: dict[str, list[tuple[int, int]]] = {}
    my_ticket: list[int] | None = None
    nearby_tickets: list[list[int]] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        if line == "your ticket:":
            i += 1
            my_ticket = [int(value) for value in lines[i].split(",")]
            i += 1
            continue
        if line == "nearby tickets:":
            i += 1
            while i < len(lines):
                nearby_tickets.append([int(value) for value in lines[i].split(",")])
                i += 1
            continue
        if ":" in line:
            name, spec = line.split(":", 1)
            ranges: list[tuple[int, int]] = []
            for span in spec.split(" or "):
                lo, hi = span.split("-")
                ranges.append((int(lo), int(hi)))
            rules[name.strip()] = ranges
            i += 1
            continue
        i += 1

    if my_ticket is None:
        raise ValueError("your ticket is missing from the input")

    return {"rules": rules, "my_ticket": my_ticket, "nearby_tickets": nearby_tickets}


def value_matches_rule(value: int, ranges: list[tuple[int, int]]) -> bool:
    return any(lo <= value <= hi for lo, hi in ranges)


def field_matches_any(value: int, rules: dict[str, list[tuple[int, int]]]) -> bool:
    return any(value_matches_rule(value, ranges) for ranges in rules.values())


def part1(parsed: dict[str, object]) -> int:
    rules = parsed["rules"]
    nearby = parsed["nearby_tickets"]
    total = 0
    for ticket in nearby:
        for value in ticket:
            if not field_matches_any(value, rules):
                total += value
    return total


def part2(parsed: dict[str, object]) -> int:
    rules = parsed["rules"]
    my_ticket = parsed["my_ticket"]
    valid_tickets = [
        ticket
        for ticket in parsed["nearby_tickets"]
        if all(field_matches_any(value, rules) for value in ticket)
    ]

    candidate_sets: list[set[str]] = []
    for position in range(len(my_ticket)):
        candidates = {
            name
            for name, ranges in rules.items()
            if all(value_matches_rule(ticket[position], ranges) for ticket in valid_tickets)
        }
        candidate_sets.append(candidates)

    while any(len(options) > 1 for options in candidate_sets):
        assigned = {next(iter(options)) for options in candidate_sets if len(options) == 1}
        if not assigned:
            break
        for options in candidate_sets:
            if len(options) > 1:
                options.difference_update(assigned)

    if any(len(options) != 1 for options in candidate_sets):
        raise ValueError("field ordering could not be resolved uniquely")

    mapping = {position: next(iter(options)) for position, options in enumerate(candidate_sets)}
    product = 1
    for position, field_name in mapping.items():
        if field_name.startswith("departure"):
            product *= my_ticket[position]
    return product


def solve(raw: str) -> tuple[int, int]:
    parsed = parse_input(raw)
    return part1(parsed), part2(parsed)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
