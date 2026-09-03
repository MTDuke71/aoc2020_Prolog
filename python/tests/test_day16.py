"""Day 16: Ticket Translation."""

import pytest

import day16

LOCKED = None

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

PART2_SAMPLE = """departure time: 0-1
departure station: 3-5
departure platform: 6-8
seat: 9-11

your ticket:
1,4,7,10

nearby tickets:
1,4,7,10
0,3,6,9
1,5,8,11
"""


def test_parse_input():
    parsed = day16.parse_input(SAMPLE)
    assert parsed["rules"]["class"] == [(1, 3), (5, 7)]
    assert parsed["rules"]["row"] == [(6, 11), (33, 44)]
    assert parsed["rules"]["seat"] == [(13, 40), (45, 50)]
    assert parsed["my_ticket"] == [7, 1, 14]
    assert parsed["nearby_tickets"] == [
        [7, 3, 47],
        [40, 4, 50],
        [55, 2, 20],
        [38, 6, 12],
    ]


def test_crlf_input():
    assert day16.parse_input(SAMPLE.replace("\n", "\r\n"))["rules"]["class"] == [(1, 3), (5, 7)]


def test_part1_example():
    assert day16.part1(day16.parse_input(SAMPLE)) == 71


def test_part2_example():
    parsed = day16.parse_input(PART2_SAMPLE)
    assert day16.part2(parsed) == 28


def test_real_input_locked(check_locked):
    check_locked(day16, LOCKED)
