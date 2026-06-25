# Tutorial Day 2: Lists and Pattern Matching

## Why this day matters
AoC in Prolog is list-heavy. If list recursion is comfortable, most puzzles
become manageable. Day 1 introduced one list predicate (`sum_list_rec/2`); today
we build a small toolbox of four and look closely at the patterns they share.

## Focus Topics
- Head/tail pattern matching: `[H|T]`
- Base cases for empty lists: `[]`
- Recursive traversal and transformation
- Building a result list with `append/3`
- Conditional logic inside a clause with the `( Cond -> Then ; Else )` if-then-else

## Learning Goals
- Write at least two recursive list predicates from scratch.
- Explain why the base case must come before the recursive case in many predicates.
- Read stack-like recursive flow mentally (what happens on the way *down* vs. the
  way back *up*).
- Recognize when a predicate computes on the way back up (`len_rec`, `sum_rec`)
  vs. builds structure as it returns (`reverse_rec`).

## Files
- `day2.pl`: the four practice predicates, exported as a module.
- `day2_tests.pl`: executable `plunit` tests, one per predicate.

This is the same two-file split introduced on Day 1 (`basics.pl` +
`day1_tests.pl`) and the same shape the real AoC days use (`src/dayNN.pl` +
`test/dayNN_tests.pl`): one file *defines and exports* predicates and runs
nothing on its own; the other *loads and queries* them. If that split is fuzzy,
re-read "How the Two Files Fit Together" in `tutorial/day1/README.md`.

```prolog
:- module(day2, [len_rec/2, sum_rec/2, reverse_rec/2, count_even/2]).
```

That first line of `day2.pl` declares the module named `day2` and exports the
four predicates by `name/arity`. Everything below it is just clauses.

## Run the tests
From repo root:

```bash
swipl -q -s tutorial/day2/day2_tests.pl
```

If all five tests pass, you're set.

## Start the REPL
From repo root:

```bash
swipl
```

Then load today's file:

```prolog
?- ['tutorial/day2/day2.pl'].
```

You should see `true.`

## The Shared Shape: every predicate here is structural recursion

All four predicates follow the *exact* same skeleton — the one you met with
`sum_list_rec/2` on Day 1:

```prolog
predicate([],      BaseResult).            % base case: empty list
predicate([H|T],   Result) :-              % recursive case: peel off head H
    predicate(T,   SubResult),             % recurse on the tail first
    combine(H, SubResult, Result).         % then combine head with the sub-result
```

The two pieces to internalize:

- **`[H|T]`** splits a non-empty list into its **head** `H` (first element) and
  **tail** `T` (the rest). The `|` is the "cons" bar. `T` is just a variable
  name; the trailing letters are convention.
- **The recursive call runs before the combine step.** So Prolog drills all the
  way down to `[]` first, then does the real work (`+1`, `+X`, append, the
  even-check) *on the way back up* the stack. Hold onto this — every trace below
  is just that idea playing out.

The base case is written first because Prolog tries clauses top-to-bottom; you
want the stopping condition checked before the recursive one. (For these
predicates the two heads, `[]` and `[H|T]`, don't actually overlap, so order
doesn't change correctness here — but writing base-case-first is the habit that
*does* matter once clauses can both match.)

## Predicate Walkthroughs (line by line)

### `len_rec/2` — "how many elements?"

```prolog
len_rec([], 0).
```
**Base case (a fact).** The length of the empty list is `0`. The stopping point.

```prolog
len_rec([_|T], N) :-
    len_rec(T, N0),
    N is N0 + 1.
```
**Recursive case.**
- **Head:** match a non-empty list. We don't care *what* the first element is, so
  it's the **anonymous variable** `_` — we only need to know one element *exists*.
- **First body goal:** recurse on the tail, binding its length to `N0`.
- **Second body goal:** `N is N0 + 1` — add one for the head we skipped over.

`is` (not `=`) is essential: it **evaluates** the arithmetic on the right and
binds the number on the left. Plain `=` would bind `N` to the unevaluated term
`+(N0, 1)`. (Day 1 covers this gotcha in detail.)

Trace of `len_rec([a,b,c], N)` — the `+1`s happen on the way back up:

```text
len_rec([a,b,c], N)
  len_rec([b,c], N1),  then N is N1 + 1
    len_rec([c], N2),  then N1 is N2 + 1
      len_rec([], N3), then N2 is N3 + 1
        N3 = 0          (base case)
      N2 is 0 + 1 -> 1
    N1 is 1 + 1 -> 2
  N  is 2 + 1 -> 3
```

This is the built-in `length/2` rebuilt by hand. (`length/2` also runs
*backwards* to generate lists of a given length; our one-directional version
does not.)

### `sum_rec/2` — "add up a list"

