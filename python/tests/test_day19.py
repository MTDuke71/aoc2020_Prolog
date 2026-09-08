"""Day 19: Monster Messages."""

from itertools import product

import pytest

import day19

LOCKED = (111, 343)

# The statement's second grammar and its five messages.
SAMPLE = """\
0: 4 1 5
1: 2 3 | 3 2
2: 4 4 | 5 5
3: 4 5 | 5 4
4: "a"
5: "b"

ababbb
bababa
abbbab
aaabbb
aaaabbb
"""

# Which of the five the statement says match rule 0 completely.
SAMPLE_VERDICTS = [
    ("ababbb", True),
    ("bababa", False),
    ("abbbab", True),
    ("aaabbb", False),
    ("aaaabbb", False),  # "an extra unmatched b on the end"
]

# The statement's part 2 grammar and its fifteen messages.  Under the given
# rules three match; with 8 and 11 replaced by the looping versions, twelve.
SAMPLE_PART2 = """\
42: 9 14 | 10 1
9: 14 27 | 1 26
10: 23 14 | 28 1
1: "a"
11: 42 31
5: 1 14 | 15 1
19: 14 1 | 14 14
12: 24 14 | 19 1
16: 15 1 | 14 14
31: 14 17 | 1 13
6: 14 14 | 1 14
2: 1 24 | 14 4
0: 8 11
13: 14 3 | 1 12
15: 1 | 14
17: 14 2 | 1 7
23: 25 1 | 22 14
28: 16 1
4: 1 1
20: 14 14 | 1 15
3: 5 14 | 16 1
27: 1 6 | 14 18
14: "b"
21: 14 1 | 1 14
25: 1 1 | 1 14
22: 14 14
8: 42
26: 14 22 | 1 20
18: 15 15
7: 14 5 | 1 21
24: 14 1

abbbbbabbbaaaababbaabbbbabababbbabbbbbbabaaaa
bbabbbbaabaabba
babbbbaabbbbbabbbbbbaabaaabaaa
aaabbbbbbaaaabaababaabababbabaaabbababababaaa
bbbbbbbaaaabbbbaaabbabaaa
bbbababbbbaaaaaaaabbababaaababaabab
ababaaaaaabaaab
ababaaaaabbbaba
baabbaaaabbaaaababbaababb
abbbbabbbbaaaababbbbbbaaaababb
aaaaabbaabaaaaababaa
aaaabbaaaabbaaa
aaaabbaabbaaaaaaabbbabbbaaabbaabaaa
babaaabbbaaabaababbaabababaaab
aabbbbbaabbbaaaaaabbbbbababaaaaabbaaabba
"""

PART2_MATCHES_ORIGINAL = {"bbabbbbaabaabba", "ababaaaaaabaaab", "ababaaaaabbbaba"}

PART2_MATCHES_LOOPED = {
    "bbabbbbaabaabba",
    "babbbbaabbbbbabbbbbbaabaaabaaa",
    "aaabbbbbbaaaabaababaabababbabaaabbababababaaa",
    "bbbbbbbaaaabbbbaaabbabaaa",
    "bbbababbbbaaaaaaaabbababaaababaabab",
    "ababaaaaaabaaab",
    "ababaaaaabbbaba",
    "baabbaaaabbaaaababbaababb",
    "abbbbabbbbaaaababbbbbbaaaababb",
    "aaaaabbaabaaaaababaa",
    "aaaabbaabbaaaaaaabbbabbbaaabbaabaaa",
    "aabbbbbaabbbaaaaaabbbbbababaaaaabbaaabba",
}


def language(rules, rule_id):
    """Every string a (loop-free) rule matches, by brute enumeration.  Test-only."""
    rule = rules[rule_id]
    if isinstance(rule, str):
        return {rule}
    strings = set()
    for sequence in rule:
        partial = {""}
        for sub in sequence:
            partial = {head + tail for head in partial for tail in language(rules, sub)}
        strings |= partial
    return strings


def all_strings(length):
    return {"".join(chars) for chars in product("ab", repeat=length)}


# --- parsing ------------------------------------------------------------------


def test_parse_rule_literal():
    assert day19.parse_rule('4: "a"') == (4, "a")


