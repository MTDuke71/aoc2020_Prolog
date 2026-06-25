# Tutorial Day 3: Determinism, Choicepoints, and Cuts

## Why this day matters
Days 1–2 leaned on backtracking as a *feature* — `member_of/2` happily enumerated
every answer. Today is the flip side: a lot of AoC code wants **exactly one
answer**, computed once, with no leftover choicepoints sitting around. Learning to
*see* choicepoints, and to prune them deliberately with the **cut** (`!`), is the
difference between a predicate that's fast and clear and one that quietly
recomputes or returns surprise extra solutions. The cut is also the single most
abused construct in Prolog, so today is as much about *when not to* use it.

## Focus Topics
- Deterministic vs. nondeterministic predicates
- What a **choicepoint** actually is and where it comes from
- The cut (`!`): what it commits to, and what it does *not* undo
- **Green cuts** (prune redundant work) vs. **red cuts** (change the answer set)
- `once/1` and the `( Cond -> Then ; Else )` if-then-else as tamer alternatives

## Learning Goals
- Identify when a predicate should produce one answer vs. many.
- Explain a choicepoint in plain language and point to where one is created.
- Use cut conservatively and say what it prunes in a given clause.
- Name at least one case where a cut is a bad idea.

## Files
- `day3.pl`: three predicates contrasting committed vs. backtracking search.
- `day3_tests.pl`: `plunit` tests, including one that asserts backtracking still
  enumerates *all* answers.

Same two-file module/test split as Days 1–2:

```prolog
:- module(day3, [classify_num/2, first_even/2, maybe_member/2]).
```

## Run the tests
From repo root:

```bash
swipl -q -s tutorial/day3/day3_tests.pl
```

## Start the REPL

```bash
swipl
```
```prolog
?- ['tutorial/day3/day3.pl'].
```

## The Core Idea: choicepoints and determinism

When Prolog runs a goal and **more than one clause could still match**, it leaves
behind a **choicepoint** — a bookmark saying "if a later goal fails, come back
here and try the next alternative." Backtracking is just Prolog returning to the
most recent bookmark.

- A goal is **deterministic** if, once it succeeds, there are *no* bookmarks left
  — there is provably no other way to satisfy it. The REPL shows this as a plain
  `true.` with no further prompt.
- A goal is **nondeterministic** if it leaves choicepoints — the REPL shows
  `true ` and waits, and pressing `;` finds another answer.

You can *see* the difference in the REPL. Watch the trailing prompt:

```prolog
?- member(X, [1,2,3]).
X = 1 ;          % the space + ; means: a choicepoint is still open
X = 2 ;
X = 3.           % the . (no space) means: that was the last answer, deterministic now
```

That dangling choicepoint is not free: it pins memory and invites accidental
re-execution. Most of today is about removing the ones you didn't want.

## What the cut (`!`) does

`!` is a goal that **always succeeds**, exactly once, and as a side effect:

1. **Commits to the current clause** — Prolog will not try any *later* clauses of
   the same predicate.
2. **Discards every choicepoint created since the predicate was entered** — i.e.
   all the bookmarks from goals to the *left* of the cut, within this clause.

What it does **not** do: it does not undo variable bindings, and it does not
affect choicepoints created to the *right* of it. Think of `!` as a one-way door
— once you step through, the alternatives behind you are gone.

### Green cut vs. red cut (the vocabulary that matters)

- A **green cut** removes only choicepoints that would have led to *redundant or
  failing* work. Delete it and the program computes the **same answers**, just
  slower. Green cuts are pure optimization.
- A **red cut** removes choicepoints that would have produced **different
  answers**. Delete it and the *meaning* of the program changes. Red cuts are
  load-bearing — and the dangerous ones, because the clause is now only correct
  for a particular calling pattern (mode) and clause order.

Both kinds appear in today's code. Knowing which is which is the skill.

## Predicate Walkthroughs (line by line)

### `classify_num/2` — negative / zero / positive (red cuts)

```prolog
classify_num(N, negative) :- N < 0, !.
classify_num(0, zero)     :- !.
classify_num(_, positive).
```

Read top-to-bottom, this is "if `N < 0` it's negative; else if it's exactly `0`
it's zero; otherwise positive." Each `!` commits as soon as a branch is chosen.

Why the cuts are **red** (load-bearing) — trace `classify_num(-4, C)` *without*
the cuts:

1. Clause 1: `-4 < 0` succeeds, `C = negative`. ✔ — but a choicepoint remains.
2. On backtracking, clause 2: `-4 = 0` fails.
3. Clause 3: `C = positive`. ✔ — a **second, wrong answer**.

