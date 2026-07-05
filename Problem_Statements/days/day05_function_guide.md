# Day 05 Function Guide — Binary Boarding

> [Day 04](day04_function_guide.md) showed a predicate *being* a lookup
> table (`valid_field/1`, one clause per case). Day 5 reuses that exact
> move for a four-line alphabet — `bit/2` — but the real lesson is a
> **representation insight** that erases the algorithm entirely: the
> puzzle describes seven halvings then three more, but F/L/B/R are just
> *bits*, so a boarding pass is a 10-bit binary number and its seat ID is
> that number read whole. Once you see that, part 1 is `max_list/2` and
> the only interesting code is part 2's **find-the-gap** scan.

## The puzzle in one paragraph

You have 799 boarding passes like `FBFBBFFRLR`. The first 7 characters
(`F`/`B`) binary-partition 128 rows; the last 3 (`L`/`R`) partition 8
columns; the **seat ID** is `Row*8 + Col`. **Part 1:** the highest seat
ID in the list. **Part 2:** your seat is the only missing ID whose
`ID-1` and `ID+1` are both present (front/back missing seats don't
count). The statement *sounds* like an interval-narrowing simulation —
"start with rows 0–127, take the lower half, …" — and you could write it
that way. You don't have to.

---

## The insight: binary partitioning *is* binary

Watch the halving on `FBFBBFF` and track only the low/high choice:

| char | region kept | half chosen | bit |
|------|-------------|-------------|----:|
| F | 0–127 → 0–63   | lower | 0 |
| B | 0–63  → 32–63  | upper | 1 |
| F | 32–63 → 32–47  | lower | 0 |
| B | 32–47 → 40–47  | upper | 1 |
| B | 40–47 → 44–47  | upper | 1 |
| F | 44–47 → 44–45  | lower | 0 |
| F | 44–45 → 44      | lower | 0 |

The bits are `0101100` = **44**. Successive halving of `[0, 2^n)` while
recording lower=0/upper=1 is *exactly* how you read a binary numeral
most-significant-bit-first — each choice fixes one bit from the top. So
`F`/`L` = 0 and `B`/`R` = 1, and:

- the 7 row characters are the row's binary digits,
- the 3 column characters are the column's binary digits,
- and `Row*8 + Col` = `Row << 3 | Col` = **the whole 10-character string
  read as one 10-bit number.**

That last line is the payoff: **you never split the pass into row and
column at all.** Decode all ten characters as one binary number and you
have the seat ID directly. Row and column are only needed to *print* an
answer the puzzle already folded into the ID for you. `seat/4` recovers
them by splitting the bits back (`Id // 8`, `Id mod 8`), but the parts
never call it.

---

## Reading Prolog: `foldl` as Horner, a 4-clause alphabet, gap scanning

**1. `foldl/4` is a left fold — here it's Horner's method.** Reading a
digit string as a number is the recurrence `acc := acc * base + digit`,
applied left to right. That is Horner's rule for evaluating a polynomial
(the numeral `d₆d₅…d₀` is `Σ dᵢ·2ⁱ`), and it's a textbook left fold:

```prolog
seat_id(Pass, Id) :-
    string_chars(Pass, Chars),
    foldl(add_bit, Chars, 0, Id).

add_bit(Char, Acc0, Acc) :-
    bit(Char, B),
    Acc is Acc0 * 2 + B.
```

`foldl(Goal, List, V0, V)` threads an accumulator through `Goal(Elem,
Acc0, Acc)` — the same tool [Day 3](day03_function_guide.md) used to
multiply five slope counts and [Day 1](day01_function_guide.md) used for
its product. Day 3 hand-wrote its strided walk as an explicit recursive
accumulator (`slope_trees_/6`); this is the same accumulator shape handed
to the library combinator, because the step here has no early exit or
index bookkeeping to justify writing the recursion out.

**2. The alphabet is a four-fact lookup table.** Day 4's headline was "a
predicate can *be* the table"; Day 5 is the smallest possible instance:

```prolog
bit('F', 0).
bit('B', 1).
bit('L', 0).
bit('R', 1).
```

No `if char == 'F'` chain — the clause *heads* dispatch by unification,
and because the four keys are distinct constants, SWI's first-argument
indexing jumps straight to the matching clause and leaves **no choice
point**. `bit/2` is also reversible in principle (`bit(C, 0)` enumerates
`F` and `L`), though the parts only use it forward. Compare Day 4's
`valid_field/1`: same idea, richer bodies.

**3. Part 2 is a gap scan over a sorted list.** Your seat is the hole in
an otherwise-contiguous block of occupied IDs:

