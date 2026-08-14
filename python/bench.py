"""Time each solved day by phase: parse, part 1, part 2.

Usage:
    python python/bench.py              # every day with an input file
    python python/bench.py 11 13        # just those days
    python python/bench.py -n 20 11     # 20 repetitions instead of the default

Reports **best** and **median** of N runs rather than a single shot.  At this
scale that is not pedantry: most days here finish in well under a
millisecond, and on Windows the ambient noise floor -- timer granularity, GC,
another process taking the core -- is itself a sizeable fraction of a
millisecond.  A single measurement of a 0.6 ms parse can land anywhere in a
range wider than the difference between two implementations you are trying to
compare, so the number would be unactionable.

Best-of-N estimates the floor: interference only ever adds time, so the
fastest observed run is the closest thing to the work itself.  The median
says what a typical run costs with the noise included.  When the two are
close the measurement is trustworthy; when best is far below median,
something on the machine is interfering and the median is mostly about that.

perf_counter is the right clock here -- it is the highest-resolution one
available and, unlike process_time, it counts wall time, which is what you
actually wait for.
"""

import argparse
import importlib
import statistics
import sys
from pathlib import Path
from time import perf_counter

REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = REPO_ROOT / "inputs"
DEFAULT_REPS = 5


def time_call(fn, arg, reps):
    """Return (best_ms, median_ms) for `reps` calls of fn(arg)."""
    samples = []
    for _ in range(reps):
        start = perf_counter()
        fn(arg)
        samples.append((perf_counter() - start) * 1000.0)
    return min(samples), statistics.median(samples)


def bench_day(day, reps):
    """Return per-phase timings for one day, or None if it should be skipped.

    Skipped when the input is missing (they are gitignored) or when the day
    is not solved yet.  "Solved" is taken to mean the module defines main():
    an unsolved day is still a placeholder whose part1 returns a line count,
    and timing that would put a meaningless 0.000 in the table next to real
    measurements.
    """
    path = INPUT_DIR / f"day{day:02d}.txt"
    if not path.exists():
        return None
    try:
        module = importlib.import_module(f"day{day:02d}")
    except ModuleNotFoundError:
        return None
    if not hasattr(module, "main"):
        return None

    raw = path.read_text()
    parsed = module.parse_input(raw)

    return {
        "parse": time_call(module.parse_input, raw, reps),
        "part1": time_call(module.part1, parsed, reps),
        "part2": time_call(module.part2, parsed, reps),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("days", nargs="*", type=int, help="days to bench (default: all)")
    parser.add_argument("-n", "--reps", type=int, default=DEFAULT_REPS, help="repetitions per phase")
    args = parser.parse_args(argv)

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    days = args.days or range(0, 26)

    header = (
        f"{'day':>3}  {'parse best/med':>18}  {'part1 best/med':>18}  {'part2 best/med':>18}  {'total':>9}"
    )
    print(f"best and median of {args.reps} runs, milliseconds\n")
    print(header)
    print("-" * len(header))

    grand = 0.0
    for day in days:
        timings = bench_day(day, args.reps)
        if timings is None:
            continue
        cells = []
        for phase in ("parse", "part1", "part2"):
            best, med = timings[phase]
            cells.append(f"{best:8.3f} /{med:8.3f}")
        total = sum(best for best, _ in timings.values())
        grand += total
        print(f"{day:>3}  {'  '.join(cells)}  {total:8.3f} ")

    print("-" * len(header))
    print(f"{'all':>3}  {'':>18}  {'':>18}  {'':>18}  {grand:8.3f} ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