So without the cut you'd get `C = negative ; C = positive`. The `!` in clause 1
fires right after `-4 < 0` succeeds, discards the choicepoint, and Prolog never
reaches clauses 2–3. Result: one clean answer. Because removing the cut *adds a
wrong answer*, it changes the solution set — that's the definition of a red cut.

**The trap (why red cuts are risky).** This predicate is only correct when called
with the first argument bound and the second unbound — mode `classify_num(+N, -C)`.
Two ways it can bite you:

- `classify_num(N, C)` with `N` unbound throws an instantiation error, because
  `N < 0` needs `N` to be a concrete number.
- The clauses rely on **order** *and* the cut together. Reorder them, or call in
  an unexpected mode, and the cut silently commits to the wrong branch. A red cut
  encodes "I promise the earlier conditions already ruled out this case" — a
  promise the compiler can't check for you.

A cut-free, mode-safe spelling of the same logic uses if-then-else and never
leaves a choicepoint to begin with:

```prolog
classify_num(N, Class) :-
    ( N < 0 -> Class = negative
    ; N =:= 0 -> Class = zero
    ; Class = positive ).
```

The `->` already commits to the first branch whose test succeeds (it behaves like
a local cut), so this is deterministic without an explicit `!`. Many Prolog
programmers prefer this precisely because the commitment is *visible and scoped*
rather than hidden in clause order.

### `first_even/2` — the first even element (red cut)

```prolog
first_even([X|_], X) :- 0 is X mod 2, !.
first_even([_|T], X) :- first_even(T, X).
```

"The first even element of the list." Clause 1 checks the head: if `X mod 2` is
`0`, the head *is* the answer and `!` commits — we stop looking. Otherwise clause
2 drops the head and recurses on the tail.

Trace of `first_even([1,3,4,6], X)`:

```text
first_even([1,3,4,6], X)
  clause 1: 0 is 1 mod 2 ? -> 1, no.   clause 2: recurse on [3,4,6]
    clause 1: 0 is 3 mod 2 ? -> 1, no. clause 2: recurse on [4,6]
      clause 1: 0 is 4 mod 2 ? -> 0, YES. X = 4, ! commits.  <- stop
```

The cut is **red** here too: without it, after binding `X = 4` Prolog could
backtrack into clause 2 and keep searching, eventually offering `X = 6` as a
second answer. The `!` is what makes "first" mean *first* rather than "any even,
on backtracking." Note the cut sits *after* the `0 is X mod 2` test, so it only
commits once we've actually confirmed the head is even — committing earlier would
be a bug.

There is **no base clause for `[]`** on purpose: a list with no even element runs
off the end and simply fails (`first_even([1,3,5], X)` → `false`). "No first even"
= "can't be proven," the same design choice as `member_of/2` on Day 1.

### `maybe_member/2` — membership *with* backtracking (no cut)

```prolog
maybe_member(X, [X|_]).
maybe_member(X, [_|T]) :- maybe_member(X, T).
```

This is plain `member/2` — and deliberately **cut-free**. It's the control case
for today: with both clauses live, it is genuinely nondeterministic, which is
exactly what we want when the *whole point* is to enumerate.

```prolog
?- maybe_member(X, [a,b,c]).
X = a ;
X = b ;
X = c.
```

Each `;` re-enters clause 2, peels another element, and clause 1 succeeds on the
new head. Putting a cut in clause 1 here would **break the feature** — it'd commit
to the first element and refuse to enumerate the rest. That's the "case where cut
is a bad idea" the exit criteria ask for: never cut away backtracking you actually
need.

### The three side by side

| Predicate | Cut? | Determinism | Why |
|---|---|---|---|
| `classify_num/2` | red `!` | one answer | mutually exclusive classes; extra answers would be wrong |
| `first_even/2` | red `!` | one answer | "first" means stop at the first match |
| `maybe_member/2` | none | many answers | enumeration *is* the purpose |

The lesson: cut is a tool for matching a predicate's behavior to its *intent*. Use
it where one answer is correct; leave it out where many answers are the point.

## Tamer alternatives to a bare cut

Two constructs give you commitment without a free-floating `!`:

### `once/1` — "just the first solution, from the outside"

`once(Goal)` succeeds at most once: it runs `Goal`, keeps the first solution, and
discards the rest. It's a cut applied *at the call site* instead of inside the
predicate — so you can keep `maybe_member/2` fully nondeterministic and still ask
for a single answer when you want one:

```prolog
?- once(maybe_member(X, [a,b,c])).
X = a.            % deterministic — no ; prompt
```

This is often the better design: write the predicate honestly (all solutions),
and let *callers* choose `once/1` when they only need one. Compare with
`first_even/2`, which bakes the commitment in.

### `( Cond -> Then ; Else )` — scoped, visible commitment

