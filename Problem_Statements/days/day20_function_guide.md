# Day 20 Function Guide — Jurassic Jigsaw

> A pile of 10×10 picture tiles, shuffled, each rotated or mirrored at
> random, that fit together into one square image because neighbouring
> tiles share their border row or column exactly. Part 1 wants the
> product of the four corner tiles' IDs; part 2 wants the tiles actually
> assembled, their borders stripped, and the resulting picture searched
> — in whichever of its eight orientations works — for sea monsters, so
> the `#` cells no monster covers can be counted. The shipping solution
> is one depth-first search that fills the grid row by row against an
> index of oriented tiles keyed by edge, and one pair of functions,
> `rotate` and `flip`, that generate the eight orientations of any
> block of pixels, tile or finished image alike. Nothing in the search
> assumes borders are unique, but in the puzzle inputs they are — every
> border matches at most one other tile — and that property, pinned as a
> test, is why the search barely backtracks and why the classic
> "a corner is a tile with two unmatched edges" shortcut gives the same
> four tiles as the assembly does.

Source: [`python/day20.py`](../../python/day20.py) ·
Tests: [`python/tests/test_day20.py`](../../python/tests/test_day20.py)

---

## 1. The problem

The input is 144 blocks like

```text
Tile 3593:
#..#.##...
.#..#.#...
.#####..#.
.......#.#
#...#.....
..#.....##
.#....#...
.#..#.....
..#......#
#.####.##.
```

Each tile's outermost row and column is a *border* that lines up
exactly with the neighbouring tile's border once both are in the right
orientation. Tiles on the outside of the image have borders that line
up with nothing. Every tile may have been rotated by any multiple of 90°
and/or mirrored, so a tile has eight possible orientations.

**Part 1.** Assemble the image and multiply the IDs of the four corner
tiles. The statement's nine-tile example assembles into

```text
1951    2311    3079
2729    1427    2473
2971    1489    1171
```

and 1951 × 3079 × 2971 × 1171 = 20899048083289.

**Part 2.** Remove every tile's border (a 10×10 tile becomes 8×8), lay
the interiors side by side to form the image (24×24 for the example,
96×96 for the real input), and look for *sea monsters*:

```text
                  #
#    ##    ##    ###
 #  #  #  #  #  #
```

Twenty wide, three tall, fifteen `#` cells; the blanks can be anything.
The image itself may need rotating or flipping before any monster
appears. The answer is the number of `#` cells that are not part of a
sea monster — the "roughness" of the water. In the example, two monsters
appear once the image is oriented correctly, and the roughness is 273.

The real input: 144 tiles, so a 12×12 arrangement. The Python answers
are 27803643063307 and 1644, produced but **not yet submitted**;
`LOCKED = None` until they are.

## 2. Representation

**A block of pixels is a tuple of strings**, one string per row —
`Block = tuple[str, ...]`. The same type serves a tile, the assembled
image and the sea monster pattern, so `rotate`, `flip` and
`orientations` are written once and used for all three. Tuples rather
than lists because a tile appears as a dict value and, later, inside a
`NamedTuple`; immutability also means orientation functions must return
new blocks rather than mutate, which is what the search needs anyway.

**Tiles are `dict[int, Block]`** keyed by ID. The order of the input is
random and never matters.

**Edges are strings**, read in one fixed direction each: top and bottom
left→right, left and right top→bottom. This is the convention the whole
assembly rests on. Two tiles fit vertically when `above.bottom ==
below.top` and horizontally when `left.right == right.left`, *with no
reversing anywhere*, because both strings were read the same way. The
alternative convention (read every edge clockwise around the tile) makes
the comparisons reversals and is a standard source of off-by-mirror bugs.

**A `Piece` is one tile in one orientation with its four edges read
out** — a `NamedTuple` of `(tile_id, rows, top, bottom, left, right)`.
Every tile is expanded to eight `Piece`s before the search starts, so
the search never rotates anything; it only compares strings and looks
things up. 144 tiles become 1,152 pieces.

**The assembled grid is `list[list[Piece]]`**, and the image is a
`Block` again.

**Monster cells are `(row, column)` offsets**, derived from the pattern
string at import time — `MONSTER_CELLS` is a comprehension over
`SEA_MONSTER`, not a hand-typed list, so the picture in the source is the
data (a test pins fifteen cells in a 20×3 box).

## 3. Function walkthrough

### `parse_input(raw) -> Tiles`

