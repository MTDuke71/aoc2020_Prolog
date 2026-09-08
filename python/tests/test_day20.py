"""Day 20: Jurassic Jigsaw."""

from collections import Counter, defaultdict
from math import prod

import pytest

import day20

LOCKED = (27803643063307, 1644)

# The statement's nine tiles, in the order given.
SAMPLE = """\
Tile 2311:
..##.#..#.
##..#.....
#...##..#.
####.#...#
##.##.###.
##...#.###
.#.#.#..##
..#....#..
###...#.#.
..###..###

Tile 1951:
#.##...##.
#.####...#
.....#..##
#...######
.##.#....#
.###.#####
###.##.##.
.###....#.
..#.#..#.#
#...##.#..

Tile 1171:
####...##.
#..##.#..#
##.#..#.#.
.###.####.
..###.####
.##....##.
.#...####.
#.##.####.
####..#...
.....##...

Tile 1427:
###.##.#..
.#..#.##..
.#.##.#..#
#.#.#.##.#
....#...##
...##..##.
...#.#####
.#.####.#.
..#..###.#
..##.#..#.

Tile 1489:
##.#.#....
..##...#..
.##..##...
..#...#...
#####...#.
#..#.#.#.#
...#.#.#..
##.#...##.
..##.##.##
###.##.#..

Tile 2473:
#....####.
#..#.##...
#.##..#...
######.#.#
.#...#.#.#
.#########
.###.#..#.
########.#
##...##.#.
..###.#.#.

Tile 2971:
..#.#....#
#...###...
#.#.###...
##.##..#..
.#####..##
.#..####.#
#..#.#..#.
..####.###
..#.#.###.
...#.#.#.#

Tile 2729:
...#.#.#.#
####.#....
..#.#.....
....#..#.#
.##..##.#.
.#.####...
####.#.#..
##.####...
##..#.##..
#.##...##.

Tile 3079:
#.#.#####.
.#..######
..#.......
######....
####.#..#.
.#...#.##.
#.#####.##
..#.###...
..#.......
..#.###...
"""

# The statement's assembled arrangement: nine oriented tiles, three per row, borders still on.
STATEMENT_ARRANGEMENT = """\
#...##.#.. ..###..### #.#.#####.
..#.#..#.# ###...#.#. .#..######
.###....#. ..#....#.. ..#.......
###.##.##. .#.#.#..## ######....
.###.##### ##...#.### ####.#..#.
.##.#....# ##.##.###. .#...#.##.
#...###### ####.#...# #.#####.##
.....#..## #...##..#. ..#.###...
#.####...# ##..#..... ..#.......
#.##...##. ..##.#..#. ..#.###...

#.##...##. ..##.#..#. ..#.###...
##..#.##.. ..#..###.# ##.##....#
##.####... .#.####.#. ..#.###..#
####.#.#.. ...#.##### ###.#..###
.#.####... ...##..##. .######.##
.##..##.#. ....#...## #.#.#.#...
....#..#.# #.#.#.##.# #.###.###.
..#.#..... .#.##.#..# #.###.##..
####.#.... .#..#.##.. .######...
...#.#.#.# ###.##.#.. .##...####

...#.#.#.# ###.##.#.. .##...####
..#.#.###. ..##.##.## #..#.##..#
..####.### ##.#...##. .#.#..#.##
#..#.#..#. ...#.#.#.. .####.###.
.#..####.# #..#.#.#.# ####.###..
.#####..## #####...#. .##....##.
##.##..#.. ..#...#... .####...#.
#.#.###... .##..##... .####.##.#
#...###... ..##...#.. ...#..####
..#.#....# ##.#.#.... ...##.....
"""

STATEMENT_IDS = [
    [1951, 2311, 3079],
    [2729, 1427, 2473],
    [2971, 1489, 1171],
]

# The 24x24 image the part 2 statement prints after removing the borders.
STATEMENT_IMAGE = """\
.#.#..#.##...#.##..#####
###....#.#....#..#......
##.##.###.#.#..######...
###.#####...#.#####.#..#
##.#....#.##.####...#.##
...########.#....#####.#
....#..#...##..#.#.###..
.####...#..#.....#......
#..#.##..#..###.#.##....
#.####..#.####.#.#.###..
###.#.#...#.######.#..##
#.####....##..########.#
##..##.#...#...#.#.#.#..
...#..#..#.#.##..###.###
.#.#....#.##.#...###.##.
###.#...#..#.##.######..
.#.#.###.##.##.#..#.##..
.####.###.#...###.#..#.#
..#.#..#..#.#.#.####.###
#..####...#.#.#.###.###.
#####..#####...###....##
#.##..#..#...#..####...#
.#.###..##..##..####.##.
...###...##...#...#..###
"""


