"""Day 23: Crab Cups."""

import random

import day23
import pytest

LOCKED = (69425837, 218882971435)

SAMPLE = "389125467"
SAMPLE_CUPS = (3, 8, 9, 1, 2, 5, 4, 6, 7)

# The statement's ten-move trace.  Each entry is the circle read clockwise
# from the current cup *before* the move, the three cups lifted, and the
# destination; the eleventh line is the statement's "final" circle.
TRACE = [
    ((3, 8, 9, 1, 2, 5, 4, 6, 7), (8, 9, 1), 2),
    ((2, 8, 9, 1, 5, 4, 6, 7, 3), (8, 9, 1), 7),
    ((5, 4, 6, 7, 8, 9, 1, 3, 2), (4, 6, 7), 3),
    ((8, 9, 1, 3, 4, 6, 7, 2, 5), (9, 1, 3), 7),
    ((4, 6, 7, 9, 1, 3, 2, 5, 8), (6, 7, 9), 3),
    ((1, 3, 6, 7, 9, 2, 5, 8, 4), (3, 6, 7), 9),
    ((9, 3, 6, 7, 2, 5, 8, 4, 1), (3, 6, 7), 8),
    ((2, 5, 8, 3, 6, 7, 4, 1, 9), (5, 8, 3), 1),
    ((6, 7, 4, 1, 5, 8, 3, 9, 2), (7, 4, 1), 5),
    ((5, 7, 4, 1, 8, 3, 9, 2, 6), (7, 4, 1), 3),
]
FINAL_AFTER_10 = (8, 3, 7, 4, 1, 9, 2, 6, 5)


def circle(nxt, start):
    """The whole circle read clockwise from `start`, `start` first."""
    out = [start]
    label = nxt[start]
    while label != start:
        out.append(label)
        label = nxt[label]
    return tuple(out)


def literal_moves(cups, moves, total=None):
    """The statement read literally, on a list: an oracle for the table.

    Yields (circle from the current cup, lifted cups, destination) for each
    move, so the statement's trace can be compared line by line.  Every
    move costs O(n) for the `index` and the splice, which is the cost the
    successor table exists to avoid.
    """
    n = len(cups) if total is None else total
    ring = list(cups) + list(range(len(cups) + 1, n + 1))
    for _ in range(moves):
        cur = ring[0]
        lifted = [ring.pop(1) for _ in range(3)]
        dest = cur - 1 if cur > 1 else n
        while dest in lifted:
            dest = dest - 1 if dest > 1 else n
        yield tuple([cur] + lifted + ring[1:]), tuple(lifted), dest
        i = ring.index(dest)
        ring[i + 1 : i + 1] = lifted
        ring.append(ring.pop(0))
    yield tuple(ring), (), None


def test_parse_input():
    assert day23.parse_input(SAMPLE) == SAMPLE_CUPS


def test_crlf_input():
    """A Windows download ends the one line in \r\n; the \r must not become a cup."""
    assert day23.parse_input(SAMPLE + "\r\n") == SAMPLE_CUPS


def test_parse_tolerates_trailing_newline():
    assert day23.parse_input(SAMPLE + "\n") == SAMPLE_CUPS


@pytest.mark.parametrize("bad", ["", "abc", "3891254670", "389125466", "38912546", "3 8 9"])
def test_parse_rejects_non_permutations(bad):
    """A zero, a repeat, a missing label or anything but digits: the countdown rule needs 1..n."""
    with pytest.raises(ValueError):
        day23.parse_input(bad)


def test_zero_moves_is_the_input_circle():
    nxt, cur = day23.play(SAMPLE_CUPS, 0)
    assert cur == 3
    assert circle(nxt, 3) == SAMPLE_CUPS


@pytest.mark.parametrize("move", range(10))
def test_statement_trace(move):
    """After `move` moves the circle from the current cup is the statement's
    `cups:` line for move+1, and the next lift and destination match too."""
    expected_circle, lifted, dest = TRACE[move]
    nxt, cur = day23.play(SAMPLE_CUPS, move)
    assert circle(nxt, cur) == expected_circle
    assert tuple(day23.clockwise_from(nxt, cur, 3)) == lifted
    # The destination is the table's next move: play one more and read who
    # now precedes the first lifted cup.
    after, _ = day23.play(SAMPLE_CUPS, move + 1)
    assert after[dest] == lifted[0]


def test_statement_final_after_10_moves():
    nxt, cur = day23.play(SAMPLE_CUPS, 10)
    assert cur == 8
    assert circle(nxt, cur) == FINAL_AFTER_10
    assert "".join(map(str, day23.clockwise_from(nxt, 1, 8))) == "92658374"


def test_literal_oracle_reproduces_the_statement_trace():
    """The list-based oracle matches every line of the statement's trace,
    which is what qualifies it to check the table on inputs the statement
    does not cover."""
    lines = list(literal_moves(SAMPLE_CUPS, 10))
    assert lines[:10] == TRACE
    assert lines[10][0] == FINAL_AFTER_10


def test_destination_countdown_skips_lifted_cups_and_wraps():
    """Move 2 of the trace: current 2, lifted 8, 9, 1.  The countdown tries
    1 (in hand), wraps to 9 (in hand), 8 (in hand) and lands on 7: the
    longest countdown possible, since only three cups are ever in hand."""
    nxt, cur = day23.play(SAMPLE_CUPS, 1)
    assert (cur, day23.clockwise_from(nxt, cur, 3)) == (2, [8, 9, 1])
    after, _ = day23.play(SAMPLE_CUPS, 2)
    assert day23.clockwise_from(after, 7, 3) == [8, 9, 1]


