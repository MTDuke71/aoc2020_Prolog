# Tutorial Day 10: Dynamic Predicates and Memoization

## Why this day matters
Every predicate you've written so far has been **static**: its clauses are fixed when
the file loads and never change while the program runs. But Prolog also lets a program
**modify its own database at runtime** — add facts, remove them, query them — turning
the clause store into mutable global state. The headline use is **memoization**: cache
a recursive result the first time you compute it, then *look it up* instead of
recomputing. That's the difference between a Fibonacci that takes exponential time and
one that's linear — and several AoC days have recurrences that are flat-out
intractable without it. Dynamic state is powerful and occasionally indispensable, but
it's also the one tool that **breaks Prolog's clean logical model**: asserts aren't
undone on backtracking, state leaks between queries, and test order suddenly matters.
So today is two lessons at once — *how* to use `dynamic`/`assertz`/`retractall`, and
the **cleanup discipline** that keeps them from biting you.

## Focus Topics
- **`:- dynamic Name/Arity`** — declare a predicate whose clauses change at runtime
- **`assertz/1`** (add a clause at the **end**) and its sibling `asserta/1` (at the
  **front**)
- **`retract/1`** (remove one matching clause) and **`retractall/1`** (remove all)
- **The memoization pattern** — check cache → compute on miss → store → return
- **Side effects vs backtracking** — why an `assertz` *survives* backtracking when a
  binding wouldn't
- **Cleanup discipline** — `setup`/`cleanup` so tests pass in any order and don't leak

## Learning Goals
- Implement a memoized recursive predicate backed by a dynamic fact.
- Explain why naive Fibonacci is exponential and memoized Fibonacci is linear.
- State the cache idiom (`( cached -> true ; compute, store )`) and the cut that makes
  a cache hit deterministic.
- Reset dynamic state between tests so they're order-independent — and say why that's
  mandatory, not optional.

## Files
- `day10.pl`: `fib_plain/2` (naive exponential Fibonacci), `fib_memo/2` (memoized via
  a dynamic cache), and `clear_fib_cache/0` (reset).
- `day10_tests.pl`: `plunit` tests that lock both versions to the same answer and use
  `setup`/`cleanup` to scrub the cache around every test.

```prolog
:- module(day10, [fib_plain/2, fib_memo/2, clear_fib_cache/0]).
:- dynamic fib_cache/2.
```

## Run the tests
From repo root:

```bash
swipl -q -s tutorial/day10/day10_tests.pl
```

## Start the REPL

```bash
swipl
```
```prolog
?- ['tutorial/day10/day10.pl'].
```

## The whole program

```prolog
:- dynamic fib_cache/2.

fib_plain(0, 0).
fib_plain(1, 1).
fib_plain(N, F) :-
    N > 1,
    N1 is N - 1,
    N2 is N - 2,
    fib_plain(N1, F1),
    fib_plain(N2, F2),
    F is F1 + F2.

fib_memo(N, F) :-
    fib_cache(N, F), !.
fib_memo(0, 0) :-
    ( fib_cache(0, 0) -> true ; assertz(fib_cache(0, 0)) ).
fib_memo(1, 1) :-
    ( fib_cache(1, 1) -> true ; assertz(fib_cache(1, 1)) ).
fib_memo(N, F) :-
    N > 1,
    N1 is N - 1,
    N2 is N - 2,
    fib_memo(N1, F1),
    fib_memo(N2, F2),
    F is F1 + F2,
    ( fib_cache(N, F) -> true ; assertz(fib_cache(N, F)) ).

clear_fib_cache :-
    retractall(fib_cache(_, _)).
```

Same function — the *n*-th Fibonacci number — computed two ways. `fib_plain/2` is the
textbook recursive definition. `fib_memo/2` is the *same* recursion wrapped in a cache.
The point of the day is everything that differs between them.

## The problem: why `fib_plain/2` is exponential

```prolog
fib_plain(N, F) :-
    N > 1,
    N1 is N - 1, N2 is N - 2,
    fib_plain(N1, F1), fib_plain(N2, F2),   % two recursive calls, no sharing
    F is F1 + F2.
```

`fib(N)` calls `fib(N-1)` *and* `fib(N-2)`, each of which fans out again. Crucially,
the **subproblems overlap**: computing `fib(5)` computes `fib(3)` twice, `fib(2)`
three times, and so on. Nothing remembers a result, so the call tree balloons:

```text
                fib(5)
            /            \
        fib(4)           fib(3)        <- fib(3) computed here...
       /     \           /     \
   fib(3)   fib(2)    fib(2)  fib(1)   <- ...AND again here
   /   \    /   \     /   \
 ...  ... ...  ...  ...  ...
```

