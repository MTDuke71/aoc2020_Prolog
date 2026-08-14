"""Day 5: Binary Boarding."""

import pytest

import day05

LOCKED = (888, 522)


@pytest.mark.parametrize(
    ("boarding_pass", "row", "col", "seat"),
    [
        ("FBFBBFFRLR", 44, 5, 357),
        ("BFFFBBFRRR", 70, 7, 567),
        ("FFFBBBFRRR", 14, 7, 119),
        ("BBFFBBFRLL", 102, 4, 820),
    ],
)
def test_decode_examples(boarding_pass, row, col, seat):
    """Every worked example in the statement, row and column included."""
    got = day05.seat_id(boarding_pass)
    assert got == seat
    assert (got // 8, got % 8) == (row, col)


def test_seat_id_is_row_times_eight_plus_col():
    """The shortcut this solution rests on, pinned rather than claimed in prose.

    Nothing here does the binary search over halves that the statement
    describes.  It works because reading the pass as one 10-bit number
    (F/L = 0, B/R = 1) *is* the seat ID: the 7 row bits and the 3 column
    bits concatenated are exactly row * 8 + col.  If that identity ever
    failed, this test would say so rather than the answer silently drifting.
    """
    for boarding_pass in ("FBFBBFFRLR", "BFFFBBFRRR", "FFFBBBFRRR", "BBFFBBFRLL"):
        row = int(boarding_pass[:7].translate(day05.BITS), 2)
        col = int(boarding_pass[7:].translate(day05.BITS), 2)
        assert day05.seat_id(boarding_pass) == row * 8 + col


def test_parse_input_decodes_to_ids():
    """parse_input returns seat IDs, not raw passes: the decode is the parse."""
    assert day05.parse_input("BFFFBBFRRR\nFFFBBBFRRR\n") == [567, 119]


def test_part1_example():
    ids = day05.parse_input("BFFFBBFRRR\nFFFBBBFRRR\nBBFFBBFRLL\n")
    assert day05.part1(ids) == 820


def test_part2_finds_the_width_two_gap():
    """Occupied 1,2,3,5,6: seat 4 is the hole with both neighbours filled."""
    assert day05.part2([1, 2, 3, 5, 6]) == 4


def test_part2_ignores_the_missing_ends():
    """Seats at the very front and back are missing too, but they have no
    occupied neighbour on both sides, so only the interior gap qualifies."""
    assert day05.part2([10, 11, 13, 14]) == 12


def test_part2_raises_when_there_is_no_gap():
    with pytest.raises(ValueError):
        day05.part2([1, 2, 3, 4])


def test_crlf_input():
    example = "BFFFBBFRRR\nFFFBBBFRRR\nBBFFBBFRLL\n"
    assert day05.parse_input(example.replace("\n", "\r\n")) == day05.parse_input(example)


def test_real_input_locked(check_locked):
    check_locked(day05, LOCKED)
