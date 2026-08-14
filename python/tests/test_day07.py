"""Day 7: Handy Haversacks."""

import day07

LOCKED = (370, 29547)

EXAMPLE = """\
light red bags contain 1 bright white bag, 2 muted yellow bags.
dark orange bags contain 3 bright white bags, 4 muted yellow bags.
bright white bags contain 1 shiny gold bag.
muted yellow bags contain 2 shiny gold bags, 9 faded blue bags.
shiny gold bags contain 1 dark olive bag, 2 vibrant plum bags.
dark olive bags contain 3 faded blue bags, 4 dotted black bags.
vibrant plum bags contain 5 faded blue bags, 6 dotted black bags.
faded blue bags contain no other bags.
dotted black bags contain no other bags.
"""

# The statement's part-2 example: a linear chain holding 126 bags.
CHAIN = """\
shiny gold bags contain 2 dark red bags.
dark red bags contain 2 dark orange bags.
dark orange bags contain 2 dark yellow bags.
dark yellow bags contain 2 dark green bags.
dark green bags contain 2 dark blue bags.
dark blue bags contain 2 dark violet bags.
dark violet bags contain no other bags.
"""


def test_parse_input_builds_weighted_edges():
    rules = day07.parse_input("light red bags contain 1 bright white bag, 2 muted yellow bags.\n")
    assert rules["light red"] == [(1, "bright white"), (2, "muted yellow")]


def test_parse_input_leaf_is_an_empty_list():
    """A "no other bags" rule is a leaf, not a child colour named "no other"."""
    assert day07.parse_input("faded blue bags contain no other bags.\n") == {"faded blue": []}


def test_parse_input_handles_singular_and_plural_bag():
    """ "1 shiny gold bag" and "2 shiny gold bags" name the same colour."""
    rules = day07.parse_input("a bags contain 1 shiny gold bag.\nb bags contain 2 shiny gold bags.\n")
    assert rules["a"] == [(1, "shiny gold")]
    assert rules["b"] == [(2, "shiny gold")]


def test_part1_example():
    assert day07.part1(day07.parse_input(EXAMPLE)) == 4


def test_part2_example():
    assert day07.part2(day07.parse_input(EXAMPLE)) == 32


def test_part2_chain_example():
    assert day07.part2(day07.parse_input(CHAIN)) == 126


def test_contained_count_of_subtrees():
    """dark olive holds 3 + 4 empties; vibrant plum holds 5 + 6."""
    rules = day07.parse_input(EXAMPLE)
    assert day07.contained_count(rules, "dark olive") == 7
    assert day07.contained_count(rules, "vibrant plum") == 11


def test_part1_counts_colours_not_paths():
    """A colour reachable by several routes still counts exactly once.

    In the example light red reaches shiny gold through bright white *and*
    through muted yellow.  The answer is 4 distinct outer colours, which is
    what makes part 1 a set-closure and not a path count.
    """
    assert day07.part1(day07.parse_input(EXAMPLE)) == 4


def test_part2_excludes_the_outer_bag():
    """The count is bags *inside* shiny gold, so the chain is 2+4+8+16+32+64."""
    assert day07.part2(day07.parse_input(CHAIN)) == 2 + 4 + 8 + 16 + 32 + 64


def test_crlf_input():
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day07.parse_input(crlf) == day07.parse_input(EXAMPLE)
    assert day07.solve(crlf) == (4, 32)


def test_real_input_locked(check_locked):
    check_locked(day07, LOCKED)
