"""Day 23: Crab Cups.

Cups labelled 1..n stand in a circle; the first one in the input is the
*current cup*.  A move: lift the three cups clockwise of the current cup
out of the circle; pick the *destination*, the cup labelled one less than
the current cup, skipping labels that are in hand and wrapping from 1 back
up to n; drop the three cups back in, clockwise of the destination, in the
order they were lifted; the new current cup is the one now clockwise of
the old one.  On the statement's `389125467`, move 1 lifts 8, 9, 1, the
destination is 2, and the circle becomes

    3 2 8 9 1 5 4 6 7      (current cup 2)

Part 1 is 100 moves on the nine input cups, and the answer is the labels
read clockwise from cup 1, cup 1 itself omitted: `67384529` on the sample.

Part 2 pads the circle to one million cups (the input's nine, then 10, 11,
... 1,000,000 clockwise), makes ten million moves, and asks for the product
of the two cups clockwise of cup 1: 934001 * 159792 = 149245887792 on the
sample.

The circle is a **successor table**, `nxt[label]` = the cup clockwise of
`label`.  A cup never moves; a move rewrites three entries of the table.
That is what makes ten million moves on a million cups a plain loop with
no list to shift, and it is the whole of the solution.
"""

from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day23.txt"

Cups = tuple[int, ...]  # the input circle, clockwise; cups[0] is the current cup
Successors = list[int]  # nxt[label] -> the cup clockwise of `label`; nxt[0] unused


def parse_input(raw: str) -> Cups:
    """One line of digits; each digit is a cup, in clockwise order.

    `strip()` drops the newline (and a Windows `\r`) before the digits are
    read one character at a time.  The cups must be exactly the labels
    1..n, each once, since the destination rule counts down through them.
    """
    digits = raw.strip()
    if not digits.isdigit():
        raise ValueError(f"expected a line of digits, got {digits!r}")
    cups = tuple(int(ch) for ch in digits)
    if sorted(cups) != list(range(1, len(cups) + 1)):
        raise ValueError(f"cups must be the labels 1..{len(cups)} once each, got {digits}")
    return cups


def play(cups: Cups, moves: int, total: int | None = None) -> tuple[Successors, int]:
    """Make `moves` moves and return (successor table, current cup).

    `total` pads the circle: after the input's cups come the labels
    len(cups)+1 .. total, clockwise, and the last of them closes the loop
    back to the first input cup.  With `total=None` the circle is just the
    input.

    One move, on the table:

        a, b, c = nxt[cur], nxt[a], nxt[b]   # lift three
        nxt[cur] = nxt[c]                    # close the gap
        dest = cur - 1, wrapping, skipping a, b, c
        nxt[c] = nxt[dest]                   # splice the three in after dest
        nxt[dest] = a
        cur = nxt[cur]                       # advance

    Three reads, three writes, and a countdown of at most four steps for
    the destination (only three labels can be in hand).
    """
    n = len(cups) if total is None else total
    if n < len(cups):
        raise ValueError(f"total={total} is smaller than the {len(cups)} input cups")

    # Build the circle: input cups in order, then the padding labels, then
    # back to the first cup.  Padding label k (k > len(cups)) is followed by
    # k + 1, so the table is initialised to that and the input's part
    # overwritten.
    nxt = list(range(1, n + 2))
    order = list(cups) + list(range(len(cups) + 1, n + 1))
    for here, there in zip(order, order[1:] + order[:1]):
        nxt[here] = there

    cur = cups[0]
    for _ in range(moves):
        a = nxt[cur]
        b = nxt[a]
        c = nxt[b]
        nxt[cur] = nxt[c]

        dest = cur - 1 if cur > 1 else n
        while dest == a or dest == b or dest == c:
            dest = dest - 1 if dest > 1 else n

        nxt[c] = nxt[dest]
        nxt[dest] = a
        cur = nxt[cur]
    return nxt, cur


def clockwise_from(nxt: Successors, label: int, count: int) -> list[int]:
    """The `count` cups clockwise of `label`, nearest first, `label` itself excluded."""
    out = []
    for _ in range(count):
        label = nxt[label]
        out.append(label)
    return out


def part1(cups: Cups) -> int:
    """After 100 moves, the labels clockwise from cup 1, read as one number."""
    nxt, _ = play(cups, 100)
    return int("".join(str(c) for c in clockwise_from(nxt, 1, len(cups) - 1)))


def part2(cups: Cups) -> int:
    """A million cups, ten million moves, the product of the two cups after cup 1."""
    nxt, _ = play(cups, 10_000_000, total=1_000_000)
    first, second = clockwise_from(nxt, 1, 2)
    return first * second


def solve(raw: str) -> tuple[int, int]:
    cups = parse_input(raw)
    return part1(cups), part2(cups)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