def block(text):
    return tuple(text.splitlines())


def id_grid(grid):
    return [[p.tile_id for p in row] for row in grid]


def grid_orientations(rows):
    """The eight orientations of a list-of-lists, test-side twin of `day20.orientations`."""
    result = []
    for start in (rows, [list(reversed(r)) for r in rows]):
        current = [list(r) for r in start]
        for _ in range(4):
            result.append(current)
            current = [list(col) for col in zip(*reversed(current))]
    return result


def strip_borders(arrangement):
    """What the statement's arrangement text becomes with every tile's border removed."""
    image = []
    for band in arrangement.strip().split("\n\n"):
        lines = band.splitlines()
        for line in lines[1:-1]:
            image.append("".join(tile[1:-1] for tile in line.split()))
    return tuple(image)


def canonical(edge):
    """An edge and its reverse are the same border seen from the two tiles that share it."""
    return min(edge, edge[::-1])


def edge_owners(tiles):
    """canonical edge -> set of tile ids that have it on some side."""
    owners = defaultdict(set)
    for tile_id, rows in tiles.items():
        p = day20.piece(tile_id, rows)
        for edge in (p.top, p.bottom, p.left, p.right):
            owners[canonical(edge)].add(tile_id)
    return owners


def unmatched_edge_counts(tiles):
    """tile id -> how many of its four edges no other tile has."""
    owners = edge_owners(tiles)
    counts = {}
    for tile_id, rows in tiles.items():
        p = day20.piece(tile_id, rows)
        counts[tile_id] = sum(len(owners[canonical(e)]) == 1 for e in (p.top, p.bottom, p.left, p.right))
    return counts


def assert_seams_match(grid):
    for r, row in enumerate(grid):
        for c, p in enumerate(row):
            if r > 0:
                assert grid[r - 1][c].bottom == p.top, (r, c)
            if c > 0:
                assert row[c - 1].right == p.left, (r, c)


# --- parsing ------------------------------------------------------------------


def test_parse_input_ids_and_rows():
    tiles = day20.parse_input(SAMPLE)
    assert sorted(tiles) == [1171, 1427, 1489, 1951, 2311, 2473, 2729, 2971, 3079]
    assert all(len(rows) == 10 and all(len(r) == 10 for r in rows) for rows in tiles.values())
    assert tiles[2311][0] == "..##.#..#."
    assert tiles[2311][-1] == "..###..###"
    assert tiles[3079] == block(
        "#.#.#####.\n.#..######\n..#.......\n######....\n####.#..#.\n"
        ".#...#.##.\n#.#####.##\n..#.###...\n..#.......\n..#.###..."
    )


def test_parse_input_tolerates_extra_blank_lines_and_whitespace():
    messy = "\n\n" + SAMPLE.replace("\n\nTile", "\n\n\n  Tile") + "\n\n\n"
    assert day20.parse_input(messy) == day20.parse_input(SAMPLE)


def test_crlf_input():
    assert day20.parse_input(SAMPLE.replace("\n", "\r\n")) == day20.parse_input(SAMPLE)


# --- rotate / flip / orientations: the dihedral group of the square ----------------


def test_rotate_is_a_quarter_turn_clockwise():
    assert day20.rotate(("ab", "cd")) == ("ca", "db")
    assert day20.rotate(("abc", "def", "ghi")) == ("gda", "heb", "ifc")


def test_flip_is_a_left_right_mirror():
    assert day20.flip(("abc", "def")) == ("cba", "fed")


def test_four_rotations_and_two_flips_are_the_identity():
    tile = day20.parse_input(SAMPLE)[2311]
    assert day20.rotate(day20.rotate(day20.rotate(day20.rotate(tile)))) == tile
    assert day20.flip(day20.flip(tile)) == tile


def test_orientations_are_eight_distinct_and_closed():
    """Eight distinct views of an asymmetric tile; rotating or flipping any one of them
    stays inside the set, and any member generates the same set -- the group D4."""
    tile = day20.parse_input(SAMPLE)[2311]
    views = day20.orientations(tile)
    assert views[0] == tile
    assert len(set(views)) == 8
    for view in views:
        assert day20.rotate(view) in views
        assert day20.flip(view) in views
        assert set(day20.orientations(view)) == set(views)


def test_orientations_of_a_symmetric_block_repeat():
    """A fully symmetric block has one distinct view, listed eight times."""
    plus = (".#.", "###", ".#.")
    assert day20.orientations(plus) == [plus] * 8


