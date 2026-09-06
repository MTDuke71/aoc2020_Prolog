"""Day 18: Operation Order.

A page of arithmetic homework -- one expression per line, made of integers,
`+`, `*` and parentheses -- to be evaluated under rules that are not the
ones taught in school.  In part 1 addition and multiplication have the
*same* precedence and go strictly left to right.  In part 2 addition binds
*tighter* than multiplication, the reverse of the usual convention.
Parentheses mean what they always mean.  The answer for each part is the
sum of every line's value.

Both parts are the same program with one table swapped, so the evaluator
takes the precedence table as a parameter and `part1`/`part2` differ only
in which table they pass.  The evaluator is the classic **two-stack
calculator** (Dijkstra's shunting-yard, evaluating as it goes rather than
emitting postfix): a stack of values not yet consumed and a stack of
operators not yet applied.  A number is pushed.  An operator first
*reduces* -- pops and applies -- every operator already waiting whose
precedence is at least its own, because those were to its left and bind at
least as hard, then waits itself.  `(` waits unconditionally; `)` reduces
back to its `(` and discards it.  At end of line, whatever is still
waiting is applied and the one value left is the answer.

The statement's first example, `1 + 2 * 3 + 4 * 5 + 6`, under both tables.
Part 1 (`+` and `*` both precedence 1) reduces at every operator, so the
values stack never holds more than two numbers -- it is a running total:

    token   values     ops     what happened
    1       [1]        []
    +       [1]        [+]
    2       [1, 2]     [+]
    *       [3]        [*]     `+` (prec 1) >= `*` (prec 1): reduce 1 + 2
    3       [3, 3]     [*]
    +       [9]        [+]     reduce 3 * 3
    4       [9, 4]     [+]
    *       [13]       [*]     reduce 9 + 4
    5       [13, 5]    [*]
    +       [65]       [+]     reduce 13 * 5
    6       [65, 6]    [+]
    end     [71]       []      reduce 65 + 6 -> 71

Part 2 (`+` is 2, `*` is 1): a `+` arriving over a waiting `*` does *not*
reduce it (1 < 2), so multiplications pile up on the operator stack while
each addition is done on the spot, and the pile is multiplied out at the
end -- exactly "(1 + 2) * (3 + 4) * (5 + 6)":

    token   values        ops        what happened
    1       [1]           []
    +       [1]           [+]
    2       [1, 2]        [+]
    *       [3]           [*]        reduce 1 + 2
    3       [3, 3]        [*]
    +       [3, 3]        [*, +]     `*` (1) < `+` (2): do not reduce; wait
    4       [3, 3, 4]     [*, +]
    *       [21]          [*]        reduce 3 + 4 = 7 (2 >= 1), then 3 * 7 = 21 (1 >= 1)
    5       [21, 5]       [*]
    +       [21, 5]       [*, +]
    6       [21, 5, 6]    [*, +]
    end     [231]         []         reduce 5 + 6 = 11, then 21 * 11 -> 231

Same tokens, same machine, two different answers -- 71 and 231 -- and the
only input that changed was the table.
"""

import re
from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day18.txt"

Token = int | str
Precedence = dict[str, int]

# The only thing that differs between the parts.  Higher binds tighter.
SAME_PRECEDENCE: Precedence = {"+": 1, "*": 1}
ADDITION_FIRST: Precedence = {"+": 2, "*": 1}

APPLY = {
    "+": lambda a, b: a + b,
    "*": lambda a, b: a * b,
}

# One number, one operator-or-paren, or one stray non-space character (so
# garbage is caught by the check in `tokenize` rather than silently skipped).
TOKEN = re.compile(r"\d+|[+*()]|\S")


def tokenize(line: str) -> list[Token]:
    """`"1 + (23 * 4)"` -> `[1, "+", "(", 23, "*", 4, ")"]`.  Whitespace separates, nothing else."""
    tokens: list[Token] = []
    for text in TOKEN.findall(line):
        if text.isdigit():
            tokens.append(int(text))
        elif text in APPLY or text in "()":
            tokens.append(text)
        else:
            raise ValueError(f"unexpected character {text!r} in {line!r}")
    return tokens


def parse_input(raw: str) -> list[list[Token]]:
    """One token list per non-blank line.

    Per-line `.strip()` drops a trailing `\r` from a CRLF download before it
    reaches `tokenize`, which would otherwise reject it as a stray character.
    """
    return [tokenize(line.strip()) for line in raw.splitlines() if line.strip()]


def evaluate(tokens: list[Token], precedence: Precedence) -> int:
    """Value of one expression under the given operator precedences (higher binds tighter).

    Two stacks: `values` holds numbers not yet consumed, `ops` holds
    operators and open parentheses not yet applied.  See the module docstring
    for a token-by-token trace.
    """
    values: list[int] = []
    ops: list[str] = []

    def reduce() -> None:
        """Apply the operator on top of `ops` to the top two values."""
        op = ops.pop()
        right = values.pop()
        left = values.pop()
        values.append(APPLY[op](left, right))

    for token in tokens:
        if isinstance(token, int):
            values.append(token)
        elif token == "(":
            ops.append(token)
        elif token == ")":
            while ops[-1] != "(":
                reduce()
            ops.pop()
        else:
            # Everything to the left that binds at least as tightly goes first;
            # `>=` rather than `>` is what makes equal-precedence operators
            # associate to the left.  An open paren stops the walk.
            while ops and ops[-1] != "(" and precedence[ops[-1]] >= precedence[token]:
                reduce()
            ops.append(token)

    while ops:
        reduce()
    if len(values) != 1:
        raise ValueError(f"malformed expression: {tokens!r}")
    return values[0]


def part1(homework: list[list[Token]]) -> int:
    """Sum of every line, with `+` and `*` at equal precedence, left to right."""
    return sum(evaluate(tokens, SAME_PRECEDENCE) for tokens in homework)


def part2(homework: list[list[Token]]) -> int:
    """Sum of every line, with `+` binding tighter than `*`."""
    return sum(evaluate(tokens, ADDITION_FIRST) for tokens in homework)


def solve(raw: str) -> tuple[int, int]:
    homework = parse_input(raw)
    return part1(homework), part2(homework)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