def test_parse_rule_single_sequence():
    assert day19.parse_rule("0: 4 1 5") == (0, [[4, 1, 5]])


def test_parse_rule_alternatives():
    assert day19.parse_rule("1: 2 3 | 3 2") == (1, [[2, 3], [3, 2]])


def test_parse_rule_tolerates_unusual_spacing():
    assert day19.parse_rule("1:  2   3|3 2 ") == (1, [[2, 3], [3, 2]])


def test_parse_input_splits_rules_from_messages():
    rules, messages = day19.parse_input(SAMPLE)
    assert rules == {
        0: [[4, 1, 5]],
        1: [[2, 3], [3, 2]],
        2: [[4, 4], [5, 5]],
        3: [[4, 5], [5, 4]],
        4: "a",
        5: "b",
    }
    assert messages == ["ababbb", "bababa", "abbbab", "aaabbb", "aaaabbb"]


def test_parse_input_rule_order_does_not_matter():
    """The part 2 sample lists rule 0 sixth and the literals wherever; the dict does not care."""
    rules, _ = day19.parse_input(SAMPLE_PART2)
    assert rules[0] == [[8, 11]]
    assert rules[1] == "a"
    assert rules[14] == "b"
    assert len(rules) == 31


def test_crlf_input():
    assert day19.parse_input(SAMPLE.replace("\n", "\r\n")) == day19.parse_input(SAMPLE)
    assert day19.parse_input(SAMPLE_PART2.replace("\n", "\r\n")) == day19.parse_input(SAMPLE_PART2)


def test_part2_loops_are_the_statement_text():
    """PART2_LOOPS is data.  Pin that it is exactly what the statement says to substitute."""
    assert dict([day19.parse_rule("8: 42 | 42 8"), day19.parse_rule("11: 42 31 | 42 11 31")]) == (
        day19.PART2_LOOPS
    )


# --- the statement's worked examples -----------------------------------------------


def test_first_grammar_matches_exactly_aab_and_aba():
    rules, _ = day19.parse_input('0: 1 2\n1: "a"\n2: 1 3 | 3 1\n3: "b"\n\nx\n')
    assert language(rules, 2) == {"ab", "ba"}
    assert language(rules, 0) == {"aab", "aba"}
    short = all_strings(1) | all_strings(2) | all_strings(3) | all_strings(4)
    assert {s for s in short if day19.matches(rules, s)} == {"aab", "aba"}


def test_second_grammar_rule_1_has_the_eight_listed_strings():
    rules, _ = day19.parse_input(SAMPLE)
    assert language(rules, 2) == {"aa", "bb"}
    assert language(rules, 3) == {"ab", "ba"}
    assert language(rules, 1) == {"aaab", "aaba", "bbab", "bbba", "abaa", "abbb", "baaa", "babb"}


def test_second_grammar_rule_0_has_the_eight_listed_strings():
    rules, _ = day19.parse_input(SAMPLE)
    listed = {"aaaabb", "aaabab", "abbabb", "abbbab", "aabaab", "aabbbb", "abaaab", "ababbb"}
    assert language(rules, 0) == listed
    # ... and the matcher agrees on all 64 six-character strings, not just those eight.
    assert {s for s in all_strings(6) if day19.matches(rules, s)} == listed


@pytest.mark.parametrize(("message", "expected"), SAMPLE_VERDICTS)
def test_statement_verdicts(message, expected):
    rules, _ = day19.parse_input(SAMPLE)
    assert day19.matches(rules, message) is expected


def test_part1_sample():
    assert day19.part1(day19.parse_input(SAMPLE)) == 2


# --- match_ends, the one function that does the work --------------------------------


def test_match_ends_docstring_trace():
    """The module docstring's walk of `ababbb`, step by step."""
    rules, _ = day19.parse_input(SAMPLE)
    text = "ababbb"
    assert day19.match_ends(rules, 4, text, 0) == {1}
    assert day19.match_ends(rules, 2, text, 1) == set()
    assert day19.match_ends(rules, 3, text, 1) == {3}
    assert day19.match_ends(rules, 2, text, 3) == {5}
    assert day19.match_ends(rules, 1, text, 1) == {5}
    assert day19.match_ends(rules, 5, text, 5) == {6}
    assert day19.match_ends(rules, 0, text, 0) == {6}


