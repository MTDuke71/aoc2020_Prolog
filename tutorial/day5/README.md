# Tutorial Day 5: Accumulators and Tail Recursion

## Why this day matters
AoC inputs are big — thousands of lines, grids with millions of cells, lists you
fold over many times. A recursive predicate that builds its answer *on the way
back up* the call stack holds every pending frame in memory at once; on a long
enough list that's a stack overflow, not a wrong answer. The fix is a single
structural change you'll apply over and over: carry the partial result **forward**
in an extra argument — an **accumulator** — so the recursive call is the *last*
thing the clause does. When it is, SWI-Prolog reuses the current stack frame
instead of growing the stack — **last-call optimization (LCO)**, Prolog's name for
tail-call elimination. This day is short on syntax and long on a habit: recognize
when a predicate is accumulator-shaped, and convert it when it isn't.

## Focus Topics
- **Accumulator-passing style** — threading a partial result through an extra arg
- **Tail recursion** and **last-call optimization (LCO)** — what makes a call "tail"
- **Prepend-then-reverse** vs. append-as-you-go (O(n) vs. O(n²))
- The **public/helper split**: a clean `arity/2` wrapper over a `arity/3` worker
- Reasoning about **space**: stack growth vs. constant-stack iteration

## Learning Goals
- Rewrite a naive right-folding predicate into accumulator form.
- State precisely *why* the accumulator version runs in constant stack space.
- Explain why `reverse` accumulates by **prepending** and why that's O(n).
- Read the two-clause `base case / recursive case` accumulator skeleton fluently.

## Files
- `day5.pl`: two canonical accumulator predicates — `sum_acc/2`, `reverse_acc/2`.
- `day5_tests.pl`: `plunit` tests pinning their results.

```prolog
:- module(day5, [sum_acc/2, reverse_acc/2]).
```

## Run the tests
From repo root:

```bash
swipl -q -s tutorial/day5/day5_tests.pl
```

## Start the REPL

```bash
swipl
```
```prolog
?- ['tutorial/day5/day5.pl'].
```

## First, the problem: what naive recursion costs

Here is the textbook "sum a list" that everyone writes first. It is **not** in
`day5.pl` — it's the thing we're replacing:

```prolog
sum_naive([], 0).
sum_naive([X|T], Sum) :-
    sum_naive(T, Rest),     % recurse FIRST...
    Sum is X + Rest.        % ...then do arithmetic on the way back
```

Read the recursive clause carefully. The call `sum_naive(T, Rest)` is **not** the
last goal — there's an `is/2` waiting to run *after* it returns. So Prolog cannot
discard the current frame when it recurses: it must keep this frame alive to come
back and compute `X + Rest`. For a list of length *n*, all *n* frames are live at
the deepest point:

```text
sum_naive([1,2,3], S)
  needs 1 + sum_naive([2,3])          frame 1 parked
    needs 2 + sum_naive([3])          frame 2 parked
      needs 3 + sum_naive([])         frame 3 parked
        = 0
      = 3+0 = 3        <- unwinding starts here, frames pop one by one
    = 2+3 = 5
  = 1+5 = 6
```

That parked-frame stack is O(n) space and, past a few hundred thousand elements,
a `Stack overflow` error. The arithmetic is fine; the *shape* is the bug.

## The fix: carry the answer forward in an accumulator

```prolog
sum_acc(List, Sum) :-
    sum_acc_(List, 0, Sum).

sum_acc_([], Acc, Acc).
sum_acc_([X|T], Acc, Sum) :-
    Acc1 is Acc + X,
    sum_acc_(T, Acc1, Sum).
```

Two things changed, and they're the whole lesson:

1. **An extra argument `Acc`** holds the running total. We do the arithmetic
   `Acc1 is Acc + X` **before** recursing, while we still have the frame anyway.
2. **The recursive call is now the last goal** in the clause. Nothing waits for it
   to return — its answer *is* this clause's answer (`Sum` is just threaded
   straight through). That's a **tail call**, and SWI replaces the current frame
   instead of stacking a new one. Constant stack, any list length.

Trace it and watch the work happen on the way *down*, with no unwinding:

```text
sum_acc([1,2,3], S)
  sum_acc_([1,2,3], 0, S)        Acc=0
  sum_acc_([2,3],   1, S)        Acc1 = 0+1 = 1
  sum_acc_([3],     3, S)        Acc1 = 1+2 = 3
  sum_acc_([],      6, S)        Acc1 = 3+3 = 6
  base case: Acc == S, so S = 6  <- answer handed straight back, no math left
```

Compare the two traces side by side: the naive one builds a tower and collapses
it; the accumulator one is a flat loop that arrives at the answer already
computed. The base case `sum_acc_([], Acc, Acc)` is doing the quiet, crucial work
— **unifying the finished accumulator with the output variable**. That single
shared variable name in both slots is how the result escapes back to the caller.

