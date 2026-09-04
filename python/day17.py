"""Day 17: Conway Cubes.

Conway's Game of Life, lifted out of the plane.  The input is a small 2-D
slice of an infinite grid; every cell in the grid is active or inactive,
and each cycle every cell looks at all the cells whose coordinates differ
from its own by at most one (26 of them in 3-D, 80 in 4-D) and applies
the Life rule: an active cell stays active with exactly 2 or 3 active
neighbours, an inactive one turns active with exactly 3.  Six cycles, then
count.  Part 1 is the 3-D pocket dimension; part 2 is the same thing in
4-D.  Nothing else changes between the parts, so the engine takes the
number of dimensions as a parameter and the slice is embedded by padding
each `(x, y)` with zeros.

The representation is the one Life on an unbounded grid wants: a set of
the active cells' coordinates and nothing else.  The "infinite" grid costs
nothing because inactive cells are simply absent, and there is no array to
resize as the pattern grows -- it can grow by at most one cell per axis
per cycle, so after six cycles the 8x8 input occupies at most 20x20x13x13.

One cycle is a scatter rather than a gather.  Instead of asking each
candidate cell "how many of my neighbours are active?" (which needs a list
of candidates first), every active cell adds one to a counter at each of
its neighbours' coordinates.  When the loop ends the counter holds the
neighbour count of every cell that has at least one active neighbour --
exactly the cells that could possibly be active next cycle -- and the rule
is one filter over it.  On the statement's example (glider `.#.` / `..#` /
`###`, x across, y down) the z=0 layer of the counter after the scatter,
and the rule applied cell by cell, is:

    counts at z=0        rule                                        next
    x: 0 1 2
    y0  1 1 2            (1,0) active,   1 neighbour  -> dies         ...
    y1  3 5 3            (0,1) inactive, 3 -> born; (2,1) active, 3   #.#
    y2  1 3 2            (0,2) active, 1 -> dies; (1,2) 3, (2,2) 2    .##
    y3  2 3 2            (1,3) inactive, 3 -> born                    .#.

which is the statement's `z=0` layer after one cycle (its frame is shifted
down one row to follow the cells).  The z=1 layer of the same counter is
all inactive cells, and its three 3s -- at (0,1), (2,2), (1,3) -- are the
statement's `#..` / `..#` / `.#.`; z=-1 is the mirror image.
"""

from collections import Counter
from functools import cache
from itertools import product
from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day17.txt"

CYCLES = 6

Cell = tuple[int, ...]


def parse_input(raw: str) -> frozenset[tuple[int, int]]:
    """The active `(x, y)` cells of the initial slice; x is the column, y the row.

    Per-line `.strip()` drops a trailing `\r` from a CRLF download, which
    would otherwise sit past the last column and never match `#` -- harmless
    here, but the day 6 lesson says do not rely on that.
    """
    return frozenset(
        (x, y)
        for y, line in enumerate(raw.splitlines())
        for x, char in enumerate(line.strip())
        if char == "#"
    )


@cache
def neighbour_offsets(dims: int) -> tuple[Cell, ...]:
    """Every non-zero offset whose coordinates are each in {-1, 0, 1}: 3**dims - 1 of them."""
    return tuple(offset for offset in product((-1, 0, 1), repeat=dims) if any(offset))


def embed(slice2d: frozenset[tuple[int, int]], dims: int) -> set[Cell]:
    """Place the 2-D slice at zero on every extra axis: `(x, y)` -> `(x, y, 0, ..., 0)`."""
    padding = (0,) * (dims - 2)
    return {cell + padding for cell in slice2d}


def step(active: set[Cell], dims: int) -> set[Cell]:
    """One simultaneous cycle of the rule, over an unbounded `dims`-dimensional grid.

    Scatter: each active cell increments a counter at each of its
    neighbours.  A cell that no active cell touches is never counted, and
    correctly so -- with zero neighbours it can be neither born nor kept.
    """
    counts: Counter[Cell] = Counter()
    for cell in active:
        for offset in neighbour_offsets(dims):
            counts[tuple(a + b for a, b in zip(cell, offset))] += 1
    return {cell for cell, n in counts.items() if n == 3 or (n == 2 and cell in active)}


def boot(slice2d: frozenset[tuple[int, int]], dims: int, cycles: int = CYCLES) -> set[Cell]:
    """The active cells after `cycles` cycles, starting from the slice embedded in `dims` dimensions."""
    active = embed(slice2d, dims)
    for _ in range(cycles):
        active = step(active, dims)
    return active


def part1(slice2d: frozenset[tuple[int, int]]) -> int:
    """Active cubes after the six-cycle boot in three dimensions."""
    return len(boot(slice2d, 3))


def part2(slice2d: frozenset[tuple[int, int]]) -> int:
    """Active hypercubes after the six-cycle boot in four dimensions."""
    return len(boot(slice2d, 4))


def solve(raw: str) -> tuple[int, int]:
    slice2d = parse_input(raw)
    return part1(slice2d), part2(slice2d)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
