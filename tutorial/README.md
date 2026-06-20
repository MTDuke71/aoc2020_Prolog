# Prolog Crash Course (Days 1-11)

This tutorial track is designed so that by July 1 your attention can be on AoC algorithms, not Prolog syntax friction.

## How to Use This Track
1. Work one day at a time in order.
2. Run each day's tests before moving on.
3. In REPL, run the listed drill queries until answers feel predictable.
4. Keep notes in each day folder if something is confusing.

## Daily Progression
- Day 1: Facts, rules, unification, backtracking, basic recursion
- Day 2: Lists, pattern matching, recursive list traversal
- Day 3: Determinism, choicepoints, cuts (`!`), and control flow
- Day 4: Input parsing with strings, splitting, and normalization
- Day 5: Accumulators and tail recursion
- Day 6: Search and state modeling (graphs/grids style)
- Day 7: CLP(FD) basics for constraints and bounded search
- Day 8: Assoc/dict usage for lookup-heavy workloads
- Day 9: Sorting, grouping, and counting patterns
- Day 10: Dynamic predicates and memoization tradeoffs
- Day 11: AoC simulation day (parse + part1 + part2 + tests)

## Standard Commands
Run one day tests:

```bash
swipl -q -s tutorial/dayN/dayN_tests.pl
```

Start REPL:

```bash
swipl
```

Load a day file in REPL:

```prolog
?- ['tutorial/dayN/dayN.pl'].
```

## Done Means
- You can predict behavior before running most queries.
- You can explain where backtracking occurs.
- You can write and test `parse_input/2`, `part1/2`, `part2/2`, `solve/3` without scaffolding help.
