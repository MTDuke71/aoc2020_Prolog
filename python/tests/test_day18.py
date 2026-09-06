"""Day 18: Operation Order."""

import re

import pytest

import day18

LOCKED = (650217205854, 20394514442037)

# The statement's six worked examples: (expression, part-1 value, part-2 value).
EXAMPLES = [
    ("1 + 2 * 3 + 4 * 5 + 6", 71, 231),
    ("1 + (2 * 3) + (4 * (5 + 6))", 51, 51),
    ("2 * 3 + (4 * 5)", 26, 46),
    ("5 + (8 * 3 + 9 + 3 * 4 * 3)", 437, 1445),
    ("5 * 9 * (7 * 3 * 3 + 9 * 3 + (8 + 6 * 4))", 12240, 669060),
    ("((2 + 4 * 9) * (6 + 9 * 8 + 6) + 6) + 2 + 4 * 2", 13632, 23340),
]

SAMPLE = "\n".join(expr for expr, _, _ in EXAMPLES) + "\n"


def value(expr: str, precedence) -> int:
    return day18.evaluate(day18.tokenize(expr), precedence)


# --- tokenizing ---------------------------------------------------------------


def test_tokenize_statement_example():
    assert day18.tokenize("1 + (2 * 3) + (4 * (5 + 6))") == [
        1, "+", "(", 2, "*", 3, ")", "+", "(", 4, "*", "(", 5, "+", 6, ")", ")"
    ]  # fmt: skip


def test_tokenize_multi_digit_numbers():
    """The real input is single digits only, but the tokenizer should not know that."""
    assert day18.tokenize("10 + 234*(5)") == [10, "+", 234, "*", "(", 5, ")"]


def test_tokenize_ignores_spacing():
    assert day18.tokenize("1+2") == day18.tokenize("  1   +  2 ") == [1, "+", 2]


@pytest.mark.parametrize("bad", ["1 - 2", "1 + x", "1 / 2", "[1]"])
def test_tokenize_rejects_stray_characters(bad):
    with pytest.raises(ValueError):
        day18.tokenize(bad)


def test_parse_input_one_token_list_per_line_skipping_blanks():
    parsed = day18.parse_input("1 + 2\n\n3 * 4\n")
    assert parsed == [[1, "+", 2], [3, "*", 4]]


def test_crlf_input():
    assert day18.parse_input(SAMPLE.replace("\n", "\r\n")) == day18.parse_input(SAMPLE)


# --- the two precedence tables on the statement's examples -----------------------


@pytest.mark.parametrize(("expr", "expected", "_"), EXAMPLES)
def test_part1_examples(expr, expected, _):
    assert value(expr, day18.SAME_PRECEDENCE) == expected


@pytest.mark.parametrize(("expr", "_", "expected"), EXAMPLES)
def test_part2_examples(expr, _, expected):
    assert value(expr, day18.ADDITION_FIRST) == expected


def test_part1_and_part2_sum_the_lines():
    homework = day18.parse_input(SAMPLE)
    assert day18.part1(homework) == sum(p1 for _, p1, _ in EXAMPLES)
    assert day18.part2(homework) == sum(p2 for _, _, p2 in EXAMPLES)


# --- the evaluator's rules, one at a time ----------------------------------------


def test_the_smallest_expression_that_tells_the_tables_apart():
    """`2 * 3 + 4`: left to right it is (2 * 3) + 4 = 10; addition first it is 2 * (3 + 4) = 14."""
    assert value("2 * 3 + 4", day18.SAME_PRECEDENCE) == 10
    assert value("2 * 3 + 4", day18.ADDITION_FIRST) == 14


def test_equal_precedence_associates_left_not_right():
    """The `>=` in the reduce condition.  With `>` the waiting `*` would not be
    applied when the `+` arrived, and `2 * 3 + 4` would come out as 2 * (3 + 4)."""
    assert value("2 * 3 + 4", day18.SAME_PRECEDENCE) == (2 * 3) + 4
    assert value("8 + 2 * 3 * 4", day18.SAME_PRECEDENCE) == ((8 + 2) * 3) * 4


def test_part1_is_a_strict_left_fold():
    """Under equal precedence every operator is applied the moment its right
    operand is complete, so a paren-free line is a running total: value so far,
    op, next number."""
    tokens = day18.tokenize("1 + 2 * 3 + 4 * 5 + 6")
    running = tokens[0]
    for op, number in zip(tokens[1::2], tokens[2::2]):
        running = day18.APPLY[op](running, number)
    assert running == 71 == value("1 + 2 * 3 + 4 * 5 + 6", day18.SAME_PRECEDENCE)


def test_part2_is_the_product_of_the_sums_between_stars():
    """Under addition-first a paren-free line splits at the `*`s into groups,
    each group is summed, and the sums are multiplied: the identity the
    docstring's second trace is showing, pinned."""
    expr = "1 + 2 * 3 + 4 * 5 + 6"
    groups = [sum(int(n) for n in group.split("+")) for group in expr.split("*")]
    assert groups == [3, 7, 11]
    assert 3 * 7 * 11 == 231 == value(expr, day18.ADDITION_FIRST)


