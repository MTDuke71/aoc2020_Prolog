# Tutorial Day 9: Sorting, Grouping, and Counting

## Why this day matters
AoC often reduces to "transform then aggregate" pipelines.

## Focus Topics
- `sort/2` vs `msort/2`
- Grouping equal neighbors after sorting
- Counting occurrences and selecting maxima/minima

## Learning Goals
- Build histogram-like operations.
- Distinguish deduplicating vs stable-count sort behavior.

## REPL Drills
```prolog
?- sort([3,1,3,2], S).
?- msort([3,1,3,2], S).
```

## Verification
- Tests proving difference between `sort/2` and `msort/2`.

## Exit Criteria
- You can write one clean aggregate pipeline end-to-end.