def test_extra_character_is_a_prefix_match_not_a_match():
    """`aaaabbb`: rule 0 consumes six characters and stops.  The set says 6, the length says 7."""
    rules, _ = day19.parse_input(SAMPLE)
    assert day19.match_ends(rules, 0, "aaaabbb", 0) == {6}
    assert not day19.matches(rules, "aaaabbb")


def test_literal_past_the_end_is_empty():
    rules, _ = day19.parse_input(SAMPLE)
    assert day19.match_ends(rules, 4, "a", 1) == set()
    assert day19.match_ends(rules, 0, "", 0) == set()


def test_ends_is_a_set_because_alternatives_can_stop_in_different_places():
    """`0: 1 | 1 1`, `1: "a"` on `aa`: the first alternative ends at 1, the second at 2.
    Returning only the first would lose the full match."""
    rules = {0: [[1], [1, 1]], 1: "a"}
    assert day19.match_ends(rules, 0, "aa", 0) == {1, 2}
    assert day19.matches(rules, "aa")
    assert day19.matches(rules, "a")


def test_sequence_threads_every_frontier_position():
    """`0: 1 2`, `1: "a" | "aa"` (as two rules), `2: "a"`: rule 1 can end at 1 or 2, and
    rule 2 must be tried from both.  Only the frontier {1, 2} -> {2, 3} finds `aaa`."""
    rules = {0: [[1, 2]], 1: [[3], [3, 3]], 2: "a", 3: "a"}
    assert day19.match_ends(rules, 1, "aaa", 0) == {1, 2}
    assert day19.match_ends(rules, 0, "aaa", 0) == {2, 3}
    assert day19.matches(rules, "aaa")
    assert day19.matches(rules, "aa")
    assert not day19.matches(rules, "a")


# --- part 2: the loops ---------------------------------------------------------------


def test_part2_sample_counts():
    parsed = day19.parse_input(SAMPLE_PART2)
    assert day19.part1(parsed) == 3
    assert day19.part2(parsed) == 12


def test_part2_sample_lists_the_right_messages():
    rules, messages = day19.parse_input(SAMPLE_PART2)
    looped = rules | day19.PART2_LOOPS
    assert {m for m in messages if day19.matches(rules, m)} == PART2_MATCHES_ORIGINAL
    assert {m for m in messages if day19.matches(looped, m)} == PART2_MATCHES_LOOPED


def test_looping_grammar_only_adds_matches():
    """Every original alternative is still an alternative, so the part 1 matches are a
    subset of the part 2 matches -- on the sample and (below) on the real input."""
    assert PART2_MATCHES_ORIGINAL <= PART2_MATCHES_LOOPED


def test_sample_42_and_31_are_fixed_width_and_disjoint():
    """Both example chunk rules match sixteen five-character strings and no string matches both."""
    rules, _ = day19.parse_input(SAMPLE_PART2)
    lang42, lang31 = language(rules, 42), language(rules, 31)
    assert {len(s) for s in lang42} == {len(s) for s in lang31} == {5}
    assert len(lang42) == len(lang31) == 16
    assert not lang42 & lang31


def test_rule_8_is_one_or_more_42s():
    rules, _ = day19.parse_input(SAMPLE_PART2)
    looped = rules | day19.PART2_LOOPS
    chunk = min(language(rules, 42))
    assert not day19.match_ends(looped, 8, "", 0)
    assert day19.match_ends(looped, 8, chunk * 4, 0) == {5, 10, 15, 20}
    assert day19.match_ends(rules, 8, chunk * 4, 0) == {5}  # the original rule 8: exactly one


def test_rule_11_is_n_42s_then_n_31s():
    rules, _ = day19.parse_input(SAMPLE_PART2)
    looped = rules | day19.PART2_LOOPS
    a = min(language(rules, 42))
    b = min(language(rules, 31))
    for n in range(1, 5):
        text = a * n + b * n
        assert day19.match_ends(looped, 11, text, 0) == {len(text)}
    # Unequal counts: 3 and 2 cannot be balanced at all; 2 and 3 balance the first
    # two pairs and stop at 20 -- a prefix match, which is not a match.
    assert day19.match_ends(looped, 11, a * 3 + b * 2, 0) == set()
    assert day19.match_ends(looped, 11, a * 2 + b * 3, 0) == {20}
    assert not day19.match_ends(looped, 11, b + a, 0)