def test_destination_wraps_without_a_skip():
    """Move 6: current 1, lifted 3, 6, 7; the destination is 9 at once."""
    after, _ = day23.play(SAMPLE_CUPS, 6)
    assert day23.clockwise_from(after, 9, 3) == [3, 6, 7]


def test_part1_example():
    assert day23.part1(SAMPLE_CUPS) == 67384529


def test_table_is_one_cycle_after_every_move():
    """The successor table is a permutation with a single cycle: following
    it from any cup visits every cup once and returns.  Checked after each
    of the first 100 moves on the sample.  A splice that dropped or
    duplicated a cup would break this at once."""
    for moves in range(101):
        nxt, cur = day23.play(SAMPLE_CUPS, moves)
        assert sorted(circle(nxt, cur)) == list(range(1, 10))


@pytest.mark.parametrize("seed", range(5))
def test_table_agrees_with_the_literal_model_on_random_circles(seed):
    """Nine cups shuffled, 200 moves, the whole circle compared after each."""
    rng = random.Random(seed)
    cups = list(range(1, 10))
    rng.shuffle(cups)
    cups = tuple(cups)
    for moves, (expected, _, _) in enumerate(literal_moves(cups, 200)):
        nxt, cur = day23.play(cups, moves)
        assert circle(nxt, cur) == expected, f"seed {seed}, after {moves} moves"


def test_padded_circle_continues_the_labels_and_closes():
    """Part 2's circle: the input's cups, then 10, 11, ... total, then back
    to the first input cup."""
    nxt, cur = day23.play(SAMPLE_CUPS, 0, total=20)
    assert cur == 3
    assert circle(nxt, 3) == SAMPLE_CUPS + tuple(range(10, 21))


def test_padding_smaller_than_the_input_is_rejected():
    with pytest.raises(ValueError):
        day23.play(SAMPLE_CUPS, 1, total=8)


def test_padded_game_agrees_with_the_literal_model():
    """Sample cups padded to 40, 300 moves, compared move by move.  Long
    enough for the current cup to leave the input cups, stride through
    the padding, wrap, and come back round."""
    for moves, (expected, _, _) in enumerate(literal_moves(SAMPLE_CUPS, 300, total=40)):
        nxt, cur = day23.play(SAMPLE_CUPS, moves, total=40)
        assert circle(nxt, cur) == expected, f"after {moves} moves"


def test_fresh_padding_is_crossed_four_cups_per_move():
    """While the current cup is inside padding nothing has touched yet, the
    three cups after it are cur+1, cur+2, cur+3, the destination is cur-1
    (never in hand, never wrapping), so the three land *behind* and the new
    current cup is cur+4.  On the sample padded to 200 the current cup
    first enters the padding after move 3, at 10, and then strides 10, 14,
    18, ... until the lift would reach past 200.  (Move 2 differs from the
    nine-cup game: current 2 with 8, 9, 1 in hand counts down to 1, in
    hand, and wraps to 200, not to 9.)  On the real million-cup circle the
    same stride runs from move 5 to move 250,002, i.e. the first 2.5% of
    the game is a straight walk."""
    firsts = [day23.play(SAMPLE_CUPS, m, total=200)[1] for m in range(8)]
    assert firsts == [3, 2, 5, 10, 14, 18, 22, 26]
    after_two, _ = day23.play(SAMPLE_CUPS, 2, total=200)
    assert day23.clockwise_from(after_two, 200, 3) == [8, 9, 1]
    m, cur = 3, 10
    while cur + 3 <= 200:
        assert day23.play(SAMPLE_CUPS, m, total=200)[1] == cur
        m, cur = m + 1, cur + 4


@pytest.mark.slow
def test_part2_example():
    """The statement's numbers: cups 934001 and 159792 follow cup 1."""
    nxt, _ = day23.play(SAMPLE_CUPS, 10_000_000, total=1_000_000)
    assert day23.clockwise_from(nxt, 1, 2) == [934001, 159792]
    assert day23.part2(SAMPLE_CUPS) == 149245887792


@pytest.fixture(scope="module")
def real(real_input):
    return day23.parse_input(real_input(23))


def test_real_input_shape(real):
    assert len(real) == 9
    assert sorted(real) == list(range(1, 10))


def test_real_part1_agrees_with_the_literal_model(real):
    expected = list(literal_moves(real, 100))[-1][0]
    nxt, cur = day23.play(real, 100)
    assert circle(nxt, cur) == expected
    i = expected.index(1)
    assert day23.part1(real) == int("".join(map(str, expected[i + 1 :] + expected[:i])))


@pytest.mark.slow
def test_real_part2_table_is_one_cycle_of_a_million(real):
    """After ten million moves the table is still a single cycle through
    every label 1..1,000,000, and the answer is the product of the two cups
    clockwise of 1.  Measured while writing this: the destination countdown
    skips nothing on 98.8% of moves, once on 1.1%, twice on 0.05%, and
    three times exactly twice in the ten million."""
    nxt, _ = day23.play(real, 10_000_000, total=1_000_000)
    assert sorted(circle(nxt, 1)) == list(range(1, 1_000_001))
    first, second = day23.clockwise_from(nxt, 1, 2)
    assert day23.part2(real) == first * second


def test_real_input_locked(check_locked):
    check_locked(day23, LOCKED)
