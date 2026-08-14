"""Day 4: Passport Processing."""

import pytest

import day04

LOCKED = (250, 158)

EXAMPLE = """\
ecl:gry pid:860033327 eyr:2020 hcl:#fffffd
byr:1937 iyr:2017 cid:147 hgt:183cm

iyr:2013 ecl:amb cid:350 eyr:2023 pid:028048884
hcl:#cfa07d byr:1929

hcl:#ae17e1 iyr:2013
eyr:2024
ecl:brn pid:760753108 byr:1931
hgt:179cm

hcl:#cfa07d eyr:2025 pid:166559648
iyr:2011 ecl:brn hgt:59in
"""

# The statement's part-2 batches: four that fail validation, four that pass.
ALL_INVALID = """\
eyr:1972 cid:100
hcl:#18171d ecl:amb hgt:170 pid:186cm iyr:2018 byr:1926

iyr:2019
hcl:#602927 eyr:1967 hgt:170cm
ecl:grn pid:012533040 byr:1946

hcl:dab227 iyr:2012
ecl:brn hgt:182cm pid:021572410 eyr:2020 byr:1992 cid:277

hgt:59cm ecl:zzz
eyr:2038 hcl:74454a iyr:2023
pid:3556412378 byr:2007
"""

ALL_VALID = """\
pid:087499704 hgt:74in ecl:grn iyr:2012 eyr:2030 byr:1980
hcl:#623a2f

eyr:2029 ecl:blu cid:129 byr:1989
iyr:2014 pid:896056539 hcl:#a97842 hgt:165cm

hcl:#888785
hgt:164cm byr:2001 iyr:2015 cid:88
pid:545766238 ecl:hzl
eyr:2022

iyr:2010 hgt:158cm hcl:#b6652a ecl:blu byr:1944 eyr:2021 pid:093154719
"""


def test_parse_input_joins_lines_within_a_block():
    """A passport's fields continue across lines until a blank line."""
    assert day04.parse_input("a:1 b:2\nc:3\n\nd:4\n") == [
        {"a": "1", "b": "2", "c": "3"},
        {"d": "4"},
    ]


def test_part1_example():
    assert day04.part1(day04.parse_input(EXAMPLE)) == 2


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("byr", "2002"),
        ("hgt", "60in"),
        ("hgt", "190cm"),
        ("hcl", "#123abc"),
        ("ecl", "brn"),
        ("pid", "000000001"),
    ],
)
def test_valid_field(key, value):
    """The statement's own table of accepted values."""
    assert day04.valid_field(key, value) is True


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("byr", "2003"),
        ("hgt", "190in"),
        ("hgt", "190"),  # a bare number has no unit
        ("hcl", "#123abz"),
        ("hcl", "123abc"),  # missing the #
        ("ecl", "wat"),
        ("pid", "0123456789"),  # ten digits, not nine
    ],
)
def test_invalid_field(key, value):
    """The statement's own table of rejected values."""
    assert day04.valid_field(key, value) is False


def test_pid_keeps_leading_zeros():
    """pid is a nine-character string, not a number: 000000001 is valid."""
    assert day04.valid_field("pid", "000000001") is True
    assert day04.valid_field("pid", "1") is False


def test_cid_is_the_one_optional_field():
    """Part 1 counts a passport missing only cid; missing any other fails."""
    complete = dict.fromkeys(day04.REQUIRED, "x")
    assert day04.has_required_fields(complete) is True
    assert day04.has_required_fields(complete | {"cid": "147"}) is True
    del complete["byr"]
    assert day04.has_required_fields(complete) is False


def test_part2_rejects_every_invalid_passport():
    passports = day04.parse_input(ALL_INVALID)
    assert len(passports) == 4
    assert day04.part2(passports) == 0


def test_part2_accepts_every_valid_passport():
    passports = day04.parse_input(ALL_VALID)
    assert len(passports) == 4
    assert day04.part2(passports) == 4


def test_crlf_input():
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day04.parse_input(crlf) == day04.parse_input(EXAMPLE)
    assert day04.solve(crlf) == day04.solve(EXAMPLE)


def test_real_input_locked(check_locked):
    check_locked(day04, LOCKED)