Split on blank lines with the regex `\n\s*\n` (so `\r\n\r\n` also
counts), take the first non-blank line of each block as `Tile NNNN:`,
the rest as rows, every line `.strip()`ed. A surviving `\r` would be an
eleventh column, and since edges are compared as whole strings, every
right edge would then end in `\r` and every left edge would not: no tile
would ever fit beside another, and the search would raise. The CRLF test
runs the sample through with `\r\n` endings.

### `rotate`, `flip`, `orientations`

```python
def rotate(block):   # quarter turn clockwise
    return tuple("".join(row[c] for row in reversed(block)) for c in range(len(block[0])))

def flip(block):     # mirror left to right
    return tuple(row[::-1] for row in block)
```

`rotate` builds each new row by reading one *column* of the old block
from the bottom up: the old left column, read bottom to top, becomes the
new top row. On a 2×2:

```text
ab      ca
cd  ->  db
```

`orientations` is the four rotations of the block followed by the four
rotations of its mirror image, eight in all, with the original first.
These eight are the symmetry group of the square (D₄), and the tests
check the group facts that matter: four rotations are the identity, two
flips are the identity, an asymmetric tile has eight distinct views, and
rotating or flipping any view lands inside the same set of eight — so
whichever orientation a tile is handed to us in, its eight views are
the same eight.

Two tests pin what rotation and mirroring do to the *edges*, because
that is what the search actually depends on. Clockwise: old left
(reversed) becomes top, old top becomes right, old right (reversed)
becomes bottom, old bottom becomes left. Mirror: top and bottom reverse,
left and right swap.

### `piece(tile_id, rows) -> Piece`

Reads the four edges under the section 2 convention. On a 3×3 `abc /
def / ghi` the edges are top `abc`, bottom `ghi`, left `adg`, right
`cfi` — a test.

### `assemble(tiles) -> Grid`

The solver. Set-up: check the tile count is a perfect square (else
raise), expand every tile to eight `Piece`s, and build two indexes —
`by_top[edge]`, the pieces whose top edge is `edge`, and `by_left[edge]`
likewise. Then a recursive `fill(cell)` places pieces into the grid in
row-major order:

```python
def fill(cell):
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
```

Three kinds of cell. The first cell has no neighbours yet and tries
every piece. A cell on the first row has a piece to its left, so the
candidates are `by_left[left.right]`. Every other cell has a piece
above it, so the candidates are `by_top[above.bottom]`, and the left
constraint is then checked explicitly. A tile already in the grid (in
any orientation) is skipped via `used`. A placement recurses; if the
recursion fails, the placement is undone and the next candidate tried;
if the candidates run out, the cell reports failure and its caller tries
its own next candidate.

Here is the sample's search, taken from an instrumented copy of the
function. Pieces are written `id/oK` for orientation `K` (0 is as
given, 4 is mirrored). Tile 2311 comes first in the input, so its eight
orientations are the first eight starts:

```text
(0,0) place 2311/o0
  (0,1) 2311/o4 already used         <- its own mirror image fits its right edge
  (0,1) place 3079/o6
    (0,2) 3079/o2 already used
    (0,2) no fit -> back up
  (0,1) no fit -> back up
(0,0) place 2311/o1
  (0,1) place 1427/o1
    (0,2) place 1489/o1
      (1,0) place 3079/o7
        (1,1) place 2473/o2
          (1,2) place 1171/o3
            (2,0) no fit -> back up  <- nothing fits under 3079: ran off the bottom
          ... back up to (0,0)
... six more 2311 starts, none reaching row 2 ...
(0,0) place 1951/o0
  (0,1) place 2311/o0
    (0,2) place 3079/o6
      (1,0) no fit -> back up        <- 1951/o0 is a corner, but its "down" is off the image
(0,0) place 1951/o1
  (0,1) place 2729/o1
    (0,2) place 2971/o1
      (1,0) place 2311/o1
        (1,1) place 1427/o1
          (1,2) place 1489/o1
            (2,0) place 3079/o7
              (2,1) place 2473/o2
                (2,2) place 1171/o3   <- done
```

Ten starts, 34 placements, 25 back-ups, and the result

```text
1951  2729  2971
2311  1427  1489
3079  2473  1171
```

which is the statement's grid with rows and columns swapped — one of its
eight orientations. `test_sample_assembles_to_the_statement_arrangement`
accepts any of the eight, since which one the search lands on depends on
input order.

