"""Day 17: Conway Cubes."""

import pytest

import day17

LOCKED = (359, 2228)

# The statement's initial state: a Life glider.
SAMPLE = """.#.
..#
###
"""

# The statement's layer-by-layer dumps after 1, 2 and 3 cycles in 3-D.  The
# frame of view follows the active cells, so x and y are relative; z is not.
LAYERS_3D = {
    1: """z=-1
#..
..#
.#.

z=0
#.#
.##
.#.

z=1
#..
..#
.#.
""",
    2: """z=-2
.....
.....
..#..
.....
.....

z=-1
..#..
.#..#
....#
.#...
.....

z=0
##...
##...
#....
....#
.###.

z=1
..#..
.#..#
....#
.#...
.....

z=2
.....
.....
..#..
.....
.....
""",
    3: """z=-2
.......
.......
..##...
..###..
.......
.......
.......

z=-1
..#....
...#...
#......
.....##
.#...#.
..#.#..
...#...

z=0
...#...
.......
#......
.......
.....##
.##.#..
...#...

z=1
..#....
...#...
#......
.....##
.#...#.
..#.#..
...#...

z=2
.......
.......
..##...
..###..
.......
.......
.......
""",
}

# The statement's Part Two dump after 1 cycle in 4-D: nine 3x3 layers.
LAYERS_4D_CYCLE_1 = """z=-1, w=-1
#..
..#
.#.

z=0, w=-1
#..
..#
.#.

z=1, w=-1
#..
..#
.#.

z=-1, w=0
#..
..#
.#.

z=0, w=0
#.#
.##
.#.

z=1, w=0
#..
..#
.#.

z=-1, w=1
#..
..#
.#.

z=0, w=1
#..
..#
.#.

z=1, w=1
#..
..#
.#.
"""


def cells_from_layers(text: str) -> set[tuple[int, ...]]:
    """Read a statement-style dump (`z=-1` or `z=-1, w=0` headers) into a cell set."""
    cells = set()
    for block in text.strip().split("\n\n"):
        header, *rows = block.splitlines()
        extra = tuple(int(part.split("=")[1]) for part in header.split(", "))
        for y, row in enumerate(rows):
            for x, char in enumerate(row):
                if char == "#":
                    cells.add((x, y) + extra)
    return cells


def normalised(cells) -> set[tuple[int, ...]]:
    """Shift x and y so each starts at 0, matching a frame that follows the active cells."""
    x0 = min(cell[0] for cell in cells)
    y0 = min(cell[1] for cell in cells)
    return {(cell[0] - x0, cell[1] - y0) + cell[2:] for cell in cells}


def test_parse_input():
    assert day17.parse_input(SAMPLE) == {(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)}


def test_crlf_input():
    assert day17.parse_input(SAMPLE.replace("\n", "\r\n")) == day17.parse_input(SAMPLE)


@pytest.mark.parametrize(("dims", "expected"), [(2, 8), (3, 26), (4, 80)])
def test_neighbour_offsets_count(dims, expected):
    """26 neighbours in 3-D and 80 in 4-D, per the statement; 3**dims - 1 in general."""
    offsets = day17.neighbour_offsets(dims)
    assert len(offsets) == len(set(offsets)) == expected
    assert all(len(offset) == dims and set(offset) <= {-1, 0, 1} for offset in offsets)
    assert (0,) * dims not in offsets


def test_neighbours_include_diagonals():
    """The statement's own example: (2,2,2) and (0,2,3) are neighbours of (1,2,3)."""
    offsets = day17.neighbour_offsets(3)
    assert (2 - 1, 2 - 2, 2 - 3) in offsets
    assert (0 - 1, 2 - 2, 3 - 3) in offsets


def test_embed_pads_the_extra_axes_with_zero():
    assert day17.embed(frozenset({(1, 2)}), 3) == {(1, 2, 0)}
    assert day17.embed(frozenset({(1, 2)}), 4) == {(1, 2, 0, 0)}


AXIS_NEIGHBOURS = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1)]


@pytest.mark.parametrize(
    ("count", "centre_active", "expected"),
    [
        (0, True, False),
        (1, True, False),
        (2, True, True),
        (3, True, True),
        (4, True, False),
        (0, False, False),
        (2, False, False),
        (3, False, True),
        (4, False, False),
    ],
)
def test_rule_by_neighbour_count(count, centre_active, expected):
    """The two rules of the statement, one neighbour count at a time: an active
    cube survives on exactly 2 or 3, an inactive one is born on exactly 3."""
    active = set(AXIS_NEIGHBOURS[:count])
    if centre_active:
        active.add((0, 0, 0))
    assert ((0, 0, 0) in day17.step(active, 3)) is expected


