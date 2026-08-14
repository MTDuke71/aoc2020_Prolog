"""Day 2: Password Philosophy."""

import pytest

import day02
from day02 import Entry

LOCKED = (460, 251)

EXAMPLE = "1-3 a: abcde\n1-3 b: cdefg\n2-9 c: ccccccccc\n"


def test_parse_input_builds_records():
    assert day02.parse_input("1-3 a: abcde\n") == [Entry(1, 3, "a", "abcde")]


def test_parse_input_rejects_a_malformed_line():
    with pytest.raises(ValueError):
        day02.parse_input("not a policy line\n")


def test_part1_example():
    assert day02.part1(day02.parse_input(EXAMPLE)) == 2


def test_part2_example():
    assert day02.part2(day02.parse_input(EXAMPLE)) == 1


@pytest.mark.parametrize(
    ("entry", "expected"),
    [
        (Entry(1, 3, "a", "abcde"), True),
        (Entry(1, 3, "b", "cdefg"), False),  # no b at all: under the minimum
        (Entry(2, 9, "c", "ccccccccc"), True),
        (Entry(1, 3, "a", "a"), True),  # lower bound is inclusive
        (Entry(1, 3, "a", "aaa"), True),  # upper bound is inclusive
        (Entry(1, 3, "a", "aaaa"), False),  # one over
    ],
)
def test_valid_count(entry, expected):
    assert day02.valid_count(entry) is expected


@pytest.mark.parametrize(
    ("entry", "expected"),
    [
        (Entry(1, 3, "a", "abcde"), True),  # position 1 only
        (Entry(1, 3, "b", "cdefg"), False),  # neither position
        (Entry(2, 9, "c", "ccccccccc"), False),  # both positions: XOR, not OR
    ],
)
def test_valid_position(entry, expected):
    assert day02.valid_position(entry) is expected


def test_positions_are_one_indexed():
    """ "1-3 a: abcde" is valid only if position 1 means 'a', not 'b'."""
    assert day02.valid_position(Entry(1, 2, "a", "ab")) is True
    assert day02.valid_position(Entry(1, 2, "b", "ab")) is True
    assert day02.valid_position(Entry(1, 2, "a", "ba")) is True


def test_crlf_input():
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day02.parse_input(crlf) == day02.parse_input(EXAMPLE)
    assert day02.solve(crlf) == day02.solve(EXAMPLE)


def test_real_input_locked(check_locked):
    check_locked(day02, LOCKED)
