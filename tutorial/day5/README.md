# Tutorial Day 5: Accumulators and Tail Recursion

## Why this day matters
Large AoC inputs punish naive recursion patterns.

## Focus Topics
- Accumulator style predicates
- Tail recursion patterns
- Reversing at end vs prepending during traversal

## Learning Goals
- Rewrite at least one naive recursive predicate to accumulator form.
- Explain memory/performance tradeoff at a high level.

## REPL Drills
```prolog
?- foldl(plus, [1,2,3,4], 0, S).
?- reverse([1,2,3], R).
```

## Verification
- Keep both versions in code and test equivalence.
- Benchmark quick timing if useful.

## Exit Criteria
- You can spot when accumulator conversion is worth doing.