The number of calls grows like **φⁿ** (φ ≈ 1.618) — *exponential*. `fib_plain(30, _)`
already makes ~2.7 million calls; `fib_plain(50, _)` is hopeless. The work isn't
inherently large (there are only *n* distinct subproblems); it's that the naive
version **recomputes each one over and over**. That's the textbook setup for
**memoization**.

## The fix: `fib_memo/2` and the dynamic cache

`:- dynamic fib_cache/2.` declares a predicate `fib_cache/2` whose clauses we'll
**add and remove at runtime**. The declaration is required: without it, the first
`assertz(fib_cache(...))` on an otherwise-undefined predicate would error (or warn),
and `fib_cache(N, F)` would raise an existence error before anything is stored.

The four clauses of `fib_memo/2` are tried in order:

```prolog
fib_memo(N, F) :- fib_cache(N, F), !.          % (1) CACHE HIT — done, commit
fib_memo(0, 0) :- ( fib_cache(0,0) -> true ; assertz(fib_cache(0,0)) ).   % (2) base
fib_memo(1, 1) :- ( fib_cache(1,1) -> true ; assertz(fib_cache(1,1)) ).   % (3) base
fib_memo(N, F) :-                              % (4) RECURSE then store
    N > 1, N1 is N-1, N2 is N-2,
    fib_memo(N1, F1), fib_memo(N2, F2),
    F is F1 + F2,
    ( fib_cache(N, F) -> true ; assertz(fib_cache(N, F)) ).
```

1. **Clause 1 is the cache lookup.** If `fib_cache(N, F)` already holds, bind `F` to
   the stored value and **`!` (cut)** — commit, don't try the other clauses. This is
   what makes a repeated subproblem O(1) instead of re-descending the recursion. The
   cut also makes a cache hit **deterministic** (no leftover choice points).
2. **Clauses 2–3 are the base cases**, reached only on a cache *miss* for 0/1. Each
   computes the answer and **stores it** so the next lookup hits clause 1.
3. **Clause 4 is the recursive case.** It recurses with `fib_memo` (not `fib_plain`!),
   so each subproblem it needs is itself cached after first computation. Then it
   **stores its own result** before returning.

Because every distinct `fib_memo(k, _)` is computed *once* and cached, the whole thing
collapses from exponential to **O(n)** calls. The recursion tree becomes a thin spine:
each `fib(k)` is genuinely computed a single time; every *second* request for it is a
clause-1 hit.

### The store idiom: `( fib_cache(N, F) -> true ; assertz(fib_cache(N, F)) )`

Read it as **"if already cached, do nothing; otherwise insert."** It guards against
writing a *duplicate* `fib_cache(N, F)` fact. (In this clause-ordered design clause 1
already caught true hits, so the guard is belt-and-suspenders — but the idiom is the
correct general pattern, and writing duplicates into a dynamic predicate is a real bug:
`fib_cache/2` would then offer two identical clauses and reintroduce a choice point.)
`assertz/1` adds the new fact at the **end** of the predicate's clauses (`asserta/1`
would add it at the front; for a pure cache the position doesn't matter).

## The dynamic-database toolbox (reference)

| Predicate | Effect |
|---|---|
| `:- dynamic f/n.` | declare `f/n` modifiable at runtime (no error when empty) |
| `assertz(Clause)` | add `Clause` as the **last** clause of its predicate |
| `asserta(Clause)` | add `Clause` as the **first** clause |
| `retract(Clause)` | remove the **first** clause that unifies with `Clause` (backtracks to more) |
| `retractall(Head)` | remove **all** clauses whose head unifies with `Head` (always succeeds) |
| `clause(Head, Body)` | inspect existing clauses (read the database) |

`clear_fib_cache :- retractall(fib_cache(_, _)).` wipes the entire cache in one call —
`retractall/1` matches every `fib_cache(_,_)` and removes them all, succeeding even if
there were none (unlike `retract/1`, which *fails* when nothing matches).

## The deep gotcha: asserts ignore backtracking

This is the property that makes dynamic state different from everything else in Prolog.
Ordinary bindings are **undone on backtracking** — that's the whole basis of search
(Day 6). Database changes are **not**:

```prolog
?- ( assertz(fib_cache(99, 12345)), fail ; true ).   % assert, then force backtrack
true.
?- fib_cache(99, V).                                  % V = 12345  -- it STUCK
```

The `assertz` happened as a **side effect**; backtracking through `fail` undid the
*bindings* but left the *database change* in place. That's exactly what you want for a
cache (the whole point is that it persists across calls) — but it's a trap everywhere
else: a half-finished computation that asserts and then fails can leave **garbage
facts** behind that poison the next query. Which leads directly to today's discipline.

## Cleanup discipline: why the tests scrub the cache

