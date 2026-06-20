# Tutorial Day 10: Dynamic Predicates and Memoization

## Why this day matters
Some recursive AoC computations benefit from caching.

## Focus Topics
- `dynamic/1`
- `assertz/1`, `retractall/1`
- Memoization pattern and cleanup discipline

## Learning Goals
- Implement a memoized recursive predicate.
- Reset state between tests to avoid leakage.

## REPL Drills
```prolog
?- dynamic(cache/2).
?- assertz(cache(foo, 10)).
?- cache(foo, V).
?- retractall(cache(_, _)).
```

## Verification
- Tests must run in any order and still pass.

## Exit Criteria
- You can explain pros/cons of dynamic state in puzzle code.