Two things in the trace are worth naming. First, the "already used"
lines: every constrained cell has *two* candidates in the index, and one
of them is always the piece above (or to the left) *itself* in another
orientation — the tile whose bottom edge is `E` also has `E` as its top
edge when flipped vertically. `used` rejects it, leaving at most one
real candidate. Second, the second 2311 start gets six tiles down before
failing: with a non-corner start, the row-major fill happily reproduces
a translated copy of the true image until it walks off an edge. On the
real input the worst wrong start places 132 tiles — eleven full rows —
before running out of image (the start was a tile from the true second
row, left column). Cheap, because each of those placements is a
single-candidate lookup.

### `corner_ids`, `stitch`

`corner_ids` reads the four corner pieces' IDs. `stitch` takes rows 1
to 8 of each piece, columns 1 to 8, and concatenates across the grid
row — a 3×3 grid of 10×10 tiles becomes a 24×24 image. On a single tile
it is just the tile's interior (a test).

Two more tests tie the stitching to the statement's own text. The
statement prints the assembled 3×3 arrangement with borders on, and
(in part 2) the 24×24 image with borders off. A test-side helper strips
the borders from the first block and asserts it equals the second, and
another asserts the stitched sample equals the second in one of its
eight orientations.

### `monster_anchors`, `monster_cells`, `roughness`

`monster_anchors(image)` slides the 20×3 pattern over every position
where it fits and returns the top-left corners at which all fifteen
monster cells are `#`. No rotating happens here — it looks at the image
as given. `monster_cells` is the union, as a set, of the fifteen cells
at every anchor. `roughness`:

```python
covered = max((monster_cells(view) for view in orientations(image)), key=len)
return sum(row.count("#") for row in image) - len(covered)
```

Try all eight orientations, take the one that covers the most cells,
subtract from the total `#` count — which is orientation-invariant, so
it is counted on the original image. Three things fall out of this
shape:

- If no orientation has monsters, `covered` is empty and the roughness
  is every `#`. The statement does not say what to do then; this is the
  only sensible answer, and a test pins it.
- Overlapping monsters are counted once. The test that pins it is a
  3×40 sea of solid `#`: a monster fits at all 21 anchors, 21 × 15 = 315
  cell hits collapse to 97 distinct cells, and the roughness is 120 − 97
  = 23, not a negative number.
- The blanks in the pattern are ignored, as the statement asks: a solid
  20×3 block of `#` holds one monster (a test).

On the sample, exactly one of the eight orientations has any monsters:
two of them, anchored at `(2, 2)` and `(16, 1)`, covering 30 cells. The
image has 303 `#` cells, and 303 − 30 = 273.

### `part1` / `part2`

`prod(corner_ids(assemble(tiles)))` and
`roughness(stitch(assemble(tiles)))`. Each part assembles for itself,
so `solve` assembles twice; section 7 measures what sharing it would
save (about a fifth of the total) and why it stays this way.

## 4. Why it is correct

**The search is complete.** `fill` is a plain depth-first enumeration of
row-major placements. At every cell it considers every piece that
satisfies the constraints with the pieces already placed — the index
lookup is a filter, not a heuristic, because `by_top[E]` contains
*every* piece whose top is `E`, and the explicit `p.top != above.bottom`
check is redundant for that branch and load-bearing for the other. So
if any arrangement of the tiles into a square with all seams matching
exists, the search finds one, and if none exists it raises. It does not
assume borders are unique, tiles are asymmetric, or that a corner can be
recognised in advance. Two tests exercise the failure paths: eight
tiles (not a square) and four tiles whose edges never match.

**Any solution is as good as any other.** The puzzle's picture has eight
orientations, so the search has at least eight solutions, and the tests
accept any of them. Part 1 is the product of the corner IDs, which is
the same set of four tiles in every orientation. Part 2 rotates and
flips the stitched image itself, so it does not matter which way up the
assembly came out — and `test_sample_monsters_in_exactly_one_orientation`
confirms that exactly one of the eight views of the sample has monsters,
so `max` has a unique winner.

**The edge convention is consistent.** Section 2's "read every edge in
a fixed direction" is what makes `above.bottom == below.top` the right
test with no reversal. The two edge tests (what rotate and flip do to
the four edges) are the sanity check that `piece` and `rotate` agree
about which way is which; if either were wrong, the sample would fail
to assemble at all.

**Why the real input is easy, pinned rather than assumed.** Reading
every tile's four edges and treating an edge and its reversal as the
same border (they are the same seam seen from either side):

| what                                    | count |
| --------------------------------------- | ----: |
| tiles                                   |   144 |
| distinct borders                        |   312 |
| borders on exactly two tiles (seams)    |   264 |
| borders on exactly one tile (perimeter) |    48 |
| palindromic borders                     |     0 |
| tiles with fewer than 8 distinct views  |     0 |

