# Tutorial Day 9: Sorting, Grouping, and Counting

## Why this day matters
A huge fraction of AoC parts are some flavor of **"transform the input, then
aggregate"**: count how many things match, find the most/least common, group equal
items and tally each group, take the top-N. The engine under almost all of those is
**sorting** — once like items sit next to each other, grouping and counting collapse
into a single linear pass. Prolog ships two sorts that look interchangeable but
differ in exactly the way that bites beginners: `sort/2` **throws duplicates away**,
`msort/2` **keeps them**. Pick wrong and your count is silently off by the number of
repeats — no error, just a wrong answer. Today nails that distinction and then builds
the canonical aggregate on top of it: **run-length encoding** (sort, then pack equal
neighbors into `(Value, Count)` pairs), which is the histogram/tally pattern you'll
reach for again and again.

## Focus Topics
- **`sort/2`** — ascending **standard order of terms**, **duplicates removed**
- **`msort/2`** — same order, **duplicates kept** (the counting-safe sort)
- **Standard order of terms** — how Prolog orders *any* two terms, not just numbers
- **Grouping equal neighbors** after sorting — the linear "pack runs" pass
- **Run-length encoding** as the histogram/frequency primitive: `[(Value,Count),…]`
- **`==/2` vs `=/2`** inside the grouping loop — identity test, *not* unification
- The wider sort family for later: `sort/4`, `predsort/3`, `aggregate_all/3`

## Learning Goals
- State precisely what `sort/2` and `msort/2` each do, and predict their outputs.
- Build a histogram-like operation (run-length encoding) end to end.
- Explain *why* sorting first makes grouping a single linear pass.
- Say why the grouping loop uses `==/2`, not `=/2`.

## Files
- `day9.pl`: `dedup_sorted/2` and `stable_sorted/2` (the two sorts, side by side)
  plus `run_lengths/2` (the sort-then-group aggregate) with its helpers
  `pack_runs/2` and `take_same/5`.
- `day9_tests.pl`: `plunit` tests pinning the `sort` vs `msort` difference and a
  run-length-encoding result.

```prolog
:- module(day9, [dedup_sorted/2, stable_sorted/2, run_lengths/2]).
```

## Run the tests
From repo root:

```bash
swipl -q -s tutorial/day9/day9_tests.pl
```

## Start the REPL

```bash
swipl
```
```prolog
?- ['tutorial/day9/day9.pl'].
```

## The whole program

```prolog
dedup_sorted(List, Sorted) :- sort(List, Sorted).
stable_sorted(List, Sorted) :- msort(List, Sorted).

run_lengths(List, Runs) :-
    msort(List, Sorted),
    pack_runs(Sorted, Runs).

pack_runs([], []).
pack_runs([X|Xs], [(X,N)|Runs]) :-
    take_same(X, Xs, 1, N, Rest),
    pack_runs(Rest, Runs).

take_same(_, [], N, N, []).
take_same(X, [Y|Ys], Acc, N, Rest) :-
    ( X == Y ->
        Acc1 is Acc + 1,
        take_same(X, Ys, Acc1, N, Rest)
    ;
        N = Acc,
        Rest = [Y|Ys]
    ).
```

Three exported predicates. The first two are one-liners that exist purely to put the
two sorts next to each other; the real lesson of *grouping* lives in `run_lengths/2`.

## The one distinction to burn in: `sort/2` vs `msort/2`

Both sort into ascending **standard order of terms**. They differ in **one thing**:
what happens to equal elements.

| | `sort/2` (`dedup_sorted`) | `msort/2` (`stable_sorted`) |
|---|---|---|
| **Order** | ascending standard order | ascending standard order |
| **Duplicates** | **removed** (one copy of each) | **kept** (every copy survives) |
| **Length** | ≤ input length | **always** = input length |
| **Use when** | you want a *set* of distinct values | you want to **count**, group, or preserve multiplicity |

```prolog
?- sort([3,1,3,2], S).      % S = [1,2,3]       -- the 3 collapses to one
?- msort([3,1,3,2], S).     % S = [1,2,3,3]     -- both 3s kept
```

> **Rule of thumb:** the moment you care *how many*, you want `msort/2` (or a real
> frequency map). Reaching for `sort/2` when counting is the classic off-by-the-
> duplicates bug — it deletes exactly the information you were about to tally.

"Equal" here means equal under **standard order of terms** (`==/2`), the total order
Prolog defines over *every* term, not just numbers:

```text
Var  <  Number  <  Atom  <  String  <  Compound
```