def test_rotate_moves_the_edges_round():
    """Clockwise: old left (reversed) becomes top, old top becomes right, old right
    (reversed) becomes bottom, old bottom becomes left."""
    tile = day20.parse_input(SAMPLE)[2311]
    before = day20.piece(2311, tile)
    after = day20.piece(2311, day20.rotate(tile))
    assert after.top == before.left[::-1]
    assert after.right == before.top
    assert after.bottom == before.right[::-1]
    assert after.left == before.bottom


def test_flip_mirrors_the_edges():
    tile = day20.parse_input(SAMPLE)[2311]
    before = day20.piece(2311, tile)
    after = day20.piece(2311, day20.flip(tile))
    assert after.top == before.top[::-1]
    assert after.bottom == before.bottom[::-1]
    assert after.left == before.right
    assert after.right == before.left


def test_piece_reads_edges_in_a_consistent_direction():
    p = day20.piece(7, ("abc", "def", "ghi"))
    assert (p.top, p.bottom, p.left, p.right) == ("abc", "ghi", "adg", "cfi")
    assert p.tile_id == 7


# --- assembly on the statement's example ---------------------------------------------


@pytest.fixture(scope="module")
def sample_tiles():
    return day20.parse_input(SAMPLE)


@pytest.fixture(scope="module")
def sample_grid(sample_tiles):
    return day20.assemble(sample_tiles)


def test_sample_assembles_to_the_statement_arrangement(sample_grid):
    """Any of the eight orientations of the statement's grid is a correct answer."""
    assert id_grid(sample_grid) in grid_orientations(STATEMENT_IDS)


def test_sample_grid_seams_match_and_use_every_tile_once(sample_grid, sample_tiles):
    assert_seams_match(sample_grid)
    ids = [p.tile_id for row in sample_grid for p in row]
    assert sorted(ids) == sorted(sample_tiles)
    for p in sample_grid[0] + sample_grid[-1]:
        assert p.rows in day20.orientations(sample_tiles[p.tile_id])


def test_sample_corners_and_part1(sample_grid, sample_tiles):
    assert set(day20.corner_ids(sample_grid)) == {1951, 3079, 2971, 1171}
    assert day20.part1(sample_tiles) == 1951 * 3079 * 2971 * 1171 == 20899048083289


def test_sample_edges_are_shared_by_at_most_two_tiles(sample_tiles):
    """36 edge slots, 12 interior seams shared by two tiles, 12 on the perimeter: 24 borders."""
    owners = edge_owners(sample_tiles)
    assert len(owners) == 24
    assert max(len(s) for s in owners.values()) == 2
    assert Counter(unmatched_edge_counts(sample_tiles).values()) == {0: 1, 1: 4, 2: 4}


def test_single_tile_assembles_to_itself():
    tiles = {5: day20.parse_input(SAMPLE)[2311]}
    grid = day20.assemble(tiles)
    assert id_grid(grid) == [[5]]
    assert day20.part1(tiles) == 5**4


def test_assemble_rejects_a_non_square_pile(sample_tiles):
    eight = dict(list(sample_tiles.items())[:8])
    with pytest.raises(ValueError, match="square"):
        day20.assemble(eight)


def test_assemble_rejects_tiles_that_cannot_fit():
    """Four tiles whose edges never match each other, in any orientation."""
    tiles = {
        1: ("...", "...", "..."),
        2: ("###", "###", "###"),
        3: ("#..", "...", "..#"),
        4: (".#.", "#.#", ".#."),
    }
    with pytest.raises(ValueError, match="assemble"):
        day20.assemble(tiles)


# --- stitching -----------------------------------------------------------------------


def test_statement_image_is_the_arrangement_with_borders_removed():
    """The two blocks the statement prints agree with each other."""
    assert strip_borders(STATEMENT_ARRANGEMENT) == block(STATEMENT_IMAGE)


def test_stitched_sample_is_the_statement_image(sample_grid):
    image = day20.stitch(sample_grid)
    assert len(image) == 24 and all(len(row) == 24 for row in image)
    assert block(STATEMENT_IMAGE) in day20.orientations(image)


def test_stitch_of_one_tile_is_its_interior():
    tile = day20.parse_input(SAMPLE)[2311]
    assert day20.stitch([[day20.piece(2311, tile)]]) == tuple(row[1:-1] for row in tile[1:-1])


# --- sea monsters --------------------------------------------------------------------


def test_sea_monster_shape():
    assert len(day20.SEA_MONSTER) == 3
    assert all(len(row) == 20 for row in day20.SEA_MONSTER)
    assert len(day20.MONSTER_CELLS) == 15
    assert day20.monster_anchors(day20.SEA_MONSTER) == [(0, 0)]


def test_monster_only_needs_its_own_cells_to_be_hashes():
    """The statement: the spaces in the pattern can be anything."""
    solid = ("#" * 20,) * 3
    assert day20.monster_anchors(solid) == [(0, 0)]
    assert day20.monster_anchors(("." * 20,) * 3) == []
    assert day20.monster_anchors(("#" * 19,) * 3) == []  # too narrow