def test_rule_0_under_loops_is_more_42s_than_31s():
    """`0: 8 11` = (one or more 42) (n 42, n 31): a run of m 42-chunks then n 31-chunks with
    m > n >= 1.  Every other arrangement fails, including the one where the counts are equal."""
    rules, _ = day19.parse_input(SAMPLE_PART2)
    looped = rules | day19.PART2_LOOPS
    a = min(language(rules, 42))
    b = min(language(rules, 31))
    for m in range(6):
        for n in range(6):
            assert day19.matches(looped, a * m + b * n) is (m > n >= 1), (m, n)
    assert not day19.matches(looped, a * 3 + b + a + b)  # a 42 after a 31


def test_long_loop_does_not_exhaust_the_recursion():
    """Each `42 8` step advances the start by a whole chunk, so depth grows with the
    chunk count, not with the branching.  100 chunks is 500 characters and well
    inside Python's default recursion limit."""
    rules, _ = day19.parse_input(SAMPLE_PART2)
    looped = rules | day19.PART2_LOOPS
    a = min(language(rules, 42))
    b = min(language(rules, 31))
    assert day19.matches(looped, a * 100 + b * 40)
    assert not day19.matches(looped, a * 40 + b * 100)


# --- the real input's structure, and an independent count that uses it ----------------
#
# The real grammar has the same shape as the part 2 sample, only wider: 42 and 31
# each match exactly 128 eight-character strings, none in common, and between them
# they cover all 256.  So every eight-character block of a message is either a 42
# or a 31, never both, never neither, and a message is a word over the alphabet
# {A, B}.  Part 1 (`0: 42 42 31`) is the word AAB; part 2 is A^m B^n with m > n >= 1.
# The shipping code knows none of this.  These tests pin that the structure holds
# and that the general matcher agrees with the count the structure makes trivial.


@pytest.fixture(scope="module")
def real(real_input):
    return day19.parse_input(real_input(19))


@pytest.fixture(scope="module")
def chunk_languages(real):
    rules, _ = real
    return language(rules, 42), language(rules, 31)


def test_real_rule_0_is_42_42_31(real):
    rules, _ = real
    assert rules[0] == [[8, 11]]
    assert rules[8] == [[42]]
    assert rules[11] == [[42, 31]]


def test_real_42_and_31_partition_the_eight_character_strings(chunk_languages):
    lang42, lang31 = chunk_languages
    assert {len(s) for s in lang42} == {len(s) for s in lang31} == {8}
    assert len(lang42) == len(lang31) == 128
    assert not lang42 & lang31
    assert lang42 | lang31 == all_strings(8)


def test_real_messages_are_whole_chunks(real):
    _, messages = real
    assert all(len(m) % 8 == 0 for m in messages)
    assert min(len(m) for m in messages) == 24


def tags(message, lang42):
    return "".join("A" if message[i : i + 8] in lang42 else "B" for i in range(0, len(message), 8))


def test_real_part1_agrees_with_the_chunk_count(real, chunk_languages):
    _, messages = real
    lang42, _ = chunk_languages
    expected = sum(tags(m, lang42) == "AAB" for m in messages)
    assert day19.part1(real) == expected


def test_real_part2_agrees_with_the_chunk_count(real, chunk_languages):
    _, messages = real
    lang42, _ = chunk_languages

    def looped_shape(word):
        m = len(word) - len(word.lstrip("A"))
        n = len(word) - m
        return m > n >= 1 and word == "A" * m + "B" * n

    expected = sum(looped_shape(tags(m, lang42)) for m in messages)
    assert day19.part2(real) == expected


def test_real_part1_matches_are_a_subset_of_part2_matches(real):
    rules, messages = real
    looped = rules | day19.PART2_LOOPS
    part1 = {m for m in messages if day19.matches(rules, m)}
    part2 = {m for m in messages if day19.matches(looped, m)}
    assert part1 <= part2


def test_real_input_locked(check_locked):
    check_locked(day19, LOCKED)
