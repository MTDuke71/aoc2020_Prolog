# Tutorial Day 7: CLP(FD) Constraints

## Why this day matters
Days 1–6 built *procedural* search: you wrote the recursion, you drove the
backtracking, you guarded against cycles. **Constraint Logic Programming over
Finite Domains — CLP(FD)** — flips that. You *describe* the relationships the
answer must satisfy (`X + Y #= 10`, `X in 1..9`) and a dedicated solver does the
searching, pruning impossible values *before* it ever tries them. This is Prolog
at its most declarative: the gap between "the spec" and "the program" nearly
vanishes. For AoC it's the right tool whenever a part is naturally "find integers
satisfying these equations/inequalities" — seating puzzles, ticket-field ranges,
small arithmetic searches — where hand-rolled brute force is both slower and more
error-prone. Today's example is deliberately tiny (all `(X,Y)` with `X+Y=10` in
`1..9`) so the *machinery* is what you study, not the puzzle.

## Focus Topics
- **`library(clpfd)`** — load it before any `#` constraint works
- **Domains** with `in`/`ins` — `X in 1..9` bounds a variable's possible values
- **Arithmetic constraints** `#=`, `#<`, `#>`, `#\=` — relations, not evaluations
- **`is/2` vs `#=/2`** — the single most important distinction of the day
- **`labeling/2`** — turn a constrained-but-unbound variable into concrete solutions
- **Constraint propagation** — how the solver shrinks domains before searching
- Enumerating *all* solutions with `findall/3`

## Learning Goals
- Solve a small integer-constraint puzzle with `ins` + `#=` + `labeling`.
- State the difference between `is/2` and `#=/2` precisely, both directions.
- Explain what `labeling/2` does and why constraints alone don't bind variables.
- Read constraint propagation as "domain shrinking."

## Files
- `day7.pl`: `pair_sum_10/2` (one constrained pair) and `all_pair_sum_10/1`
  (collect them all).
- `day7_tests.pl`: `plunit` tests pinning a sample pair and the total count.

```prolog
:- module(day7, [pair_sum_10/2, all_pair_sum_10/1]).
:- use_module(library(clpfd)).
```

## Run the tests
From repo root:

```bash
swipl -q -s tutorial/day7/day7_tests.pl
```

## Start the REPL

```bash
swipl
```
```prolog
?- ['tutorial/day7/day7.pl'].
```

## The whole program

```prolog
pair_sum_10(X, Y) :-
    X in 1..9,
    Y in 1..9,
    X + Y #= 10,
    labeling([], [X, Y]).

all_pair_sum_10(Pairs) :-
    findall((X,Y), pair_sum_10(X, Y), Pairs).
```

Four lines of `pair_sum_10/2` are the entire lesson. Read them as a **spec the
solver must satisfy**, not as steps that compute a value:

1. `X in 1..9` — *declare a domain.* `X` may be any integer from 1 to 9. Nothing
   is chosen yet; you've just fenced the possibilities. `1..9` is a CLP(FD) domain
   term, and `in/2` attaches it to `X`.
2. `Y in 1..9` — same fence for `Y`.
3. `X + Y #= 10` — *post a constraint.* The `#=` reads "is constrained to equal."
   This does **not** compute anything; it records a relation the solver must keep
   true and **immediately propagates** it (see below).
4. `labeling([], [X, Y])` — *search.* Constraints narrow the domains but rarely
   pin a single value; `labeling/2` systematically tries the remaining candidates
   and, on backtracking, yields every assignment consistent with all constraints.

`all_pair_sum_10/1` then wraps `pair_sum_10/2` in `findall/3` to collect the full
enumeration into a list.

## The one distinction to burn in: `is/2` vs `#=/2`

This is the heart of the day. Both look like "equals." They are profoundly
different.

| | `Z is X + Y` (Day 1) | `X + Y #= Z` (CLP(FD)) |
|---|---|---|
| **What it is** | *evaluate* the right side **now** | *post a relation* that must hold |
| **Requires bound inputs?** | **Yes** — `X`, `Y` must already be numbers, or it throws | **No** — any subset may be unbound |
| **Direction** | one-way: inputs → result | multi-way: any variable can be the unknown |
| **When it acts** | once, immediately | persists; re-fires as domains change |
| **`?- 10 #= X + 3`** | `is` would throw (RHS has unbound `X`) | binds/constrains `X` to `7` |