The if-then-else (seen in the cut-free `classify_num` above and in Day 2's
`count_even/2`) commits to the first branch whose `Cond` succeeds. It's a cut
whose scope is obvious from the syntax, which is why it's usually preferred over
hand-rolled `!` for simple branching.

## The Tests, One by One

```prolog
:- begin_tests(day3).
:- use_module('./day3.pl').

test(classify_negative) :- classify_num(-4, C), assertion(C == negative).
test(classify_zero)     :- classify_num(0,  C), assertion(C == zero).
test(classify_positive) :- classify_num(9,  C), assertion(C == positive).
test(first_even)        :- first_even([1,3,4,6], X), assertion(X == 4).
test(maybe_member_backtracks, all(X == [a,b,c])) :- maybe_member(X, [a,b,c]).

:- end_tests(day3).
```

| Test | What it pins down |
|---|---|
| `classify_negative` | the `N < 0` branch + its cut |
| `classify_zero` | the `0` branch — note it relies on clause 1's cut *not* having fired |
| `classify_positive` | the fall-through clause for everything else |
| `first_even` | returns `4`, the **first** even, proving the cut stops the search (a buggy cut-free version could return `6` on backtracking) |
| `maybe_member_backtracks` | the interesting one — see below |

The last test uses `plunit`'s **`all/1`** option:

```prolog
test(maybe_member_backtracks, all(X == [a,b,c])) :- maybe_member(X, [a,b,c]).
```

`all(X == [a,b,c])` forces backtracking over *every* solution and asserts the
collected list of `X` values is exactly `[a,b,c]`, in order. This is the
counterpart to a cut test: instead of checking "we committed to one answer," it
checks "we still produce *all* the answers." If someone slipped a cut into
`maybe_member/2`, this test would fail — making it a guard against accidentally
destroying wanted backtracking. (Day 1 used the same `all/1` form for
`member_of/2`.)

## REPL Drills (watch the choicepoints)

```prolog
?- member(X, [1,2,3]).         % X = 1 ;  -- leaves choicepoints, enumerate with ;
?- once(member(X, [1,2,3])).   % X = 1.   -- once/1 commits: deterministic
?- (1 < 2 -> writeln(ok) ; writeln(no)).  % prints ok; -> commits to the then-branch
```

Then probe today's predicates:

```prolog
?- classify_num(-4, C).     % C = negative.
?- classify_num(0, C).      % C = zero.
?- classify_num(7, C).      % C = positive.
?- first_even([1,3,4,6], X).% X = 4.     (not 6 — the cut stops here)
?- first_even([1,3,5], X).  % false.     (no even element)
?- maybe_member(b, [a,b,c]).% true.      (membership test, single fact match)
?- maybe_member(X, [a,b,c]).% X = a ; X = b ; X = c.
```

## Verification (maps to the checklist)
- **Intended backtracking:** `maybe_member/2` — and `maybe_member_backtracks`
  proves it still enumerates all of `[a,b,c]`.
- **Should be deterministic, enforced:** `classify_num/2` and `first_even/2` use
  cut so they yield exactly one answer.
- **A test that fails if extra solutions appear:** `all(X == [a,b,c])` is exact —
  any extra (or missing, or reordered) solution fails it.

## Common Gotchas
- **Cut doesn't undo bindings.** It prunes choicepoints; variables stay bound.
- **Placement matters.** A cut commits to everything to its *left*. In
  `first_even`, the `!` must come *after* the `0 is X mod 2` test — cutting before
  the test would commit before confirming the match.
- **Red cuts encode a mode assumption.** `classify_num/2` only works as
  `classify_num(+N, -C)`. Calling it with `N` unbound throws; relying on it in
  another mode silently misbehaves. When in doubt, prefer explicit if-then-else.
- **Don't cut away backtracking you need.** A cut in `maybe_member/2` would turn a
  feature into a bug. Match the construct to the intent.
- **`=:=` vs. `=` vs. `is`.** Arithmetic *comparison* is `=:=` / `<` / `>`;
  *evaluation-and-bind* is `is`; *unification* is `=`. The cut-free `classify_num`
  uses `N =:= 0` (compare), not `N = 0` (unify) — though for an integer they
  happen to coincide here.

## Exit Criteria
- You can explain a choicepoint in plain language and point at one in the REPL
  (the `;` prompt).
- You can state what `!` commits to and what it leaves alone.
- You can tell a green cut from a red cut and classify the ones in `day3.pl`.
- You can name a case where cut is the wrong tool (`maybe_member/2`).
- You can reach for `once/1` or `( -> ; )` instead of a bare cut when that's
  clearer.

## Next Step
Day 4 builds on determinism with:
- the start of real input parsing — turning a raw text blob into typed data
- the SWI text types (string vs. atom vs. code/char list) and `split_string/4`
- keeping the parser **deterministic** (today's lesson) so both parts reuse it