264 = 2 × 12 × 11, the number of interior seams in a 12×12 grid, and 48
= 4 × 12, its perimeter. No border appears on three tiles, so every
seam has exactly one partner and the search is nearly deterministic
after its first placement. Counting unmatched edges per tile gives
100 tiles with none, 40 with one, 4 with two — the interior, the sides,
the corners of a 12×12. `test_real_corners_agree_with_the_edge_count_shortcut`
takes those four tiles and asserts they are exactly the four the
assembly puts in the corners, and that their product is `part1`. A
sibling test checks the assembled grid's 48 perimeter edges are exactly
the 48 borders no other tile has. The sample has the same structure one
size down: 24 borders, 12 seams and 12 on the perimeter, tiles split
1 / 4 / 4.

**Part 2 on the real input.** The stitched image is 96×96 with 2,199
`#` cells. Exactly one of the eight orientations has monsters — 37 of
them, covering 555 = 37 × 15 cells, so none overlap — and 2,199 − 555 =
1,644. The test asserts the single-orientation and no-overlap facts and
that `part2` equals the `#` count minus 37 × 15, so the answer is tied
to a count a reader can reproduce by hand, rather than to itself.

## 5. Complexity

Parsing is linear. Orienting 144 tiles is 1,152 pieces of 100
characters each; the index build is linear in pieces. The search, in
the worst case, is exponential (it is a backtracking search over
placements), but with unique borders it is effectively linear: after
the first cell every cell has at most one usable candidate, so each of
the wrong starts costs at most the number of tiles it can place before
walking off the image. Instrumented on the real input:

| statistic                          | sample | real |
| ---------------------------------- | -----: | ---: |
| starts tried at cell (0, 0)        |     10 |  139 |
| placements                         |     34 | 1,701 |
| back-ups                           |     25 | 1,557 |
| deepest wrong start (tiles placed) |      6 |  132 |
| candidates at a constrained cell   |    ≤ 2 |  ≤ 2 |

The monster scan is the big fixed cost: 8 orientations × (96 − 2) ×
(96 − 19) = 8 × 7,238 = 57,904 anchor positions, each testing up to
fifteen cells (most fail on the first one or two).

Measured on the real input (`python\bench.py 20 -n 10`, best / median):

| phase  |     best |   median |
| ------ | -------: | -------: |
| parse  | 0.214 ms | 0.220 ms |
| part 1 | 10.58 ms | 11.14 ms |
| part 2 | 40.25 ms | 40.86 ms |

And where part 2's time goes, timed piece by piece from a scratch
script:

| step                                    |   ms |
| --------------------------------------- | ---: |
| orient 144 tiles (`orientations`)       |  7.6 |
| build 1,152 `Piece`s (includes the above) |  9.3 |
| the search itself (`assemble` minus set-up) | ~1.2 |
| `stitch`                                |  0.1 |
| orient the 96×96 image                  |  3.2 |
| `monster_anchors` × 8 orientations      | 26.3 |

The search that the whole day is about is about a millisecond. Two
thirds of part 2 is the monster scan and most of the rest is building
orientations — `rotate` is a Python-level double loop over characters.
Across the repo (`python\bench.py -n 3`) day 20's 51 ms is the fifth
slowest total, after day 15's 3.7 s, day 11's 594 ms, day 17's 242 ms
and day 19's 214 ms, and just above day 14's 49 ms.

## 6. If I were writing this in Rust

The same algorithm, with one representation change that is the natural
one in Rust and the one an embedded engineer reaches for anyway: **an
edge is a 10-bit integer**, not a string. `#..#.##...` is `1001011000`,
which is 600. Reading an edge becomes a fold:

```rust
fn bits<'a>(cells: impl Iterator<Item = &'a u8>) -> u16 {
    cells.fold(0u16, |acc, &ch| (acc << 1) | (ch == b'#') as u16)
}

struct Piece { id: u64, rows: Vec<Vec<u8>>, top: u16, bottom: u16, left: u16, right: u16 }

fn piece(id: u64, rows: Vec<Vec<u8>>) -> Piece {
    let top = bits(rows[0].iter());
    let bottom = bits(rows[rows.len() - 1].iter());
    let left = bits(rows.iter().map(|r| &r[0]));
    let right = bits(rows.iter().map(|r| &r[r.len() - 1]));
    Piece { id, rows, top, bottom, left, right }
}
```

