"""Day 8: Handheld Halting."""

import pytest

import day08

LOCKED = (1331, 1121)

# Loops with the accumulator at 5 (part 1).  Flipping the jmp on the
# second-to-last line to a nop makes it halt at 8 (part 2).
EXAMPLE = """\
nop +0
acc +1
jmp +4
acc +3
jmp -3
acc -99
acc +1
jmp -4
acc +6
"""


def test_parse_input_keeps_signs():
    """The +/- prefix is part of the argument, and +0 is 0, not a syntax error."""
    assert day08.parse_input("acc +13\njmp -6\nnop +0\n") == [
        ("acc", 13),
        ("jmp", -6),
        ("nop", 0),
    ]


def test_run_reports_a_loop_before_repeating():
    """The accumulator is read the instant *before* an instruction runs twice."""
    assert day08.run(day08.parse_input(EXAMPLE)) == (False, 5)


def test_run_reports_a_halt_off_the_end():
    """nop +0 then acc +6 steps the PC to 2 == len(program): a clean halt."""
    assert day08.run(day08.parse_input("nop +0\nacc +6\n")) == (True, 6)


def test_halting_means_pc_equals_length_exactly():
    """A jmp landing past the end is not a halt in this machine's terms.

    The statement defines termination as attempting to execute the
    instruction immediately after the last one.  `while pc != n` therefore
    means a jmp beyond n runs off into an IndexError rather than being
    quietly accepted as termination.
    """
    assert day08.run([("jmp", 1)]) == (True, 0)
    with pytest.raises(IndexError):
        day08.run([("jmp", 5)])


def test_part1_example():
    assert day08.part1(day08.parse_input(EXAMPLE)) == 5


def test_part2_example():
    assert day08.part2(day08.parse_input(EXAMPLE)) == 8


def test_part2_flips_exactly_one_jmp_or_nop():
    """The repair is a single jmp<->nop swap, and never touches an acc.

    In the example only the jmp -4 on the second-to-last line halts when
    flipped, so this pins both which instruction the search lands on and
    that it was a jmp -- not an acc quietly rewritten to reach 8.
    """
    program = day08.parse_input(EXAMPLE)
    flip = {"jmp": "nop", "nop": "jmp"}
    halting = [
        i
        for i, (op, arg) in enumerate(program)
        if op in flip and day08.run(program[:i] + [(flip[op], arg)] + program[i + 1 :])[0]
    ]
    assert halting == [7]
    assert program[7] == ("jmp", -4)
    assert day08.part2(program) == 8


def test_part2_raises_when_there_is_no_candidate():
    """A program of nothing but acc instructions has nothing to flip."""
    with pytest.raises(ValueError):
        day08.part2([("acc", 1)])


def test_part2_leaves_the_original_program_alone():
    """Each candidate runs on a patched copy, so the search cannot poison itself."""
    program = day08.parse_input(EXAMPLE)
    before = list(program)
    day08.part2(program)
    assert program == before


def test_crlf_input():
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day08.parse_input(crlf) == day08.parse_input(EXAMPLE)
    assert day08.solve(crlf) == (5, 8)


def test_real_input_locked(check_locked):
    check_locked(day08, LOCKED)