```prolog
test(fib_plain_small, [setup(clear_fib_cache), cleanup(clear_fib_cache)]) :-
    once(fib_plain(10, F)),
    assertion(F == 55).

test(fib_memo_small, [setup(clear_fib_cache), cleanup(clear_fib_cache)]) :-
    once(fib_memo(10, F)),
    assertion(F == 55).

test(fib_consistent, [setup(clear_fib_cache), cleanup(clear_fib_cache)]) :-
    once(fib_plain(12, A)),
    clear_fib_cache,
    once(fib_memo(12, B)),
    assertion(A == B).
```

Every test carries `[setup(clear_fib_cache), cleanup(clear_fib_cache)]`. **`setup`**
runs `clear_fib_cache` *before* the test, **`cleanup`** runs it *after* — guaranteeing
each test starts and ends with an **empty** `fib_cache/2`, no matter what the previous
test left behind or what order the tests run in. This is the **cleanup discipline**:
because dynamic state is **global and persistent**, tests that touch it are *not*
independent unless you explicitly reset between them. Skip the `setup` and you get
classic flaky behavior — `fib_memo_small` "passes" only because `fib_plain_small`
happened to run first, or a stale `fib_cache(10, 55)` makes a *broken* `fib_memo`
appear to work. `fib_consistent` even resets **mid-test** (`once(fib_plain(12, A)),
clear_fib_cache, once(fib_memo(12, B))`) so the memo run starts cold and the two paths
are compared fairly. The `once/1` wrappers keep each call deterministic (one solution,
no dangling choice points).

> **Rule:** any predicate that asserts/retracts needs a known-state contract. In tests,
> that's `setup`/`cleanup`. In real code, it's resetting at the start of `solve/2`, or
> scoping the dirty work so leftover facts can't escape.

## Trace: `fib_memo(5, F)` on a cold cache

```text
fib_memo(5): clause1 miss -> clause4: needs fib_memo(4), fib_memo(3)
  fib_memo(4): miss -> needs fib_memo(3), fib_memo(2)
    fib_memo(3): miss -> needs fib_memo(2), fib_memo(1)
      fib_memo(2): miss -> needs fib_memo(1), fib_memo(0)
        fib_memo(1)=1  assert cache(1,1)
        fib_memo(0)=0  assert cache(0,0)
      fib_memo(2)=1   assert cache(2,1)
      fib_memo(1)=1   clause1 HIT (cache(1,1))      <- no re-descent
    fib_memo(3)=2     assert cache(3,2)
    fib_memo(2)=1     clause1 HIT (cache(2,1))      <- no re-descent
  fib_memo(4)=3       assert cache(4,3)
  fib_memo(3)=2       clause1 HIT (cache(3,2))      <- no re-descent
fib_memo(5)=5         assert cache(5,5)
```

Each `fib(k)` is computed once (the `assert` lines); every later need for it is a
clause-1 **HIT** that returns instantly. Compare that to `fib_plain(5, _)`, which would
re-expand `fib(3)` and `fib(2)` in full. Same answer, `F = 5`; vastly less work.

## REPL Drills

```prolog
?- clear_fib_cache, fib_plain(10, F).            % F = 55
?- clear_fib_cache, fib_memo(10, F).             % F = 55  (and cache now populated)
?- listing(fib_cache/2).                         % see every cached fact after a memo run
?- clear_fib_cache, fib_memo(20, _), aggregate_all(count, fib_cache(_,_), N).  % N = 21
?- assertz(note(hi)), note(X).                   % X = hi   -- runtime fact add
?- retract(note(hi)), ( note(_) -> true ; writeln(gone) ).  % gone
?- ( assertz(t(1)), fail ; true ), t(X).         % X = 1    -- assert survives backtracking
?- clear_fib_cache, ( fib_cache(_,_) -> true ; writeln(empty) ).  % empty
```

The two to *feel*: `listing(fib_cache/2)` after a memo run shows the cache filling up
linearly (drill 4: 21 facts for `fib_memo(20)`), and the `assertz/fail` drill proves
the change **outlives** the backtrack.

## Verification (maps to the checklist)
- **Same answer, both ways:** `fib_plain(10,55)` and `fib_memo(10,55)` agree;
  `fib_consistent` proves it at `n = 12` from a cold cache.
- **Cache populates:** after `fib_memo(20, _)` there are exactly 21 `fib_cache/2` facts
  (`fib(0)`…`fib(20)`), one per distinct subproblem — evidence each is computed once.
- **Order independence:** with `setup(clear_fib_cache)` the tests pass in **any** order;
  remove it and they become order-dependent — the symptom of leaked state.
- **Reset works:** after `clear_fib_cache`, `fib_cache(_,_)` has no solutions.

