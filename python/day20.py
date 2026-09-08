"""Day 20: Jurassic Jigsaw.

The input is a pile of square monochrome tiles, each 10x10 with an ID, in
random order and each rotated or flipped at random.  Adjacent tiles share a
border row/column exactly, so the pile can be reassembled into one square
image.  Part 1 multiplies the IDs of the four corner tiles.  Part 2 strips
every tile's border, stitches the interiors into one picture, finds the sea
monsters in it (a fixed 20x3 pattern, in whichever of the image's eight
orientations they appear), and counts the `#` cells no monster covers.

Everything is a tuple of strings, one string per row -- a tile, the whole
image, the sea monster.  `rotate` (a quarter turn clockwise) and `flip`
(left-right mirror) generate the eight orientations of any such block, and
the same two functions serve both the tiles and the finished picture.

Assembly is a depth-first search that fills the grid in row-major order.
Every tile is expanded to its eight orientations up front, each recorded as
a `Piece` with its four edges read out as strings, and the pieces are
indexed by top edge and by left edge.  At each cell the candidates are the
pieces whose top edge equals the bottom edge of the piece above (or, on
the first row, whose left edge equals the right edge of the piece to the
left); a candidate is placed if its ID is unused and its other constraint
holds, and the search backs up when a cell has no fit.  The first cell has
no constraints and tries every piece.  Nothing here assumes edges are
unique -- but in the puzzle inputs they are (every border string matches
at most one other tile, pinned as a test), so after the first placement
each cell has at most one candidate and the search never backtracks more
than a few steps.

The statement's nine-tile example assembles to (one orientation of)

    1951  2311  3079
    2729  1427  2473
    2971  1489  1171

and 1951 * 3079 * 2971 * 1171 = 20899048083289.  Its stitched 24x24
image holds 303 `#` cells and, once flipped and rotated correctly, two sea
monsters of 15 cells each, so the roughness is 303 - 30 = 273.

The orientation the search happens to land on is irrelevant to both
answers: the corner product does not care which corner is which, and
part 2 tries all eight orientations of the stitched image anyway.
"""

import re
from collections import defaultdict
from math import isqrt, prod
from pathlib import Path
from typing import NamedTuple

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day20.txt"

# A block of pixels: one string per row, all the same length.
Block = tuple[str, ...]
Tiles = dict[int, Block]

SEA_MONSTER: Block = (
    "                  # ",
    "#    ##    ##    ###",
    " #  #  #  #  #  #   ",
)
# (row, column) offsets of the monster's cells from its top-left corner.
MONSTER_CELLS = [(dr, dc) for dr, row in enumerate(SEA_MONSTER) for dc, ch in enumerate(row) if ch == "#"]


def parse_input(raw: str) -> Tiles:
    """`{tile_id: rows}` for every `Tile NNNN:` block.

    Blocks are split on blank lines with a regex that accepts `\\r\\n\\r\\n`, and
    every row is `.strip()`ed, so a CRLF file cannot leave a `\\r` as an
    eleventh column (which would silently break every edge comparison).
    """
    tiles: Tiles = {}
    for block in re.split(r"\n\s*\n", raw.strip()):
        header, *rows = (line.strip() for line in block.splitlines() if line.strip())
        tile_id = int(header.removeprefix("Tile ").rstrip(":"))
        tiles[tile_id] = tuple(rows)
    return tiles


# --- the eight orientations ------------------------------------------------------------


def rotate(block: Block) -> Block:
    """A quarter turn clockwise: the left column, read bottom to top, becomes the top row."""
    return tuple("".join(row[c] for row in reversed(block)) for c in range(len(block[0])))


def flip(block: Block) -> Block:
    """Mirror left to right."""
    return tuple(row[::-1] for row in block)


def orientations(block: Block) -> list[Block]:
    """All eight: four rotations of the block and four of its mirror image."""
    result = []
    for start in (block, flip(block)):
        current = start
        for _ in range(4):
            result.append(current)
            current = rotate(current)
    return result


# --- assembly --------------------------------------------------------------------------


