"""Day 11: Seating System.

A cellular automaton on a grid of floor ('.'), empty seats ('L') and
occupied seats ('#').  Each round every seat looks at a fixed set of other
seats: an empty seat with no occupied neighbours fills, an occupied seat
with `tolerance` or more occupied neighbours empties.  Iterate to a
fixpoint and count the occupied seats.

The parts differ only in the neighbour relation and the tolerance, so the
simulation is written once and driven by a precomputed neighbour table:
  part 1 -- the 8 adjacent squares, tolerance 4;
  part 2 -- the first seat visible along each of the 8 rays, tolerance 5.
"""

from pathlib import Path
from typing import NamedTuple

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day11.txt"


class Layout(NamedTuple):
    """The grid reduced to just its seats.

    Floor squares never change and never count toward a neighbour tally, so
    they are dropped here and never seen again.  Each remaining seat gets a
    dense integer id, which is what lets the neighbour tables and the state
    vector be plain lists indexed by id rather than dicts keyed by (r, c).
    """

    rows: int
    cols: int
    coords: list[tuple[int, int]]
    index: dict[tuple[int, int], int]


def parse_input(raw: str) -> Layout:
    """Parse the raw grid all the way down to a seat Layout.

    The line split is only the first half of the job.  Both parts need the
    seat numbering, and it does not depend on which part is asking, so it
    belongs here -- doing it inside part1 and part2 would build the same
    table twice.
    """
    grid = [line.strip() for line in raw.splitlines() if line.strip()]
    rows, cols = len(grid), len(grid[0])
    coords = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] != "."]
    index = {coord: i for i, coord in enumerate(coords)}
    return Layout(rows, cols, coords, index)


def adjacent_table(layout: Layout) -> list[list[int]]:
    _rows, _cols, coords, index = layout
    return [
        [index[(r + dr, c + dc)] for dr, dc in DIRECTIONS if (r + dr, c + dc) in index] for r, c in coords
    ]


def visible_table(layout: Layout) -> list[list[int]]:
    rows, cols, coords, index = layout

    def first_seat(r: int, c: int, dr: int, dc: int) -> int | None:
        r, c = r + dr, c + dc
        while 0 <= r < rows and 0 <= c < cols:
            if (r, c) in index:
                return index[(r, c)]
            r, c = r + dr, c + dc
        return None

    table = []
    for r, c in coords:
        seen = (first_seat(r, c, dr, dc) for dr, dc in DIRECTIONS)
        table.append([i for i in seen if i is not None])
    return table


def stable_occupancy(table: list[list[int]], tolerance: int) -> int:
    state = [0] * len(table)
    while True:
        nxt = []
        for i, neighbours in enumerate(table):
            count = sum(state[j] for j in neighbours)
            if state[i] == 0 and count == 0:
                nxt.append(1)
            elif state[i] == 1 and count >= tolerance:
                nxt.append(0)
            else:
                nxt.append(state[i])
        if nxt == state:
            return sum(state)
        state = nxt


def part1(layout: Layout) -> int:
    return stable_occupancy(adjacent_table(layout), 4)


def part2(layout: Layout) -> int:
    return stable_occupancy(visible_table(layout), 5)


def solve(raw: str) -> tuple[int, int]:
    layout = parse_input(raw)
    return part1(layout), part2(layout)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
