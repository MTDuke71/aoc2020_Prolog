# Day 19 Function Guide — Monster Messages

> A numbered grammar and a pile of messages: count the messages the
> grammar accepts in full. Part 1's grammar is loop-free. Part 2 swaps two
> rules for self-referencing ones, so the grammar can now describe
> arbitrarily long messages — the classic "make your part 1 parser handle
> recursion" twist. The shipping matcher is one recursive function that
> returns *every* position a rule could stop at, and because every step
> of the recursion advances into the text, the loops need no special
> handling: the same function runs both parts, and the two rewritten
> rules are two lines of data. The real input turns out to have a very
> regular shape — every message is a sequence of eight-character blocks,
> each of which is exactly one of the two chunk rules — and the tests use
> that shape as an independent oracle, but the code never learns it.

Source: [`python/day19.py`](../../python/day19.py) ·
Tests: [`python/tests/test_day19.py`](../../python/tests/test_day19.py)

---

## 1. The problem

The input has two blocks. The first is a numbered grammar:

```text
0: 4 1 5
1: 2 3 | 3 2
2: 4 4 | 5 5
3: 4 5 | 5 4
4: "a"
5: "b"
```

A rule is either a single literal character or a list of *alternatives*
separated by `|`, each alternative a sequence of rule numbers to match in
order. Rule 2 above matches `aa` or `bb`; rule 3 matches `ab` or `ba`;
rule 1 is one of each in either order; rule 0 wraps that in an `a` and a
`b`. The second block is the messages, one per line.

**Part 1.** Count the messages that rule 0 matches *completely* — every
character consumed, none left over. On the six-rule grammar above and
the messages `ababbb bababa abbbab aaabbb aaaabbb`, the answer is 2. The
statement makes a point of `aaaabbb`: rule 0 happily matches its first
six characters, but the seventh is unmatched, so it does not count.

**Part 2.** Replace two rules:

```text
8: 42 | 42 8
11: 42 31 | 42 11 31
```

Rule 8 is now "one or more 42s" and rule 11 is "*n* 42s followed by *n*
31s" — the grammar has loops, and the statement warns that "you might
need to modify the rules" rather than write a general solver. Count
again. The statement's part 2 example has 31 rules and 15 messages; 3
match under the rules as given and 12 under the loops.

The real input is 132 rules and 427 messages. Only two rules are
literals (`7: "a"` and `13: "b"`); every other rule has one or two
alternatives of one or two sub-rules. Messages are 24 to 96 characters
long, and — the fact the tests lean on — every length is a multiple of
8. Rule 0 is `8 11`, rule 8 is `42` and rule 11 is `42 31`, so in part 1
rule 0 is simply `42 42 31`.

## 2. Representation

**Rules** are a `dict[int, Rule]` where a `Rule` is either a `str` (the
literal) or a `list[list[int]]` — a list of alternatives, each a list of
rule ids. `1: 2 3 | 3 2` is `{1: [[2, 3], [3, 2]]}`; `4: "a"` is
`{4: "a"}`. A single-alternative rule like `0: 4 1 5` is still a list of
one list, `[[4, 1, 5]]`, so the matcher has one shape to handle. The
dict, rather than a list indexed by id, is because the input lists rules
in no particular order (the part 2 sample puts rule 0 sixth) and because
the ids in the real input have gaps.

**Part 2's replacements** are a second dict, `PART2_LOOPS`, holding
exactly the parsed form of the two lines above. `part2` runs the matcher
on `rules | PART2_LOOPS` — the original table with two entries
overwritten. The matcher does not know that these two are loops; it is
the same function with a different table. A test pins that the constant
is what `parse_rule` produces from the statement's text, so it cannot
drift from the puzzle.

**Match results** are a `set[int]` of *end positions*, not a boolean.
This is the one representation decision that matters and section 4 is
about why.

## 3. Function walkthrough

### `parse_rule(line) -> (id, Rule)`

Split at the first colon. If the body starts with a quote it is a
literal, stripped of its quotes. Otherwise split on `|` for the
alternatives and on whitespace within each for the ids. Spacing is
irrelevant (`"1:  2   3|3 2 "` parses the same as the tidy form — a
test).

### `parse_input(raw) -> (Rules, list[str])`

The two blocks are separated by a blank line, and the split is a regex
on `\n\s*\n` rather than on the literal `"\n\n"`. On a CRLF file the
blank line is `\r\n\r\n`, and a literal split would not find it — the
whole file would be one rules block and the first message line would
raise inside `parse_rule`. Every line is also `.strip()`ed, so a
surviving `\r` on a message cannot become an extra character that no
literal matches (which would silently make every message invalid, the
day 6 failure mode in a different costume). `test_crlf_input` runs both
samples through with `\r\n` line endings.