@pytest.mark.parametrize("precedence", [day18.SAME_PRECEDENCE, day18.ADDITION_FIRST])
def test_parentheses_override_either_table(precedence):
    assert value("(1 + 2) * 3", precedence) == 9
    assert value("1 + (2 * 3)", precedence) == 7
    assert value("2 * (3 + 4)", precedence) == 14


@pytest.mark.parametrize("precedence", [day18.SAME_PRECEDENCE, day18.ADDITION_FIRST])
def test_degenerate_expressions(precedence):
    assert value("42", precedence) == 42
    assert value("((((7))))", precedence) == 7
    assert value("(1 + 2)", precedence) == 3


def test_nested_parens_are_reduced_innermost_first():
    """Statement's second walkthrough: `(4 * (5 + 6))` -> `(4 * 11)` -> 44 before the outer `+` runs."""
    assert value("(4 * (5 + 6))", day18.SAME_PRECEDENCE) == 44
    assert value("1 + (2 * 3) + (4 * (5 + 6))", day18.SAME_PRECEDENCE) == 1 + 6 + 44


def test_malformed_expression_is_rejected_not_guessed():
    with pytest.raises((ValueError, IndexError)):
        value("1 2", day18.SAME_PRECEDENCE)
    with pytest.raises((ValueError, IndexError)):
        value("1 +", day18.SAME_PRECEDENCE)


# --- an independent oracle: Python's own parser with the operators relabelled -----
#
# Python already has a left-to-right equal-precedence pair (`+` and `-`) and a
# tighter/looser pair (`*` over `+`).  Relabel the homework's operators onto
# those, on an int subclass whose dunder methods do the *homework's* arithmetic
# rather than the symbol's, and `eval` becomes a second evaluator written by
# somebody else.  Test-only: the shipping code does not eval its input.


class LeftToRight(int):
    """`-` is spelled `*` in the homework: same precedence as `+`, left associative."""

    def __add__(self, other):
        return LeftToRight(int(self) + int(other))

    def __sub__(self, other):
        return LeftToRight(int(self) * int(other))


class AdditionFirst(int):
    """`+` and `*` swap symbols so Python's tighter `*` does the homework's `+`."""

    def __mul__(self, other):
        return AdditionFirst(int(self) + int(other))

    def __add__(self, other):
        return AdditionFirst(int(self) * int(other))


def oracle_part1(expr: str) -> int:
    wrapped = re.sub(r"\d+", r"LeftToRight(\g<0>)", expr)
    return int(eval(wrapped.replace("*", "-")))


def oracle_part2(expr: str) -> int:
    wrapped = re.sub(r"\d+", r"AdditionFirst(\g<0>)", expr)
    return int(eval(wrapped.translate(str.maketrans("+*", "*+"))))


# The table the puzzle does not ask for.  Python's own `+` and `*` already have
# this precedence, so plain `eval` of the untouched line is the oracle here.
SCHOOL_PRECEDENCE = {"+": 1, "*": 2}


def oracle_school(expr: str) -> int:
    return eval(expr)


@pytest.mark.parametrize(("expr", "p1", "p2"), EXAMPLES)
def test_oracles_agree_with_the_statement(expr, p1, p2):
    assert oracle_part1(expr) == p1
    assert oracle_part2(expr) == p2


def test_real_input_matches_the_oracles_line_by_line(real_input):
    lines = [line.strip() for line in real_input(18).splitlines() if line.strip()]
    homework = day18.parse_input(real_input(18))
    for line, tokens in zip(lines, homework, strict=True):
        assert day18.evaluate(tokens, day18.SAME_PRECEDENCE) == oracle_part1(line)
        assert day18.evaluate(tokens, day18.ADDITION_FIRST) == oracle_part2(line)


def test_school_precedence_is_ordinary_arithmetic():
    """The evaluator is not tuned to the two puzzle tables.  Hand it school
    precedence -- `*` outranks `+` -- and it agrees with Python evaluating the
    same text natively.  The statement's first example is 33 this way, against
    71 and 231 under the puzzle's two tables."""
    assert value("1 + 2 * 3 + 4 * 5 + 6", SCHOOL_PRECEDENCE) == 33 == 1 + 2 * 3 + 4 * 5 + 6
    for expr, _, _ in EXAMPLES:
        assert value(expr, SCHOOL_PRECEDENCE) == oracle_school(expr)


def test_real_input_under_school_precedence_matches_python(real_input):
    lines = [line.strip() for line in real_input(18).splitlines() if line.strip()]
    homework = day18.parse_input(real_input(18))
    for line, tokens in zip(lines, homework, strict=True):
        assert day18.evaluate(tokens, SCHOOL_PRECEDENCE) == oracle_school(line)


def test_real_input_locked(check_locked):
    check_locked(day18, LOCKED)
