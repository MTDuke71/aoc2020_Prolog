"""Day 0: The Tyranny of the Rocket Equation (tutorial dry run)."""

import pytest

import day00

LOCKED = (3481005, 5218616)

EXAMPLE = "12\n14\n1969\n100756\n"


@pytest.mark.parametrize(
    ("mass", "expected"),
    [(12, 2), (14, 2), (1969, 654), (100756, 33583)],
)
def test_fuel_examples(mass, expected):
    assert day00.fuel(mass) == expected


@pytest.mark.parametrize(
    ("mass", "expected"),
    [(14, 2), (1969, 966), (100756, 50346)],
)
def test_total_fuel_examples(mass, expected):
    assert day00.total_fuel(mass) == expected


def test_parse_input():
    assert day00.parse_input(EXAMPLE) == [12, 14, 1969, 100756]


def test_part1_example():
    assert day00.part1([12, 14, 1969, 100756]) == 2 + 2 + 654 + 33583


def test_part2_example():
    assert day00.part2([14, 1969, 100756]) == 2 + 966 + 50346


def test_small_masses_never_go_negative():
    """The recursion must stop at the first non-positive step, not add it.

    A mass of 6 needs 0 fuel and a mass of 2 needs -2 by the raw formula;
    part 2 treats both as contributing nothing.
    """
    assert day00.fuel(6) == 0
    assert day00.fuel(2) == -2
    assert day00.total_fuel(6) == 0
    assert day00.total_fuel(2) == 0


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    assert day00.parse_input(EXAMPLE.replace("\n", "\r\n")) == day00.parse_input(EXAMPLE)


def test_real_input_locked(check_locked):
    check_locked(day00, LOCKED)
