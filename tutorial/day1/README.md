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
?- member_of(X, [10,20,30]).
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
