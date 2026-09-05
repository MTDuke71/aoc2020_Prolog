"""Day 17: Conway Cubes -- the flat brute-force alternative (`day17_alt.py`).

These tests are about *agreement*.  `day17.py` is the shipping engine and
carries the statement's layer dumps; the alternative only has to produce
the same cells, cycle for cycle, and the same two answers.  The one
assumption the alternative rests on -- that its fixed box is big enough --
is pinned by checking that no active cell ever reaches the box's edge.

The 4-D scan costs about 10 s per six-cycle boot regardless of input, so
the two tests that run it are marked `slow`.  Deselect them with
`pytest -m "not slow"`; the rest of this module runs in under a second.
"""

from itertools import pairwise

import pytest

import day17
import day17_alt

# The accepted answers, as in test_day17.  The alternative must reproduce them.
LOCKED = (359, 2228)

SAMPLE = """.#.
..#
###
"""

# Mirrors the `range(...)` literals inside cycle_3d / cycle_4d: (lo, hi) per axis,
# hi exclusive as in `range`.  If those literals change, change these.
BOX_3D = ((-15, 15), (-15, 15), (-7, 8))
BOX_4D = ((-15, 15), (-15, 15), (-7, 8), (-8, 8))


def strictly_inside(cells, box) -> bool:
    """No cell on the box's edge: a cell *at* the edge could have an unscanned neighbour."""
    return all(lo < c < hi - 1 for cell in cells for c, (lo, hi) in zip(cell, box))


def alt_states(slice2d, dims, cycles=6):
    """The alternative's state after 0, 1, ..., `cycles` cycles."""
    cycle = day17_alt.cycle_3d if dims == 3 else day17_alt.cycle_4d
    states = [{cell + (0,) * (dims - 2) for cell in slice2d}]
    for _ in range(cycles):
        states.append(cycle(states[-1]))
    return states


@pytest.fixture(scope="module")
def example_states_4d():
    """Six 4-D cycles of the example, computed once (about 10 s) and shared."""
    return alt_states(day17_alt.parse_input(SAMPLE), 4)


def test_parse_input_is_row_col():
    assert day17_alt.parse_input(SAMPLE) == {(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)}


def test_parse_input_is_the_transpose_of_the_shipping_parse():
    """`day17.py` reads (x, y) = (col, row); this module reads (row, col)."""
    assert {(c, r) for r, c in day17_alt.parse_input(SAMPLE)} == day17.parse_input(SAMPLE)


def test_crlf_input():
    assert day17_alt.parse_input(SAMPLE.replace("\n", "\r\n")) == day17_alt.parse_input(SAMPLE)


AXIS_NEIGHBOURS = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1)]


@pytest.mark.parametrize(
    ("count", "centre_active", "expected"),
    [
        (0, True, False),
        (1, True, False),
        (2, True, True),
        (3, True, True),
        (4, True, False),
        (0, False, False),
        (2, False, False),
        (3, False, True),
        (4, False, False),
    ],
)
def test_rule_by_neighbour_count(count, centre_active, expected):
    """The two rule lines that fell off the screenshot, checked one count at a time."""
    ON = set(AXIS_NEIGHBOURS[:count])
    if centre_active:
        ON.add((0, 0, 0))
    assert ((0, 0, 0) in day17_alt.cycle_3d(ON)) is expected


def test_a_lone_cube_dies_and_nothing_is_born_from_one():
    assert day17_alt.cycle_3d({(0, 0, 0)}) == set()


def test_cycle_3d_agrees_with_the_shipping_step_every_cycle():
    """Same input set, same output set as `day17.step(..., 3)`, all six cycles."""
    states = alt_states(day17_alt.parse_input(SAMPLE), 3)
    for before, after in pairwise(states):
        assert after == day17.step(before, 3)
    assert strictly_inside(states[-1], BOX_3D)


def test_part1_example():
    assert day17_alt.part1(day17_alt.parse_input(SAMPLE)) == 112


@pytest.mark.slow
def test_cycle_4d_agrees_with_the_shipping_step_every_cycle(example_states_4d):
    """Same as the 3-D check with one more axis, and the statement's 848 at the end."""
    for before, after in pairwise(example_states_4d):
        assert after == day17.step(before, 4)
    assert len(example_states_4d[-1]) == 848


def test_example_never_reaches_the_box_edge_4d(example_states_4d):
    for state in example_states_4d:
        assert strictly_inside(state, BOX_4D)


@pytest.mark.slow
def test_real_input_locked_and_inside_the_box(real_input):
    """The accepted answers, and the box assumption on the real 8x8 slice.

    Done by hand rather than through `check_locked` so the 4-D boot runs
    once (10 s) and both the count and the edge condition read from it.
    """
    slice2d = day17_alt.parse_input(real_input(17))
    states_3d = alt_states(slice2d, 3)
    states_4d = alt_states(slice2d, 4)
    assert (len(states_3d[-1]), len(states_4d[-1])) == LOCKED
    assert all(strictly_inside(state, BOX_3D) for state in states_3d)
    assert all(strictly_inside(state, BOX_4D) for state in states_4d)
