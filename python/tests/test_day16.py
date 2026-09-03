"""Day 16: Ticket Translation."""

from itertools import pairwise

import pytest

import day16

LOCKED = (21996, 650080463519)

# The statement's Part One notes.
SAMPLE = """class: 1-3 or 5-7
row: 6-11 or 33-44
seat: 13-40 or 45-50

your ticket:
7,1,14

nearby tickets:
7,3,47
40,4,50
55,2,20
38,6,12
"""

# The statement's Part Two notes: three valid tickets that pin the column
# order to row, class, seat.
PART2_SAMPLE = """class: 0-1 or 4-19
row: 0-5 or 8-19
seat: 0-13 or 16-19

your ticket:
11,12,13

nearby tickets:
3,9,18
15,1,5
5,14,9
"""

# Same notes with two fields promoted to "departure ..." so part 2 has
# something to multiply: my row (11) times my seat (13).
DEPARTURE_SAMPLE = PART2_SAMPLE.replace("row:", "departure row:").replace("seat:", "departure seat:")


def test_parse_input():
    notes = day16.parse_input(SAMPLE)
    assert notes.rules == {
        "class": ((1, 3), (5, 7)),
        "row": ((6, 11), (33, 44)),
        "seat": ((13, 40), (45, 50)),
    }
    assert notes.mine == [7, 1, 14]
    assert notes.nearby == [[7, 3, 47], [40, 4, 50], [55, 2, 20], [38, 6, 12]]


def test_field_names_may_contain_spaces():
    notes = day16.parse_input(DEPARTURE_SAMPLE)
    assert list(notes.rules) == ["class", "departure row", "departure seat"]


def test_crlf_input():
    """Blank-line block separators become \\r\\n\\r\\n on a Windows download;
    the parse must still find three blocks and no \\r on any ticket value."""
    assert day16.parse_input(SAMPLE.replace("\n", "\r\n")) == day16.parse_input(SAMPLE)


@pytest.mark.parametrize(
    ("value", "expected"),
    [(1, True), (3, True), (4, False), (5, True), (7, True), (0, False), (8, False)],
)
def test_ranges_are_inclusive_and_the_gap_is_not(value, expected):
    """The statement spells it out for `class: 1-3 or 5-7`: 3 and 5 are
    valid, 4 is not."""
    assert day16.accepts(((1, 3), (5, 7)), value) is expected


@pytest.mark.parametrize(
    ("ticket", "expected"),
    [
        ([7, 3, 47], []),
        ([40, 4, 50], [4]),
        ([55, 2, 20], [55]),
        ([38, 6, 12], [12]),
    ],
)
def test_invalid_values_per_nearby_ticket(ticket, expected):
    """The statement's markup: 4, 55 and 12 are the values valid for no field."""
    assert day16.invalid_values(ticket, day16.parse_input(SAMPLE).rules) == expected


def test_part1_example():
    assert day16.part1(day16.parse_input(SAMPLE)) == 71


def test_part1_sums_every_invalid_value_on_a_ticket():
    """A ticket with two bad values contributes both, not just the first."""
    assert day16.part1(day16.parse_input(SAMPLE + "60,4,20\n")) == 71 + 60 + 4


def test_part1_ignores_my_ticket():
    """The statement says to ignore my ticket for now: a bad value on it is not counted."""
    assert day16.part1(day16.parse_input(SAMPLE.replace("7,1,14", "7,1,99"))) == 71


def test_candidate_sets_are_a_staircase():
    """The statement's Part Two example, column by column: one, two, three
    candidates -- the nested shape that makes elimination sufficient."""
    notes = day16.parse_input(PART2_SAMPLE)
    assert day16.candidate_fields(notes.rules, notes.nearby) == [
        {"row"},
        {"class", "row"},
        {"class", "row", "seat"},
    ]


def test_assign_fields_example():
    notes = day16.parse_input(PART2_SAMPLE)
    assert day16.assign_fields(notes.rules, notes.nearby) == ["row", "class", "seat"]


def test_my_ticket_reads_through_the_assignment():
    """The statement's conclusion: on my ticket class is 12, row is 11, seat is 13."""
    notes = day16.parse_input(PART2_SAMPLE)
    order = day16.assign_fields(notes.rules, notes.nearby)
    assert dict(zip(order, notes.mine)) == {"class": 12, "row": 11, "seat": 13}


def test_part2_multiplies_the_departure_columns():
    assert day16.part2(day16.parse_input(DEPARTURE_SAMPLE)) == 11 * 13


def test_part2_with_no_departure_field_is_the_empty_product():
    assert day16.part2(day16.parse_input(PART2_SAMPLE)) == 1


def test_part2_discards_invalid_tickets_before_deducing():
    """`20,2,3` carries a 20 that no field accepts, so the whole ticket goes.
    Left in, its 2 in column 1 would strike `class` there and the order
    could no longer be deduced."""
    assert day16.part2(day16.parse_input(DEPARTURE_SAMPLE + "20,2,3\n")) == 11 * 13


def test_assign_fields_refuses_to_guess():
    """Two interchangeable fields: elimination cannot break the tie, and the
    code must say so rather than pick one."""
    rules = {"a": ((0, 9),), "b": ((0, 9),)}
    with pytest.raises(ValueError):
        day16.assign_fields(rules, [[1, 2]])


def test_real_input_candidates_are_a_full_staircase(real_input):
    """The property the elimination in assign_fields leans on, pinned on the
    real input rather than asserted in prose: after filtering, the twenty
    candidate sets have sizes exactly 1, 2, ..., 20 and each is nested in
    the next, so every round of elimination forces exactly one column."""
    notes = day16.parse_input(real_input(16))
    valid = [ticket for ticket in notes.nearby if not day16.invalid_values(ticket, notes.rules)]
    candidates = sorted(day16.candidate_fields(notes.rules, valid), key=len)
    assert [len(c) for c in candidates] == list(range(1, 21))
    assert all(small <= big for small, big in pairwise(candidates))


def test_real_input_locked(check_locked):
    check_locked(day16, LOCKED)
