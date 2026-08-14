"""Day 10: Adapter Array."""

import day10

LOCKED = (2482, 96717311574016)

# The statement's first example: 11 adapters, deliberately out of order.
SMALL = "16\n10\n15\n5\n1\n11\n7\n19\n6\n12\n4\n"
SMALL_RATINGS = [16, 10, 15, 5, 1, 11, 7, 19, 6, 12, 4]

# The statement's larger example: 31 adapters.
LARGE = """\
28
33
18
42
31
14
46
20
48
47
24
23
49
45
19
38
39
11
1
32
25
35
8
17
7
9
4
2
34
10
3
"""


def test_parse_input_preserves_file_order():
    """Sorting is the algorithm's job, not the parser's."""
    assert day10.parse_input(SMALL) == SMALL_RATINGS


def test_full_chain_sorts_and_adds_both_sentinels():
    """Outlet 0 at the front, device at highest + 3 at the back."""
    assert day10.full_chain(SMALL_RATINGS) == [0, 1, 4, 5, 6, 7, 10, 11, 12, 15, 16, 19, 22]


def test_differences_of_the_small_chain():
    chain = day10.full_chain(SMALL_RATINGS)
    assert day10.differences(chain) == [1, 3, 1, 1, 1, 3, 1, 1, 3, 1, 3, 3]


def test_part1_small_example():
    """7 one-jolt steps times 5 three-jolt steps."""
    diffs = day10.differences(day10.full_chain(SMALL_RATINGS))
    assert (diffs.count(1), diffs.count(3)) == (7, 5)
    assert day10.part1(SMALL_RATINGS) == 35


def test_part2_small_example():
    assert day10.part2(SMALL_RATINGS) == 8


def test_part1_large_example():
    assert day10.part1(day10.parse_input(LARGE)) == 220


def test_part2_large_example():
    assert day10.part2(day10.parse_input(LARGE)) == 19208


def test_sorting_makes_the_chain_unique():
    """The non-obvious step that turns part 1 into a histogram.

    Every adapter must be used and each accepts an input 1-3 jolts below its
    rating, so once sorted there is exactly one order that uses them all --
    which is why part 1 can count adjacent differences rather than search.
    This holds only because no two adapters share a rating and no gap
    exceeds 3; both are pinned here.
    """
    for ratings in (SMALL_RATINGS, day10.parse_input(LARGE)):
        chain = day10.full_chain(ratings)
        assert len(set(chain)) == len(chain)
        assert all(1 <= d <= 3 for d in day10.differences(chain))


def test_every_step_of_the_dp_is_a_tribonacci_sum():
    """ways[v] = ways[v-1] + ways[v-2] + ways[v-3], and ascending order is a
    topological order of the DAG, so one left-to-right pass suffices."""
    chain = day10.full_chain(SMALL_RATINGS)
    ways = {chain[0]: 1}
    for value in chain[1:]:
        ways[value] = sum(ways.get(value - gap, 0) for gap in (1, 2, 3))
    assert ways[chain[-1]] == day10.arrangements(chain) == 8


def test_single_adapter():
    """0 -> 3 -> 6: two three-jolt steps, no one-jolt steps, one arrangement."""
    assert day10.part1([3]) == 0
    assert day10.part2([3]) == 1


def test_crlf_input():
    assert day10.parse_input(SMALL.replace("\n", "\r\n")) == SMALL_RATINGS


def test_real_input_locked(check_locked):
    check_locked(day10, LOCKED)
