# CLAUDE.md -- AoC 2020 in Prolog

This is **Matt LaDuke's** AoC 2020 / Prolog repo, the third leg of
a planned language-rotation run. Use this file to orient on
conventions, working style, and cross-repo context before helping on
a first request in a new session.

## The language rotation

| Year | Language | Repo |
|-----:|----------|------|
| 2017 | Rust + Python side-by-side | `../rust_study/advent_of_code/aoc2017/` |
| 2018 | Haskell | `../aoc2018_Haskell/` |
| 2019 | Racket | `../aoc2019_racket/` |
| 2020 | Prolog | **this repo** |
| 2021 | OCaml | (planned) |
| all other years | Rust | scattered |

**Why this rotation exists:** breadth-first language exposure across
paradigms. The goal is reading fluency and transferable problem
solving, not deep specialization in one language.

## Timeline and cadence

- Tutorial phase: 11 days.
- AoC 2020 proper starts: **2026-07-01**.
- Tutorial is expected to run from **2026-06-20** through
  **2026-06-30**.

## About the user

- 20+ year engineer; senior-level depth.
- Rust is the anchor language for comparisons.
- Comfortable with compiler/VM and algorithmic vocabulary.
- Workflow preference: assistant writes code, user reads and reviews.

## Working style

- Language-first on initial walkthroughs: focus on Prolog mechanics,
  unification, backtracking, cuts, recursion, and data modeling.
- Algorithm-depth on demand: if asked "why this works" or "prove it",
  go all the way down with correctness arguments and performance tradeoffs.
- Name algorithms in standard literature terms so techniques transfer.
- If syntax frustration appears, pivot back to algorithmic structure.

## Project shape (target)

```text
aoc2020_Prolog/
  tutorial/
    day1/ ... day11/
  src/
    day00.pl .. day25.pl
    common/
  test/
    day00_tests.pl .. day25_tests.pl
  bench/
    main.pl
  Problem_Statements/
    days/
      dayNN.md
      dayNN_function_guide.md
      summary_2020.md
  python/
    dayNN.py
  inputs/
    dayNN.txt
```

Notes:
- Keep one main source file per day in `src/`.
- Use SWI-Prolog as the default runtime unless explicitly changed.
- Use `plunit` for tests.

## Per-day deliverable

Each solved day should include:

1. Source file in `src/dayNN.pl` with clear predicate contracts in comments,
   plus a consistent shape:
   - `parse_input/2`
   - `part1/2`
   - `part2/2`
   - `solve/3` (or `solve/2` returning both answers)
2. Test file in `test/dayNN_tests.pl`:
   - puzzle example tests
   - real-input answer locks for part 1 and part 2
3. Bench hook in `bench/main.pl` with parse/part timings when practical.
4. Function guide at
   `Problem_Statements/days/dayNN_function_guide.md`.
5. Python algorithm reference in `python/dayNN.py` for every day
   (cross-validates the Prolog answers in a second language).
6. Summary row in `Problem_Statements/days/summary_2020.md`.

## Function guides are the durable artifact

Guides should be written for a reader who is cold after 12+ months.
Restate key Prolog forms and cross-link days aggressively.

Each guide should include:
- Problem framing and representation choices.
- Predicate-by-predicate walkthrough.
- Why the algorithm is correct.
- Complexity discussion.
- "If I were writing this in Rust" bridge section.
- Optional optimization sidebar without forcing premature rewrites.

## Optimization policy

- Shipping source should be idiomatic and readable Prolog first.
- Faster alternatives can be documented in the function guide as
  "Possible optimization" sidebars.
- Prefer correctness + clarity in `src/`; keep deep optimization
  experimental unless required.

## Tutorial policy (11 days)

Tutorial outputs live under `tutorial/dayN/README.md` and small,
working `.pl` examples.

Goals of tutorial phase:
- Build fast reading fluency for core Prolog constructs.
- Establish daily solve/test/guide rhythm.
- Prepare directly for AoC day files starting July 1.

## What not to do

- Do not suggest abandoning the language rotation.
- Do not force write-drill exercises unless explicitly requested.
- Do not skip guides just to increase day throughput.
- Do not replace readable source with clever but opaque tricks by default.

## Likely first requests

Expect requests to:
1. Scaffold the repo layout.
2. Settle Prolog toolchain details (runtime, test command, bench script).
3. Create tutorial day 1 with code + guide.
4. Set up a repeatable solve/test template for upcoming AoC days.
