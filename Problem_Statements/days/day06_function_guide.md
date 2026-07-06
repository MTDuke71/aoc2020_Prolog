# Day 06 Function Guide — Custom Customs

> [Day 04](day04_function_guide.md) split a batch file into blank-line
> blocks and turned each block into a record. Day 6 has the *same* block
> structure — groups separated by blank lines — so its `blocks/2`
> splitter is lifted from Day 4 **verbatim**. The new lesson is a
> **representation choice**: every person is a *set* of letters, and the
> two parts are the two set aggregates. "Anyone answered yes" is the
> **union**; "everyone answered yes" is the **intersection**. Pick the
> right data structure — an ordset — and each part collapses to
> `maplist` a per-group count, then `sum_list`.

## The puzzle in one paragraph

The customs form has 26 yes/no questions, `a`–`z`. People travel in
groups separated by blank lines; within a group, each line is one
person's "yes" letters (e.g. `abcx`). **Part 1:** for each group, count
the questions **anyone** said yes to, and sum those counts across all
groups. **Part 2:** for each group, count the questions **everyone**
said yes to, and sum. On the statement's five-group example the part-1
counts are `3 3 3 1 1 = 11` and the part-2 counts are `3 0 1 1 1 = 6`.

---

## The insight: a group is a bag of sets, and the parts are ∪ and ∩

Represent each person as the **set** of letters they answered. Then the
whole puzzle is set algebra, one operation per part:

| group | people (sets) | ∪ (anyone) | \|∪\| | ∩ (everyone) | \|∩\| |
|-------|---------------|-----------|------:|--------------|------:|
| `abc`            | {a,b,c}                     | {a,b,c}   | 3 | {a,b,c} | 3 |
| `a` `b` `c`      | {a},{b},{c}                 | {a,b,c}   | 3 | {}      | 0 |
| `ab` `ac`        | {a,b},{a,c}                 | {a,b,c}   | 3 | {a}     | 1 |
| `a` `a` `a` `a`  | {a},{a},{a},{a}             | {a}       | 1 | {a}     | 1 |
| `b`              | {b}                         | {b}       | 1 | {b}     | 1 |

Sum the `|∪|` column for part 1 (`11`), the `|∩|` column for part 2
(`6`). Nothing else is going on. Once the representation is "list of
groups, each a list of per-person sets," the code writes itself:
`part1` maps each group to its union size and sums; `part2` maps each
group to its intersection size and sums. **The two parts differ by one
word — `ord_union` vs `ord_intersection`.**

One subtlety worth naming: **union has an identity element (the empty
set) but intersection does not.** You can fold a union starting from `{}`
and a lone person just contributes their own letters; there is no "empty"
you can start an intersection from (intersecting with `{}` annihilates
everything), so an intersection fold must be *seeded* with the first
person. SWI's `ord_intersection/2` handles that seeding internally, but
the asymmetry is real and shows up plainly in the Python reference
(`set().union(*people)` vs `people[0].intersection(*people[1:])`).

---

## Reading Prolog: ordsets, two list-aggregates, reused block-splitting

**1. `library(ordsets)` — sets are sorted, duplicate-free lists.** An
*ordset* is just an ordinary list kept in standard order of terms with no
duplicates, so `{a,b,c}` is the term `[a,b,c]`. `list_to_ord_set/2`
builds one by sorting and deduplicating:

```prolog
person_set(Line, Set) :-
    string_chars(Line, Chars),   % "abcx" -> [a,b,c,x]
    list_to_ord_set(Chars, Set). % sort + dedup -> ordset
```

Because ordsets are *sorted*, the set operations are linear merges — the
same merge step as mergesort — not hash lookups. `ord_union(A,B,U)` and
`ord_intersection(A,B,I)` each walk both sorted lists once in `O(|A|+|B|)`.

**2. `ord_union/2` and `ord_intersection/2` fold a *list of* sets.**
library(ordsets) provides list-aggregate forms that take a whole list of
ordsets and return the union / intersection of all of them:

```prolog
group_anyone(People, Count) :-
    ord_union(People, Union),        % ∪ of all people's sets
    length(Union, Count).

group_everyone(People, Count) :-
    ord_intersection(People, Inter), % ∩ of all people's sets
    length(Inter, Count).
```

These are exactly the two aggregates the table above computes. `length/2`
turns a set into its cardinality — for an ordset, plain list length *is*
`|S|` because there are no duplicates. (Both list-forms exist in this
repo's SWI 10.0.2; `ord_union/2` folds from the empty set, and
`ord_intersection/2` seeds from the first element as noted above.)

