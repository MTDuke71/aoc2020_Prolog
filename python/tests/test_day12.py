"""Day 12: Rain Risk."""

import pytest

import day12

LOCKED = (1956, 126797)

EXAMPLE = "F10\nN3\nF7\nR90\nF11\n"


def test_parse_input_splits_action_from_value():
    assert day12.parse_input(EXAMPLE) == [("F", 10), ("N", 3), ("F", 7), ("R", 90), ("F", 11)]


def test_parse_input_handles_multi_digit_values():
    assert day12.parse_input("N1\nS22\nE333\nW4\nL180\nR270\nF12\n") == [
        ("N", 1),
        ("S", 22),
        ("E", 333),
        ("W", 4),
        ("L", 180),
        ("R", 270),
        ("F", 12),
    ]


@pytest.mark.parametrize(("left", "right"), [(90, 270), (180, 180), (270, 90)])
def test_left_folds_onto_right(left, right):
    """L d and R (360-d) are the same rotation, so only one direction is coded."""
    assert day12.quarter_turns("L", left) == day12.quarter_turns("R", right)


def test_a_full_turn_is_no_turn():
    assert day12.quarter_turns("R", 360) == 0
    assert day12.quarter_turns("L", 360) == 0


def test_a_non_right_angle_is_rejected():
    """45 degrees has no exact integer representation here, so it must not
    silently truncate to zero quarter turns."""
    with pytest.raises(AssertionError):
        day12.quarter_turns("R", 45)


def test_right_turns_walk_the_compass():
    """From east, turning right goes E -> S -> W -> N."""
    assert [day12.rotate(q, 1, 0) for q in range(4)] == [(1, 0), (0, -1), (-1, 0), (0, 1)]


@pytest.mark.parametrize("vector", [(1, 0), (10, 1), (-3, 7), (0, 0)])
def test_four_quarter_turns_is_the_identity(vector):
    """Rotation is exact integer arithmetic on a Gaussian integer, so this
    closes exactly rather than drifting the way sin/cos would."""
    assert day12.rotate(4, *vector) == vector


def test_negative_left_turns_use_floored_modulo():
    """quarter_turns folds L onto R with `-turns % 4`, which is right only
    because Python's % takes the sign of the divisor.  A C or Rust `%` would
    yield -1 here and rotate() would spin zero times."""
    assert day12.quarter_turns("L", 90) == 3
    assert day12.rotate(day12.quarter_turns("L", 90), 10, 1) == (-1, 10)


def test_part1_example():
    assert day12.part1(day12.parse_input(EXAMPLE)) == 25


def test_a_cardinal_move_does_not_change_the_facing():
    """After F10, N3, F7 the ship is at east 17, north 3 -- which only holds
    if N3 left it still pointing east."""
    assert day12.part1(day12.parse_input("F10\nN3\nF7\n")) == 20


def test_part2_example():
    assert day12.part2(day12.parse_input(EXAMPLE)) == 286


def test_f_scales_the_waypoint_offset():
    """The waypoint starts 10 east, 1 north, and F10 multiplies that offset
    rather than repeating a single step."""
    assert day12.part2(day12.parse_input("F1\n")) == 11
    assert day12.part2(day12.parse_input("F10\n")) == 110


def test_rotating_the_waypoint_does_not_move_the_ship():
    """R90 sends (10, 1) to (1, -10); the turn only shows up in the next F."""
    assert day12.part2(day12.parse_input("R90\n")) == 0
    assert day12.part2(day12.parse_input("R90\nF1\n")) == 11


def test_an_empty_program_goes_nowhere():
    assert day12.parse_input("") == []
    assert day12.part1([]) == 0
    assert day12.part2([]) == 0


def test_distance_is_unsigned():
    """Manhattan distance: west and south is as far out as east and north."""
    assert day12.part1(day12.parse_input("W17\nS8\n")) == 25


def test_crlf_input():
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day12.parse_input(crlf) == day12.parse_input(EXAMPLE)
    assert day12.solve(crlf) == (25, 286)


def test_real_input_locked(check_locked):
    check_locked(day12, LOCKED)