The indexes are `HashMap<u16, Vec<usize>>` from edge to piece index,
the grid is a flat `Vec<usize>` of piece indices, and `fill` is the
same recursion with `&mut` for the grid and the used set threaded
through as parameters (the Python closure captures them; Rust's borrow
checker wants them explicit, which is the honest version of what the
closure does). The monster scan is the same double loop over a
`Vec<Vec<u8>>` with a `Vec<Vec<bool>>` for coverage.

The port was compiled with `rustc -O` (1.93.1) and run three times on
the real input while writing this guide, best of five inside each run.
Same two answers; parse **0.08–0.10 ms**, part 1 **1.2–1.3 ms**, part 2
**1.6–1.7 ms**. That is 8× on part 1 and 25× on part 2 — the day 18
kind of ratio (Python's per-character overhead *is* the cost) rather
than the day 19 kind (an algorithm's redundancy that no language fixes).
Everything expensive here is a tight loop over bytes: rotating a block,
reading edges, testing fifteen cells at 58,000 anchors. Notes:

- **The 10-bit edge buys a free canonical form.** A border seen from
  the other tile is the bit-reversal of the 10-bit value, so "the same
  seam either way round" is `min(e, reverse10(e))`, and `reverse10` is
  a ten-step shift loop or a lookup table of 1,024 entries. With strings
  it is `min(e, e[::-1])`, which allocates.
- **`Piece` owns its rows.** A `Vec<Vec<u8>>` per piece is 1,152 small
  allocations at set-up; a `[[u8; 10]; 10]` would be none, at the cost
  of hard-wiring the tile size. For an AoC input that is the better
  trade; the port kept `Vec` to stay generic like the Python.
- **The search's `used` set** is a `HashSet<u64>` in the port. A
  `Vec<bool>` indexed by tile position would be faster and is what you
  would do if the search were the bottleneck; it is not.
- **Coverage as `Vec<Vec<bool>>`** rather than a `HashSet<(usize,
  usize)>`: a 96×96 bool grid is 9 KB and indexing it is a multiply and
  an add. This is the change that most separates the two part 2
  numbers.

## 7. Possible optimization

Four things measured on the real input from a scratch script (not the
repo), all giving the same answers:

| variant                                        | shipping | variant |
| ---------------------------------------------- | -------: | ------: |
| part 1 by counting unmatched edges, no assembly | 10.6 ms | 0.54 ms |
| `roughness`, stop at the first orientation with monsters | 29.3 ms | 9.7 ms |
| monster scan via per-row regex, × 8            | 26.3 ms |  4.8 ms |
| both parts sharing one assembly                | 50.6 ms | 40.3 ms |

**Corners by edge counting** is the standard AoC part 1 and it is 20×
faster: read every tile's four edges, count how many tiles own each
border (up to reversal), and a corner is a tile with two borders nobody
else has. It is *not* shipped as `part1` because it is only correct when
borders are unique — a fact about the input, not a promise in the
statement — whereas `assemble` is correct regardless. It lives in the
tests as the independent oracle that section 4 describes, which is the
right place for a shortcut that depends on a property of the data.

**Stopping at the first orientation with monsters** saves the remaining
scans after the hit. On this input the monsters are in the second
orientation tried, so it saves six of eight scans; on another input it
could save none. It also changes the semantics slightly (first hit
rather than best hit). The eight-way `max` is the version that says
what it means.

**A regex per monster row.** Turn each of the three pattern rows into a
regex with `.` for the blanks, wrapped in a lookahead so overlapping
matches are found, and intersect the match columns across the three
image rows at each height. `re` does the fifteen-cell test in C, and it
is 5.5× faster. Same idea as day 19's compiled grammar: correct, faster,
and harder to read than fifteen coordinates in a comprehension.

**Sharing the assembly** between the parts would drop `solve` from 51
to 40 ms. The day-module convention is that `part1(parsed)` and
`part2(parsed)` are independent of each other, and `parse_input` is a
parse rather than a solve, so the assembly is done twice. Ten
milliseconds is the price of keeping the interface uniform across the
repo, and it is not worth a special case.

Not measured but worth naming: **rotate the edges, not the tiles.**
The search only needs each piece's four edges; the rows are only
needed for `stitch`, and only for the eight pieces that win. Section
3's edge-rotation test says exactly how the four edges of a rotated or
mirrored tile derive from the original's, so all eight `Piece`s could
be built from four strings and two reversals without ever building the
rotated rows, deferring `rotate` to the 144 winning pieces. That would
remove most of the 9.3 ms set-up cost. It is not done because
`orientations(tile)` being the same function as `orientations(image)` is
the thing that makes the module short.
