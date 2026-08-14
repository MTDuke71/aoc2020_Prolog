# Day 02 Function Guide — Password Philosophy

> **Written during this repo's Prolog era.** The solution it describes lives
> in the frozen `src/` tree. The maintained solution for this day is
> `python/day02.py`, tested by `python/tests/test_day02.py`. This guide is
> kept for its problem framing and algorithm reasoning, which did not change
> with the language; it will be rewritten Python-first when this day is next
> touched. See the README for what "frozen" means here.

---

> [Day 01](day01_function_guide.md) was about **search** — backtracking did
> all the work. Day 2 is about **parsing**: it's the first day where an input
> line has internal structure (`1-3 a: abcde`) instead of being a bare number.
> That makes it the right day to introduce **DCGs** (Definite Clause
> Grammars), Prolog's built-in grammar notation. The "algorithm" is just a
> filtered count; the parsing is the lesson. Later parse-heavy days (4, 7,
> 14, 16, 18, 19 — Day 19 literally hands you grammar rules as input) will
> reuse this machinery.

## The puzzle in one paragraph

Each of the 1000 input lines pairs a policy with a password:
`Lo-Hi L: password`. **Part 1:** the password is valid when letter `L`
occurs between `Lo` and `Hi` times, inclusive (a frequency-count rule).
**Part 2:** reinterpret the same numbers as 1-indexed *positions* — the
password is valid when **exactly one** of positions `Lo` and `Hi` holds `L`
(an XOR rule). Both parts count the valid lines.

---

## Reading Prolog: DCGs, three kinds of text, and if-then-else

**1. A DCG rule is a grammar rule that consumes a list.** `Head --> Body`
defines a nonterminal. Each element of the body either consumes input —
a literal like `": "` matches those exact characters, `[C]` matches any
single element and binds it — or is another nonterminal. `phrase(entry(E), Codes)`
runs the grammar against a list of character codes; it succeeds if the
grammar consumes the list exactly and binds `E` on the way. Under the hood
each rule is an ordinary predicate with two hidden list arguments (the
"before" and "after" input), which is why grammar rules compose and backtrack
like everything else in Prolog. **In literature terms: a DCG is a recursive
descent parser you get for free from the clause engine** — the analogue of a
parser-combinator library (Rust's `nom`, Haskell's `parsec`).

**2. `{ Goal }` escapes the grammar.** Inside a DCG body, braces wrap plain
Prolog goals that should run *without* consuming input — here,
`{ char_code(Letter, C) }` converts the consumed code to a char atom.
Grammar outside braces eats input; code inside braces computes.

**3. `library(dcg/basics)` is the standard toolkit.** It ships ready-made
nonterminals: `integer//1` (consume a decimal integer), `remainder//1`
(consume everything left), plus `blanks//0`, `string//1`, and friends. The
`//1` notation means "nonterminal with 1 visible argument" — a reminder of
the two hidden ones.

**4. Prolog has three text representations — pick deliberately.**
*Strings* (`"abc"` under SWI defaults) are opaque scalars: good for I/O and
`split_string/4`, bad for element access. *Code lists* are lists of integers
(`0'a` = 97): what `phrase/2` traditionally consumes. *Char lists* are lists
of one-character atoms (`[a,b,c]`): print readably and compare with `==`.
Day 2 uses all three in a deliberate pipeline: split the raw *string* into
lines, convert each line to *codes* for the grammar, store the password as
*chars* for counting and indexing. `string_codes/2`, `char_code/2`, and
`string_chars/2` are the bridges.

**5. `( Cond -> Then ; Else )` is if-then-else, and it commits.** The arrow
runs `Cond` once; if it succeeds, only `Then` is tried (no backtracking into
`Cond` or over to `Else`), otherwise only `Else`. Contrast with a bare
disjunction `( A ; B )`, which leaves a **choice point** even after `A`
succeeds. The first draft of `valid_position/1` used a disjunction and worked
— but every success carried a dangling choice point (plunit even warns
"test succeeded with choicepoint"). The if-then-else version is deterministic
*and* reads as the XOR it implements. This determinism-by-construction
concern is the flip side of Day 1's `once/1`.

**6. Partial application: `==(Letter)`.** `include(==(Letter), Password, Hits)`
passes each element `X` to the partially-applied goal, calling
`==(Letter, X)` — i.e. `Letter == X`. Any predicate can be curried this way
by supplying a prefix of its arguments; it's the point-free cousin of Day 1's
`yall` lambda.

**7. `between/3` runs both directions.** With `N` unbound it *generates*
`Lo..Hi`; with everything bound it's a pure range *check* — here,
`between(Lo, Hi, N)` is just `Lo =< N, N =< Hi` in one goal. Same
relational-predicate story as `length/2` and `nth1/3`: modes, not separate
functions.

