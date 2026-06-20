# Tutorial Day 7: CLP(FD) Constraints

## Why this day matters
Some AoC days are cleaner with constraints than manual brute force.

## Focus Topics
- `library(clpfd)`
- Domain constraints with `ins`
- Arithmetic constraints `#=`, `#<`, `#>`
- `labeling/2`

## Learning Goals
- Solve a small integer-constraint puzzle.
- Understand difference between `is` and `#=`.

## REPL Drills
```prolog
?- use_module(library(clpfd)).
?- X in 1..9, Y in 1..9, X + Y #= 10, labeling([], [X,Y]).
```

## Verification
- Tests should assert expected assignments or counts.

## Exit Criteria
- You can choose between plain arithmetic and CLP(FD) intentionally.