So `sort/2` works on atoms, strings, and compound terms too — `sort([c,a,b,a], S)`
gives `S = [a,b,c]`. This is why the tally pattern below is generic: it groups
*whatever* the list holds.

> **Naming note:** the predicate is called `stable_sorted` because `msort/2` is a
> *stable* sort (equal elements keep their input order). For terms that are `==`-equal
> that's invisible — they're indistinguishable — but the property matters with
> `sort/4` when you sort on a *key* and want ties to stay in original order.

## Building the histogram: `run_lengths/2`

```prolog
run_lengths(List, Runs) :-
    msort(List, Sorted),        % 1. bring equal items together
    pack_runs(Sorted, Runs).    % 2. fold each run into (Value, Count)
```

The whole strategy is two steps. **Step 1** sorts so that every group of equal
elements becomes a *contiguous run*. **Step 2** walks that sorted list once, packing
each run into a `(Value, Count)` pair. This is **run-length encoding**, and because
the input is sorted it's also a **frequency table / histogram**: every distinct value
appears exactly once, paired with how many times it occurred.

Why sort first? Without it, counting "how many `a`s" means scanning the *entire* list
for every distinct value — O(n) per value, O(n·k) total. After sorting, all the `a`s
are adjacent, so one left-to-right sweep tallies *every* group in O(n). Sorting costs
O(n log n); the grouping pass is O(n). **Sort-then-group** is the standard way to turn
a quadratic tally into an n-log-n one.

### `pack_runs/2` — one run per recursion

```prolog
pack_runs([], []).
pack_runs([X|Xs], [(X,N)|Runs]) :-
    take_same(X, Xs, 1, N, Rest),
    pack_runs(Rest, Runs).
```

`pack_runs/2` peels the head `X`, asks `take_same/5` to consume the rest of *X's run*
and report its length `N` plus whatever's left (`Rest`), emits `(X, N)`, then recurses
on `Rest`. Each recursive call starts at the next *distinct* value, so the output has
exactly one pair per distinct element. The base case maps the empty list to the empty
result.

### `take_same/5` — count one run, then stop

```prolog
take_same(_, [], N, N, []).                 % list exhausted: final count = accumulator
take_same(X, [Y|Ys], Acc, N, Rest) :-
    ( X == Y ->                             % same value? (identity, not unification)
        Acc1 is Acc + 1,
        take_same(X, Ys, Acc1, N, Rest)     % keep counting this run
    ;
        N = Acc,                            % different value: freeze the count...
        Rest = [Y|Ys]                       % ...and hand the rest back unconsumed
    ).
```

This is an **accumulator** loop (Day 5): `Acc` carries the running count, starting at
`1` because the caller already saw one copy (the `X` it peeled off). The `( Cond ->
Then ; Else )` is an **if-then-else** (Day 3): while the next element matches, bump the
accumulator and recurse; on the first mismatch, unify `N` with the accumulated count
and return the remaining list — including the mismatching `Y` — so `pack_runs` can
start the next run with it. The two clauses cover "ran off the end mid-run" and "hit a
different value."

> **Why `==/2`, not `=/2`?** `X == Y` tests whether the two terms are *already
> identical* — it never binds anything. `X = Y` would *unify*, succeeding (and
> instantiating a variable) when the elements merely *could* be made equal. For
> grouping concrete data that's a real bug: `=` would happily fuse an unbound variable
> with the next element. Grouping wants "are these the same value?" → `==`. (This pairs
> with the `=:=` / `#=` / `=` distinction from Days 1 and 7: pick the equality that
> matches your intent.)

## Trace: `run_lengths([b,a,b,a,a], Runs)`

```text
input            [b, a, b, a, a]
msort         -> [a, a, a, b, b]          % equal items now contiguous
pack_runs:
  X=a, take_same a [a,a,b,b] 1  -> N=3, Rest=[b,b]     emit (a,3)
  X=b, take_same b [b]       1  -> N=2, Rest=[]        emit (b,2)
  []  -> []
result        -> [(a,3), (b,2)]
```

Note the output is ordered by **value** (`a` before `b`), not by frequency — a direct
consequence of sorting first. The two `b`s that started at the front and the three
`a`s scattered through the input each collapse to a single tallied pair. That
`[(a,3),(b,2)]` is exactly what the second test locks.

## The Tests, One by One