def test_a_lone_cube_dies_and_nothing_is_born_from_one():
    assert day17.step({(0, 0, 0)}, 3) == set()


@pytest.mark.parametrize("cycles", [1, 2, 3])
def test_example_layers_3d(cycles):
    """Every layer the statement prints after cycles 1, 2 and 3."""
    assert normalised(day17.boot(day17.parse_input(SAMPLE), 3, cycles)) == normalised(
        cells_from_layers(LAYERS_3D[cycles])
    )


def test_part1_example():
    assert day17.part1(day17.parse_input(SAMPLE)) == 112


def test_example_layers_4d_cycle_1():
    """The statement's Part Two dump after one cycle."""
    assert normalised(day17.boot(day17.parse_input(SAMPLE), 4, 1)) == normalised(
        cells_from_layers(LAYERS_4D_CYCLE_1)
    )


def test_first_4d_cycle_is_the_first_3d_cycle_replicated():
    """Why those nine layers look the way they do: after one cycle only the
    initial slice can have been anyone's neighbour, and a cell sees the same
    slice cells whether it is one step away in z, in w, or in both.  So the
    (0,0) layer equals 3-D's z=0 and every other (z,w) layer equals 3-D's z=1."""
    slice2d = day17.parse_input(SAMPLE)
    after_3d = day17.boot(slice2d, 3, 1)
    after_4d = day17.boot(slice2d, 4, 1)
    layer_3d = {z: {(x, y) for x, y, zz in after_3d if zz == z} for z in (0, 1)}
    for z in (-1, 0, 1):
        for w in (-1, 0, 1):
            layer_4d = {(x, y) for x, y, zz, ww in after_4d if (zz, ww) == (z, w)}
            assert layer_4d == layer_3d[0 if (z, w) == (0, 0) else 1]


def test_part2_example():
    assert day17.part2(day17.parse_input(SAMPLE)) == 848


def test_two_dimensions_is_plain_life_and_the_seed_is_a_glider():
    """With dims=2 the engine is ordinary Conway's Life, and the statement's
    example is the glider: after four generations it is itself, moved one
    cell down and one right."""
    start = day17.embed(day17.parse_input(SAMPLE), 2)
    assert day17.boot(day17.parse_input(SAMPLE), 2, 4) == {(x + 1, y + 1) for x, y in start}


def test_growth_is_at_most_one_cell_per_axis_per_cycle():
    """The docstring's bound on the occupied box, pinned: the example's 3x3
    slice can reach at most x,y in -6..8 and z,w in -6..6 after six cycles."""
    for dims in (3, 4):
        for cell in day17.boot(day17.parse_input(SAMPLE), dims):
            assert -6 <= cell[0] <= 8 and -6 <= cell[1] <= 8
            assert all(-6 <= c <= 6 for c in cell[2:])


def mirrored(cells, axis):
    return {cell[:axis] + (-cell[axis],) + cell[axis + 1 :] for cell in cells}


@pytest.mark.parametrize("cycles", [1, 2, 3, 6])
def test_example_is_mirror_symmetric_in_the_extra_axes(cycles):
    """The slice sits at z=0 (and w=0), and the rule is the same in every
    direction, so the state stays symmetric under z -> -z and w -> -w for
    ever -- and, in 4-D, under swapping z and w.  This is the identity the
    guide's folded-simulation sidebar leans on."""
    slice2d = day17.parse_input(SAMPLE)
    after_3d = day17.boot(slice2d, 3, cycles)
    assert after_3d == mirrored(after_3d, 2)
    after_4d = day17.boot(slice2d, 4, cycles)
    assert after_4d == mirrored(after_4d, 2) == mirrored(after_4d, 3)
    assert after_4d == {(x, y, w, z) for x, y, z, w in after_4d}


def test_real_input_is_mirror_symmetric_in_the_extra_axes(real_input):
    slice2d = day17.parse_input(real_input(17))
    after_3d = day17.boot(slice2d, 3)
    assert after_3d == mirrored(after_3d, 2)
    after_4d = day17.boot(slice2d, 4)
    assert after_4d == mirrored(after_4d, 2) == mirrored(after_4d, 3)
    assert after_4d == {(x, y, w, z) for x, y, z, w in after_4d}


def test_real_input_locked(check_locked):
    check_locked(day17, LOCKED)