> **What makes a call "tail"?** It's the *last goal* of its clause **and** there
> are no untried alternatives left (no choicepoints) — then LCO can fire. Here the
> two clauses match disjoint patterns (`[]` vs `[X|T]`), so there's no dangling
> choicepoint, and the recursion is genuinely iterative. (Day 3's determinism
> lesson pays off again: leftover choicepoints would defeat LCO.)

## The public/helper split

Notice the shape `sum_acc/2` (public) calling `sum_acc_/3` (helper):

```prolog
sum_acc(List, Sum) :-          % the interface the world calls
    sum_acc_(List, 0, Sum).    % seeds the accumulator and delegates
```

The caller shouldn't have to pass an initial `0` — that's an implementation
detail. The wrapper's only job is to **seed the accumulator** (`0` for a sum, `[]`
for a reverse) and hand off to the worker. The trailing-underscore name
(`sum_acc_`) is the repo's convention for "private helper, don't call directly."
You'll see this exact two-level split in nearly every `src/dayNN.pl`: a clean
`part1/2` over a `foo_/3` that does the accumulating.

## `reverse_acc/2` — the same skeleton, with a list accumulator

```prolog
reverse_acc(List, Rev) :-
    reverse_acc_(List, [], Rev).

reverse_acc_([], Acc, Acc).
reverse_acc_([X|T], Acc, Rev) :-
    reverse_acc_(T, [X|Acc], Rev).
```

Identical structure to `sum_acc` — only the accumulator's *type* and *update*
differ. The seed is `[]` instead of `0`, and the update is **prepend** `[X|Acc]`
instead of `Acc + X`. Trace it:

```text
reverse_acc([1,2,3], R)
  reverse_acc_([1,2,3], [],      R)
  reverse_acc_([2,3],   [1],     R)     % 1 pushed onto front
  reverse_acc_([3],     [2,1],   R)     % 2 pushed onto front
  reverse_acc_([],      [3,2,1], R)     % 3 pushed onto front
  base case: R = [3,2,1]
```

The reversal is **free**: pushing each head onto the front of the accumulator
naturally flips the order. And prepending `[X|Acc]` is O(1) — Prolog just makes a
new cons cell pointing at the old list. The whole thing is O(n) time, constant
stack.

### Why not `append` as you go?

The "obvious" reverse appends each element to the end:

```prolog
reverse_slow([], []).
reverse_slow([X|T], R) :- reverse_slow(T, RT), append(RT, [X], R).
```

This is doubly bad. `append(RT, [X], R)` walks the *entire* accumulated list to
reach its end, every step — that's 1+2+···+n = **O(n²)** time. And like
`sum_naive`, the recursion isn't tail (the `append` runs after it), so it's also
O(n) stack. **Prepend-then-let-the-order-flip-itself** is the idiomatic move: when
you find yourself reaching for `append/3` inside a recursion to tack onto the end,
that's the signal to flip to an accumulator and prepend instead.

> This is exactly how SWI's own `reverse/2` is implemented — an accumulator that
> prepends. `reverse_acc` is a faithful reimplementation of the library predicate.

## The shared accumulator recipe

Both predicates are the same four-part template. Learn it once:

| Part | `sum_acc` | `reverse_acc` |
|---|---|---|
| **Seed** (in wrapper) | `0` | `[]` |
| **Update** (recursive clause) | `Acc1 is Acc + X` | `[X\|Acc]` (prepend) |
| **Base case** | `..._([], Acc, Acc)` | `..._([], Acc, Acc)` |
| **Recurse** | tail call on `T` | tail call on `T` |

