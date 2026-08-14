"""Day 6: Custom Customs."""

import pytest

import day06

LOCKED = (6683, 3122)

# Five groups.  anyone: 3 3 3 1 1 -> 11.  everyone: 3 0 1 1 1 -> 6.
EXAMPLE = "abc\n\na\nb\nc\n\nab\nac\n\na\na\na\na\n\nb\n"


def test_parse_input_builds_per_person_sets():
    assert day06.parse_input("abcx\nabcy\nabcz\n") == [[set("abcx"), set("abcy"), set("abcz")]]


def test_parse_input_group_count():
    assert len(day06.parse_input(EXAMPLE)) == 5


@pytest.mark.parametrize(
    ("people", "expected"),
    [
        ([set("abcx"), set("abcy"), set("abcz")], 6),  # union {a,b,c,x,y,z}
        ([set("abc")], 3),
        ([set("ab"), set("ac")], 3),
    ],
)
def test_group_anyone_is_the_union(people, expected):
    assert day06.group_anyone(people) == expected


@pytest.mark.parametrize(
    ("people", "expected"),
    [
        ([set("ab"), set("ac")], 1),  # intersection {a}
        ([set("abc")], 3),
        ([set("a"), set("b")], 0),  # disjoint: nobody agrees on anything
    ],
)
def test_group_everyone_is_the_intersection(people, expected):
    assert day06.group_everyone(people) == expected


def test_a_lone_person_agrees_with_themselves():
    """With one person, union and intersection are the same set."""
    people = [set("abc")]
    assert day06.group_anyone(people) == day06.group_everyone(people) == 3


def test_part1_example():
    assert day06.part1(day06.parse_input(EXAMPLE)) == 11


def test_part2_example():
    assert day06.part2(day06.parse_input(EXAMPLE)) == 6


def test_crlf_input():
    r"""Each person is one line and each character is an answer, so a
    surviving \r would be counted as a 27th question and inflate part 1."""
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day06.parse_input(crlf) == day06.parse_input(EXAMPLE)
    assert day06.solve(crlf) == (11, 6)


def test_real_input_locked(check_locked):
    check_locked(day06, LOCKED)
