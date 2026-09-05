"""Day 17: Conway Cubes -- alternative implementation, the flat brute-force scan.

Same puzzle and same answers as `day17.py`, written the other way round.
`day17.py` starts from the active cells and *scatters* counts outward, with
the number of dimensions as a parameter.  This module starts from the
*space*: it walks every cell in a box known to be big enough, counts that
cell's active neighbours by hand with one nested `for` per axis, applies
the two rules, and moves on.  Nothing is generic.  Three dimensions is
three loops, four dimensions is four, and the whole difference between
part 1 and part 2 is one more `for` and one more `d?`.

The shape is the classic AoC brute force (it follows the screenshot this
was asked for from, down to the names `ON`, `NEW_ON` and `nbr`), and it
is the version to read first if the scatter in `day17.py` feels too
clever.  It is also a few hundred times slower -- see "Cost" below --
which is why it is the alternative and not the shipping module.

Why the box is safe
-------------------
A cell can only turn active if it already touches an active cell, so the
occupied region grows by at most one cell per side per cycle.  The real
input is 8x8 at rows and columns 0..7; after six cycles nothing can be
outside -6..13 on the two slice axes or -6..6 on z and w.  The ranges
below (`-15..14`, `-7..7`, `-8..7`) are the screenshot's and are merely
generous.  The test module pins that no active cell ever reaches the edge
of the box, which is the one assumption this approach rests on.

Cost
----
The scan visits every cell of the box whether or not anything is near it:
30 * 30 * 15 = 13,500 cells per 3-D cycle and 30 * 30 * 15 * 16 = 216,000
per 4-D cycle, each doing 3**d - 1 set lookups.  Six 4-D cycles is about
105 million loop iterations of plain Python.  Measured on the real input
(best of 3 / best of 2): part 1 0.18 s, part 2 10.0 s, against 12.5 ms and
229 ms for `day17.py` -- roughly 15x and 45x slower.  The cost is
independent of the input, because the box is fixed: the statement's 3x3
example takes exactly as long as the real 8x8 input.

Orientation
-----------
The slice is read as `(row, col)`, the screenshot's order, not `(x, y)` as
in `day17.py`.  Only counts are ever reported, and the rule is symmetric
in every axis, so which axis is called what cannot change an answer.
"""

from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day17.txt"

CYCLES = 6


def parse_input(raw: str) -> frozenset[tuple[int, int]]:
    """The active `(row, col)` cells of the initial slice.

    `.strip()` per line drops a trailing `\r` from a CRLF download (day 6's
    lesson), so a stray carriage return can never be mistaken for a column.
    """
    ON = set()
    for r, line in enumerate(raw.splitlines()):
        for c, ch in enumerate(line.strip()):
            if ch == "#":
                ON.add((r, c))
    return frozenset(ON)


def cycle_3d(ON: set[tuple[int, int, int]]) -> set[tuple[int, int, int]]:
    """One cycle in three dimensions: every cell in the box, 26 neighbours each."""
    NEW_ON = set()
    for x in range(-15, 15):
        for y in range(-15, 15):
            for z in range(-7, 8):
                nbr = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        for dz in [-1, 0, 1]:
                            # Two questions, kept as two `if`s on purpose (ruff would
                            # merge them): is this offset not the cell itself, and is
                            # the cell there active?
                            if dx != 0 or dy != 0 or dz != 0:  # noqa: SIM102
                                if (x + dx, y + dy, z + dz) in ON:
                                    nbr += 1
                # The rules -- the part that fell off the bottom of the screen.
                # Active with exactly 2 or 3 active neighbours stays active;
                # inactive with exactly 3 becomes active; everything else is off.
                if (x, y, z) in ON and nbr in [2, 3]:
                    NEW_ON.add((x, y, z))
                if (x, y, z) not in ON and nbr == 3:
                    NEW_ON.add((x, y, z))
    return NEW_ON


def cycle_4d(ON: set[tuple[int, int, int, int]]) -> set[tuple[int, int, int, int]]:
    """One cycle in four dimensions: `cycle_3d` with one more loop and one more offset."""
    NEW_ON = set()
    for x in range(-15, 15):
        for y in range(-15, 15):
            for z in range(-7, 8):
                for w in range(-8, 8):
                    nbr = 0
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            for dz in [-1, 0, 1]:
                                for dw in [-1, 0, 1]:
                                    if dx != 0 or dy != 0 or dz != 0 or dw != 0:  # noqa: SIM102
                                        if (x + dx, y + dy, z + dz, w + dw) in ON:
                                            nbr += 1
                    if (x, y, z, w) in ON and nbr in [2, 3]:
                        NEW_ON.add((x, y, z, w))
                    if (x, y, z, w) not in ON and nbr == 3:
                        NEW_ON.add((x, y, z, w))
    return NEW_ON


def boot_3d(slice2d: frozenset[tuple[int, int]], cycles: int = CYCLES) -> set[tuple[int, int, int]]:
    """The active cells after `cycles` cycles, the slice placed at z=0."""
    ON = {(r, c, 0) for r, c in slice2d}
    for _ in range(cycles):
        ON = cycle_3d(ON)
    return ON


def boot_4d(slice2d: frozenset[tuple[int, int]], cycles: int = CYCLES) -> set[tuple[int, int, int, int]]:
    """The active cells after `cycles` cycles, the slice placed at z=0, w=0."""
    ON = {(r, c, 0, 0) for r, c in slice2d}
    for _ in range(cycles):
        ON = cycle_4d(ON)
    return ON


def part1(slice2d: frozenset[tuple[int, int]]) -> int:
    """Active cubes after the six-cycle boot in three dimensions."""
    return len(boot_3d(slice2d))


def part2(slice2d: frozenset[tuple[int, int]]) -> int:
    """Active hypercubes after the six-cycle boot in four dimensions."""
    return len(boot_4d(slice2d))


def solve(raw: str) -> tuple[int, int]:
    slice2d = parse_input(raw)
    return part1(slice2d), part2(slice2d)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
