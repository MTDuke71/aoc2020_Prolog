# Day 03 Function Guide — Toboggan Trajectory

> [Day 01](day01_function_guide.md) was search, [Day 02](day02_function_guide.md)
> was parsing. Day 3 is the first **2-D grid** day, and grids are where a
> language shows its data-representation cards: Prolog has no arrays, so the
> questions are *what do we store* (a list of rows) and *how do we index it*
> (walk, don't subscript). It's also the repo's first **accumulator-pair
> recursion** in `src/` and its first explicit cut (`!`). Grid days get
> harder later (11, 17, 20); this is the gentle version — each row is
> visited at most once, in order.

## The puzzle in one paragraph

The input is a 323×31 map of open squares (`.`) and trees (`#`) whose
pattern **repeats infinitely to the right**. A toboggan starts at the
top-left and descends at a fixed slope — `Right` columns and `Down` rows
per step — until it passes the bottom. **Part 1:** count the trees hit on
slope right 3, down 1. **Part 2:** multiply the tree counts of five given
slopes: (1,1), (3,1), (5,1), (7,1), (1,2). **In algorithm terms:** a strided
linear scan, with the infinite repetition handled by **modular column
arithmetic** — column `c` of the infinite map is column `c mod 31` of the
stored one, so the "many copies" are never materialized.

---

## Reading Prolog: grids without arrays, accumulators, and a first cut

**1. Lists are the sequence type; indexing is walking.** `nth0(I, List, X)`
finds the `I`-th element by walking `I` cons cells — `O(I)`, not `O(1)`.
That sounds alarming for a grid, but this puzzle never *random-accesses*:
the slope visits rows top-to-bottom, so the row list is consumed
structurally (head, then rest), and only the 31-wide row gets an `nth0`
walk. When a later day (11, 17, 20) needs true random access, the guide
sidebar's `arg/3` trick or `library(assoc)` becomes real; today, lists are
exactly right.

**2. The accumulator pair `Acc0 → Acc`.** `slope_trees_/6` carries two
extra arguments: the count *so far* (`Acc0`) and the *final* count
(`Count`), threaded unchanged until the base case unifies them
(`slope_trees_([], _, _, _, Count, Count)`). This is the standard Prolog
idiom for a running total — the same role as a `mut` loop variable in Rust
or a fold's accumulator. Because the recursive call is the clause's last
goal, SWI's **last-call optimization** turns the recursion into a loop:
constant stack, no matter how many rows. Naming convention worth copying:
`Acc0` is "before", `Acc1`/`Count` is "after"; the trailing-underscore
`slope_trees_/6` is the private worker behind the clean `slope_trees/4`
face.

**3. The first explicit cut — and why it's green.** `drop/3`'s first two
clauses end in `!`:

```prolog
drop(0, List, List) :- !.
drop(_, [], []) :- !.
drop(N, [_|Xs], Rest) :- N > 0, ...
```

A **green cut** removes choice points the program logically never needs
(the clauses are mutually exclusive anyway: `N = 0`, list empty, `N > 0`
with a nonempty list); a **red cut** changes what the program can compute.
These are green: called with `N` and the list bound, exactly one clause
applies, and the cut plus the `N > 0` guard just makes that explicit so no
dead choice point survives the call. Same determinism concern as Day 2's
if-then-else — this is the clause-level spelling of it. (Day 1's guide
called `once/1` "the disciplined cut"; here is the raw tool, used in the
tamest possible way.)

**4. Pairs are just terms: `3-1`.** Prolog has no tuple type; the
convention for a pair is the infix `-` functor — `3-1` *is* the term
`-(3, 1)`, and a clause head like `slope_trees_pair(Rows, Right-Down, Count)`
destructures it on arrival. The `Key-Value` shape is blessed by the
standard library (`keysort/2`, `library(pairs)`), which is why it's the
idiomatic pair and not, say, `slope(3, 1)` — though for anything bigger
than a pair, a named record like Day 2's `entry/4` wins.

**5. Partial application again, one arity up.**
`maplist(slope_trees_pair(Rows), Slopes, Counts)` supplies the first
argument now; `maplist/3` supplies each slope pair and receives each count.
Day 2 curried a comparison (`==(Letter)`); today curries a real predicate
over the shared grid — the closure idiom for "map this function, with
context, over a list."

**6. `mod` is the whole "infinite grid".** The statement's arboreal
melodrama reduces to one goal: `Index is Col mod Width`. Working modulo the
row width makes the stored map a cylinder — right edge glued to left — which
is exactly what "the pattern repeats to the right" means. Recognizing
"infinite by repetition = modular index" saves both memory and code on any
wrapping-world puzzle.

---

## The Day 3 code, predicate by predicate

### `parse_input/2`

```prolog
parse_input(Raw, Rows) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(string_chars, Lines, Rows).
```

The standard line-splitter (Days 0–2), finishing with `string_chars/2` per
line: the grid is a **list of rows, each a list of char atoms**. Chars
(not codes, not strings) so cells print readably (`'#'`) and compare with
`==` — the same representation choice, for the same reasons, as Day 2's
passwords.

### `slope_trees/4` and `slope_trees_/6` — the walk

```prolog
slope_trees(Rows, Right, Down, Count) :-
    slope_trees_(Rows, Right, Down, 0, 0, Count).

slope_trees_([], _, _, _, Count, Count).
slope_trees_([Row|Rest], Right, Down, Col, Acc0, Count) :-
    length(Row, Width),
    Index is Col mod Width,
    nth0(Index, Row, Cell),
    (   Cell == '#'
    ->  Acc1 is Acc0 + 1
    ;   Acc1 = Acc0
    ),
    Col1 is Col + Right,
    Skip is Down - 1,
    drop(Skip, Rest, Rest1),
    slope_trees_(Rest1, Right, Down, Col1, Acc1, Count).
```

One step per visited row: wrap the column (`mod`), look up the cell
(`nth0/3`), bump the accumulator if it's a tree (Day 2's if-then-else,
now used for *counting* rather than validity), then advance — column
moves `Right`, and the next visited row is `Down` below, i.e. the head is
consumed and `Down - 1` more rows are dropped. The starting square (row 0,
column 0) is checked like any other; the statement guarantees it's open,
so this costs nothing and keeps the recursion uniform — no special first
step.