---

## The Day 2 code, predicate by predicate

### `parse_input/2` and `parse_line/2`

```prolog
parse_input(Raw, Entries) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(parse_line, Lines, Entries).

parse_line(Line, Entry) :-
    string_codes(Line, Codes),
    phrase(entry(Entry), Codes).
```

The outer line-splitter is byte-for-byte the [Day 00](day00_function_guide.md)
/ [Day 01](day01_function_guide.md) parser; what's new is the last step —
instead of `number_string/2` per line, each line becomes a code list and is
handed to the grammar. Splitting lines with `split_string/4` *first* and
running the DCG per line keeps the grammar tiny (no newline handling inside
it) — a division of labor worth copying on future days.

### `entry//1` — the grammar

```prolog
entry(entry(Lo, Hi, Letter, Password)) -->
    integer(Lo), "-", integer(Hi), " ",
    [C], { char_code(Letter, C) },
    ": ",
    remainder(Cs), { maplist(char_code, Password, Cs) }.
```

Read it left to right against `1-3 a: abcde`: consume an integer (`1`), a
literal dash, another integer (`3`), a space; consume exactly one code and
convert it to the char atom `a`; consume the literal `": "`; consume
everything left and convert codes → chars for the password. The result is
one term:

```prolog
entry(1, 3, a, [a, b, c, d, e])
```

This is the repo's first **compound-term record**. Where Day 1's parsed
input was a bare list of integers, Day 2 bundles four fields into
`entry(Lo, Hi, Letter, Password)` — the Prolog spelling of a struct. Pattern
matching in a clause head (`valid_count(entry(Lo, Hi, Letter, Password))`)
is simultaneously destructuring and documentation.

### `valid_count/1` — the Part 1 policy

```prolog
valid_count(entry(Lo, Hi, Letter, Password)) :-
    include(==(Letter), Password, Hits),
    length(Hits, N),
    between(Lo, Hi, N).
```

Count occurrences by filtering (`include/3` keeps the chars `==` to
`Letter`), measuring the survivors with `length/2`, then range-checking with
`between/3`. Three library predicates, no recursion, no arithmetic beyond
the bounds check.

### `valid_position/1` — the Part 2 policy

```prolog
valid_position(entry(Lo, Hi, Letter, Password)) :-
    nth1(Lo, Password, A),
    nth1(Hi, Password, B),
    (   A == Letter
    ->  B \== Letter
    ;   B == Letter
    ).
```

`nth1/3` is 1-indexed list access — a direct match for the puzzle's
"no concept of index zero," so no `-1` adjustment ever appears. The
if-then-else spells out **exclusive or**: if position `Lo` holds the letter,
position `Hi` must not; otherwise position `Hi` must. (The four cases:
match/match → fail, match/miss → valid, miss/match → valid, miss/miss →
fail.) A bonus of relational access: if a policy position ever exceeded the
password length, `nth1/3` would simply *fail*, classifying the line as
invalid instead of throwing like an out-of-bounds index would.

### `count_valid/3`, `part1/2`, `part2/2`, `solve/3`

```prolog
count_valid(Policy, Entries, N) :-
    include(Policy, Entries, Valid),
    length(Valid, N).

part1(Entries, Answer) :- count_valid(valid_count, Entries, Answer).
part2(Entries, Answer) :- count_valid(valid_position, Entries, Answer).
```

Both parts are the same higher-order shape — "count the entries satisfying
this policy" — with the policy passed as a goal. It's the same
generalize-then-instantiate move as Day 1's `k_sum(K, ...)`, done with a
predicate argument instead of a numeric one. Note `include/3` doing double
duty at two levels: filtering *chars within* a password in `valid_count/1`,
and filtering *entries within* the input here. `solve/3` is the standard
parse-once-answer-both shape.

---

## Correctness notes

- **Parser:** `integer//1` consumes the maximal digit run, and the literal
  separators (`-`, space, `": "`) anchor the fields, so on well-formed lines
  the grammar has exactly one parse. `phrase/2` requires the *whole* line to
  be consumed — trailing garbage fails loudly rather than parsing partially.
  A malformed line makes `parse_line/2` fail (and `maplist/3` with it), not
  silently skip.
- **Part 1:** `include/3` keeps exactly the occurrences of `Letter`, so `N`
  is the occurrence count; `between(Lo, Hi, N)` is the inclusive bounds test
  verbatim from the statement.
- **Part 2:** the if-then-else is exhaustive over the four match/miss cases
  and succeeds on exactly the two XOR cases. Positions are checked with
  1-indexed `nth1/3`, matching the puzzle's indexing.
- Example verified: `2` valid for part 1, `1` for part 2 — both match the
  statement's worked example, and each of the three example lines is also
  pinned individually against the policy predicates.