### `match_ends(rules, rule_id, text, start) -> set[int]`

The whole solution. "Match `rule_id` against `text` starting at `start`,
and return every index the match could end at." Empty set means the
rule does not match here at all.

```python
rule = rules[rule_id]
if isinstance(rule, str):
    return {start + len(rule)} if text.startswith(rule, start) else set()

ends = set()
for sequence in rule:
    positions = {start}
    for sub in sequence:
        positions = {end for pos in positions for end in match_ends(rules, sub, text, pos)}
        if not positions:
            break
    ends |= positions
return ends
```

Three cases:

- **A literal** ends at `start + 1` if that character is there, else
  nowhere. (`str.startswith(prefix, start)` does the bounds check, so a
  literal asked to match past the end returns the empty set rather than
  raising — a test.)
- **A sequence** threads a *frontier* of positions through its
  sub-rules, left to right. Start with `{start}`; for each sub-rule,
  replace the frontier with the union of that sub-rule's ends from every
  position currently in it. If the frontier empties, the sequence has
  failed and the remaining sub-rules are skipped.
- **An alternation** is the union of its sequences' frontiers.

A message matches when `len(text)` is in the set for rule 0 from 0. That
is `matches`, and `count_matches` sums it over the message list.

Here is the statement's `ababbb` under the six-rule grammar. Each line is
a call; indentation is recursion depth. Every number below was checked
by `test_match_ends_docstring_trace`, which asserts each intermediate
set.

```text
rule 0 = [4, 1, 5] from 0            frontier {0}
  4 at 0: 'a' is there                       -> {1}
  1 at 1: alternative [2, 3]
            2 at 1: [4,4] on 'ba' fails, [5,5] on 'ba' fails   -> {}   (sequence abandoned)
          alternative [3, 2]
            3 at 1: [4,5] on 'ba' fails, [5,4] on 'ba' matches -> {3}
            2 at 3: [4,4] on 'bb' fails, [5,5] on 'bb' matches -> {5}
          union                                                -> {5}
  5 at 5: 'b' is there                       -> {6}
rule 0 from 0 -> {6}.   len("ababbb") == 6: match.
```

`aaaabbb` walks the same path and also ends in `{6}` — but its length
is 7, so `6 in {6}` is true and `7 in {6}` is false. The set already
contains the statement's "extra unmatched character" as a fact: the
match stopped one short. `test_extra_character_is_a_prefix_match_not_a_match`
pins exactly this.

In the grammars above every frontier is a singleton, which hides why it
has to be a set at all. Two tiny grammars in the tests show it.
`0: 1 | 1 1`, `1: "a"` on `aa` returns `{1, 2}` — the two alternatives
stop in different places, and a matcher that returned only the first
would report `aa` as a non-match. And `0: 1 2`, `1: 3 | 3 3`, `2: "a"`,
`3: "a"` on `aaa`: rule 1 ends at `{1, 2}`, rule 2 must be tried from
*both*, giving `{2, 3}`, and only the second of those is the full match.
Threading the whole frontier is what makes "the ones that match might be
different each time the rule is encountered" come out right without
backtracking.

### `part1` / `part2`

`count_matches(rules, messages)` and `count_matches(rules | PART2_LOOPS,
messages)`. On the statement's samples: 2 for part 1's grammar; 3 and 12
for the part 2 grammar, and the tests check not just the counts but that
the matching messages are exactly the three and the twelve the statement
lists.

On the real input the answers are **111** and **343**, both submitted
and accepted, and `LOCKED` asserts them. The tests also establish that
an independent count, built from the input's structure (section 4),
agrees with both numbers.

## 4. Why it is correct

**The set is the whole argument.** Define *ends(r, i)* as the set of
indices *j* such that rule *r* matches `text[i:j]`. For a literal that
is `{i+1}` or empty by inspection. For a sequence *s₁ s₂ … sₖ*, the
string matches from *i* to *j* iff there are cut points
*i = p₀ ≤ p₁ ≤ … ≤ pₖ = j* with each piece matching its sub-rule; the
frontier after processing *s₁ … sₘ* is exactly the set of possible
*pₘ*, by induction on *m*, because it is the union over every possible
*pₘ₋₁* of *ends(sₘ, pₘ₋₁)*. For an alternation the sets simply union.
So `match_ends` computes *ends* exactly, with no approximation and no
search order to get wrong, and `len(text) in ends(0, 0)` is the
statement's "completely match". A greedy or first-match implementation
would need backtracking to be correct; this one does not, because it
never commits.

**Why the loops terminate.** `8: 42 | 42 8` refers to itself, so the
recursion could in principle be infinite. It is not, for two reasons
that both hold in the puzzle's grammars and are both worth naming
because either one failing would break it:

1. **Every rule consumes at least one character.** There is no
   empty-matching rule, so every position in a frontier is strictly
   greater than the start it came from.
2. **The self-reference is not leftmost.** In `42 8` and `42 11 31`, a
   42 has to be matched *before* the recursive call, so the recursive
   call's `start` is strictly greater than its caller's. Left recursion
   (`8: 8 42`) would call `match_ends(8, text, start)` from inside
   `match_ends(8, text, start)` with the same start and never return.

Together: along any chain of recursive calls, `start` never decreases
and increases at every self-reference, so depth is bounded by the
message length. Measured with an instrumented copy of the function:
maximum recursion depth on the real input is 11 in part 1 and 17 in
part 2 (chunks are 8 characters and the deepest path is one level per
chunk plus about five inside a chunk); Python's default limit is 1000.
`test_long_loop_does_not_exhaust_the_recursion` runs a 100-chunk,
700-character message through the looped example grammar.

**What the loops mean.** With the example grammar's chunk strings *a*
(a rule-42 string) and *b* (a rule-31 string), the tests pin the
semantics the statement gives in prose:

- rule 8 on `aaaa` (four chunks) ends at `{5, 10, 15, 20}` — every
  chunk boundary, i.e. "one or more"; under the original `8: 42` it
  ends at `{5}` only;
- rule 11 fully matches `aⁿbⁿ` for *n* = 1..4, and on `aabbb` stops at
  20 — a prefix match, not a match;
- rule 0 = `8 11` on `aᵐbⁿ` matches iff *m > n ≥ 1*, checked for all
  36 pairs *m, n* ∈ 0..5, and a 42 after a 31 fails.

**Loops only add.** Each rewritten rule keeps its original alternative,
so anything that matched in part 1 still matches in part 2. The three
part 1 matches of the example are among the twelve, and on the real
input the part 1 match set is a subset of the part 2 match set (both
tests).

**The real input's shape, and an independent count.** The tests
enumerate the languages of rules 42 and 31 by brute force (a test-only
helper; the grammar is loop-free below rule 0). The result:

| rule | strings | length | 
| ---- | ------: | -----: |
| 42   |     128 |      8 |
| 31   |     128 |      8 |

Disjoint, and 128 + 128 = 256 = 2⁸: **42 and 31 partition the
eight-character strings over {a, b}**. (The part 2 example has the same
property one size down — 16 + 16 = 32 = 2⁵ five-character strings.) So
every eight-character block of a message is a 42 or a 31, never both,
never neither, and a message is a word over the alphabet {A, B}. Part 1
(`42 42 31`) is the word `AAB`; part 2 is `AᵐBⁿ` with *m > n ≥ 1*.
`test_real_part1_agrees_with_the_chunk_count` and its part 2 sibling tag
each message this way, count the words of the right shape, and assert
the general matcher gets the same two numbers. On this input the word
`AAB` appears 111 times among the 127 24-character messages, and the
`AᵐBⁿ` shapes total 343.

The agreement is the useful part: two methods that share no code — one
general, one that only works because of a property of this input —
land on the same two numbers, and those numbers are the accepted ones.

## 5. Complexity

Parsing is linear in the input. The matcher's cost is the number of
`match_ends` calls, which is where the "returns every end" design pays
for its simplicity: the same `(rule, start)` pair is recomputed every
time a different path reaches it. Instrumented on the real input:

| phase  | calls   | per message | max depth | largest frontier |
| ------ | ------: | ----------: | --------: | ---------------: |
| part 1 |  79,664 |         187 |        11 |                1 |
| part 2 | 667,288 |       1,563 |        17 |                6 |

Part 2 is 8× the calls of part 1 for the same messages, because rule 8
retries rule 42 from every chunk boundary and rule 11 then retries
42/31 pairs from each of those. In the worst case the work is
polynomial in message length times grammar size (every `(rule, start)`
can be reached from every earlier position), never exponential, because
frontiers are sets and duplicates collapse. Memoising `(rule, start)`
per message would make it strictly O(rules × length × alternatives);
section 7 measures that and finds it only helps part 2.

Measured on the real input (`python\bench.py 19 -n 10`, best / median):

| phase  |       best |     median |
| ------ | ---------: | ---------: |
| parse  |   0.148 ms |   0.152 ms |
| part 1 |  22.10 ms  |  23.09 ms  |
| part 2 | 190.44 ms  | 192.56 ms  |

About 280 ns per `match_ends` call, which is roughly what a Python
function call with a set comprehension inside costs. Across the repo
(`python\bench.py -n 3`, every day) this is the fourth-slowest phase,
behind day 15's 3.7 s, day 11's 313 ms and day 17's 234 ms, and it is
still under a fifth of a second.

## 6. If I were writing this in Rust

