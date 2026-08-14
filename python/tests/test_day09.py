"""Day 9: Encoding Error."""

import pytest

import day09

LOCKED = (1930745883, 268878261)

# The statement's example runs on a preamble of 5 rather than the real 25.
EXAMPLE = """\
35
20
15
25
47
40
62
55
65
95
102
117
150
182
127
219
299
277
309
576
"""

NUMBERS = [35, 20, 15, 25, 47, 40, 62, 55, 65, 95, 102, 117, 150, 182, 127, 219, 299, 277, 309, 576]


def test_parse_input():
    assert day09.parse_input(EXAMPLE) == NUMBERS


def test_part1_example():
    assert day09.part1(NUMBERS, preamble=5) == 127


def test_part2_example():
    assert day09.part2(NUMBERS, preamble=5) == 62


def test_contiguous_range_example():
    assert day09.contiguous_range(NUMBERS, 127) == [15, 25, 47, 40]


def test_weakness_is_min_plus_max_not_the_ends():
    """15 + 47 = 62, and the range is not sorted, so first+last would be 55."""
    values = day09.contiguous_range(NUMBERS, 127)
    assert min(values) + max(values) == 62
    assert values[0] + values[-1] == 55


def test_the_two_addends_must_be_different_values():
    """25 + 25 does not validate 50, even from two separate entries.

    The statement is explicit: "The two numbers will have different values."
    So the guard is on the values (a != b), not on the positions -- a window
    holding two 25s still cannot make 50, which is why the pair loop cannot
    simply be itertools.combinations over indices.
    """
    assert day09.has_valid_sum(50, [25, 25]) is False
    assert day09.has_valid_sum(50, [25, 1]) is False
    assert day09.has_valid_sum(55, [25, 25, 30]) is True


@pytest.mark.parametrize(
    ("target", "window", "expected"),
    [
        (40, [35, 20, 15, 25, 47], True),  # 25 + 15
        (62, [20, 15, 25, 47, 40], True),  # 15 + 47
        (127, [95, 102, 117, 150, 182], False),  # the first invalid number
    ],
)
def test_has_valid_sum(target, window, expected):
    assert day09.has_valid_sum(target, window) is expected


def test_no_invalid_number_raises():
    """Every number after the preamble is a sum here, so there is no answer."""
    with pytest.raises(ValueError):
        day09.part1([1, 2, 3, 5, 8], preamble=2)


def test_crlf_input():
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day09.parse_input(crlf) == NUMBERS


def test_real_input_locked(check_locked):
    check_locked(day09, LOCKED)
