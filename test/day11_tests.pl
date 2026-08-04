:- begin_tests(day11).

:- use_module('../src/day11.pl').

% The statement's 10x10 waiting area.
example_input("\
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
").

example_grid(Grid) :-
    example_input(Raw),
    parse_input(Raw, Grid).

% seat_neighbours(+Grid, +Table, +Seat, -Coords)
% Resolve one row of a neighbour table back to R-C coordinates, so the
% expectations below read as grid positions rather than seat ids.
seat_neighbours(Grid, Which, Seat, Coords) :-
    seat_layout(Grid, Layout),
    Layout = layout(_Rows, _Cols, SeatCoords, _Index),
    call(Which, Layout, Table),
    arg(Seat, Table, Ids),
    maplist([I, Coord]>>nth1(I, SeatCoords, Coord), Ids, Coords).

test(parse_rows_of_chars) :-
    example_grid(Grid),
    Grid = [FirstRow|_],
    assertion(FirstRow == ['L', '.', 'L', 'L', '.', 'L', 'L', '.', 'L', 'L']),
    length(Grid, Rows),
    assertion(Rows == 10).

% Floor is dropped at layout time: 100 squares, 71 of them seats.
test(layout_keeps_only_seats) :-
    example_grid(Grid),
    seat_layout(Grid, layout(Rows, Cols, Coords, _Index)),
    length(Coords, Seats),
    assertion(Rows-Cols == 10-10),
    assertion(Seats == 71),
    assertion(Coords = [1-1, 1-3|_]).

% Seat 1 is the top-left corner. Adjacently it touches only the two seats
% below it -- the square to its right is floor.
test(adjacent_table_corner) :-
    example_grid(Grid),
    seat_neighbours(Grid, adjacent_table, 1, Coords),
    assertion(Coords == [2-1, 2-2]).

% Looking along the rays, the same corner also sees past that floor square
% to the seat at 1-3.
test(visible_table_corner) :-
    example_grid(Grid),
    seat_neighbours(Grid, visible_table, 1, Coords),
    assertion(Coords == [1-3, 2-1, 2-2]).

% --- The Part Two sight-line vignettes ---

% Eight occupied seats, one per direction, all beyond some floor.
test(visible_sees_eight) :-
    parse_input("\
.......#.
...#.....
.#.......
.........
..#L....#
....#....
.........
#........
...#.....
", Grid),
    seat_neighbours(Grid, visible_table, 5, Coords),
    length(Coords, N),
    assertion(N == 8).

% The leftmost empty seat sees exactly one seat: the empty one beside it,
% which blocks its view of every occupied seat further right.
test(visible_blocked_by_empty_seat) :-
    parse_input("\
.............
.L.L.#.#.#.#.
.............
", Grid),
    seat_neighbours(Grid, visible_table, 1, Coords),
    assertion(Coords == [2-4]).

% Walled in by floor along every ray: this seat sees nothing at all.
test(visible_sees_nothing) :-
    parse_input("\
.##.##.
#.#.#.#
##...##
...L...
##...##
#.#.#.#
.##.##.
", Grid),
    seat_layout(Grid, Layout),
    Layout = layout(_, _, Coords, Index),
    get_assoc(4-4, Index, Middle),
    assertion(nth1(Middle, Coords, 4-4)),
    visible_table(Layout, Table),
    arg(Middle, Table, Ids),
    assertion(Ids == []).

% --- Fixpoint answers ---

test(part1_example) :-
    example_input(Raw),
    solve(Raw, Part1, _Part2),
    assertion(Part1 == 37).

test(part2_example) :-
    example_input(Raw),
    solve(Raw, _Part1, Part2),
    assertion(Part2 == 26).

% A layout with no seats at all is already stable, with nobody seated.
test(floor_only_layout_is_stable) :-
    parse_input("...\n...\n", Grid),
    part1(Grid, Occupied1),
    part2(Grid, Occupied2),
    assertion(Occupied1 == 0),
    assertion(Occupied2 == 0).

% A lone seat has no neighbours, so it fills on the first round and stays.
test(single_seat_fills) :-
    parse_input(".L.\n", Grid),
    part1(Grid, Occupied1),
    part2(Grid, Occupied2),
    assertion(Occupied1 == 1),
    assertion(Occupied2 == 1).

% --- Real-input answer locks ---
% Each part runs its own simulation here rather than going through solve/3,
% so the suite pays for two runs to the fixpoint instead of four.

real_grid(Grid) :-
    read_file_to_string('inputs/day11.txt', Raw, []),
    parse_input(Raw, Grid).

test(part1_real) :-
    real_grid(Grid),
    part1(Grid, Occupied),
    assertion(Occupied == 2321).

test(part2_real) :-
    real_grid(Grid),
    part2(Grid, Occupied),
    assertion(Occupied == 2102).

:- end_tests(day11).