```prolog
part2(Ids, Seat) :-
    sort(Ids, Sorted),
    gap(Sorted, Seat).

gap([A, B|_], Seat) :-
    B =:= A + 2,
    !,
    Seat is A + 1.
gap([_|Rest], Seat) :-
    gap(Rest, Seat).
```

`sort/2` orders *and* dedups (seat IDs are unique, so nothing is lost).
`gap/2` walks adjacent pairs looking for the first that skips exactly one
value — `A` and `A+2` with `A+1` absent. The two-element head pattern
`[A, B|_]` is the classic "look at a sliding window of two" idiom: match
the first two elements, and on failure recurse on the tail so the window
slides by one. This is [Day 3's `drop/3`](day03_function_guide.md)
steadfast-cut discipline again — the output `Seat` is bound *after* the
`!`, never in the clause head, so the commit rests on the inputs alone
and a pre-bound `Seat` can't smuggle control past the cut into the second
clause. (It's the repo style from Day 3 on.)

**4. `=:=` vs `=`.** `B =:= A + 2` is *arithmetic* equality — it
evaluates both sides and compares numbers. `B = A + 2` would be
*unification* and, with `B` already an integer, would try to unify `522`
with the compound term `+(520, 2)` and fail. When both operands are
bound numbers you want, use `=:=`; Day 2's `between/3` range checks lived
in the same all-bound-arithmetic world.

---

## The Day 5 code, predicate by predicate

### `parse_input/2`

```prolog
parse_input(Raw, Ids) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(seat_id, Lines, Ids).
```

The repo's standard split-and-clean opener (pad chars strip `\r` and
trailing spaces, `exclude(=(""), …)` drops blank lines — same three lines
as Day 3), then `maplist(seat_id, …)` decodes each line in place. Note
the parse produces **integers, not strings**: unlike Days 2–4, which kept
raw text around for later validation, Day 5 has nothing left to inspect
once a pass is a number, so decoding belongs in the parse.

### `seat_id/2` and `add_bit/3`

Covered above — `string_chars` to a char list, `foldl` Horner-folds the
`bit/2` values into one integer. `string_chars` (not `string_codes`)
because `bit/2`'s keys are the one-character atoms `'F'`/`'B'`/`'L'`/`'R'`;
a codes version (`bit(0'F, 0)`) would work identically and is what Day 4
used for its hex checks — either is fine, this picks the one that reads
closest to the puzzle's letters.

### `bit/2` and `seat/4`

```prolog
seat(Pass, Row, Col, Id) :-
    seat_id(Pass, Id),
    Row is Id // 8,
    Col is Id mod 8.
```

`seat/4` is the decode the *statement* asks about (row 44, column 5) but
the *parts* never need: `Id // 8` is the high 7 bits, `Id mod 8` the low
3 — literally reslicing the 10-bit number the insight said not to split.
It exists so the tests can pin the statement's worked triples and so a
cold reader sees the row/column really are recoverable.

### `part1/2`, `part2/2`, `solve/3`

```prolog
part1(Ids, Max) :- max_list(Ids, Max).
```

Part 1 collapses to a library one-liner — the representation did the
work. `part2/2` sorts and gap-scans (above). `solve/3` is the standard
parse-once-answer-both, and because `parse_input/2` already decoded to
IDs, both parts operate on the same integer list with no re-parsing.

---

## Correctness notes

- **Decode:** `seat_id/2` reads all ten characters as one binary number.
  The statement's four worked passes decode to (row, col, id) =
  (44,5,357), (70,7,567), (14,7,119), (102,4,820) — all pinned in tests,
  each `Id =:= Row*8 + Col` by construction.
- **Part 1** is `max_list/2` over the decoded IDs — no ordering
  assumption on the input, `max_list` scans the whole list.
- **Part 2** relies on the puzzle's promise: every seat between the
  lowest and highest occupied ID is filled *except yours*, and the
  missing front/back seats lie *outside* `[min, max]`. So within the
  sorted occupied list there is exactly one adjacent pair differing by 2,
  `gap/2` returns at the first (and only) one via its cut, and `Seat` is
  the enclosed value. On the `[1,2,3,5,6]` test that's `4`.
- **Determinism:** `bit/2` is indexed to a single clause per character
  (no choice point); `gap/2`'s cut commits at the found gap; `sort/2`,
  `foldl/4`, `max_list/2` are all deterministic. The suite runs with no
  "succeeded with choicepoint" warnings.
- Locked real-input answers: **Part 1 = 888**, **Part 2 = 522**,
  cross-validated by [python/day05.py](../../python/day05.py).

## Tests — what's pinned and why

[test/day05_tests.pl](../../test/day05_tests.pl) pins four layers, **7
tests + 4 forall sub-tests green** (run `swipl test/run_tests.pl` from
the repo root):

1. **Decode** — the statement's four worked passes, run as a
   `forall`-parameterized test over `seat/4`, each checking row, column
   *and* ID (so a bug that swaps row/col or mis-weights a bit can't hide).
2. **The identity** — `seat_id("BBFFBBFRLL")` equals `102*8 + 4`,
   asserting the "ID is the whole number" claim directly.
3. **Parts on examples** — `part1` over the three example passes is 820;
   `part2` over a hand-built `[1,2,3,5,6]` finds 4.
4. **Real answers** — `888` / `522` locked against `inputs/day05.txt`.

## Complexity & benchmarks

Let `n` = number of passes (799), each a constant 10 characters.

- **Parse + decode:** `O(n)` — each pass is a fixed-length fold, so the
  whole file is linear in its size.
- **Part 1:** `O(n)` — one `max_list` scan.
- **Part 2:** `O(n log n)` for `sort/2`, then `O(n)` for the gap scan —
  the sort dominates.

Mean of 1,000 iterations:

| Phase | Time (ms) |
|-------|----------:|
| parse | 1.200 |
| part1 | 0.022 |
| part2 | 0.059 |

The familiar profile: string work in the parse (splitting 799 lines and
folding 10 chars each) dwarfs the arithmetic parts, which are a scan and
a sort over 799 small integers. Part 2 costs ~2.7× part 1 — the `sort`
over `max_list`'s single pass.

## If I were writing this in Rust

```rust
fn seat_id(pass: &str) -> u32 {
    pass.bytes().fold(0, |acc, b| acc * 2 + matches!(b, b'B' | b'R') as u32)
}

fn part1(ids: &[u32]) -> u32 { *ids.iter().max().unwrap() }

fn part2(ids: &[u32]) -> u32 {
    let mut occ = ids.to_vec();
    occ.sort_unstable();
    occ.windows(2).find(|w| w[1] == w[0] + 2).map(|w| w[0] + 1).unwrap()
}
```

- `foldl(add_bit, …)` ↔ `bytes().fold(0, …)` — the same left fold, the
  same Horner recurrence. Rust folds a closure; Prolog folds a predicate.
- `bit/2`'s four-clause table ↔ `matches!(b, b'B' | b'R') as u32` — Rust
  collapses the lookup to a boolean-to-int cast because the alphabet is
  binary; Prolog keeps it a table so it reads as the puzzle's four
  letters and stays reversible. Day 4's `valid_field` clause table
  mapped to a `match` for the same reason — clause heads ≈ `match` arms.
- `gap/2` ↔ `windows(2).find(…)` — the sliding-pair scan is a first-class
  iterator adapter in Rust and a two-element head pattern plus tail
  recursion in Prolog. The cut ↔ `find` short-circuiting at the first
  hit.
- `sort/2` ↔ `sort_unstable()` — both order the IDs; Prolog's also
  dedups, which is free here since IDs are unique.

The Python reference ([python/day05.py](../../python/day05.py)) leans on
`str.translate(maketrans("FBLR", "0101"))` + `int(s, 2)` — a third way to
say "the pass is a base-2 numeral," and arguably the most direct
statement of the whole insight.

## Possible optimization

- **No sort for part 2:** part 1 already needs a full pass; extend it to
  also collect `min` and a bitset (or boolean array) of occupied IDs in
  one scan, then find the lone `false` flanked by `true`s in `[min,
  max]`. Trades `O(n log n)` sort for `O(n)` at the cost of an auxiliary
  array — invisible at n = 799, and the sorted gap reads more like the
  puzzle ("find the hole in the sorted seats").
- **XOR trick for part 2:** the missing ID equals `XOR(min..max) XOR
  XOR(all occupied)` — one pass, no sort, no array, `O(1)` space. Cute
  and worth knowing, but it reads as a magic incantation next to the gap
  scan; declined for clarity, same spirit as Day 3's fused-slopes call.
- **`number_codes` on a translated string:** map the pass to a `"0101…"`
  code list and read it as base 2 — but SWI's `number_codes` is base-10,
  so this needs `0b` term syntax or a manual radix; the explicit `foldl`
  is clearer than the trick.
- All sidebar material at ~1.3 ms total; the shipped shape follows the
  repo's correctness-and-clarity-first policy.
