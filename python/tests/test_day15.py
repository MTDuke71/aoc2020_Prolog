"""Day 15: Rambunctious Recitation."""

import pytest

import day15

LOCKED = (1665, 16439)

# The statement's worked example, spoken aloud turn by turn: the three
# starting numbers, then 0 (6 was new), 3 (0's age), 3, 1, 0, 4, 0.
SPOKEN_0_3_6 = [0, 3, 6, 0, 3, 3, 1, 0, 4, 0]


def test_parse_input():
    assert day15.parse_input("0,1,4,13,15,12,16\n") == [0, 1, 4, 13, 15, 12, 16]


def test_crlf_input():
    assert day15.parse_input("0,3,6\r\n") == [0, 3, 6]


@pytest.mark.parametrize("turn", range(1, 11))
def test_play_matches_the_statement_trace(turn):
    """The full turn-by-turn walkthrough for 0,3,6, not just its endpoint.

    This is the test that pins the engine's bookkeeping: `last_seen` must
    lag one occurrence behind the current number, or every age comes out
    wrong from turn 5 onward.
    """
    assert day15.play([0, 3, 6], turn) == SPOKEN_0_3_6[turn - 1]


def test_a_turn_inside_the_starting_numbers_is_just_read_off():
    assert day15.play([0, 1, 4, 13], 2) == 1


def test_a_repeated_starting_number_already_has_an_age():
    """With starting numbers 0,0 the number 0 has been spoken twice by turn
    2, so turn 3 speaks its age, 1 -- not 0 as if it were new."""
    assert day15.play([0, 0], 3) == 1


@pytest.mark.parametrize(
    ("starting", "expected"),
    [
        ([0, 3, 6], 436),
        ([1, 3, 2], 1),
        ([2, 1, 3], 10),
        ([1, 2, 3], 27),
        ([2, 3, 1], 78),
        ([3, 2, 1], 438),
        ([3, 1, 2], 1836),
    ],
)
def test_part1_examples(starting, expected):
    """All seven 2,020th-number examples from the statement."""
    assert day15.play(starting, day15.PART1_TURNS) == expected


def test_part2_example():
    """The statement's 30,000,000th number for 0,3,6.

    One example rather than all seven: each costs ~4 seconds of pure
    looping, and one is enough to catch anything that only breaks at
    scale (the short examples already pin the mechanism).
    """
    assert day15.play([0, 3, 6], day15.PART2_TURNS) == 175594


def test_real_input_locked(check_locked):
    check_locked(day15, LOCKED)
