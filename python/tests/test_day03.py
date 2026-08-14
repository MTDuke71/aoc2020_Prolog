"""Day 3: Toboggan Trajectory."""

import math

import pytest

import day03

LOCKED = (148, 727923200)

EXAMPLE = """\
..##.......
#...#...#..
.#....#..#.
..#.#...#.#
.#...##..#.
..#.##.....
.#.#.#....#
.#........#
#.##...#...
#...##....#
.#..#...#.#
"""


def test_parse_input():
    assert day03.parse_input("..#\n#..\n") == ["..#", "#.."]


@pytest.mark.parametrize(
    ("right", "down", "expected"),
    [(1, 1, 2), (3, 1, 7), (5, 1, 3), (7, 1, 4), (1, 2, 2)],
)
def test_slope_counts(right, down, expected):
    """The five counts the statement works out by hand."""
    assert day03.slope_trees(day03.parse_input(EXAMPLE), right, down) == expected


def test_part1_example():
    assert day03.part1(day03.parse_input(EXAMPLE)) == 7


def test_part2_example():
    assert day03.part2(day03.parse_input(EXAMPLE)) == math.prod([2, 7, 3, 4, 2]) == 336


def test_column_wraps_around():
    """The map repeats to the right, so column 2 of a 2-wide grid is column 0."""
    assert day03.slope_trees(["#.", ".#"], 2, 1) == 1


def test_down_greater_than_one_skips_rows():
    """Three tree rows visited at down=2 hits rows 0 and 2, not all three."""
    assert day03.slope_trees(["#", "#", "#"], 0, 2) == 2


def test_starting_square_counts_when_it_is_a_tree():
    """The toboggan starts at (0, 0); a tree there is on the path."""
    assert day03.slope_trees(["#", "."], 3, 1) == 1


def test_crlf_input():
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day03.parse_input(crlf) == day03.parse_input(EXAMPLE)
    assert day03.solve(crlf) == day03.solve(EXAMPLE)


def test_real_input_locked(check_locked):
    check_locked(day03, LOCKED)
