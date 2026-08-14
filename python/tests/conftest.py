"""Shared fixtures for the day test modules.

Two problems this file exists to solve:

1. Puzzle inputs are gitignored (AoC asks that they not be redistributed), so
   a fresh clone has no inputs/ at all.  Tests that need one must *skip*, not
   fail -- otherwise the suite is red for everybody who did not personally
   download 25 files.  That is `real_input`.

2. An answer nobody has submitted is not an answer.  If a test asserted
   whatever the code happened to print, it would pass by construction and
   prove nothing.  That is `check_locked`: it asserts only against a value a
   human has confirmed, and otherwise reports.  See LOCKED below.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = REPO_ROOT / "inputs"


@pytest.fixture(scope="session")
def real_input():
    """Return `load(day) -> str`, skipping the test when the input is absent.

    Reads with newline="" left at the default, i.e. universal newlines: a
    CRLF file arrives as \n-separated text.  Solutions must still tolerate a
    stray \r on their own (see the crlf test in every day module) because
    input can also reach parse_input from a string literal or a byte read that
    did no translation.
    """

    def load(day: int) -> str:
        path = INPUT_DIR / f"day{day:02d}.txt"
        if not path.exists():
            pytest.skip(f"no {path.relative_to(REPO_ROOT)} (inputs are gitignored)")
        return path.read_text()

    return load


@pytest.fixture
def check_locked(real_input):
    """Return `check(module, LOCKED)` -- assert confirmed answers, report the rest.

    LOCKED is a (part1, part2) tuple of answers accepted by adventofcode.com,
    or None for a day whose answers have not been submitted yet.

    - LOCKED is a tuple: assert.  A refactor that changes the answer fails.
    - LOCKED is None:    print what the code currently produces and skip.

    The asymmetry is the point.  There is no third path where an unverified
    number gets asserted against itself, so a green suite never implies more
    confidence than somebody actually has.  Turning a day green means pasting
    a real answer into LOCKED by hand.
    """

    def check(module, locked):
        raw = real_input(int(module.__name__.removeprefix("day")))
        got = module.solve(raw)

        if locked is None:
            pytest.skip(
                f"{module.__name__}: LOCKED is None -- code currently produces "
                f"part1={got[0]} part2={got[1]}. Submit these, then set LOCKED."
            )

        assert got == tuple(locked), f"{module.__name__}: expected {tuple(locked)}, got {got}"

    return check