The same function, with the rule as an enum and the frontier as a small
`Vec` rather than a hash set (frontiers never exceed six entries, so a
linear `contains` beats hashing):

```rust
enum Rule { Lit(u8), Alts(Vec<Vec<usize>>) }

fn match_ends(rules: &HashMap<usize, Rule>, id: usize, text: &[u8], start: usize) -> Vec<usize> {
    match &rules[&id] {
        Rule::Lit(c) => if start < text.len() && text[start] == *c { vec![start + 1] } else { vec![] },
        Rule::Alts(alts) => {
            let mut ends = Vec::new();
            for seq in alts {
                let mut positions = vec![start];
                for &sub in seq {
                    let mut next = Vec::new();
                    for &pos in &positions {
                        for end in match_ends(rules, sub, text, pos) {
                            if !next.contains(&end) { next.push(end); }
                        }
                    }
                    positions = next;
                    if positions.is_empty() { break; }
                }
                for end in positions { if !ends.contains(&end) { ends.push(end); } }
            }
            ends
        }
    }
}
```

The full port was compiled with `rustc -O` (1.93.1) and run three times
on the real input while writing this guide. Same two answers; parse
**62–94 µs**, part 1 **5.1–5.3 ms**, part 2 **41–51 ms** — only 4–5×
the Python. That ratio is the interesting number. Day 18's shunting-yard
was 15× faster in Rust because Python's per-token overhead *was* the
cost; here the cost is the 667,000 recursive calls the algorithm makes
regardless of language, and each call allocates a `Vec`. Rust cannot fix
an algorithm's redundancy, only its constant factor. Notes:

- **`&[u8]` and `text[start] == *c`** replace `str.startswith(rule,
  start)`: the bounds check is explicit, the comparison is one byte.
  Python's version generalises to multi-character literals for free;
  the Rust one would need `starts_with` on a slice, and the puzzle never
  uses them.
- **The enum does the `isinstance`.** `match &rules[&id]` is one jump on
  the discriminant, and forgetting a variant is a compile error.
- **Frontier as `Vec<usize>`.** Six entries at most, so a `SmallVec` or
  a fixed `[usize; 8]` with a length would remove the heap allocation
  per call, which is most of the remaining 40 ms. That is the
  optimisation with a real payoff here — not the language change.
- **Index the rules by `Vec<Option<Rule>>`** rather than `HashMap` once
  the ids are known to be small (0..131 here): the hash per call is
  measurable at 667,000 calls.
- **The recursion bound is the same argument** and the same 17 frames;
  Rust's default main-thread stack is 8 MB and would not notice.

## 7. Possible optimization

Five ways to count the messages, all run on the real input from a
scratchpad script (not the repo), all agreeing on 111 / 343
(best / median of 10, milliseconds):

| variant                                  | part 1 | part 2 |
| ---------------------------------------- | -----: | -----: |
| shipping `match_ends`                    |  22.9  | 190.5  |
| memoised `(rule, start)` per message     |  33.2  |  70.4  |
| regex: compile rule 0, match each line   |   0.95 |   2.20 |
| chunk tags via enumerated 42 language    |   0.55 |   0.62 |
| chunk tags via a regex for rule 42       |   0.98 |   1.08 |

**Memoisation** is the honest fix for the algorithm's redundancy: an
`lru_cache` on `(rule_id, start)` inside a per-message closure. Part 2
drops to a third. Part 1 gets *slower* — there is nothing to reuse in a
loop-free `42 42 31` and the cache lookups are pure overhead. It stays in
the sidebar because the shipping version is the textbook definition of
*ends(r, i)* with nothing in the way, and 190 ms is not a problem.

**Compile the grammar to a regex.** A loop-free rule is a regular
expression by construction — literal, concatenation, alternation — and
the part 1 pattern for rule 0 is 3,203 characters long, built in 0.7 ms.
Part 2 is *not* regular (`42ⁿ31ⁿ` is the canonical non-regular
language), but the messages are at most 96 characters, so *n* ≤ 6 and
`(?:42){n}(?:31){n}` for *n* = 1..6 unioned is a 13,928-character
pattern that is exact for every message that can occur. Ten times
faster than the shipping code and the standard AoC solution. It is not
shipped because the bound on *n* is a fact about the input smuggled into
the grammar, and because a reader cold in a year should be able to see
the matcher, not `re`'s.

**Chunk tagging** is the section 4 oracle: enumerate rule 42's 128
strings once (0.22 ms), tag each eight-character block A or B, and count
`AAB` and `AᵐBⁿ`. It is 300× faster than the shipping code and it is
the *least* general thing in this guide — it depends on 42 and 31 being
fixed-width and a partition, which nothing in the puzzle text promises.
That is exactly why it lives in the tests as a second opinion and not in
`day19.py` as the answer.