### `drop/3`

```prolog
drop(0, List, List) :- !.
drop(_, [], []) :- !.
drop(N, [_|Xs], Rest) :- N > 0, N1 is N - 1, drop(N1, Xs, Rest).
```

Haskell's `drop`, spelled in Prolog (SWI has no library version with this
clamping behavior). The second clause is the load-bearing subtlety: when
fewer than `N` rows remain, it answers `[]` instead of failing, so a
`Down = 2` slope that "steps past the bottom" terminates cleanly at the
base case — precisely the statement's "until you go past the bottom of the
map."

### `slope_trees_pair/3`, `part1/2`, `part2/2`, `solve/3`

```prolog
slope_trees_pair(Rows, Right-Down, Count) :-
    slope_trees(Rows, Right, Down, Count).

part1(Rows, Answer) :-
    slope_trees(Rows, 3, 1, Answer).

part2(Rows, Answer) :-
    Slopes = [1-1, 3-1, 5-1, 7-1, 1-2],
    maplist(slope_trees_pair(Rows), Slopes, Counts),
    foldl([X, Acc0, Acc]>>(Acc is Acc0 * X), Counts, 1, Answer).
```

Part 1 is one slope; part 2 maps the same predicate over five slope pairs
and folds the counts into a product — the identical `foldl`-lambda product
from [Day 1](day01_function_guide.md). Same generalize-then-instantiate
shape as both previous days: write the general engine (`slope_trees/4`),
make each part a one-line instantiation.

---

## Correctness notes

- **The trajectory is exactly the spec.** By induction, after `I` steps the
  walk stands at row `I·Down`, column `I·Right`: the base call starts at
  (0, 0), and each clause application consumes `Down` rows (one head +
  `Down-1` dropped) while adding `Right` to the column.
- **Wrapping is sound.** Column `c` of the infinitely repeated map is, by
  definition of repetition, column `c mod Width` of the stored map — `mod`
  isn't an approximation of the infinite grid, it *is* the infinite grid.
- **Termination.** Every step removes at least one row (the head; `drop/3`
  can only remove more), so the row list strictly shrinks to `[]`.
- **Counting the start square is harmless** — the statement guarantees
  it's open — and steps past the bottom of the map check nothing:
  `drop/3` clamps at `[]` rather than failing.
- Example verified: part 1 hits `7` trees; the five slopes count
  `2, 7, 3, 4, 2`, product `336` — all matching the statement.
- Locked real-input answers: **Part 1 = 148**, **Part 2 = 727923200**,
  cross-validated by [python/day03.py](../../python/day03.py).