```prolog
sum_rec([], 0).
sum_rec([X|T], Sum) :-
    sum_rec(T, Tail),
    Sum is X + Tail.
```

Identical skeleton to `len_rec/2`, with two differences: the head element is
**named** `X` (we need its value now, not just its existence), and the combine
step adds `X` instead of a constant `1`. This is the same predicate as Day 1's
`sum_list_rec/2`, renamed.

Trace of `sum_rec([1,2,3,4], S)`:

```text
sum_rec([1,2,3,4], S)
  sum_rec([2,3,4], T1),  then S is 1 + T1
    sum_rec([3,4], T2),  then T1 is 2 + T2
      sum_rec([4], T3),  then T2 is 3 + T3
        sum_rec([], T4), then T3 is 4 + T4
          T4 = 0          (base case)
        T3 is 4 + 0 -> 4
      T2 is 3 + 4 -> 7
    T1 is 2 + 7 -> 9
  S  is 1 + 9 -> 10
```

`len_rec` and `sum_rec` side by side make the pattern obvious: same recursion,
different `combine` — `+1` for counting, `+X` for summing. Change only the
combine step and you get `product_rec`, `max_rec`, and so on.

### `reverse_rec/2` — "flip a list" (the naive version)

```prolog
reverse_rec([], []).
```
**Base case.** The reverse of the empty list is the empty list.

```prolog
reverse_rec([X|T], R) :-
    reverse_rec(T, RT),
    append(RT, [X], R).
```
**Recursive case.**
- Reverse the **tail** first, giving `RT`.
- Then put the head `X` **at the end**: `append(RT, [X], R)` joins `RT` and the
  one-element list `[X]` into `R`.

`append/3` is the standard library list-concatenation predicate:
`append(A, B, C)` is true when `C` is `A` followed by `B`. Here we use it
forward, but it's relational — it can also *split* a list, which later days
exploit.

Trace of `reverse_rec([1,2,3], R)` — note the result is **built** by the
`append`s on the way back up:

```text
reverse_rec([1,2,3], R)
  reverse_rec([2,3], RT1),  then append(RT1, [1], R)
    reverse_rec([3], RT2),  then append(RT2, [2], RT1)
      reverse_rec([], RT3), then append(RT3, [3], RT2)
        RT3 = []             (base case)
      append([], [3], RT2)  -> RT2 = [3]
    append([3], [2], RT1)   -> RT1 = [3,2]
  append([3,2], [1], R)     -> R = [3,2,1]
```

**Why "naive"?** Each recursive step calls `append/3`, and `append` itself walks
its whole first argument. Appending to lists of length 0,1,2,…,n−1 costs
1+2+…+n steps, so this reverse is **O(n²)**. The classic fix is an *accumulator*:
carry the partial result down as an extra argument and prepend (`[X|Acc]`, which
is O(1)) instead of appending, giving an **O(n)** reverse. That's the
"accumulator version later" hinted in the practice list — a good Day 2+ exercise,
and exactly how the built-in `reverse/2` behaves.

#### Rust bridge

```rust
fn reverse_rec(list: &[i32]) -> Vec<i32> {
    match list {
        []                => vec![],
        [head, tail @ ..] => {
            let mut r = reverse_rec(tail);   // reverse the tail
            r.push(*head);                   // then put head at the end
            r
        }
    }
}
```

`r.push(head)` is the imperative cousin of `append(RT, [X], R)`. The Prolog
version pays the O(n²) price because it rebuilds the list rather than mutating a
`Vec` in place.

### `count_even/2` — "how many even numbers?"

```prolog
count_even([], 0).
count_even([X|T], N) :-
    count_even(T, N0),
    ( 0 is X mod 2 -> N is N0 + 1 ; N = N0 ).
```

Same counting skeleton as `len_rec/2`, but the head is now **conditional**: we
only add 1 when `X` is even. The new piece is the **if-then-else**:

```prolog
( Condition -> Then ; Else )
```

Read it as "if `Condition` succeeds, do `Then`; otherwise do `Else`." Here:

- **Condition:** `0 is X mod 2` — compute `X mod 2`; it equals `0` exactly when
  `X` is even. (`mod` is the modulo operator; `is` evaluates it.)
- **Then:** `N is N0 + 1` — count this element.
- **Else:** `N = N0` — leave the count unchanged. Note this is `=` (unification),
  not `is`, because nothing needs evaluating; we're just saying "`N` is whatever
  `N0` was."

The `->` commits to the first branch whose condition succeeds — it acts like a
local cut, so there's no backtracking *between* the `Then` and `Else` arms. This
is the idiomatic way to write a per-element conditional without splitting into two
separate clauses.

Trace of `count_even([1,2,3,4,6], N)` — the conditional fires on the way back up:

```text
count_even([1,2,3,4,6], N)
  count_even([2,3,4,6], N1)         1 is odd -> N  is N1 + 0... actually N = N1
    count_even([3,4,6], N2)         2 is even -> N1 is N2 + 1
      count_even([4,6], N3)         3 is odd  -> N2 = N3
        count_even([6], N4)         4 is even -> N3 is N4 + 1
          count_even([], N5)        6 is even -> N4 is N5 + 1
            N5 = 0                  (base case)
          N4 is 0 + 1 -> 1          (6 even)
        N3 is 1 + 1 -> 2            (4 even)
        N2 = 2                      (3 odd, unchanged)
      N1 is 2 + 1 -> 3              (2 even)
    N = 3                           (1 odd, unchanged)
```

Three evens (`2, 4, 6`), so `N = 3`.

#### Rust bridge

```rust
fn count_even(list: &[i32]) -> i32 {
    match list {
        []                => 0,
        [head, tail @ ..] => {
            let rest = count_even(tail);
            if head % 2 == 0 { rest + 1 } else { rest }   // the ( -> ; ) arm
        }
    }
}
```

Prolog's `( 0 is X mod 2 -> N is N0+1 ; N = N0 )` is just an `if/else`
expression. The difference is that Prolog's condition is a *goal that can fail*
rather than a `bool` — and `->` discards the choice points the condition created,
which is why this doesn't leave the predicate able to backtrack.

The general practice-list name for this is `count_if/3` (count elements
satisfying *any* predicate); `count_even/2` is that idea specialized to one fixed
test. Generalizing it — passing the test in as a goal and applying it with
`call/1` — is a natural next exercise.

## The Tests, One by One

`day2_tests.pl` poses one goal per predicate. Recall the Day 1 idea: **a test
passes when its goal can be proven true**, and `assertion/1` additionally checks
that a bound value is what we expect.

| Test | What it calls | What it checks |
|---|---|---|
| `len_empty` | `len_rec([], N)` | `assertion(N == 0)` — the base case alone |
| `len_three` | `len_rec([a,b,c], N)` | `assertion(N == 3)` — multi-element recursion (note: works on atoms, not just numbers, since `len_rec` never inspects the elements) |
| `sum_list` | `sum_rec([1,2,3,4], S)` | `assertion(S == 10)` |
| `reverse_list` | `reverse_rec([1,2,3], R)` | `assertion(R == [3,2,1])` |
| `count_even` | `count_even([1,2,3,4,6], N)` | `assertion(N == 3)` — the conditional, with both odd and even inputs |

```prolog
:- begin_tests(day2).
:- use_module('./day2.pl').   % the link: makes day2's predicates callable here

test(len_empty)    :- len_rec([], N),            assertion(N == 0).
test(len_three)    :- len_rec([a,b,c], N),       assertion(N == 3).
test(sum_list)     :- sum_rec([1,2,3,4], S),     assertion(S == 10).
test(reverse_list) :- reverse_rec([1,2,3], R),   assertion(R == [3,2,1]).
test(count_even)   :- count_even([1,2,3,4,6], N),assertion(N == 3).

:- end_tests(day2).
:- initialization(main, main).
main(_) :- ( run_tests -> halt(0) ; halt(1) ).
```

`==` (not `=`) is used in the assertions: it tests that the two terms are
**already identical**, with no unification/binding. After the goal has run, `N`
is bound to a concrete number, so `==` is the right "did we get exactly this?"
check. The final three lines make the file double as a runnable program: it runs
the tests and exits `0` on pass, `1` on failure — handy for CI.

## First Queries (with expected behavior)

Try each in the REPL after loading `day2.pl`:

```prolog
?- len_rec([10,20,30], N).
N = 3.
```

Careful — `len_rec/2` returns `N = 3` (the *count* of elements), not `60` (their
sum). The built-in `length([10,20,30], N)` gives the same `N = 3`; `len_rec/2` is
our hand-rolled equivalent. Use `sum_rec/2` when you want the total:

```prolog
?- sum_rec([5,5,5], S).
S = 15.

?- reverse_rec([a,b,c,d], R).
R = [d,c,b,a].

?- count_even([2,4,6,8], N).
N = 4.

?- count_even([1,3,5], N).
N = 0.
```

## REPL Drills (core list built-ins)
These exercise the library predicates that underpin today's code:

```prolog
?- [1,2,3] = [H|T].        % H = 1, T = [2,3]   -- unifying against [H|T]
?- member(X, [a,b,c]).     % X = a ; X = b ; X = c   (press ; to enumerate)
?- append([1,2], [3,4], R).% R = [1,2,3,4]      -- the predicate reverse_rec uses
?- length([10,20,30], N).  % N = 3              -- built-in cousin of len_rec/2
```

`member/2` enumerates on backtracking (press `;`) — that's the "intentionally
backtracks for multiple answers" case from the verification checklist below.