```prolog
:- begin_tests(day9).
:- use_module('./day9.pl').

test(sort_vs_msort) :-
    dedup_sorted([3,1,3,2], A),
    stable_sorted([3,1,3,2], B),
    assertion(A == [1,2,3]),
    assertion(B == [1,2,3,3]).

test(run_lengths) :-
    run_lengths([b,a,b,a,a], Runs),
    assertion(Runs == [(a,3),(b,2)]).

:- end_tests(day9).
```

| Test | What it pins down |
|---|---|
| `sort_vs_msort` | The whole point of the day in one test: same input, `sort/2` yields `[1,2,3]` (duplicate `3` gone), `msort/2` yields `[1,2,3,3]` (both `3`s kept). If you ever swap the two predicates, this test fails loudly. |
| `run_lengths` | The full sort-then-group pipeline produces the correct tally `[(a,3),(b,2)]` — right values, right counts, value-sorted order. |

Both assertions use `==/2` — **structural identity**, the right check when comparing
fully-formed result terms (you want "is the list exactly this?", not unification).

## REPL Drills

```prolog
?- sort([3,1,3,2], S).                 % S = [1,2,3]        -- dedups
?- msort([3,1,3,2], S).                % S = [1,2,3,3]      -- keeps dups
?- sort([c,a,b,a], S).                 % S = [a,b,c]        -- atoms sort too
?- run_lengths([b,a,b,a,a], R).        % R = [(a,3),(b,2)]
?- run_lengths([], R).                 % R = []             -- empty edge case
?- msort([3,1,2], X), last(X, Max).    % Max = 3            -- max via sort
?- sort(0, @>=, [3,1,3,2], S).         % S = [3,3,2,1]      -- sort/4: descending, keep dups
?- aggregate_all(count, member(_,[a,b,c]), N).  % N = 3     -- count without sorting
?- aggregate_all(max(X), member(X,[3,1,2]), M). % M = 3     -- max without sorting
```

The last three drills preview the **wider sort/aggregate family** (next section): once
you understand `sort/2` vs `msort/2`, `sort/4` and `aggregate_all/3` are just more
control over the same "order/group/reduce" idea.

## The sort & aggregate family (reference)

| Predicate | Order | Dups | Notes |
|---|---|---|---|
| `sort/2` | ascending | **removed** | the "set" sort |
| `msort/2` | ascending | **kept** | the "count" sort — stable |
| `sort(Key, Order, In, Out)` (`sort/4`) | `@<`, `@=<`, `@>`, `@>=` | kept iff `=<`/`>=` | sort on a key position; stable; the Swiss-army sort |
| `predsort(Pred, In, Out)` | your `Pred` | **removed when `Pred` says `=`** | custom comparison; drops "equal" elements |
| `keysort/2` | by key | kept | stable sort of `Key-Value` pairs by `Key` |
| `aggregate_all/3` | — | — | `count`/`sum`/`max`/`min`/`bag`/`set` in one call, no manual loop |

For real AoC tallies you'll often skip the hand-rolled `run_lengths` entirely and use
`aggregate_all(count, Goal, N)` for a count, or a `library(assoc)` frequency map
(Day 8) when you need O(log n) updates. `run_lengths/2` is here because writing the
group-and-count pass *by hand once* makes all the library shortcuts legible.

## Verification (maps to the checklist)
- **Dedup vs keep:** `sort([3,1,3,2],[1,2,3])` and `msort([3,1,3,2],[1,2,3,3])` —
  the duplicate `3` is the entire difference.
- **Length invariant:** `msort` output length always equals input length; `sort`
  output length equals the number of *distinct* elements.
- **Tally correctness:** `run_lengths([b,a,b,a,a], [(a,3),(b,2)])` — counts sum to the
  input length (3 + 2 = 5) and the order is value-sorted.
- **Empty edge case:** `run_lengths([], [])` — the base cases handle an empty list.

## Common Gotchas
- **`sort/2` when you meant `msort/2`.** Counting after `sort/2` is wrong by exactly
  the number of duplicates — and there's **no error**, just a quietly low tally. If the
  question is "how many," reach for `msort/2` or a frequency map, never `sort/2`.
- **Expecting frequency order.** `run_lengths` sorts by **value**, so the result is
  value-ordered, not most-common-first. To get "top by count," sort the *pairs* on
  their second element afterward (e.g. `sort(2, @>=, Runs, ByCount)`).
- **`=/2` instead of `==/2` in the grouping test.** `X = Y` unifies (can bind a
  variable and wrongly merge elements); `X == Y` asks "already identical?". Grouping
  needs `==`. Using `=` is a subtle, data-dependent bug.
