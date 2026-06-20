# Tutorial Day 11: AoC Dry Run (Full Workflow)

## Why this day matters
This day rehearses the exact structure you will use from July 1 onward.

## Focus Topics
- File layout discipline
- Parse-once pattern
- Part 1 and Part 2 predicate separation
- plunit answer locks

## Learning Goals
- Build one mini puzzle solution in final AoC shape:
  - `parse_input/2`
  - `part1/2`
  - `part2/2`
  - `solve/3`
- Add tests for example and real-style input.

## Suggested Checklist
1. Parse into explicit structure.
2. Solve part 1 deterministically.
3. Solve part 2 using same parsed data.
4. Add tests for parser, part1, part2.
5. Add one performance note in comments.

## Verification
Run:

```bash
swipl -q -s tutorial/day11/day11_tests.pl
```

## Exit Criteria
- You can implement a day skeleton without looking up conventions.
- You are ready to start AoC Day 1 with algorithm-first focus.
