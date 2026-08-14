"""Day 1: Report Repair."""

import pytest

import day01

LOCKED = (902451, 85555470)

EXAMPLE = "1721\n979\n366\n299\n675\n1456\n"
ENTRIES = [1721, 979, 366, 299, 675, 1456]


def test_parse_input():
    assert day01.parse_input(EXAMPLE) == ENTRIES


def test_part1_example():
    assert day01.part1(ENTRIES) == 1721 * 299 == 514579


def test_part2_example():
    assert day01.part2(ENTRIES) == 979 * 366 * 675 == 241861950


@pytest.mark.parametrize(
    ("k", "target", "entries", "expected"),
    [
        (2, 10, [1, 2, 3, 4, 6, 8, 9], [[1, 9], [2, 8], [4, 6]]),
        (3, 10, [1, 2, 3, 4, 5], [[1, 4, 5], [2, 3, 5]]),
        (3, 10, [1, 2, 3, 4], []),  # 2+3+4 = 9 is the largest triple
        (2, 3, [1, 2, 3, 4], [[1, 2]]),
        (1, 4, [1, 2, 3, 4], [[4]]),
        (0, 0, [1, 2], [[]]),
    ],
)
def test_k_sum_enumerates_every_combination(k, target, entries, expected):
    """k_sum is a generator over *all* solutions, not just the first."""
    assert list(day01.k_sum(k, target, sorted(entries))) == expected


def test_k_sum_needs_no_element_twice():
    """`start=i+1` is what stops 5+5 from answering a target of 10."""
    assert list(day01.k_sum(2, 10, [5])) == []


def test_duplicate_entries_are_two_distinct_entries():
    """Two separate 1010 lines legitimately pair with each other."""
    assert day01.part1([5, 1010, 7, 1010]) == 1010 * 1010


def test_no_solution_raises():
    with pytest.raises(StopIteration):
        day01.part1([1, 2, 3])


def test_crlf_input():
    assert day01.parse_input(EXAMPLE.replace("\n", "\r\n")) == ENTRIES


def test_real_input_locked(check_locked):
    check_locked(day01, LOCKED)
