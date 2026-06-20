# Tutorial Day 8: Maps and Lookup Structures

## Why this day matters
Frequency counts and key-value lookups are common AoC building blocks.

## Focus Topics
- `library(assoc)`
- Dict basics
- Update and lookup patterns

## Learning Goals
- Build a frequency table from input tokens.
- Compare assoc/dict style readability.

## REPL Drills
```prolog
?- empty_assoc(A0), put_assoc(a, A0, 1, A1), get_assoc(a, A1, V).
?- D0 = _{}, D = D0.put(foo, 42), V = D.foo.
```

## Verification
- Tests for missing key and repeated key increments.

## Exit Criteria
- You can pick a map structure and use it consistently in a solution.
