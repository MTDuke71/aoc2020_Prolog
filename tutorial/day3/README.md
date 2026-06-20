# Tutorial Day 3: Determinism, Choicepoints, and Cuts

## Why this day matters
Unintended choicepoints can hurt both clarity and performance on AoC inputs.

## Focus Topics
- Deterministic vs nondeterministic predicates
- Where choicepoints come from
- `once/1` and cut (`!`) basics
- If-then-else style with `->` and `;`

## Learning Goals
- Identify when a predicate should produce one answer vs many.
- Remove accidental extra solutions.
- Use cut conservatively and intentionally.

## REPL Drills
```prolog
?- member(X, [1,2,3]).
?- once(member(X, [1,2,3])).
?- (1 < 2 -> writeln(ok) ; writeln(no)).
```

## Verification
- Write one predicate with intended backtracking.
- Write one predicate that should be deterministic and enforce it.
- Add tests that fail if extra solutions appear.

## Exit Criteria
- You can explain what a choicepoint is in plain language.
- You know at least one case where using cut is a bad idea.
