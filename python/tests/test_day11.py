"""Day 11: Seating System."""

import day11

LOCKED = (2321, 2102)

EXAMPLE = """\
L.LL.LL.LL
LLLLLLL.LL
L.L.L..L..
LLLL.LL.LL
L.LL.LL.LL
L.LLLLL.LL
..L.L.....
LLLLLLLLLL
L.LLLLLL.L
L.LLLLL.LL
"""


def neighbour_coords(raw, table_fn, row, col):
    """Resolve one row of a neighbour table back to (row, col) pairs.

    The tables hold dense seat ids; reading them back as coordinates is what
    lets the expectations below be checked against the printed grid.
    """
    layout = day11.parse_input(raw)
    ids = table_fn(layout)[layout.index[(row, col)]]
    return [layout.coords[i] for i in ids]


def test_parse_input_drops_the_floor():
    """100 squares in the example, 71 of which are seats."""
    layout = day11.parse_input(EXAMPLE)
    assert (layout.rows, layout.cols) == (10, 10)
    assert len(layout.coords) == 71
    assert layout.coords[:2] == [(0, 0), (0, 2)]


def test_adjacent_table_of_the_corner_seat():
    """(0,0) touches only the two seats below: the square to its right is floor."""
    assert neighbour_coords(EXAMPLE, day11.adjacent_table, 0, 0) == [(1, 0), (1, 1)]


def test_visible_table_of_the_corner_seat():
    """Along the rays the same corner also sees past that floor to (0,2)."""
    assert sorted(neighbour_coords(EXAMPLE, day11.visible_table, 0, 0)) == [
        (0, 2),
        (1, 0),
        (1, 1),
    ]


def test_visible_sees_eight_seats_through_floor():
    """The statement's vignette: one occupied seat in each of the 8 directions."""
    grid = """\
.......#.
...#.....
.#.......
.........
..#L....#
....#....
.........
#........
...#.....
"""
    assert len(neighbour_coords(grid, day11.visible_table, 4, 3)) == 8


def test_an_empty_seat_blocks_the_sight_line():
    """Blocking is by seat, not by occupancy.

    The leftmost L sees exactly one seat -- the empty one beside it -- which
    hides every occupied seat further right.  A ray that stopped only at
    occupied seats would report several.
    """
    grid = ".............\n.L.L.#.#.#.#.\n.............\n"
    assert neighbour_coords(grid, day11.visible_table, 1, 1) == [(1, 3)]


def test_a_seat_walled_in_by_floor_sees_nothing():
    grid = """\
.##.##.
#.#.#.#
##...##
...L...
##...##
#.#.#.#
.##.##.
"""
    assert neighbour_coords(grid, day11.visible_table, 3, 3) == []


def test_part1_example():
    assert day11.part1(day11.parse_input(EXAMPLE)) == 37


def test_part2_example():
    assert day11.part2(day11.parse_input(EXAMPLE)) == 26


def test_a_floor_only_layout_is_already_stable():
    layout = day11.parse_input("...\n...\n")
    assert day11.part1(layout) == 0
    assert day11.part2(layout) == 0


def test_a_lone_seat_fills_and_stays():
    """No neighbours means the fill rule applies forever and the empty rule never does."""
    layout = day11.parse_input(".L.\n")
    assert day11.part1(layout) == 1
    assert day11.part2(layout) == 1


def test_the_update_is_simultaneous():
    """Every seat reads the *previous* round's state, never a half-updated one.

    Two adjacent empty seats both fill on round 1, because each sees the
    other as still empty.  An in-place update would fill the first and then
    leave the second empty, giving 1 instead of 2.
    """
    layout = day11.parse_input("LL\n")
    assert day11.part1(layout) == 2


def test_crlf_input():
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day11.parse_input(crlf) == day11.parse_input(EXAMPLE)
    assert day11.solve(crlf) == (37, 26)


def test_real_input_locked(check_locked):
    check_locked(day11, LOCKED)
