# Tutorial Day 2: Lists and Pattern Matching

## Why this day matters
AoC in Prolog is list-heavy. If list recursion is comfortable, most puzzles become manageable.

## Focus Topics
- Head/tail pattern matching: `[H|T]`
- Base cases for empty lists: `[]`
- Recursive traversal and transformation
- Membership and filtering patterns

## Learning Goals
- Write at least two recursive list predicates from scratch.
- Explain why base case must come before recursive case in many predicates.
- Read stack-like recursive flow mentally.

## Suggested Practice Predicates
- `len_rec/2`
- `sum_rec/2`
- `reverse_rec/2` (naive first, accumulator version later)
- `count_if/3`

## REPL Drills
```prolog
?- [1,2,3] = [H|T].
?- member(X, [a,b,c]).
?- append([1,2], [3,4], R).
?- length([10,20,30], N).
```

## Verification
- Add tests for empty list, one-element list, and multi-element list.
- Confirm at least one predicate intentionally backtracks for multiple answers.

## Exit Criteria
- You can implement list recursion without looking up syntax.
- You can explain each variable binding in `[H|T]`.
