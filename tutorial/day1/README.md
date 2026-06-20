# Tutorial Day 1: Facts, Rules, and Backtracking

This is a true first-contact walkthrough.
If Prolog feels strange right now, that is normal.

You will learn:
- facts
- rules
- unification (matching)
- backtracking (searching for more answers)
- simple recursion

## Learning Goals
- Read and write basic facts and rules.
- Predict what Prolog will return for a query.
- See recursion through a small `ancestor/2` rule.
- Run `plunit` tests in SWI-Prolog.

## Files
- `basics.pl`: small knowledge base and list predicates.
- `day1_tests.pl`: executable `plunit` tests.

## Mental Model (2 minutes)
Prolog is not "do this, then this" like Python/Rust.
You mostly:
1. Define truths (facts).
2. Define relationships (rules).
3. Ask questions (queries).

Prolog tries to prove your query from facts/rules.
- If it can prove it: `true`.
- If it cannot: `false`.
- If there are variables, it may return bindings like `X = 10`.

## What Kind of Language Is Prolog?

Prolog is a **logic programming** language — a genuinely different family from
the rest of the rotation.

| Paradigm | You write... | Rotation example |
|---|---|---|
| Imperative / procedural | step-by-step commands that mutate state | Rust, Python |
| Functional | expressions and value transformations | Haskell, Racket |
| **Logic** | **facts and rules; the engine searches for what's true** | **Prolog** |

It is the first **declarative** language in the run where you don't write an
algorithm in the usual sense. You state *what relationships hold* and a built-in
search engine works out *how* to satisfy your query. In this day's code you never
wrote a loop to walk the family tree — you declared `ancestor/2` and Prolog did
the searching.

More precisely, Prolog is:

- **Logic / declarative** — a program is a set of clauses (facts + rules).
  Running it = asking whether something can be *proven* from those clauses.
- **Relational, not functional** — predicates are relations, not functions.
  `parent(alice, bob)` returns nothing; it is simply true or false. That is why a
  predicate runs "backwards" too: `parent(X, bob)` asks *who* is bob's parent
  using the same clause.
- **Powered by three engine mechanics** — unification (two-way matching),
  backtracking (try alternatives on failure), and resolution (the proof search).
  These are the "runtime" you are really learning.
- **Dynamically typed** — no type declarations; the one data structure is the
  **term** (atoms, numbers, variables, and compound terms like
  `parent(alice, bob)`). Lists are just nested terms.
- **Homoiconic** — code *is* data. `parent(alice, bob)` is both a clause you can
  run and a term you can inspect and build (the same idea as Racket s-expressions).

### The mental flip from Rust

In Rust *you* are the planner: you choose the control flow, the loops, the order
of operations. In Prolog you are closer to **writing a spec and handing it to a
solver** — you describe the shape of a valid answer and the engine explores the
possibilities, backtracking through dead ends on its own.

The catch (it will show up in later days): the search still has a concrete
operational behavior — clause order matters, backtracking has a cost, and `!`
(the cut) prunes the search. Prolog is declarative in spirit, but you must
understand the procedural reality underneath when termination or performance
matters. That tension is much of what makes Prolog interesting.

## Start Here: Run the tests
From repo root:

```bash
swipl -q -s tutorial/day1/day1_tests.pl
```

If all tests pass, your environment is working.

## Start the REPL
From repo root:

```bash
swipl
```

Then load the tutorial file:

```prolog
?- ['tutorial/day1/basics.pl'].
```

You should see `true.`

## First Queries (with expected behavior)

### 1) Fact lookup

```prolog
?- parent(alice, bob).
true.
```

This is asking: "Is `parent(alice, bob)` true in the knowledge base?"

### 2) Fact that does not exist

```prolog
?- parent(bob, alice).
false.
```

### 3) Rule that uses recursion

```prolog
?- ancestor(alice, diana).
true.
```

`ancestor/2` works both for direct parent and parent-of-parent chains.

### 4) Query with a variable

```prolog
?- 
X = 10 ;
X = 20 ;
X = 30.
```

What happened:
- `X` is uppercase, so it is a variable.
- Prolog found one answer, then waits.
- Press `;` to ask for another answer.
- Press Enter (without `;`) to stop searching.

### 5) Recursive list sum

```prolog
?- sum_list_rec([1,2,3,4], Sum).
Sum = 10.
```

## How Prolog Solves a Query (step-by-step)
Use this query:

```prolog
?- ancestor(alice, diana).
```

How resolution proceeds conceptually:
1. Try first rule: `ancestor(X, Y) :- parent(X, Y).`
2. Substitute `X = alice`, `Y = diana`; now need `parent(alice, diana)`.
3. That fact does not exist, so backtrack to another rule.
4. Try recursive rule: `ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).`
5. Need `parent(alice, Z)`; first match gives `Z = bob`.
6. Now solve `ancestor(bob, diana)` recursively.
7. Repeat until `parent(carol, diana)` is matched.
8. Query is proven, so answer is `true`.

This is the core Prolog loop:
- try a clause
- unify terms
- recurse/go deeper
- backtrack on failure

