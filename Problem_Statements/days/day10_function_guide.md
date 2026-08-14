# Day 10 Function Guide — Adapter Array

> **Written during this repo's Prolog era.** The solution it describes lives
> in the frozen `src/` tree. The maintained solution for this day is
> `python/day10.py`, tested by `python/tests/test_day10.py`. This guide is
> kept for its problem framing and algorithm reasoning, which did not change
> with the language; it will be rewritten Python-first when this day is next
> touched. See the README for what "frozen" means here.

---

> One sorted list, two very different questions. **Part 1 is a
> difference histogram**: sort the ratings, cap the ends with the outlet
> and the device, take adjacent differences, and multiply how many are
> `1` by how many are `3`. The whole puzzle collapses because *every
> adapter must be used* — that single constraint makes the chain unique,
> so there is nothing to search. **Part 2 removes that constraint and
> asks for a count**: how many distinct sub-chains still connect outlet
> to device? That is **path counting in a DAG**, and because the nodes
> are already in topological order (ascending joltage), one
> left-to-right sweep with running totals does it in linear time — the
> classic `ways(v) = ways(v−1) + ways(v−2) + ways(v−3)` recurrence, a
> **tribonacci** in disguise. The naive reading of Part 2 ("enumerate the
> arrangements") is a 97-trillion-item enumeration; the DP is 108
> additions. The sorted-gap scan is the same move as
> [Day 5](day05_function_guide.md)'s hunt for the missing seat, and the
> count-don't-enumerate discipline is [Day 7](day07_function_guide.md)'s
> weighted bag count seen from a new angle.

## The puzzle in one paragraph

The input is 106 adapter ratings, one per line, unsorted. An adapter
rated `j` accepts any input in `j−3 … j−1`. The wall outlet is an
effective `0`; the device's built-in adapter is `max + 3`. **Part 1:**
use *all* the adapters in one chain and report
`(#gaps of 1) × (#gaps of 3)` across the whole chain including both ends
(examples → `7 × 5 = 35` and `22 × 10 = 220`). **Part 2:** drop the
"use all" rule and count the distinct chains from outlet to device
(examples → `8` and `19208`).

For the real input the answers are **2482** and **96,717,311,574,016** —
about 97 trillion arrangements, which is the number that tells you Part 2
must be counted rather than listed.

---

## Representation: a sorted list with two sentinels

`full_chain/2` is the only data-modeling decision in the day, and both
parts run on its output:

```prolog
full_chain(Ratings, Chain) :-
    msort(Ratings, Sorted),
    last(Sorted, Highest),
    Device is Highest + 3,
    append([0|Sorted], [Device], Chain).
```

Three things are happening, each load-bearing:

- **Sorting.** Adapters only ever step *up*, by 1–3 jolts. So any legal
  chain visits its adapters in ascending order, and sorting puts the
  input into the only order that can matter. After this, "which adapters
  can follow this one" is answered by looking a couple of cells to the
  right — no graph structure needs to be built at all.
- **The outlet sentinel `0`.** Prepending it means the first real
  adapter's gap is computed by the same rule as every other gap. Without
  it, Part 1 needs a special case for "the step from the wall," and
  Part 2 needs a special case for "the chain's first link."
- **The device sentinel `max + 3`.** The same trick at the other end: the
  final always-3 step becomes an ordinary gap, and the device becomes an
  ordinary node whose path count *is* the Part 2 answer.

Sentinels are the recurring theme here. The reason the shipped code has
no boundary conditions anywhere is that both boundaries were turned into
data.

**Why `msort/2` and not `sort/2`.** SWI's `sort/2` sorts *and removes
duplicates*; `msort/2` sorts and keeps them. The real input has no
repeated rating, so either would work — but `sort/2` would be quietly
asserting uniqueness. If a duplicate ever appeared, `msort` surfaces it
honestly as a 0-jolt gap (visible in Part 1's histogram) instead of
silently deleting an adapter the puzzle says must be used. Pick the
predicate that doesn't hide the anomaly. (Compare
[Day 1](day01_function_guide.md), which reaches for `msort/2` for the
same "order matters, multiplicity matters" reason.)

---

## Reading Prolog: the five forms this day turns on

**1. Accumulator recursion, and why it beats a two-element head.** The
obvious way to write "adjacent differences" is to match two elements at
once:

```prolog
differences([_], []).                                   % <- the tempting version
differences([Lower, Upper|Rest], [Diff|Diffs]) :- ...
```

That is *correct* but **nondeterministic**, and the reason is worth
internalizing. SWI indexes clauses on the **principal functor of the
first argument**. Both `[_]` and `[Lower, Upper|Rest]` have the same
principal functor — `'[|]'/2`, the cons cell — so indexing cannot tell
them apart, and every recursive step leaves a choice point behind. The
suite reports `Test succeeded with choicepoint`, and 107 dead choice
points sit on the stack until the query finishes.

The fix is to carry the previous link in an **accumulator**, so the
recursive clauses split on `[]` versus `[_|_]` — which indexing *can*
discriminate:

```prolog
differences([Lower|Rest], Diffs) :-
    differences_from(Rest, Lower, Diffs).

differences_from([], _Lower, []).
differences_from([Upper|Rest], Lower, [Diff|Diffs]) :-
    Diff is Upper - Lower,
    differences_from(Rest, Upper, Diffs).
```

Same answers, zero choice points, no cut required. This is the general
recipe: *when two clauses would need the same functor in the first
argument, move the distinguishing information into an accumulator.* It
is the cheapest determinism win in the language, and it shows up
constantly once you start looking for it.

**2. `include/3` as the counting idiom.** Prolog has no `count_if`, so
"how many of these are 1?" is filter-then-measure:

```prolog
include(=(1), Diffs, OneSteps),
length(OneSteps, Ones)
```

`=(1)` is a **partial application**: `include/3` calls it with one extra
argument, so each element `E` is tested by `=(1, E)` — plain unification
against the integer `1`. That works because the differences are already
evaluated integers; if they were unevaluated arithmetic terms you would
need `[X]>>(X =:= 1)` instead. (Contrast [Day 4](day04_function_guide.md),
where the filter was a named predicate, and
[Day 2](day02_function_guide.md), where `include/3` counted valid
passwords.)

**3. `foldl/4` as the sweep, with a compound accumulator.** Part 2's
entire loop is one `foldl`:

```prolog
foldl(place_adapter, Rest, [Outlet-1], Recent)
```

`foldl(:Goal, +List, +V0, -V)` threads a state value through the list,
calling `Goal(Element, StateIn, StateOut)` at each step. The state here
isn't a number but a **small list of `Value-Ways` pairs** — the DP's
sliding frontier. Using a structured accumulator is what lets an
imperative-looking dynamic program stay a pure fold: no `assert`, no
mutable array, no hand-written recursion.

**4. Pair terms and `pairs_values/2`.** `Value-Ways` is just the term
`-(Value, Ways)`; the infix `-` is Prolog's conventional pair
constructor (the same one `keysort/2`, the `assoc` library, and
[Day 4](day04_function_guide.md)'s `Key-Value` passport fields use).
`pairs_values/2` from `library(pairs)` strips a list of pairs down to its
second components, which turns "sum the reachable path counts" into
`pairs_values` + `sum_list`.

**5. Cut, then unify — the repo's steadfast style.**

```prolog
recent_three([A, B, C|_], Recent) :-
    !,
    Recent = [A, B, C].
recent_three(Pairs, Recent) :-
    Recent = Pairs.
```

The output `Recent` is deliberately *not* bound in the head. Committing
first with `!` and unifying the output afterwards keeps the predicate
**steadfast**: calling it with an already-bound `Recent` that happens not
to match fails cleanly, instead of cutting away the second clause after a
partial head unification has already succeeded. House style since
[Day 3](day03_function_guide.md).

---

## The Day 10 code, predicate by predicate

### `parse_input/2`

```prolog
parse_input(Raw, Ratings) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(number_string, Ratings, Lines).
```

The repo's standard opener, unchanged since [Day 0](day00_function_guide.md):
split on newlines, trim `" \t\r"` (the `\r` is what survives Windows
CRLF), drop the trailing empty line, read each remaining line as an
integer. Note `maplist(number_string, Ratings, Lines)` runs
"backwards" — `number_string/2` is bidirectional, and here the *string*
side is bound and the number side is produced.

Parsing deliberately does **not** sort. The parsed value is the input as
given; `full_chain/2` owns the canonical form. That keeps the parser
honest (the `parse_ratings` test can pin the original order) and puts the
one interesting transformation in a predicate with a name.

### `full_chain/2`

Covered above. Worth noting that `last/2` is `O(N)` — a full walk of the
sorted list — but it runs once, and reaching for the last element of an
ascending list is exactly the "no random access" tax a cons list charges.
`append([0|Sorted], [Device], Chain)` then builds the capped chain in one
pass.

### Part 1: `chain_part1/2`, `differences/2`, `difference_counts/3`

```prolog
chain_part1(Chain, Product) :-
    differences(Chain, Diffs),
    difference_counts(Diffs, Ones, Threes),
    Product is Ones * Threes.

difference_counts(Diffs, Ones, Threes) :-
    include(=(1), Diffs, OneSteps),
    include(=(3), Diffs, ThreeSteps),
    length(OneSteps, Ones),
    length(ThreeSteps, Threes).
```

Three lines of pipeline: gaps, histogram, product. `chain_part1/2` exists
separately from `part1/2` so `solve/3` can feed it a chain that was built
once (see below).

Only 1s and 3s are counted because that is what the puzzle asks for;
nothing in the code assumes 2-jolt gaps are absent. On the real input
there are none — the gap histogram is exactly **73 ones and 34 threes**,
and `73 × 34 = 2482`. That "1s and 3s only" shape is not an accident of
this one input; it is what makes Part 2's structure so clean (see the
optimization sidebar).

### Part 2: `arrangements/2` and friends

```prolog
arrangements([Outlet|Rest], Count) :-
    foldl(place_adapter, Rest, [Outlet-1], Recent),
    Recent = [_Device-Count|_].

place_adapter(Value, Recent0, Recent) :-
    reachable_ways(Recent0, Value, Ways),
    recent_three([Value-Ways|Recent0], Recent).

reachable_ways(Recent, Value, Ways) :-
    include(within_reach(Value), Recent, Reachable),
    pairs_values(Reachable, Counts),
    sum_list(Counts, Ways).

within_reach(Value, Lower-_Ways) :-
    Value - Lower =< 3.
```

Read it as a dynamic program with a three-cell window:

- **The quantity being computed.** `Ways` for a link `v` is *the number
  of distinct chains that start at the outlet and end at `v`*. The
  outlet itself seeds the fold with `[0-1]`: one way to be at the wall,
  namely do nothing.
- **The recurrence.** A chain ending at `v` is some chain ending at an
  admissible predecessor `u` (with `v − u ≤ 3`), extended by one step to
  `v`. Distinct predecessors give distinct chains, and every chain ending
  at `v` has exactly one predecessor, so the counts **partition**:
  `ways(v) = Σ ways(u)` over reachable `u`. That is `reachable_ways/3`
  verbatim — filter the frontier by `within_reach`, take the counts, sum.
- **The state.** `Recent` holds up to three `Value-Ways` pairs,
  **newest first**. `place_adapter/3` computes the new link's count,
  conses it on, and `recent_three/2` trims the tail off.
- **The answer.** After the fold the newest pair is the device, and its
  count is the Part 2 answer — hence `Recent = [_Device-Count|_]`.

Three cells is enough, and the argument is short: the chain is strictly
ascending over integers, so consecutive links differ by **at least 1
jolt**. Going back four links therefore drops at least 4 jolts, which is
already out of reach. Keeping three makes each step `O(1)` and the whole
sweep linear. (Keeping the entire prefix would also be *correct* —
`within_reach` filters it anyway — but each step would rescan everything
seen so far, turning a linear sweep into `O(N²)`.)

**On the size of the numbers.** The running counts reach ~9.7 × 10¹³,
past 2⁴⁶. SWI integers are arbitrary precision (GMP-backed), so this
requires no `i64`/`u64` thought at all — the same code would be fine if
the answer had 400 digits. This is one of the places where Prolog and
Python quietly agree and C, Rust, and Haskell's `Int` all make you choose
a width.

### `part1/2`, `part2/2`, `solve/3`

```prolog
part1(Ratings, Product) :- full_chain(Ratings, Chain), chain_part1(Chain, Product).
part2(Ratings, Count)   :- full_chain(Ratings, Chain), arrangements(Chain, Count).

solve(Raw, Product, Count) :-
    parse_input(Raw, Ratings),
    full_chain(Ratings, Chain),
    chain_part1(Chain, Product),
    arrangements(Chain, Count).
```

The same split as [Day 9](day09_function_guide.md): the two public parts
are **self-contained** (each builds its own chain, so each can be tested
and benchmarked in isolation), while `solve/3` is the combined path that
builds the chain once and hands it to both. Here the saving is small —
one sort and one `append` — but the shape is the repo's convention and it
is the right habit for days where the shared work is expensive.

---

## Correctness notes

- **Part 1's chain is the only one there is.** The puzzle says use every
  adapter, and steps are strictly upward. Take any ordering that uses all
  of them; if it ever placed a larger rating before a smaller one, the
  later smaller adapter could not be reached — its input would have to be
  *above* its own rating. So ascending order is the unique candidate, and
  sorting produces it. Part 1 needs no search because the search space
  has exactly one element. (This is also why a legal input can have no
  gap larger than 3 in sorted order: if it did, no chain using all the
  adapters would exist at all.)
- **The histogram covers exactly the right steps.** With both sentinels
  in place the chain has `N + 2` links and `differences/2` yields `N + 1`
  gaps — outlet→first, each adapter→next, and last→device. That is
  precisely the set the puzzle says to count.
- **Part 2 counts each arrangement exactly once.** The recurrence
  partitions chains ending at `v` by their immediate predecessor. Two
  chains with different predecessors are different chains; two chains
  with the same predecessor are counted by that predecessor's own count,
  which is exact by induction. The base case `ways(outlet) = 1` is the
  empty chain. So nothing is double-counted and nothing is missed.
- **The sweep order is valid.** A DP over a DAG is correct only if every
  node's predecessors are finalized before it is visited. Here the chain
  is ascending and all edges point upward, so ascending order *is* a
  topological order — the fold reaches each link only after every link it
  could plug into has its final count. This is the same "process in
  dependency order" obligation [Day 7](day07_function_guide.md) met by
  recursing to the leaves first; sorting hands it to us for free.
- **The three-link window loses nothing.** Consecutive links differ by
  ≥ 1 jolt, so the fourth-most-recent link is ≥ 4 jolts below the current
  one and cannot be a predecessor. `within_reach/2` re-checks the three
  that are kept, so the window is an optimization layered on an already
  correct filter, never a substitute for it.
- **Determinism.** `differences_from/3` splits `[]` vs `[_|_]` for clean
  first-argument indexing; `recent_three/2` commits with a cut and unifies
  after it; `foldl/4`, `include/3`, `msort/2`, and `sum_list/2` are all
  deterministic. The suite runs with **no "succeeded with choicepoint"
  warnings** — the repo's determinism bar since
  [Day 5](day05_function_guide.md). Getting there took one rewrite; see
  form 1 above.
- Locked real-input answers: **Part 1 = 2482**, **Part 2 =
  96717311574016**, cross-validated by
  [python/day10.py](../../python/day10.py), which computes Part 2 with an
  independent implementation — a `dict` keyed by joltage, probing `v−1`,
  `v−2`, `v−3` — rather than a port of the window fold.

## Tests — what's pinned and why

[test/day10_tests.pl](../../test/day10_tests.pl) pins five layers, **11/11
green** (run `swipl test/run_tests.pl` from the repo root, or
`swipl -g "consult('test/day10_tests.pl'), run_tests(day10), halt"` for
this day alone):

1. **Parser** — the 11-line example parses to the exact list *in input
   order*, locking that parsing does not sort.
2. **The chain construction** — `full_chain/2` on the small example is
   pinned to `[0, 1, 4, 5, 6, 7, 10, 11, 12, 15, 16, 19, 22]`, which locks
   all three of its jobs at once: sorted, outlet-capped, device-capped.
3. **The intermediates** — the gap list and the `7-5` count pair are
   asserted directly, not just the product. If the histogram ever breaks,
   the failure names the actual step instead of a wrong final number.
4. **Both parts on both examples** — `35`/`8` and `220`/`19208`. The
   larger example is the one that matters for Part 2: at 19208 it is big
   enough that an off-by-one in the window or a double-count shows up,
   while the small example's `8` is small enough to check by hand against
   the statement's listing.
5. **Edge case and real answers** — a one-adapter bag (`[3]` → chain
   `0, 3, 6`, product `0 × 2 = 0`, exactly one arrangement) exercises the
   degenerate path where the window never fills to three; then `2482` /
   `96717311574016` are locked against `inputs/day10.txt`.

## Complexity & benchmarks

Let `N` be the number of adapters (106).

- **Parse:** `O(N)`.
- **`full_chain/2`:** `O(N log N)` for the sort, plus `O(N)` for `last/2`
  and `append/3`. **This is the asymptotic cost of the entire day** —
  both parts are linear once the chain exists.
- **Part 1:** `O(N)` — one differencing pass, two filter passes, two
  length walks.
- **Part 2:** `O(N)` — one `foldl` step per link, each doing bounded work
  over a 3-element window. Arithmetic is on big integers, so strictly the
  additions cost `O(digits)`, a constant at this size.

Inference counts are exact and reproducible (`swipl bench/main.pl day10`
prints the same numbers every run); times are representative single runs:

| Phase | Inferences | Time (ms) |
|-------|-----------:|----------:|
| parse | 1,591 | 0.54 |
| part1 | 1,460 | 0.12 |
| part2 | 3,726 | 0.52 |

The cheapest day in the repo so far by a wide margin — for comparison,
[Day 9](day09_function_guide.md)'s Part 2 alone is ~1.03M inferences and
~26 ms. Part 2 costs ~2.5× Part 1 here because each of the 107 fold steps
builds a closure for `include/3` and walks a small pair list, where
Part 1's passes are flat integer comparisons. Warm — after every
predicate has been called once, so clause indexing is already built —
`solve/3` runs ~3,940 inferences against ~4,155 for `parse` + `part1` +
`part2` separately, the ~220 saved being the second `full_chain/2` build.

## If I were writing this in Rust

```rust
fn full_chain(ratings: &[u64]) -> Vec<u64> {
    let mut chain = Vec::with_capacity(ratings.len() + 2);
    chain.push(0);
    chain.extend_from_slice(ratings);
    chain[1..].sort_unstable();
    chain.push(chain[chain.len() - 1] + 3);
    chain
}

fn part1(chain: &[u64]) -> usize {
    let (ones, threes) = chain.windows(2).fold((0, 0), |(o, t), w| match w[1] - w[0] {
        1 => (o + 1, t),
        3 => (o, t + 1),
        _ => (o, t),
    });
    ones * threes
}

fn part2(chain: &[u64]) -> u64 {
    // ways[i] = chains from the outlet ending at chain[i]. Ascending order
    // is a topological order, so one forward pass suffices.
    let mut ways = vec![0u64; chain.len()];
    ways[0] = 1;
    for i in 1..chain.len() {
        ways[i] = (i.saturating_sub(3)..i)
            .filter(|&j| chain[i] - chain[j] <= 3)
            .map(|j| ways[j])
            .sum();
    }
    ways[chain.len() - 1]
}
```

- **`differences/2` ↔ `chain.windows(2)`.** Rust's slice windows give
  adjacent pairs directly, and one `fold` counts both buckets in a single
  pass instead of Prolog's two `include/3` filters. The Prolog version
  materializes the gap list; Rust fuses it away. At `N = 106` neither
  matters, but it is the honest difference between a list-building
  language and an iterator-fusing one.
- **The three-pair window ↔ `i.saturating_sub(3)..i`.** Prolog carries
  the frontier explicitly because a cons list has no `O(1)` random
  access; Rust just indexes backwards into the `ways` array. Same
  recurrence, same bounded-by-3 argument, no accumulator threading. This
  is the clearest place in the day where random access changes the
  *shape* of the code and not merely its speed.
- **`foldl` with a compound accumulator ↔ a `for` loop over a `Vec`.**
  The functional fold and the imperative loop are the same computation;
  Prolog needs the fold because it has no mutable array, and gets purity
  and easy testability in exchange.
- **The one thing Rust makes you think about: width.** `u64` holds
  9.7 × 10¹³ comfortably, but you have to *decide* that, and a
  larger-input variant could overflow silently in release mode. SWI's
  arbitrary-precision integers make the question disappear.

The Python reference ([python/day10.py](../../python/day10.py)) sits
between the two — a `dict` keyed by joltage, probing `value − 1`,
`value − 2`, `value − 3` with `.get(_, 0)` — and re-confirms `2482` /
`96717311574016`.

## Possible optimization

- **Part 2 in closed form, by run length.** The real input's gaps are
  *only* 1s and 3s. A 3-gap is forced — no arrangement can skip across
  it — so the chain decomposes into independent **runs of consecutive
  1-gaps**, and the total is the product of each run's arrangement count.
  A run of `k` consecutive 1-gaps admits `T(k)` arrangements, where
  `T(1)=1, T(2)=2, T(3)=4, T(4)=7`: the tribonacci numbers (each term is
  the sum of the previous three — Fibonacci, one term wider, which is no
  coincidence given the recurrence above), since within a run any subset of
  interior links may be dropped so long as no three in a row go. This input has runs of length 1 (×2), 2 (×6), 3 (×9) and 4 (×8),
  giving `1² · 2⁶ · 4⁹ · 7⁸ = 96,717,311,574,016` — verified identical to
  the DP's answer. It is a lovely reduction and about as fast as
  arithmetic gets, but it is **not shipped**: it silently assumes no
  2-jolt gaps ever appear, which the puzzle never promises. The DP makes
  no such assumption and is already sub-millisecond. Correctness and
  clarity first, per the repo policy — the closed form belongs in the
  guide, which is where it is.
- **Fuse Part 1's two filters into one pass.** `difference_counts/3` walks
  the gap list twice. A single `foldl` carrying an `Ones-Threes` pair
  would halve it. At 107 gaps this is beneath measurement, and two named
  `include/3` calls read better than one fold with a compound
  accumulator, so the shipped code keeps the pair of filters.
- **Skip the intermediate gap list.** `differences/2` builds a 107-element
  list that is immediately consumed; `chain_part1/2` could count gaps
  during the walk and never materialize it. Rejected for the same reason:
  the intermediate list is directly *testable* (the
  `differences_of_small_chain` test pins it), and that is worth more than
  107 cons cells.
- Sidebar material only; the shipped shape follows the repo's
  correctness-and-clarity-first policy.