To accumulate something new (a max, a count, a list of matches), you change only
the **seed** and the **update**; the base case and the tail-recursive shape stay
fixed. `foldl/4` (Day's REPL drill) is this recipe generalized into a library
higher-order predicate.

## The Tests, One by One

```prolog
:- begin_tests(day5).
:- use_module('./day5.pl').

test(sum_acc)       :- sum_acc([1,2,3,4], S), assertion(S == 10).
test(sum_acc_empty) :- sum_acc([], S),        assertion(S == 0).
test(reverse_acc)   :- reverse_acc([1,2,3], R), assertion(R == [3,2,1]).

:- end_tests(day5).
```

| Test | What it pins down |
|---|---|
| `sum_acc` | the accumulator threads correctly: 1+2+3+4 = 10 |
| `sum_acc_empty` | the **base case in isolation** — the seed `0` is returned untouched for `[]`, proving the wrapper seeds correctly |
| `reverse_acc` | the prepend-flips-order property: `[1,2,3]` → `[3,2,1]` |

`sum_acc_empty` is the quietly important one: it tests that the seed value is
right and that the empty-list base case returns it directly. The `==` (not `=`)
asserts the result is *exactly* that value, fully bound.

## REPL Drills

```prolog
?- sum_acc([1,2,3,4], S).            % S = 10
?- reverse_acc([a,b,c], R).          % R = [c,b,a]
?- foldl([X,A,B]>>(B is A+X), [1,2,3,4], 0, S).  % S = 10 -- foldl IS the accumulator recipe
?- foldl(plus, [1,2,3,4], 0, S).     % S = 10 -- plus/3 as the folding goal
?- reverse([1,2,3], R).              % R = [3,2,1] -- the library version, same algorithm
?- numlist(1, 100000, L), sum_acc(L, S).   % S = 5000050000 -- big list, no stack overflow
```

The last drill is the proof: sum a 100k-element list and watch it return instantly
with no `Stack overflow`. Try the same with `sum_naive` and you'll see the
difference the shape makes.

## Verification (maps to the checklist)
- **Equivalence with the library:** `reverse_acc(L, R), reverse(L, R2)` gives
  `R == R2` for any `L` — the accumulator version matches the built-in.
- **Empty input:** `sum_acc([], 0)` and `reverse_acc([], [])` — base cases fire
  cleanly.
- **Single element:** `reverse_acc([x], [x])` — prepend onto `[]` is just `[x]`.
- **Scale test:** `numlist(1, 1000000, L), sum_acc(L, _)` completes in constant
  stack; the naive version overflows. That's the whole point, demonstrated.

## Common Gotchas
- **The recursive call must be *last*.** Putting *any* goal after it (even a cheap
  `is/2` or a print) defeats LCO and reintroduces O(n) stack. Do all the work
  *before* you recurse, then recurse as the final goal.
- **Leftover choicepoints also defeat LCO.** If your clauses overlap (so Prolog
  keeps an alternative open), the call isn't a true tail call. Disjoint head
  patterns (`[]` vs `[X|T]`) — or a cut — keep it deterministic. (Day 3.)
- **Don't `append` to the end in a loop.** That's the O(n²) trap. Accumulate by
  **prepending**, and reverse once at the end if you need the original order.
- **`is/2` needs a bound right-hand side.** `Acc1 is Acc + X` requires `Acc` and
  `X` already bound to numbers — which is exactly why we update the accumulator on
  the way *down* (when the head `X` is in hand), not on the way back up.
- **The output variable is threaded, not computed, in the recursive clause.** Note
  `Sum`/`Rev` appears in both the head and the recursive call unchanged — it's a
  pipe to the eventual base case, not something this clause fills in.

## The AoC Payoff: fold the parsed data without blowing the stack

Day 4 gave you a parser that turns a text blob into a big list. Day 5 is how you
*consume* that list safely. The shipping shape composes the two:

```prolog
part1(Ints, Sum) :- sum_acc(Ints, Sum).   % or foldl/4 for the general case

solve(File, Part1, _Part2) :-
    read_file_to_string(File, Raw, []),
    parse_int_lines(Raw, Ints),           % Day 4's parser
    part1(Ints, Part1).                    % Day 5's constant-stack fold
```

Most "reduce the input to one number/structure" parts are an accumulator (or its
library form `foldl/4`) over the parsed list. Getting comfortable with the shape
now means the big-input days don't surprise you with stack overflows.

## Rust bridge

The accumulator predicate *is* an imperative loop with a mutable variable —
Prolog just spells the mutation as "pass a new value to the next iteration":

```rust
fn sum_acc(list: &[i64]) -> i64 {
    let mut acc = 0;           // the seed, 0
    for &x in list {           // walk head by head
        acc = acc + x;         // Acc1 is Acc + X
    }
    acc                        // base case: return the accumulator
}

fn reverse_acc<T: Clone>(list: &[T]) -> Vec<T> {
    let mut acc = Vec::new();  // the seed, []
    for x in list {
        acc.insert(0, x.clone());  // [X|Acc] -- prepend
    }
    acc
}
```

Two things to hold onto. (1) Rust's `for` loop is already constant-stack, so the
"why doesn't this overflow" question never comes up; in Prolog you *earn* that
property by making the call tail-recursive — LCO is the compiler turning your
recursion back into Rust's loop. (2) `acc.insert(0, x)` in Rust is O(n) (it shifts
the whole Vec), so the literal translation of the prepend is actually slow in
Rust — Prolog's `[X|Acc]` is O(1) because it shares structure rather than copying.
Same algorithm, different cost model for the prepend; idiomatic Rust would push to
the end and read back-to-front, or use `.rev()`.

## Exit Criteria
- You can convert a naive right-folding predicate into accumulator form.
- You can point at the recursive call and say why it is (or isn't) a tail call.
- You can explain LCO in one sentence: *last goal + no choicepoints → frame reuse →
  constant stack.*
- You can explain why `reverse` prepends (O(n)) instead of appending (O(n²)).
- You can read the wrapper/helper split and name what the wrapper seeds.

## Next Step
Day 6 builds on the accumulator habit with:
- modeling **state** as predicates: nodes, edges, and transitions
- DFS/BFS-style recursion over graphs and grids
- **visited sets** (an accumulator!) to stay finite on cyclic graphs