**3. `blocks/2` is reused from Day 4, unchanged.** Blank-line-separated
groups are structurally identical to Day 4's passports, so the splitter
is the same two predicates:

```prolog
blocks([], []).
blocks([""|Rest], Blocks) :- !, blocks(Rest, Blocks).
blocks([Line|Rest], [[Line|More]|Blocks]) :-
    block_rest(Rest, More, Tail),
    blocks(Tail, Blocks).
```

`split_string(Raw, "\n", " \t\r", Lines)` turns the file into lines with
`\r`/spaces stripped, so blank lines become the empty string `""`.
`blocks/2` then folds runs of non-`""` lines into sub-lists, using the
`""`s as separators (the cut on the `[""|Rest]` clause commits to
"this is a separator, skip it"). Only the *per-line* work differs from
Day 4: Day 4 mapped a joined block to `Key-Value` pairs; Day 6 maps each
line to a letter set. See [Day 04](day04_function_guide.md) for the
splitter's full walkthrough.

**4. `maplist` + `sum_list` is "map to counts, then reduce."**

```prolog
part1(Groups, Answer) :-
    maplist(group_anyone, Groups, Counts),
    sum_list(Counts, Answer).
```

`maplist(group_anyone, Groups, Counts)` produces one count per group
(the classic map); `sum_list/2` reduces the counts to the answer. This
is the same map-then-aggregate shape [Day 4](day04_function_guide.md)
used (`include` + `length`) and [Day 3](day03_function_guide.md) used
(`maplist` + `foldl` product) — here the aggregate is a numeric sum.

---

## The Day 6 code, predicate by predicate

### `parse_input/2`

```prolog
parse_input(Raw, Groups) :-
    split_string(Raw, "\n", " \t\r", Lines),
    blocks(Lines, Blocks),
    maplist(block_group, Blocks, Groups).
```

The repo's split-and-clean opener, then Day 4's `blocks/2`, then
`block_group/2` on each block. The parsed value is a **list of groups,
each a list of per-person ordsets** — one representation feeding both
parts (parse-once, like every day since Day 4).

### `block_group/2` and `person_set/2`

```prolog
block_group(Lines, People) :- maplist(person_set, Lines, People).

person_set(Line, Set) :-
    string_chars(Line, Chars),
    list_to_ord_set(Chars, Set).
```

A block's lines map to a list of sets; each line's characters become a
sorted, duplicate-free ordset. Reading a person as a *set* is the design
decision — it makes `ord_union` / `ord_intersection` directly applicable
and silently absorbs any repeated letter on a line.

### `group_anyone/2`, `group_everyone/2`

Covered above: union size and intersection size of one group. Exported
so the tests can pin them on hand-built groups without going through the
parser.

### `part1/2`, `part2/2`, `solve/3`

```prolog
part1(Groups, Answer) :- maplist(group_anyone,  Groups, Cs), sum_list(Cs, Answer).
part2(Groups, Answer) :- maplist(group_everyone, Groups, Cs), sum_list(Cs, Answer).
```

Identical shape, one word apart. `solve/3` is the standard
parse-once-answer-both; both parts consume the same `Groups`.

---

## Correctness notes

- **Grouping:** `blocks/2` is the verified Day 4 splitter; blank lines
  separate groups and never appear inside one, and a run of non-blank
  lines becomes exactly one group. On the real input this yields **484
  groups**.
- **Part 1 = union cardinality.** "Questions anyone answered yes" is by
  definition the set of letters appearing on *some* line of the group —
  the union. `ord_union/2` starts from `{}` (its identity), so a single
  person's group correctly scores their own letter count.
- **Part 2 = intersection cardinality.** "Questions everyone answered" is
  the set of letters on *every* line — the intersection. It is seeded
  with the first person (no identity to start from), so a single-person
  group scores that person's count, and a group where the people share
  nothing scores `0` (example group 2, `{a}∩{b}∩{c} = {} → 0`).
- **De-duplication is free.** `list_to_ord_set` removes duplicate letters
  within a line and `length` on an ordset is a true cardinality, so
  "duplicate answers don't count extra" holds automatically.
- **Determinism:** `split_string`, `maplist`, `sum_list`, `list_to_ord_set`,
  `ord_union/2`, `ord_intersection/2` are all deterministic; `blocks/2`
  and `block_rest/2` commit their separator choice with a cut. The suite
  runs with no "succeeded with choicepoint" warnings.
- Locked real-input answers: **Part 1 = 6683**, **Part 2 = 3122**,
  cross-validated by [python/day06.py](../../python/day06.py) (and the
  `_opt`/`_mtl` variants).

