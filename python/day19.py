"""Day 19: Monster Messages.

The input is a numbered grammar and a list of messages.  A rule is either a
single literal character (`4: "a"`) or one or more *alternatives*, each a
sequence of other rule numbers (`1: 2 3 | 3 2`).  A message is valid when
rule 0 matches it *completely* -- every character consumed, none left over.
Part 1 counts the valid messages.  Part 2 replaces two rules with
self-referencing ones,

    8: 42 | 42 8
    11: 42 31 | 42 11 31

so the grammar gains loops (rule 8 is "one or more 42s", rule 11 is "n 42s
then n 31s"), and counts again.

The matcher is one recursive function, `match_ends(rules, id, text, start)`,
which returns **every** index the text could be consumed up to when `id` is
matched starting at `start` -- a set, because an alternative can succeed
more than one way and the caller needs all of them.  A literal returns
`{start + 1}` if the character is there, else nothing.  A sequence threads a
set of positions through its sub-rules: start with `{start}`, replace it
with the union of each sub-rule's ends from each position, and so on.  An
alternation is the union over its sequences.  A message matches when
`len(text)` is in the set for rule 0 from position 0.

The statement's first grammar, `0: 4 1 5 / 1: 2 3 | 3 2 / 2: 4 4 | 5 5 /
3: 4 5 | 5 4 / 4: "a" / 5: "b"`, on the message `ababbb`:

    rule 0 = [4, 1, 5] from 0
      4 at 0: 'a' matches           -> {1}
      1 at 1: alternative [2, 3]
                2 at 1: [4,4] 'ba' fails, [5,5] 'ba' fails   -> {}
              alternative [3, 2]
                3 at 1: [4,5] 'ba' fails, [5,4] 'ba' matches -> {3}
                2 at 3: [4,4] 'bb' fails, [5,5] 'bb' matches -> {5}
              rule 1 from 1                                   -> {5}
      5 at 5: 'b' matches           -> {6}
    rule 0 from 0 -> {6}; len("ababbb") == 6, so it matches.

On `aaaabbb` the same walk ends in {6}, and 6 != 7: the extra `b` is the
statement's "unmatched character", and the set says so directly.

Because every alternative in the puzzle's grammars consumes at least one
character, and the part 2 loops are right-recursive (`42 8`, never
`8 42`), each recursive call starts strictly further into the text than
its caller's, so the recursion is bounded by the message length and the
loops need no special handling -- the same function runs both parts.
"""

import re
from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day19.txt"

# A rule is a literal string, or a list of alternatives, each a sequence of rule ids.
Rule = str | list[list[int]]
Rules = dict[int, Rule]

# Part 2's two replacements.  Written as data, not code: the matcher does not
# know these are loops, it just recurses, and the recursion is bounded because
# each 42 consumes text before the rule refers to itself again.
PART2_LOOPS: Rules = {
    8: [[42], [42, 8]],
    11: [[42, 31], [42, 11, 31]],
}


def parse_rule(line: str) -> tuple[int, Rule]:
    """`'2: 1 3 | 3 1'` -> `(2, [[1, 3], [3, 1]])`;  `'3: "b"'` -> `(3, "b")`."""
    head, body = line.split(":", 1)
    body = body.strip()
    if body.startswith('"'):
        return int(head), body.strip('"')
    return int(head), [[int(n) for n in alt.split()] for alt in body.split("|")]


def parse_input(raw: str) -> tuple[Rules, list[str]]:
    """The rule table and the message list, split at the blank line.

    The block split is a regex on `\\n\\s*\\n` so a CRLF file's `\\r\\n\\r\\n`
    still counts as one blank line, and every line is `.strip()`ed so a
    surviving `\\r` cannot become part of a message (it would never match
    a literal and the message would be silently invalid).
    """
    rules_block, messages_block = re.split(r"\n\s*\n", raw.strip(), maxsplit=1)
    rules = dict(parse_rule(line.strip()) for line in rules_block.splitlines() if line.strip())
    messages = [line.strip() for line in messages_block.splitlines() if line.strip()]
    return rules, messages


def match_ends(rules: Rules, rule_id: int, text: str, start: int) -> set[int]:
    """Every index `text` can be consumed up to by matching `rule_id` from `start`.

    Empty set means the rule does not match here at all.  See the module
    docstring for a traced example.
    """
    rule = rules[rule_id]
    if isinstance(rule, str):
        return {start + len(rule)} if text.startswith(rule, start) else set()

    ends: set[int] = set()
    for sequence in rule:
        # Thread the frontier of positions through the sequence, left to right.
        positions = {start}
        for sub in sequence:
            positions = {end for pos in positions for end in match_ends(rules, sub, text, pos)}
            if not positions:
                break
        ends |= positions
    return ends


def matches(rules: Rules, text: str) -> bool:
    """True when rule 0 consumes exactly all of `text`."""
    return len(text) in match_ends(rules, 0, text, 0)


def count_matches(rules: Rules, messages: list[str]) -> int:
    return sum(matches(rules, message) for message in messages)


def part1(parsed: tuple[Rules, list[str]]) -> int:
    """Messages that rule 0 matches completely, grammar as given."""
    rules, messages = parsed
    return count_matches(rules, messages)


def part2(parsed: tuple[Rules, list[str]]) -> int:
    """Same count with rules 8 and 11 replaced by the looping versions."""
    rules, messages = parsed
    return count_matches(rules | PART2_LOOPS, messages)


def solve(raw: str) -> tuple[int, int]:
    parsed = parse_input(raw)
    return part1(parsed), part2(parsed)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