## Common Gotchas
- **Forgetting `:- dynamic fib_cache/2.`** The first `assertz` or query on an
  undeclared, never-defined predicate raises an existence error. Declare it.
- **Asserts survive backtracking.** A database change is a *side effect* — `fail` won't
  roll it back. A predicate that asserts then fails leaves litter behind. Scope it, or
  clean up explicitly.
- **No cleanup → flaky, order-dependent tests.** Global dynamic state leaks between
  tests. Always pair memoizing tests with `setup`/`cleanup` (or reset at the top of the
  predicate). A test that only passes because of a previous test's leftovers is a bug.
- **`retract/1` fails when nothing matches; `retractall/1` always succeeds.** Use
  `retractall/1` for "ensure none remain" — `retract/1` in that role will fail your
  clause unexpectedly when the database is already empty.
- **Duplicate asserted facts.** Asserting the same fact twice gives the predicate two
  identical clauses and a spurious choice point. Guard inserts with
  `( exists -> true ; assertz(...) )`.
- **Recursing into the wrong version.** In `fib_memo`'s recursive clause, calling
  `fib_plain` instead of `fib_memo` silently restores exponential behavior — the cache
  never gets consulted for the sub-calls. Memoization only works if the recursion goes
  *through* the cached predicate.

## Possible optimization: tabling (declarative memoization)

SWI-Prolog can do all of this **for you** with one directive — **tabling**:

```prolog
:- table fib/2.
fib(0, 0).
fib(1, 1).
fib(N, F) :- N > 1, N1 is N-1, N2 is N-2, fib(N1, F1), fib(N2, F2), F is F1 + F2.
```

`:- table fib/2.` tells SWI to **automatically memoize** `fib/2`: it caches answers in
an engine-managed table, no `dynamic`, no `assertz`, no manual cache idiom, and — the
big win — **no cleanup discipline**, because the table is scoped and managed for you
rather than living as global facts you must scrub. Tabling also handles things hand-
rolled caches don't (it terminates on certain *left-recursive* definitions that would
loop forever otherwise). The manual `fib_memo` here is the teaching version — it makes
the cache **visible** (`listing(fib_cache/2)`) so you understand the mechanism. In real
AoC code, reach for `:- table` first; drop to hand-rolled `dynamic` only when you need
to *inspect* or *share* the cache in ways tabling doesn't expose.

## Rust bridge

Rust has no clause database, so memoization is an explicit `HashMap` you thread or
hang off a struct — which makes the moving parts of `fib_memo` obvious:

```rust
use std::collections::HashMap;

fn fib_memo(n: u64, cache: &mut HashMap<u64, u64>) -> u64 {
    if let Some(&f) = cache.get(&n) {   // clause 1: cache hit
        return f;
    }
    let f = match n {                   // clauses 2-4: compute on miss
        0 => 0,
        1 => 1,
        _ => fib_memo(n - 1, cache) + fib_memo(n - 2, cache),
    };
    cache.insert(n, f);                 // the ( -> true ; assertz ) store
    f
}
```

The structure is identical: *check the map, compute on miss, insert, return.* The
difference is **where the state lives**. Rust threads a `&mut HashMap` explicitly — the
cache is a value with a clear scope and lifetime, dropped when it goes out of scope.
Prolog's `fib_cache/2` is **global** in the module database, which is why Prolog needs
the `clear_fib_cache` discipline that Rust gets for free from ownership. (Idiomatic
Rust would more often just write the **iterative** bottom-up DP — `let (mut a, mut b) =
(0, 1); for _ in 0..n { ... }` — sidestepping caching entirely; the same option exists
in Prolog via a tail-recursive accumulator, Day 5.) SWI's `:- table` is the closest
thing to "memoization without managing the map yourself."

## Exit Criteria
- You can declare a `dynamic` predicate and use `assertz`/`retract`/`retractall`
  correctly, knowing which fail and which always succeed.
- You can implement a memoized recursion and explain the exponential → linear collapse.
- You can state why asserted facts survive backtracking and why that demands cleanup.
- You can write order-independent tests over dynamic state with `setup`/`cleanup`.
- You can articulate the trade-offs of dynamic state (global, impure, leak-prone) and
  name `:- table` as the declarative alternative.

## Next Step
Day 11 is the **AoC dry run** — your first end-to-end solution in the exact shape every
real puzzle will take:
- the canonical predicate skeleton: `parse_input/2`, `part1/2`, `part2/2`, `solve/3`
- the **parse-once** pattern — parse the input a single time, feed the structure to
  both parts
- **plunit answer locks** that pin part 1 and part 2 to known-good results
- file-layout discipline, so from July 1 your attention is on algorithms, not scaffolding
