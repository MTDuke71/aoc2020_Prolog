# CLAUDE.md -- Advent of Code 2020, in Python

This is **Matt LaDuke's** AoC 2020 repo. The directory is named
`aoc2020_Prolog` for historical reasons; see "The name" below. Read this
file before helping on a first request in a new session.

## The name

The repo began as the Prolog leg of a language-rotation experiment. **That
rotation is over** -- juggling several languages at once was not working,
and Advent of Code itself is the point. The name is kept so existing
clones, links and remotes keep working.

Do not propose renaming the repo, and do not propose reviving the rotation.

## Language

**Python only.** Solutions live in `python/dayNN.py`.

Every day exposes the same five names:

- `parse_input(raw) -> structure` -- the **full** parse. Not a line split
  with the real work deferred into `part1`. If both parts need a derived
  structure that does not depend on which part is asking, it is built here.
- `part1(parsed) -> int`
- `part2(parsed) -> int`
- `solve(raw) -> (part1, part2)`
- `main() -> None` -- reads `INPUT`, prints `part1=... part2=...`

`INPUT` is resolved from `__file__`, not the working directory, so
`python python/day07.py` works from anywhere.

## The frozen Prolog tree

`src/`, `test/`, `bench/main.pl` and `tutorial/` are **frozen**. They still
work and are left in place, deliberately.

- Do not add new code there.
- Do not modify what is there.
- Do not offer to port Python solutions back into Prolog.
- Do not delete it, including the unsolved-day stubs.

`pyproject.toml` fences both ruff and pytest to `python/` so neither tool
can wander into it.

## Environment

Windows, **not WSL**. Virtualenv executables are in `Scripts\`, not `bin/`.

```
python -m venv .venv
.venv\Scripts\python.exe -m pytest
.venv\Scripts\ruff.exe format python\
.venv\Scripts\python.exe python\bench.py
```

Inputs downloaded on Windows can carry CRLF, so parsing must tolerate a
trailing `\r`. A per-line `.strip()` or `.splitlines()` handles it --
`block.split("\n")` does not, and that has already caused one real bug
(day06, where the surviving `\r` counted as a 27th customs answer). Every
day module has a CRLF test case.

## Testing

`plunit` is gone with the Prolog. Tests are **pytest**, one module per
solved day at `python/tests/test_dayNN.py`.

- Statement worked examples via `@pytest.mark.parametrize`, plus the edge
  cases the statement implies.
- A CRLF case.
- `LOCKED` and the `check_locked` fixture for real-input answers.

`LOCKED = (part1, part2)` asserts. `LOCKED = None` reports what the code
currently produces and skips. Never close that gap by pasting in whatever
the code printed -- the whole point is that an unverified answer cannot
masquerade as a verified one. A day goes green when a real accepted answer
is entered by hand.

The `real_input` fixture **skips** when a gitignored input is missing, so a
fresh clone stays green.

## Two standing rules

1. **If a solution leans on a non-obvious identity or shortcut, pin it as a
   test, not a claim in prose.** A claim no test checks is a claim that can
   rot. Day 5 rests on "the boarding pass read as a 10-bit number *is* the
   seat ID"; day 13 on Python's `%` being floored. Both are tests, not
   sentences.
2. **Anything stated as fact gets run and verified.** A timing, a language
   behaviour, an arithmetic result -- measure it or execute it. Do not
   recall it from memory and write it down as though it were checked.

## Per-day deliverable

1. `python/dayNN.py` with the five names above.
2. `python/tests/test_dayNN.py`.
3. `Problem_Statements/days/dayNN_function_guide.md`.
4. Row in `Problem_Statements/days/summary_2020.md`.
5. Bench timings when interesting.

## Function guides are the durable artifact

They always were, and they survive the language change. Write them for a
reader who is cold after 12+ months.

New guides are **Python-first**. Guides for days 00-13 were written during
the Prolog era and are frozen with a banner saying so; rewrite one when
that day is next touched rather than in a batch.

Each guide should include:

- Problem framing and representation choices.
- Function-by-function walkthrough.
- Why the algorithm is correct.
- Complexity discussion.
- A "if I were writing this in Rust" bridge section. Rust is the anchor
  language for comparisons and the corpus Matt returns to
  (`C:\Users\m_lad\Repos\rust_study`).
- Optional "possible optimization" sidebar, without forcing a rewrite.

## About the user

- 20+ year engineer, Software Program Manager; senior-level depth.
- EE by training, embedded C daily, Python for scripting.
- Bit/register/machine framings land well.
- Rust is the anchor for comparisons.
- **Matt reads code; the assistant writes it.** Pitch explanations at
  lead/PM altitude -- what and why and tradeoffs over syntax drills.
- Lead with a concrete numeric trace before stating an invariant
  abstractly.

`python/dayNN_mtl.py` files are Matt's own independent attempts. Do not let
them anchor a solution, and do not treat them as day modules.

## Optimization policy

Shipping source is readable Python first. Document faster alternatives in
the function guide as sidebars rather than replacing clear code with clever
opaque code.

## What not to do

- Do not suggest reviving the language rotation.
- Do not suggest renaming the repo.
- Do not add to, edit, or delete the frozen Prolog tree.
- Do not skip guides to increase day throughput.
- Do not assert an unverified answer as though it were confirmed.
