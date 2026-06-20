# Tutorial Day 4: Parsing Input Text

## Why this day matters
Most AoC bugs happen in parsing and normalization, not core algorithm logic.

## Focus Topics
- `split_string/4`
- Trimming and dropping empty lines
- Parsing integers safely
- Structuring parsed data for part1/part2 reuse

## Learning Goals
- Build robust `parse_input/2` handling trailing newlines.
- Convert line-oriented text to typed structures.
- Keep parser deterministic.

## REPL Drills
```prolog
?- split_string("a\nb\n", "\n", " \t\r", L).
?- maplist(number_string, Ns, ["10","20","30"]).
```

## Verification
- Tests for empty input, single line, and malformed line.
- Assert parser shape directly in tests.

## Exit Criteria
- You can write a parser once and reuse parsed data in both parts.