The killer property is **reversibility**. With `is/2`, `X + Y = 10` can only run
"forwards" — give it `X` and `Y`, get `10`. With `#=/2`, the *same equation* runs
in **any** direction: fix the sum and the solver constrains the addends; fix one
addend and it constrains the other. That's why a constraint model often reads like
the problem statement transcribed — you state the relationship once and query it
from whichever side you happen to know.

```prolog
?- X = 3, Y = 4, Z is X + Y.        % Z = 7        -- forward evaluation
?- X = 3, Y = 4, X + Y #= Z.        % Z = 7        -- same answer, but...
?- Z = 7, X = 3, X + Y #= Z.        % Y = 4        -- ...solve for the OTHER unknown
?- Z is X + Y.                      % ERROR: Arguments are not sufficiently instantiated
?- X + Y #= Z.                      % succeeds, posts the constraint, binds nothing yet
```

> **Rule of thumb:** if every input is already a bound number and you want one
> result, `is/2` is simpler and faster. The moment you want to *search over*
> integers, run an equation *backwards*, or post a relation before you know the
> values, reach for `#=` and friends.

## What propagation does *before* `labeling`

Pause the program right before `labeling` and tighten one domain so the effect is
visible — say `Y` can only be `5..9`:

```prolog
?- X in 1..9, Y in 5..9, X + Y #= 10.
X in 1..5,         % SHRUNK from 1..9 by propagation
X+Y#=10,
Y in 5..9.
```

`X` started at `1..9` but the toplevel reports it as `1..5`. The solver reasoned
`X = 10 - Y` and `Y ≥ 5`, so `X ≤ 5` — it **removed `6..9` from `X`'s domain
before any search**, the instant the constraint was posted. (With both domains at
the full `1..9`, nothing is prunable yet, so you'd see `X in 1..9` unchanged; the
constraint still sits there as a *residual goal* waiting to fire as soon as a
domain narrows.) That is **constraint propagation**: each posted constraint prunes
the domains of the variables it touches, and re-fires whenever a related domain
shrinks. The payoff: **the solver throws away dead branches before searching
them**, which is why CLP(FD) beats naive generate-and-test on bigger problems.
Naive code *guesses then checks*; CLP(FD) *shrinks then guesses* from a much
smaller space.

## What `labeling/2` is for

Constraints narrow domains but usually leave variables *constrained yet unbound* —
`X` is "some value in 1..9 with `Y = 10 - X`," not a concrete number. `labeling/2`
is the step that **commits**: it picks actual values from the surviving domains and
backtracks through them, yielding one concrete solution at a time.

```prolog
?- X in 1..9, Y in 1..9, X + Y #= 10, labeling([], [X, Y]).
X = 1, Y = 9 ;
X = 2, Y = 8 ;
X = 3, Y = 7 ;
... ;
X = 9, Y = 1.
```

- The **first argument `[]`** is the list of labeling *options* — search strategy
  (variable-selection like `ffc`/`min`/`max`, value ordering). `[]` means "default
  strategy," fine for small problems.
- The **second argument `[X, Y]`** is the list of variables to ground. Order can
  matter for performance on big searches; here it sets the enumeration order.

Without `labeling`, `pair_sum_10(X, Y)` would succeed with `X`, `Y` still carrying
domains — true, but not the concrete pairs the tests want. `labeling` is what turns
"a description of the solutions" into "the solutions."

## Trace: `all_pair_sum_10/1`

```prolog
all_pair_sum_10(Pairs) :-
    findall((X,Y), pair_sum_10(X, Y), Pairs).
```

`findall/3` runs `pair_sum_10(X, Y)` to *exhaustion*, collecting the `(X,Y)` term
for every solution `labeling` produces:

```text
pair_sum_10 yields  (1,9) (2,8) (3,7) (4,6) (5,5) (6,4) (7,3) (8,2) (9,1)
findall collects -> [ (1,9),(2,8),(3,7),(4,6),(5,5),(6,4),(7,3),(8,2),(9,1) ]
length            -> 9
```

Nine pairs: `X` runs 1..9 and `Y = 10 - X` is forced and always lands in `1..9`.
(`X` can't be 0 or 10 — out of domain.) That count of **9** is what the second test
locks.

## The Tests, One by One

```prolog
:- begin_tests(day7).
:- use_module('./day7.pl').

test(pair_example) :-
    once(pair_sum_10(X, Y)),
    assertion(X + Y =:= 10).

test(all_pairs_count) :-
    all_pair_sum_10(Pairs),
    length(Pairs, N),
    assertion(N == 9).

:- end_tests(day7).
```

| Test | What it pins down |
|---|---|
| `pair_example` | The *first* solution is a genuine pair summing to 10. `once/1` keeps just one; the assertion uses `=:=` (arithmetic equality) because by now `X` and `Y` are bound integers. |
| `all_pairs_count` | The full enumeration has **exactly 9** members — the constraint admits no more, no fewer. A count test is the cheap, robust way to verify a solver's completeness. |

Note the deliberate operator choice in the assertion: `=:=` is **arithmetic
equality on evaluated numbers** (Day 1), correct here because `X` and `Y` are fully
bound after `once(pair_sum_10(...))`. You would *not* write `#=` in the assertion —
that posts a constraint rather than checking a fact, and against already-bound
integers it's just a roundabout `=:=`.

## REPL Drills

```prolog
?- use_module(library(clpfd)).
?- X in 1..9, Y in 1..9, X + Y #= 10, label([X,Y]).   % label/1 = labeling([], ...)
?- pair_sum_10(X, Y).                       % X=1,Y=9 ; X=2,Y=8 ; ...  (all 9 on ;)
?- all_pair_sum_10(Ps), length(Ps, N).      % N = 9
?- 10 #= X + 3.                             % X = 7   -- run the equation backwards
?- X in 1..9, Y in 1..9, X + Y #= 10.       % no labeling: see the propagated domains
?- X in 1..3, Y in 1..3, X #< Y, label([X,Y]).  % X=1,Y=2 ; X=1,Y=3 ; X=2,Y=3
?- numlist(1,9,L), member(X,L), member(Y,L), X+Y=:=10.  % the brute-force contrast
```

The last two drills are the contrast worth feeling: `#<` posts an *inequality
relation* the solver prunes with, while the `member/member/=:=` line is classic
**generate-and-test** — it produces all 81 `(X,Y)` combinations and *filters*.
Same answers; CLP(FD) reaches them by shrinking the space instead of walking all of
it.

## Verification (maps to the checklist)
- **Expected assignment:** `once(pair_sum_10(X, Y))` gives a concrete pair with
  `X + Y =:= 10`.
- **Expected count:** `all_pair_sum_10(Ps), length(Ps, 9)` — the model admits
  exactly nine solutions.
- **Reversibility:** `10 #= X + 3` binds `X = 7`, demonstrating multi-directional
  evaluation `is/2` can't do.
- **Domain boundaries:** no pair includes `0` or `10` — the `1..9` domain excludes
  them, so e.g. `(0,10)` never appears.

## Common Gotchas
- **Forgetting `:- use_module(library(clpfd)).`** Without it, `#=`, `in`, and
  `labeling` are undefined and you get a procedure-existence error (or, worse,
  `in/2` resolves to something unexpected). It's the first line of `day7.pl` for a
  reason.
- **Reaching for `is/2` when you mean `#=/2`.** `Z is X + Y` with `X` or `Y`
  unbound **throws** `Arguments are not sufficiently instantiated`. That error is
  almost always the signal "you wanted a constraint here."
- **Expecting constraints to bind variables on their own.** Posting
  `X + Y #= 10` does *not* give you `X = 1, Y = 9`; it leaves both constrained but
  unbound. You must `labeling/2` (or `label/1`) to get concrete values. Missing
  `labeling` is the #1 "why is my answer a domain, not a number?" bug.
- **`=:=` vs `#=` vs `=`.** `=:=` evaluates *both* sides as arithmetic and compares
  (needs bound numbers). `#=` posts a *constraint* (works on unbound vars). `=` is
  plain *unification* (structural, no arithmetic — `3 = 1 + 2` is **false**). Pick
  by intent: check a number → `=:=`; constrain a search → `#=`; match a term → `=`.
- **`label/1` vs `labeling/2`.** `label(Vars)` is just `labeling([], Vars)` — the
  default strategy. Use `labeling/2` when you need options (`ff`, `min(Cost)`,
  etc.) for performance on real searches.
- **Domain too narrow silently drops solutions.** If you'd written `X in 1..8`, the
  pair `(9,1)` vanishes and the count becomes 8 — no error, just a wrong answer.
  Domains are part of the spec; get them right.

## The AoC Payoff: when to model instead of march

Some AoC days are *naturally constraint problems*. The 2020 ticket-translation day,
for instance, asks you to assign field-names to ticket positions subject to "each
field's value falls in its allowed ranges" — a constraint-satisfaction problem that
CLP(FD) expresses almost verbatim. The general shape:

```prolog
solve(Vars) :-
    Vars = [A, B, C, ...],
    Vars ins 1..N,            % every variable's domain at once (ins = plural in)
    A + B #= ...,             % transcribe the puzzle's relations
    all_distinct(Vars),       % a single global constraint for "all different"
    label(Vars).              % search what survives propagation
```

`ins/2` (plural) sets a whole list's domain in one go; `all_distinct/1` is a
*global constraint* that propagates "these must all differ" far more aggressively
than pairwise `#\=`. The judgment call — the actual exit skill — is **recognizing**
when a part is constraint-shaped (small integer domains, equations/inequalities,
all-different) versus when explicit search (Day 6) or a direct fold (Day 5) is
simpler. Reach for CLP(FD) when the relations are easy to *state* but awkward to
*drive* by hand.

## Rust bridge

Rust has no built-in constraint solver, so the honest translation is
**generate-and-test** — which is precisely the thing CLP(FD) improves on:

```rust
fn all_pair_sum_10() -> Vec<(i32, i32)> {
    let mut pairs = Vec::new();
    for x in 1..=9 {                 // X in 1..9
        for y in 1..=9 {             // Y in 1..9
            if x + y == 10 {         // the test — NOT a constraint, runs after generating
                pairs.push((x, y));
            }
        }
    }
    pairs                            // length 9
}
```

This nested loop generates all 81 candidates and filters to 9. It gets the same
answer, but notice what's missing: there's no *propagation*. Rust tries `(1,1)`,
`(1,2)`, … `(1,9)` and checks each, whereas CLP(FD), the instant it posts
`X + Y #= 10`, already knows `Y = 10 - X` and never enumerates the 72 dead pairs.
On a 9×9 toy that's invisible; on a problem with ten variables over `1..100` it's
the difference between milliseconds and "still running." To get *true* constraint
solving in Rust you'd pull in a crate (a SAT/SMT binding or a CP library) — which is
exactly the engine `library(clpfd)` hands you for free. Same declarative idea
("describe, don't drive"); in Prolog it's a one-line `use_module`.

## Exit Criteria
- You can write a small `ins` + `#=` + `labeling` model from a word problem.
- You can state the `is/2` vs `#=/2` difference both ways and predict which throws.
- You can explain why constraints alone don't bind variables and what `labeling/2`
  adds.
- You can describe propagation as "domains shrink before search" and say why that
  beats generate-and-test.
- You can recognize when an AoC part is constraint-shaped versus better served by
  Day 5/Day 6 techniques.

## Next Step
Day 8 moves from *searching* to *fast lookup* with **maps and key-value
structures**:
- `library(assoc)` for balanced-tree maps and SWI **dicts** for record-style access
- building a **frequency table** from input tokens — the bread-and-butter AoC tally
- the update/lookup patterns that replace the O(n) `member/2` scans you've leaned on
  so far