## Standard Library Cheat-Sheet (you don't have to hand-roll these)

Everything we wrote today already exists in SWI-Prolog's standard library. We
build them by hand to *learn the recursion* — but in real AoC solutions you'd
reach for the library version. Here's the mapping:

| Our hand-rolled predicate | Library equivalent | Lives in |
|---|---|---|
| `len_rec/2` | `length/2` | `library(lists)` |
| `sum_rec/2` | `sum_list/2` (alias `sumlist/2`) | `library(lists)` |
| `reverse_rec/2` (naive O(n²)) | `reverse/2` (O(n), accumulator-based) | `library(lists)` |
| `count_even/2` | `include/3` + `length/2`, or `aggregate_all/3` | `library(apply)` / `library(aggregate)` |

```prolog
?- length([a,b,c], N).            N = 3.
?- sum_list([1,2,3,4], S).        S = 10.
?- reverse([1,2,3], R).           R = [3,2,1].
```

There's no single built-in for "count the evens," but two idiomatic one-liners do
it. **Filter then measure** with `include/3` (keep elements that satisfy a goal):

```prolog
?- include([X]>>(0 is X mod 2), [1,2,3,4,6], Evens), length(Evens, N).
Evens = [2,4,6], N = 3.
```

The `[X]>>(0 is X mod 2)` is a **yall lambda** (`library(yall)`) — an inline,
anonymous predicate, like a Rust closure `|x| x % 2 == 0`. Or **count directly**
with `aggregate_all/3`:

```prolog
?- aggregate_all(count, (member(X, [1,2,3,4,6]), 0 is X mod 2), N).
N = 3.
```

### Two layers of "standard library"

- **ISO built-ins** — always available, no import: `is/2`, `=/2`, `==/2`, `</2`,
  `findall/3`, `call/1`, `!/0`, `append/3`, `member/2`, …
- **`library(...)` modules** — loaded with `:- use_module(library(name))`:
  `lists`, `apply` (`maplist/foldl/include/exclude`), `aggregate`, `pairs`,
  `assoc` (tree-maps), `dcg/basics` (parsing).

In SWI, `library(lists)` and `library(apply)` are **autoloaded** — that's why our
test files call `append/3` and `length/2` with no `use_module`. Convenient, but in
the real `src/dayNN.pl` files prefer the explicit `:- use_module(library(lists)).`
so the dependency is visible and the code stays portable.

The big payoff predicates for AoC — the ones that collapse the hand-written
recursion above into one line — are `maplist/2..5` (≈ Rust `.map`), `foldl/4..6`
(≈ `.fold`, the accumulator pattern), `include/3`/`exclude/3` (≈ `.filter`), and
`findall/3`/`aggregate_all/3` (≈ collect into a `Vec` / `.count()`/`.sum()`).

### Explore the library yourself

```prolog
?- apropos(reverse).                     % fuzzy-search the docs for a term
?- help(append/3).                        % full doc for one predicate (in REPL)
?- predicate_property(member(_,_), P).    % is it built-in? autoloaded? from where?
```

Full reference: <https://www.swi-prolog.org/pldoc/>.

## Verification
- Tests cover the empty list (`len_empty`), and multi-element lists for every
  predicate.
- For the "one element" and "backtracking" checkpoints, drill in the REPL:
  `len_rec([x], N)` (expect `N = 1`) and `member(X, [a,b,c])` (press `;` to get
  all three answers).

## Common Gotchas (carried from Day 1, plus today's)
- `=` vs `is`: use `is` to *evaluate* arithmetic (`N is N0 + 1`), `=` only to
  *unify* (`N = N0`). Mixing them up is the #1 day-2 bug.
- `=` vs `==` in tests: `=` would *bind*; `==` checks already-bound terms are
  identical. Assertions want `==`.
- Naive `reverse_rec/2` is O(n²); don't reach for it on large lists — use an
  accumulator or the built-in `reverse/2`.
- Forgetting the base case gives infinite recursion (or, here, plain failure when
  you hit `[]` with no matching clause).

## Exit Criteria
- You can implement `len_rec`, `sum_rec`, and `count_even` without looking up
  syntax.
- You can explain each variable binding in `[H|T]`.
- You can explain why the additions/counts happen on the way back *up* the
  recursion.
- You can read the `( Cond -> Then ; Else )` if-then-else and say what each arm
  does.
- You can explain why naive `reverse_rec/2` is O(n²) and sketch the O(n) fix.

## Next Step
Day 3 builds on this with:
- deterministic vs. nondeterministic predicates and what a **choicepoint** is
- the cut (`!`) — green vs. red cuts, and when *not* to use it
- `once/1` and the `( Cond -> Then ; Else )` if-then-else as tamer alternatives