## Tests — what's pinned and why

[test/day06_tests.pl](../../test/day06_tests.pl) pins four layers, **9
tests green** (run `swipl test/run_tests.pl` from the repo root):

1. **Parser shape** — `abcx/abcy/abcz` parses to one group of three
   ordsets `[[a,b,c,x],[a,b,c,y],[a,b,c,z]]`, and the five-group example
   parses to five groups (structure and count both pinned).
2. **Set ops in isolation** — `group_anyone` on that three-person group
   is `6` (union `{a,b,c,x,y,z}`); `group_everyone` on `{a,b},{a,c}` is
   `1` (`{a}`).
3. **The identity/seed edge case** — a lone-person group scores equal
   under both ops (`anyone == everyone == 3`), the case that would break
   a naive intersection fold started from `{}`.
4. **Example and real** — `solve` on the statement example is `11 / 6`;
   real answers `6683 / 3122` locked against `inputs/day06.txt`.

## Complexity & benchmarks

Let `G` = groups (484), `p` = people per group, `k` = letters per person
(≤ 26). Each group's union/intersection is a sequence of linear merges,
so a group costs `O(p·k)` and the whole solve is `O(total input size)` —
linear in the file.

Mean of 3,000 iterations:

| Phase | Time (ms) |
|-------|----------:|
| parse | 1.05 |
| part1 | 1.19 |
| part2 | 1.06 |

Unusually for this repo, the parts cost about as much as the parse: the
parse only splits lines and builds small sorted sets, while each part
runs 484 fold-of-merges over those sets. All three are ~1 ms — the file
is small and the merges are short.

## If I were writing this in Rust

```rust
use std::collections::BTreeSet;

fn groups(raw: &str) -> Vec<Vec<BTreeSet<char>>> {
    raw.split("\n\n")
        .map(|b| b.lines().map(|l| l.chars().collect()).collect())
        .collect()
}

fn part1(gs: &[Vec<BTreeSet<char>>]) -> usize {
    gs.iter()
        .map(|g| g.iter().flatten().collect::<BTreeSet<_>>().len())
        .sum()
}

fn part2(gs: &[Vec<BTreeSet<char>>]) -> usize {
    gs.iter()
        .map(|g| {
            g.iter()
                .cloned()
                .reduce(|a, b| a.intersection(&b).cloned().collect())
                .map_or(0, |s| s.len())
        })
        .sum()
}
```

- **ordset ↔ `BTreeSet`.** Prolog's ordset (sorted list, linear-merge
  ops) is the direct analog of Rust's `BTreeSet` (sorted tree, linear
  set ops). A `HashSet` would also work and is what the Python reference
  uses; the *sorted* set is the closest structural match to
  `list_to_ord_set`.
- **`ord_union/2` ↔ `flatten().collect::<BTreeSet>()`** — both fold a
  list of sets into their union; Rust's `reduce(|a,b| a.union(&b)…)`
  would mirror it more literally.
- **`ord_intersection/2` ↔ `reduce(|a,b| a.intersection(&b)…)`** — the
  seed-with-the-first-element asymmetry becomes Rust's `reduce` returning
  `Option` (empty group → `None`), handled by `map_or(0, …)`. Same
  "intersection has no identity" fact, expressed by the type.
- **`maplist(_, _, Cs), sum_list(Cs, _)` ↔ `.map(…).sum()`** — map each
  group to a count, reduce by addition.

The Python reference
([python/day06.py](../../python/day06.py)) says the same thing with
`set().union(*people)` and `people[0].intersection(*people[1:])` — the
clearest one-line statement of "union starts empty, intersection starts
from the first person."

## Possible optimization

- **26-bit bitmask instead of ordsets.** Map letter `c` to bit `c-'a'`;
  a person is a `u32`, union is `|`, intersection is `&`, and the count
  is `popcount`. Part 1 folds with `0` (OR identity), part 2 with
  `0x3FFFFFF` = all-26-bits (AND identity — the intersection *does* have
  an identity once the universe is fixed at 26 letters, which removes the
  seeding special case). This is the fastest representation and a natural
  fit for anyone from an embedded/register background — but at ~1 ms
  total the ordset version reads closer to the puzzle's "sets of
  questions," so the shipped source keeps sets.
- **Fuse the two folds.** A single pass per group could accumulate the
  union and the intersection together, halving the group walks. Invisible
  at this size and it entangles the two parts, so declined.
- Sidebar material only; the shipped shape follows the repo's
  correctness-and-clarity-first policy.