- **Forgetting to sort before grouping.** `pack_runs` only groups *adjacent* equals.
  On unsorted input it produces a *run-length encoding of the sequence*, not a
  histogram — `[a,b,a]` would give `[(a,1),(b,1),(a,1)]`, with `a` appearing twice.
  The `msort/2` in `run_lengths/2` is what guarantees one pair per distinct value.
- **`sort/4` argument order.** It's `sort(KeyIndex, Order, List, Sorted)` — `0` means
  "the whole term as key," and the *order* atom (`@<`, `@>=`, …) decides ascending vs
  descending *and* whether duplicates survive (`@=<`/`@>=` keep them, `@<`/`@>` drop
  them). Easy to flip and get a deduped result you didn't want.

## The AoC Payoff: tally, then read off the answer

A recurring AoC shape is "count occurrences, then answer a question about the counts":
most common byte, number of distinct values, how many groups have size ≥ k, the
difference between the largest and smallest tally. All of them are **build a histogram,
then reduce it**:

```prolog
% Most frequent element of Xs:
most_common(Xs, Value) :-
    run_lengths(Xs, Runs),                 % [(V,Count), ...]  sorted by value
    sort(2, @>=, Runs, [(Value,_)|_]).     % re-sort by Count desc; take the head

% Number of distinct elements:
distinct_count(Xs, N) :- sort(Xs, S), length(S, N).   % sort/2 dedups; count survivors
```

`distinct_count` is the cleanest demonstration of why `sort/2` exists: dedup *is* the
operation, and `length/2` of the result is the answer. `most_common` shows the
two-stage sort — group by value, then re-sort the *groups* by count — which is the
template for every "max/min by frequency" question. The judgment call is the same one
from Day 8: a hand-rolled `run_lengths` is fine for a one-shot tally over a list you
already have, but for streaming updates or huge inputs an `assoc` frequency map or
`aggregate_all/3` is the better tool.

## Rust bridge

Rust's standard library mirrors this almost predicate-for-predicate — `sort` keeps
duplicates (it's `msort/2`), and you dedup *explicitly*:

```rust
use std::collections::BTreeMap;

// sort/2  -> sort + dedup (note: dedup only removes *adjacent* equals, so sort first)
fn dedup_sorted(mut v: Vec<i32>) -> Vec<i32> {
    v.sort();          // == msort/2 : keeps duplicates
    v.dedup();         // now drop adjacent repeats  => behaves like sort/2
    v                  // [3,1,3,2] -> [1,2,3]
}

// run_lengths/2  -> a frequency map (BTreeMap keeps keys sorted, like value-order)
fn run_lengths(v: &[char]) -> Vec<(char, usize)> {
    let mut counts = BTreeMap::new();
    for &x in v {
        *counts.entry(x).or_insert(0) += 1;   // tally
    }
    counts.into_iter().collect()              // [('a',3), ('b',2)]
}
```

Two things to notice. First, Rust's `Vec::sort` *is* `msort/2` (stable, keeps dups);
to get `sort/2` you append `.dedup()` — and `dedup` only removes *adjacent* equals, so
it's wrong without sorting first, the exact trap the "forgetting to sort" gotcha
describes. Second, Rust reaches for a `BTreeMap` for the tally rather than
sort-then-pack, which is really the **Day 8** frequency-map approach (a `BTreeMap`
keeps keys in sorted order, giving the same value-ordered output as `run_lengths`).
Same two ideas — *dedup* and *tally* — just split across `sort`/`dedup` and the
collections library instead of `sort/2` vs `msort/2` plus a hand-written pack.

## Exit Criteria
- You can state the `sort/2` vs `msort/2` difference and predict both outputs for a
  list with duplicates.
- You can explain *why* counting needs `msort/2` (or a frequency map) and never
  `sort/2`.
- You can write a sort-then-group aggregate (run-length encoding) and trace why
  sorting first makes it one linear pass.
- You can say why the grouping loop uses `==/2` rather than `=/2`.
- You can pick between hand-rolled grouping, `sort/4`, and `aggregate_all/3` for a
  given tally.

## Next Step
Day 10 shifts from *recomputing* to *remembering* with **dynamic predicates and
memoization**:
- `dynamic/1` to declare a predicate whose clauses change at runtime, and
  `assertz/1` / `retractall/1` to add and clear those clauses
- the **memoization** pattern — cache a recursive result the first time you compute
  it, then look it up instead of recomputing (the speedup that rescues exponential
  recurrences)
- **cleanup discipline**: resetting dynamic state between tests so they pass in any
  order and don't leak facts into each other