## Tests — what's pinned and why

[test/day03_tests.pl](../../test/day03_tests.pl) pins three layers, **9/9
green** (79/79 repo-wide):

1. **Parser** — a 2×3 mini-grid parses to exact char-lists, pinning the
   representation.
2. **Walk semantics on hand-built grids** — `column_wraps` forces a wrap
   (`Right = 2` on a 2-wide grid) and would catch a missing `mod`;
   `down_skips_rows` pins that `Down = 2` visits rows 0 and 2 of three
   (catching an off-by-one in `drop/3`'s `Down - 1`); `empty_grid` pins the
   base case.
3. **Whole-part examples and real answers** — part 1 = 7 on the example;
   `slope_counts_example` pins all five per-slope counts `[2,7,3,4,2]` (not
   just their product, so a compensating pair of errors can't hide);
   part 2 asserted as the product `2*7*3*4*2`; real answers `148` /
   `727923200` locked against `inputs/day03.txt`.

Run: `swipl test/run_tests.pl` from the repo root (runs every day's suite).

## Complexity & benchmarks

Let `n` = 323 rows, `w` = 31 columns.

- **Parse:** `O(n·w)` — every character becomes a char atom.
- **One slope:** the walk visits `n / Down` rows, doing `O(w)` work per
  visit (`length/2` + `nth0/3` on a 31-list): `O(n·w / Down)`.
- **Part 2:** five slopes — four at `Down = 1`, one at `Down = 2`, so about
  `4.5×` a single slope's row visits.

Mean of 1,000 iterations (`swipl bench/main.pl day03` is the single-shot
version):

| Phase | Time (ms) |
|-------|----------:|
| parse | 0.132 |
| part1 | 0.096 |
| part2 | 0.437 |

The part2/part1 ratio is ~4.6 — almost exactly the predicted 4.5 visit
ratio, a small sanity check that the cost model (work ∝ rows visited) is
the true one. Everything is far below Day 2's times: no grammar, just a
single strided pass.

## If I were writing this in Rust

```rust
fn slope_trees(rows: &[&[u8]], right: usize, down: usize) -> usize {
    rows.iter()
        .step_by(down)
        .enumerate()
        .filter(|(i, row)| row[(i * right) % row.len()] == b'#')
        .count()
}

fn part2(rows: &[&[u8]]) -> usize {
    [(1, 1), (3, 1), (5, 1), (7, 1), (1, 2)]
        .iter()
        .map(|&(r, d)| slope_trees(rows, r, d))
        .product()
}
```

- The whole `slope_trees_/6` accumulator recursion collapses into an
  iterator chain: `drop/3` + tail call ↔ `.step_by(down)`, the accumulator
  ↔ `.filter(...).count()`. Prolog's LCO-optimized recursion and Rust's
  iterator are the same loop wearing different clothes.
  ([python/day03.py](../../python/day03.py) sits in between: `rows[::down]`
  slicing plus a generator `sum`.)
- `nth0/3` on a list ↔ `row[i]` on a slice — but the costs differ: `O(i)`
  walk vs `O(1)` subscript. At `w = 31` it's invisible; on a big-grid day
  it's the difference that forces a representation change in Prolog while
  Rust shrugs.
- `Right-Down` pair terms ↔ tuple `(usize, usize)` destructured in the
  closure; `maplist` + `foldl` product ↔ `.map(...).product()`.
- Cells as char atoms compared with `==` ↔ bytes compared with `==` — Rust's
  `b'#'` byte literal is the analogue of Prolog's `0'#` code notation the
  codes-based alternative would use.

## Possible optimization

- **O(1) cell access via `arg/3`:** convert each row (or the whole grid)
  to a compound term — `Row =.. [row|Cells]`, then `arg(I, Row, Cell)` is
  constant-time. The idiomatic Prolog "array." Pointless for one strided
  pass, essential to remember for Day 11/17-style neighbor lookups.
- **All five slopes in one pass:** carry five column accumulators and
  check each row against every active slope — one grid walk instead of
  4.5 row-visits' worth. Real speedup, real readability cost; the five
  independent walks state the problem, the fused walk states an
  optimization.
- **Hoist the width:** all rows are 31 wide, so `length/2` per visit could
  be computed once and threaded through. Saves a 31-step walk per row —
  the kind of micro-move that matters only after the data structure is
  already right.
- At 0.44 ms for part 2, all of it stays in the sidebar per the repo's
  optimization policy.