- Locked real-input answers: **Part 1 = 460**, **Part 2 = 251**,
  cross-validated by [python/day02.py](../../python/day02.py).

## Tests — what's pinned and why

[test/day02_tests.pl](../../test/day02_tests.pl) pins three layers, **11/11
green** (72/72 repo-wide):

1. **Parser** — one line parses to the exact term
   `entry(1, 3, a, [a, b, c, d, e])`, pinning the representation (char
   atoms, 4-field record), not just "something parsed."
2. **Policy predicates, line by line** — each of the statement's three
   example lines is tested against the *individual* policy predicate, with
   plunit's `[fail]` option asserting the invalid ones fail cleanly.
   Boundary cases lock the inclusive bounds (counts of exactly `Lo` and
   exactly `Hi` pass; `Hi + 1` fails) and the XOR (both-match fails —
   the case that separates XOR from OR).
3. **Whole-part examples and real answers** — part 1 = 2 / part 2 = 1 on the
   example; `460` / `251` locked against `inputs/day02.txt`.

Run: `swipl test/run_tests.pl` from the repo root (runs every day's suite).

## Complexity & benchmarks

Let `n` = 1000 lines, `m` = password length (≤ ~20).

- **Parse:** `O(n·m)` — each character is consumed once.
- **Part 1:** `O(n·m)` — every password is scanned in full to count.
- **Part 2:** `O(n·m)` worst case, but each line only walks to positions
  `Lo` and `Hi` (`nth1/3` is a list walk, `O(position)`), so typically far
  less.

Inferences are exact and reproducible (`swipl bench/main.pl day02` reports
the same counts every run); the times are the mean of 1,000 iterations:

| Phase | Inferences | Time (ms) |
|-------|-----------:|----------:|
| parse | 63,689 | 2.614 |
| part1 | 36,449 | 0.839 |
| part2 | 8,915 | 0.245 |

Two reversals from Day 1 worth noticing. First, **parse now dominates** —
grammar-per-line costs more than the arithmetic it feeds, which will be the
normal profile for the parse-heavy days ahead. Second, **part 2 is ~3×
faster than part 1**, the opposite of Day 1: part 1 must scan every
character of every password, while part 2 stops at two positions. The
asymptotic class is the same; the constant factor isn't.

## If I were writing this in Rust

```rust
struct Entry { lo: usize, hi: usize, letter: u8, password: Vec<u8> }

fn valid_count(e: &Entry) -> bool {
    let n = e.password.iter().filter(|&&c| c == e.letter).count();
    (e.lo..=e.hi).contains(&n)
}

fn valid_position(e: &Entry) -> bool {
    (e.password[e.lo - 1] == e.letter) != (e.password[e.hi - 1] == e.letter)
}

fn part1(entries: &[Entry]) -> usize {
    entries.iter().filter(|e| valid_count(e)).count()
}
```

- `entry(Lo, Hi, Letter, Password)` ↔ a named `struct Entry`; clause-head
  destructuring ↔ field access (or a `let Entry { lo, hi, .. } = e` pattern).
- The DCG ↔ `nom` parser combinators is the deep bridge:
  `integer(Lo), "-", integer(Hi)` is `separated_pair(u32, tag("-"), u32)`
  almost token for token. A regex (as
  [python/day02.py](../../python/day02.py) uses) is the low-ceremony
  alternative, but combinators — like DCGs — compose into big grammars,
  which is why both will still be standing on Day 19.
- `include(==(Letter), ...) + length` ↔ `.iter().filter(...).count()`;
  `between(Lo, Hi, N)` ↔ `(lo..=hi).contains(&n)`.
- The XOR if-then-else ↔ `!=` on two `bool`s — Rust gets XOR as an operator;
  Prolog spells it as control flow.
- `nth1/3` failing on an out-of-range position ↔ `.get(i)` returning
  `Option`, where Rust's `[i]` indexing would panic — Prolog's failure is
  closer to the `Option` idiom than to the panic.

## Possible optimization

- **Fuse count into one pass:** `include/3` + `length/2` builds an
  intermediate `Hits` list. `aggregate_all(count, member(X, Password), X == Letter, N)`
  or a `foldl` counter would count without allocating. Saves an `O(m)`
  allocation per line — invisible at this scale.
- **Skip chars, index codes:** keep the password as a string and use
  `string_code/3` for `O(1)` position access in part 2 instead of `nth1/3`'s
  list walk, and `string_codes/2` only where counting needs it.
- **Parse straight to answers:** the grammar could compute validity during
  the parse and never materialize `entry/4` terms at all — a fun DCG trick,
  but it destroys the parse/part1/part2 separation the repo's shape (and
  bench) depends on.
- All three are noise at 1000 lines / <3 ms total; the record-based version
  stays per the repo's optimization policy.