## What To Look For
- `ancestor/2` demonstrates recursion + transitive relationships.
- `member_of/2` demonstrates backtracking across list elements.
- `sum_list_rec/2` shows structural recursion over lists.

## Predicate Walkthroughs (line by line)

Both predicates lean on the **list pattern `[H|T]`**:
- `[X|Xs]` means "a list whose **head** (first element) is `X` and whose **tail**
  (everything after) is `Xs`."
- The `|` is the "cons" bar — it splits the front element from the rest.
- `Xs` is just a variable name; the trailing `s` is a convention for "a list."

### `member_of/2` — "is X somewhere in this list?"

```prolog
member_of(X, [X|_]).
```
**The base case (success).** No `:-`, so this is a **fact**. The *same* variable
`X` sits in both the search slot and the list head, so unification makes this
clause match only when the thing you are looking for **is the head of the list**.
`_` is the **anonymous variable** — "don't care what the tail is."

```prolog
member_of(X, [_|Xs]) :-
    member_of(X, Xs).
```
**The recursive case ("keep looking").** Here `_` is the head ("don't care what
the first element is") and `Xs` is the tail. Read it: "X is a member of the list
**if** X is a member of the tail." We drop the head and ask the same question
about the shorter list.

Trace of `member_of(20, [10,20,30])`:
1. Clause 1 needs `20` to unify with head `10`. Fails.
2. Clause 2: tail `Xs = [20,30]`, so ask `member_of(20, [20,30])`.
3. Clause 1 now needs `20` to unify with head `20`. Succeeds.

There is **no clause for `[]`** on purpose: run off the end of the list and every
clause fails, so the query returns `false`. "Not found" = "can't be proven."
With an unbound variable, both clauses apply, which is why `member_of(X, [10,20,30])`
**enumerates** `X = 10 ; X = 20 ; X = 30` on backtracking.

### `sum_list_rec/2` — "add up a list"

```prolog
sum_list_rec([], 0).
```
**The base case.** A fact: "the sum of the empty list is `0`." This is the
stopping point every recursion needs.

```prolog
sum_list_rec([X|Xs], Sum) :-
    sum_list_rec(Xs, TailSum),
    Sum is X + TailSum.
```
**The recursive case.**
- **Head:** match a non-empty list as head `X` + tail `Xs`. `Sum` is just a name
  here — not computed yet; the body will fill it in.
- **First body goal:** recurse on the tail, binding its total to `TailSum`. This
  call drills all the way down to `[]` before anything is added.
- **Second body goal:** `Sum is X + TailSum` — now compute head plus tail-sum.

`is` is critical (and a classic day-1 gotcha): it means **"evaluate the
arithmetic on the right, bind the result on the left."** With plain `=`,
`Sum = X + TailSum` would bind `Sum` to the unevaluated *term* `+(1,6)`, not the
number `7`. `=` is unification; `is` forces real arithmetic.

Trace of `sum_list_rec([1,2,3], S)` — note the additions happen **on the way
back up**, because the recursive call (line 1 of the body) runs before the `is`
(line 2):

```text
sum_list_rec([1,2,3], S)
  sum_list_rec([2,3], T1),  then S is 1 + T1
    sum_list_rec([3], T2),  then T1 is 2 + T2
      sum_list_rec([], T3), then T2 is 3 + T3
        T3 = 0            (base case)
      T2 is 3 + 0  -> 3
    T1 is 2 + 3  -> 5
  S is 1 + 5  -> 6
```

### Rust bridge

Both are the Prolog spelling of a recursive `match`:

```rust
fn member_of(x: i32, list: &[i32]) -> bool {
    match list {
        [head, ..] if *head == x => true,        // clause 1: head matches
        [_, tail @ ..]           => member_of(x, tail), // clause 2: recurse
        []                       => false,        // Prolog gets this for free
    }
}

fn sum_list_rec(list: &[i32]) -> i32 {
    match list {
        []                => 0,                   // base case
        [head, tail @ ..] => head + sum_list_rec(tail), // recurse, then add
    }
}
```

Two differences worth holding onto: (1) Prolog splits the `match` arms into
**separate clauses** tried top-to-bottom with backtracking, and (2) Prolog's
`member_of` is *relational* — give it an unbound variable and the same code
**enumerates** the list instead of testing one value, which the Rust `bool`
version cannot do.

## Tiny Syntax Cheatsheet
- A fact or rule ends with `.`
- Query prompt is `?-`
- Variables start with uppercase: `X`, `Sum`
- Atoms/identifiers are lowercase: `alice`, `parent`
- `:-` means "is true if"

Example rule shape:

```prolog
head(X) :- condition1(X), condition2(X).
```

Read as: `head(X)` is true if both conditions are true.

## Why Does Everything End With a `.` ?

Short version: the `.` (a "fullstop") means **"this thing is finished, you can
process it now."** It is not a separator like `;` in Rust or C. It is an
end-of-clause marker.

A "clause" is the basic unit Prolog reads: one fact, one rule, one directive,
or one query. A clause can sprawl across many lines:

```prolog
ancestor(X, Y) :-
    parent(X, Z),
    ancestor(Z, Y).
```

That whole block is **one clause**. Prolog can't use newlines to know you're
done, because you use newlines just for tidiness. There are no `{ }` braces and
no `end` keyword either. So Prolog needs *some* explicit "I'm done" signal — and
that signal is the `.`

### The one rule that trips people up

The period must be followed by **whitespace** (a space, a newline, or the end of
the file). That is how Prolog tells a *clause-ending* dot apart from a dot inside
something:

```prolog
3.14          % dot glued to digits -> still just a number
end_of_list.  % dot + newline       -> end of the clause
```

So `foo.bar` is *not* a clause end; `foo.` followed by Enter is.

### Same dot everywhere (this is the cool part)

Facts, rules, directives, and even the questions you type at the `?-` prompt all
end the same way, because to Prolog they are all just **terms** — one kind of
object:

```prolog
parent(alice, bob).                 % fact
ancestor(X, Y) :- parent(X, Y).     % rule
:- use_module(library(lists)).      % directive (runs at load time)
?- member_of(X, [10,20,30]).        % query you type yourself
```

Loading a file is literally: "read one term up to its `.`, store it, repeat."
Typing a query is the same: the `.` says "that's my whole question, go answer
it." One terminator for everything, because everything is the same kind of
thing.

### Why you sometimes see the REPL just "hang"

If you type a query and forget the `.`, Prolog thinks your term isn't finished
and keeps waiting for more input. It isn't broken — it just hasn't seen the dot
yet. Type the `.` and press Enter.

### Rust bridge

Closest Rust feelings: the `;` that ends a `let` statement, plus the way a REPL
needs a *complete* expression before it runs. Difference: Prolog has exactly
**one** terminator for facts, rules, directives, *and* queries — Rust spreads
that job across `;`, `{ }`, and grammar keywords.

## What Does the `/2` After a Name Mean?

First, a word swap that matters: these are **predicates**, not functions. A
function takes inputs and *returns a value*. A Prolog predicate is a
*relation* that just **succeeds or fails** (and may bind some variables along
the way). Say "predicate" and a lot of Prolog stops feeling weird.

The `/2` is the **arity** — how many arguments the predicate takes. The shape is
`name/arity`:

```prolog
ancestor(alice, diana).   % ancestor/2  -> 2 arguments
member_of(X, [10,20,30]). % member_of/2 -> 2 arguments
halt.                     % halt/0      -> 0 arguments
```

You only *write* the `/2` when you are **talking about** a predicate (in docs,
module exports, error messages). You never type it when you actually **call**
the predicate.

### The surprising part: name + arity is the identity

The name alone does **not** identify a predicate. The name **and** the arity
together do. So `foo/2` and `foo/3` are two completely separate, unrelated
predicates that merely share a spelling — no overloading, no default arguments.
They are as different as if they had different names:

```prolog
write(X).         % write/1 -> write to current output
write(Stream, X). % write/2 -> write to a specific stream
```

You already rely on this in `basics.pl`, where the module export list names each
predicate by `name/arity`:

```prolog
:- module(day1_basics, [
    parent/2,
    ancestor/2,
    member_of/2,
    sum_list_rec/2
]).
```

The `/2` is how the module says *exactly which* predicate to export. Add a
3-argument version and you would export it separately as `ancestor/3`.

### Rust bridge

There is no clean equivalent — Rust picks overloads via types and traits. Closest
mental hook: pretend `fn foo(a)` and `fn foo(a, b)` were not overloads but two
*distinct items* you always had to refer to as `foo#1` and `foo#2`, and that
suffix showed up in every import and every error message. That suffix is
`/arity`. The standard library docs are organized this way too — you look up
`append/3` or `nth0/3`, not just `append`.

## Common Beginner Gotchas
- Missing final `.` in a query or fact.
- Using lowercase for variables (`x` is not a variable).
- Forgetting to load the file before querying.
- Confusing `=` (unification) with arithmetic evaluation.

For arithmetic in this tutorial, we use `is`, for example:

```prolog
Sum is X + TailSum.
```

## Mini Drills (do these in REPL)
1. List all children of `alice`:

```prolog
?- parent(alice, Child).
```

2. Ask for all ancestors known from the graph:

```prolog
?- ancestor(alice, Descendant).
```

Press `;` repeatedly to enumerate all solutions.

3. Verify membership failure:

```prolog
?- member_of(99, [10,20,30]).
false.
```

4. Sum edge case:

```prolog
?- sum_list_rec([], Sum).
Sum = 0.
```

## Day 1 Exit Criteria
- You can explain what a fact is and what a rule is.
- You can load a file in REPL without looking up syntax.
- You can read at least one variable-binding answer (`X = ...`).
- You can use `;` to request more solutions.
- You can describe why `ancestor/2` is recursive.

## If You Get Stuck
- Reload file in REPL: `['tutorial/day1/basics.pl'].`
- Exit REPL: `halt.` or Ctrl+D
- Re-run tests: `swipl -q -s tutorial/day1/day1_tests.pl`

## Next Step
After this feels comfortable, Day 2 should add:
- pattern matching on more complex terms
- cuts (`!`) and when to avoid overusing them
- more list-processing predicates
