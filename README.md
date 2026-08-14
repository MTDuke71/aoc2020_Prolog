# aoc2020_Prolog

> **The language in the repo name is history, not the current language.**
>
> This repo started as the Prolog leg of a language-rotation experiment, and
> the name is kept so old links, clones and remotes keep working. **Advent of
> Code 2020 is the point; the rotation is over. New work here is Python.**
>
> The Prolog tree (`src/`, `test/`, `bench/main.pl`) is **frozen**: it still
> builds, still passes, and is left exactly as it was. It is not maintained,
> not extended, and not something to port new Python solutions back into.

## Layout

| Path | What it is |
|---|---|
| `python/dayNN.py` | the solutions — `parse_input` / `part1` / `part2` / `solve` / `main` |
| `python/tests/test_dayNN.py` | one pytest module per solved day |
| `python/tests/conftest.py` | the `real_input` and `check_locked` fixtures |
| `python/bench.py` | per-phase timings, best and median of N runs |
| `Problem_Statements/days/` | puzzle text and function guides |
| `inputs/dayNN.txt` | puzzle inputs (gitignored — AoC asks they not be redistributed) |
| `src/`, `test/`, `bench/` | **frozen Prolog.** See the note above. |
| `tutorial/` | the Prolog tutorial phase. Also history. |

## Setup

Windows, no WSL. Virtualenv executables live in `Scripts\`, not `bin/`:

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install pytest ruff
```

## Test

```
.venv\Scripts\python.exe -m pytest
```

`pyproject.toml` sets `testpaths` and `pythonpath`, so a test module can just
say `import day03` — no package layout, no `sys.path` juggling.

Inputs are gitignored, so a fresh clone has none. Tests that need one **skip**
rather than fail, which keeps the suite green for a clone that has not
downloaded 25 files.

Each test module carries a `LOCKED` tuple of the day's real-input answers:

- `LOCKED = (part1, part2)` — asserted. A refactor that changes the answer fails.
- `LOCKED = None` — the test reports what the code currently produces and skips.

There is deliberately no third path. An answer nobody has submitted never gets
asserted against itself, so a green suite never implies more confidence than
somebody actually has.

## Format

```
.venv\Scripts\ruff.exe format python\
```

Line length 110. `include`/`exclude` in `pyproject.toml` fence ruff to
`python/` so it cannot reach the frozen tree.

## Bench

```
.venv\Scripts\python.exe python\bench.py          # every day with an input
.venv\Scripts\python.exe python\bench.py -n 20 11 # 20 reps, day 11 only
```

Reports best and median per phase. Best-of-N rather than one shot: most days
run in well under a millisecond, where single-run spread is wider than the
differences worth measuring.

## Solved

Day 0 is a tutorial dry run, not an AoC 2020 puzzle. See
[Problem_Statements/days/summary_2020.md](Problem_Statements/days/summary_2020.md)
for the day-by-day table.
