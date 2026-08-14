"""Day 14: Docking Data."""

import pytest

import day14

LOCKED = (3059488894985, 2900994392308)

# Part 1's example: the mask forces the 64s bit on and the 2s bit off.
EXAMPLE = """\
mask = XXXXXXXXXXXXXXXXXXXXXXXXXXXXX1XXXX0X
mem[8] = 11
mem[7] = 101
mem[8] = 0
"""

# Part 2's example: X is a floating address bit, not a value bit.
EXAMPLE2 = """\
mask = 000000000000000000000000000000X1001X
mem[42] = 100
mask = 00000000000000000000000000000000X0XX
mem[26] = 1
"""


def test_parse_input_groups_writes_under_their_mask():
    """A mask governs every write until the next mask line."""
    assert day14.parse_input(EXAMPLE) == [
        ("XXXXXXXXXXXXXXXXXXXXXXXXXXXXX1XXXX0X", [(8, 11), (7, 101), (8, 0)])
    ]
    assert day14.parse_input(EXAMPLE2) == [
        ("000000000000000000000000000000X1001X", [(42, 100)]),
        ("00000000000000000000000000000000X0XX", [(26, 1)]),
    ]


def test_parse_input_rejects_a_short_mask():
    """Values and addresses are 36-bit; a mask of any other width is a typo."""
    with pytest.raises(ValueError):
        day14.parse_input("mask = X1X0\nmem[8] = 11\n")


def test_parse_input_rejects_a_write_before_any_mask():
    with pytest.raises(ValueError):
        day14.parse_input("mem[8] = 11\n")


def test_parse_input_rejects_a_malformed_line():
    with pytest.raises(ValueError):
        day14.parse_input("mask = " + "X" * 36 + "\nmemory 8 <- 11\n")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (11, 73),  # the statement's first worked write
        (101, 101),  # mask has no effect: those bits already matched
        (0, 64),  # only the forced 1 survives
    ],
)
def test_part1_masked_values(value, expected):
    """Every value the statement expands out bit by bit."""
    ones, zeros = day14.value_masks("XXXXXXXXXXXXXXXXXXXXXXXXXXXXX1XXXX0X")
    assert value & zeros | ones == expected


def test_value_masks_leave_x_positions_alone():
    """The identity part 1 rests on, pinned rather than claimed in prose.

    X is 0 in `ones` and 1 in `zeros`, so OR-then-AND cannot disturb it.
    Checked directly: under an all-X mask every value must survive intact,
    and under an all-0 / all-1 mask every value must be flattened.
    """
    all_x = "X" * 36
    ones, zeros = day14.value_masks(all_x)
    assert ones == 0
    assert zeros == (1 << 36) - 1
    for value in (0, 1, 11, 101, (1 << 36) - 1):
        assert value & zeros | ones == value

    ones, zeros = day14.value_masks("0" * 36)
    assert all(value & zeros | ones == 0 for value in (0, 11, (1 << 36) - 1))

    ones, zeros = day14.value_masks("1" * 36)
    assert all(value & zeros | ones == (1 << 36) - 1 for value in (0, 11))


def test_part1_example():
    assert day14.part1(day14.parse_input(EXAMPLE)) == 165


def test_a_later_write_overwrites_an_earlier_one():
    """Address 8 is written twice; only the second value counts toward the sum."""
    memory_sum = day14.part1(day14.parse_input(EXAMPLE))
    assert memory_sum == 101 + 64  # address 7 then address 8, not 73 + 101 + 64


def test_floating_bits_are_indexed_from_the_least_significant_end():
    """The mask is written most-significant-first, so position 0 is the last
    character, not the first."""
    assert day14.floating_bits("0" * 35 + "X") == [0]
    assert day14.floating_bits("X" + "0" * 35) == [35]
    assert day14.floating_bits("000000000000000000000000000000X1001X") == [0, 5]


@pytest.mark.parametrize(
    ("address", "mask", "expected"),
    [
        # The statement's first worked decode: 42 under X1001X -> 26,27,58,59.
        (42, "000000000000000000000000000000X1001X", [26, 27, 58, 59]),
        # And its second: 26 under X0XX -> 16,17,18,19,24,25,26,27.
        (26, "00000000000000000000000000000000X0XX", [16, 17, 18, 19, 24, 25, 26, 27]),
    ],
)
def test_floating_addresses_examples(address, mask, expected):
    assert sorted(day14.floating_addresses(address, mask)) == expected


def test_a_mask_with_no_x_writes_exactly_one_address():
    """2**0 == 1: the degenerate case of the subset enumeration."""
    assert day14.floating_addresses(42, "0" * 36) == [42]
    assert day14.floating_addresses(0, "0" * 35 + "1") == [1]


def test_floating_addresses_are_distinct_and_count_two_to_the_k():
    """Each of the 2**k counter values scatters to a different address, so
    the write count is exact rather than an upper bound with duplicates."""
    for mask in (
        "000000000000000000000000000000X1001X",
        "00000000000000000000000000000000X0XX",
        "X" * 4 + "0" * 32,
    ):
        got = day14.floating_addresses(42, mask)
        assert len(got) == len(set(got)) == 2 ** mask.count("X")


def test_part2_example():
    assert day14.part2(day14.parse_input(EXAMPLE2)) == 208


def test_part2_ignores_the_zero_bits_of_the_mask():
    """A 0 in a part-2 mask leaves the address bit alone, which is the exact
    opposite of what the same character means in part 1."""
    assert day14.floating_addresses(42, "0" * 36) == [42]
    ones, zeros = day14.value_masks("0" * 36)
    assert 42 & zeros | ones == 0


def test_the_two_parts_read_the_same_mask_differently():
    """Same program, same masks, different answers -- the parts are two
    interpretations of one instruction stream, not two programs."""
    blocks = day14.parse_input(EXAMPLE2)
    assert day14.part2(blocks) == 208
    assert day14.part1(blocks) != 208


def test_crlf_input():
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day14.parse_input(crlf) == day14.parse_input(EXAMPLE)
    assert day14.part1(day14.parse_input(crlf)) == 165


def test_real_input_locked(check_locked):
    check_locked(day14, LOCKED)