def test_monster_cells_are_a_set_so_overlaps_count_once():
    """A 3x40 sea of '#' holds a monster at every one of 21 anchors; the 315 cell hits
    collapse to 97 distinct cells, and roughness is 120 - 97, never negative."""
    sea = ("#" * 40,) * 3
    assert len(day20.monster_anchors(sea)) == 21
    assert len(day20.monster_cells(sea)) == 97
    assert day20.roughness(sea) == 120 - 97


def test_roughness_with_no_monsters_is_every_hash():
    assert day20.roughness(("#.#", "...", "##.")) == 4


def test_sample_monsters_in_exactly_one_orientation(sample_grid):
    image = day20.stitch(sample_grid)
    found = [day20.monster_anchors(view) for view in day20.orientations(image)]
    assert sum(bool(anchors) for anchors in found) == 1
    (anchors,) = [a for a in found if a]
    assert len(anchors) == 2
    assert sorted(anchors) == [(2, 2), (16, 1)]


def test_sample_part2(sample_grid, sample_tiles):
    image = day20.stitch(sample_grid)
    assert sum(row.count("#") for row in image) == 303
    assert day20.roughness(image) == 303 - 2 * 15 == 273
    assert day20.part2(sample_tiles) == 273


def test_solve_sample():
    assert day20.solve(SAMPLE) == (20899048083289, 273)


# --- the real input's structure, and an independent corner count ------------------------
#
# Nothing in `assemble` assumes borders are unique.  The real input makes them
# so, which is why the search barely backtracks and why the classic shortcut
# -- a corner is a tile with exactly two edges nobody else has -- gives the
# same four tiles as the assembly.  Both facts are pinned here.


@pytest.fixture(scope="module")
def real(real_input):
    return day20.parse_input(real_input(20))


@pytest.fixture(scope="module")
def real_grid(real):
    return day20.assemble(real)


def test_real_is_144_ten_by_ten_tiles(real):
    assert len(real) == 144
    assert all(len(rows) == 10 and all(len(r) == 10 for r in rows) for rows in real.values())


def test_real_borders_are_unique(real):
    """312 distinct borders; 264 shared by exactly two tiles (the 2*12*11 interior seams),
    48 on the perimeter (4*12); none palindromic, no tile symmetric."""
    owners = edge_owners(real)
    assert len(owners) == 312
    assert max(len(s) for s in owners.values()) == 2
    assert Counter(len(s) for s in owners.values()) == {2: 264, 1: 48}
    assert not any(edge == edge[::-1] for edge in owners)
    assert all(len(set(day20.orientations(rows))) == 8 for rows in real.values())


def test_real_tiles_by_unmatched_edges(real):
    """4 corners, 40 sides, 100 interior."""
    assert Counter(unmatched_edge_counts(real).values()) == {0: 100, 1: 40, 2: 4}


def test_real_grid_is_consistent(real_grid, real):
    assert len(real_grid) == 12 and all(len(row) == 12 for row in real_grid)
    assert_seams_match(real_grid)
    assert sorted(p.tile_id for row in real_grid for p in row) == sorted(real)


def test_real_corners_agree_with_the_edge_count_shortcut(real_grid, real):
    by_count = {tile_id for tile_id, n in unmatched_edge_counts(real).items() if n == 2}
    assert set(day20.corner_ids(real_grid)) == by_count
    assert day20.part1(real) == prod(by_count)


def test_real_grid_perimeter_is_exactly_the_unmatched_edges(real_grid, real):
    owners = edge_owners(real)
    perimeter = (
        [p.top for p in real_grid[0]]
        + [p.bottom for p in real_grid[-1]]
        + [row[0].left for row in real_grid]
        + [row[-1].right for row in real_grid]
    )
    assert len(perimeter) == 48
    assert {canonical(e) for e in perimeter} == {e for e, s in owners.items() if len(s) == 1}


def test_real_image_and_monsters(real_grid, real):
    image = day20.stitch(real_grid)
    assert len(image) == 96 and all(len(row) == 96 for row in image)
    found = [day20.monster_anchors(view) for view in day20.orientations(image)]
    assert sum(bool(anchors) for anchors in found) == 1
    (anchors,) = [a for a in found if a]
    assert len(anchors) == 37
    (covered,) = [day20.monster_cells(v) for v in day20.orientations(image) if day20.monster_anchors(v)]
    assert len(covered) == 37 * 15  # no two monsters overlap
    hashes = sum(row.count("#") for row in image)
    assert day20.part2(real) == hashes - 37 * 15


def test_real_input_locked(check_locked):
    check_locked(day20, LOCKED)