class Piece(NamedTuple):
    """One tile in one orientation, with its four edges read out.

    Top and bottom are read left to right, left and right top to bottom, so
    two pieces fit vertically when `above.bottom == below.top` and
    horizontally when `left.right == right.left`, with no reversing.
    """

    tile_id: int
    rows: Block
    top: str
    bottom: str
    left: str
    right: str


def piece(tile_id: int, rows: Block) -> Piece:
    return Piece(
        tile_id,
        rows,
        top=rows[0],
        bottom=rows[-1],
        left="".join(row[0] for row in rows),
        right="".join(row[-1] for row in rows),
    )


Grid = list[list[Piece]]


def assemble(tiles: Tiles) -> Grid:
    """Place every tile, in some orientation, so that all shared borders match.

    Depth-first search in row-major order; see the module docstring.
    Raises if the tiles admit no square arrangement.
    """
    side = isqrt(len(tiles))
    if side * side != len(tiles):
        raise ValueError(f"{len(tiles)} tiles do not form a square")

    pieces = [piece(tile_id, rows) for tile_id, tile in tiles.items() for rows in orientations(tile)]
    by_top: dict[str, list[Piece]] = defaultdict(list)
    by_left: dict[str, list[Piece]] = defaultdict(list)
    for p in pieces:
        by_top[p.top].append(p)
        by_left[p.left].append(p)

    grid: list[list[Piece | None]] = [[None] * side for _ in range(side)]
    used: set[int] = set()

    def fill(cell: int) -> bool:
        if cell == side * side:
            return True
        r, c = divmod(cell, side)
        above = grid[r - 1][c] if r > 0 else None
        left = grid[r][c - 1] if c > 0 else None
        if above is not None:
            candidates = by_top[above.bottom]
        elif left is not None:
            candidates = by_left[left.right]
        else:
            candidates = pieces
        for p in candidates:
            if p.tile_id in used:
                continue
            if above is not None and p.top != above.bottom:
                continue
            if left is not None and p.left != left.right:
                continue
            grid[r][c] = p
            used.add(p.tile_id)
            if fill(cell + 1):
                return True
            used.discard(p.tile_id)
        grid[r][c] = None
        return False

    if not fill(0):
        raise ValueError("tiles do not assemble")
    return [[p for p in row if p is not None] for row in grid]


def corner_ids(grid: Grid) -> list[int]:
    return [grid[0][0].tile_id, grid[0][-1].tile_id, grid[-1][0].tile_id, grid[-1][-1].tile_id]


def stitch(grid: Grid) -> Block:
    """The image: every piece's interior (border row and column removed), laid side by side."""
    image = []
    for grid_row in grid:
        for r in range(1, len(grid_row[0].rows) - 1):
            image.append("".join(p.rows[r][1:-1] for p in grid_row))
    return tuple(image)


# --- sea monsters ----------------------------------------------------------------------


def monster_anchors(image: Block) -> list[tuple[int, int]]:
    """Top-left corners of every sea monster in `image` as oriented (no rotating here)."""
    height, width = len(SEA_MONSTER), len(SEA_MONSTER[0])
    return [
        (r, c)
        for r in range(len(image) - height + 1)
        for c in range(len(image[0]) - width + 1)
        if all(image[r + dr][c + dc] == "#" for dr, dc in MONSTER_CELLS)
    ]


def monster_cells(image: Block) -> set[tuple[int, int]]:
    """Every cell of `image` covered by at least one sea monster, as oriented."""
    return {(r + dr, c + dc) for r, c in monster_anchors(image) for dr, dc in MONSTER_CELLS}


def roughness(image: Block) -> int:
    """`#` cells not covered by a monster, in whichever orientation shows the most monsters."""
    covered = max((monster_cells(view) for view in orientations(image)), key=len)
    return sum(row.count("#") for row in image) - len(covered)


# --- parts -----------------------------------------------------------------------------


def part1(tiles: Tiles) -> int:
    """Product of the four corner tiles' IDs."""
    return prod(corner_ids(assemble(tiles)))


def part2(tiles: Tiles) -> int:
    """Roughness of the stitched image."""
    return roughness(stitch(assemble(tiles)))


def solve(raw: str) -> tuple[int, int]:
    tiles = parse_input(raw)
    return part1(tiles), part2(tiles)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
