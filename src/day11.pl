:- module(day11, [parse_input/2, part1/2, part2/2, solve/3,
                  seat_layout/2, adjacent_table/2, visible_table/2,
                  stable_occupancy/3]).

% Day 11: Seating System.
% A cellular automaton on a grid of floor (.), empty seats (L) and occupied
% seats (#). Every round each seat looks at a fixed set of other seats and
% flips: an empty seat with no occupied neighbours fills, an occupied seat
% with Tolerance or more occupied neighbours empties. Iterate to a fixpoint
% and count the occupied seats.
%
% The two parts differ only in what "neighbour" means and in the tolerance:
%   part 1: the 8 immediately adjacent squares, tolerance 4;
%   part 2: the first seat visible along each of the 8 rays, tolerance 5.
% So the simulation is written once and driven by a precomputed neighbour
% table. Building that table up front is what makes the whole day cheap:
% the rays are re-walked zero times, not once per round.

% ---------------------------------------------------------------------------
% Parsing and the seat layout
% ---------------------------------------------------------------------------

% parse_input(+Raw, -Grid)
% Grid is a list of rows, each a list of char atoms ('.', 'L' or '#'),
% the same shape day03 used for the toboggan map.
parse_input(Raw, Grid) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(string_chars, Lines, Grid).

% seat_layout(+Grid, -Layout)
% Layout = layout(Rows, Cols, Coords, Index).
%   Coords is every seat coordinate R-C in row-major order; the seat at
%   position I in that list is "seat I" from here on.
%   Index is an assoc R-C -> I, the inverse map, used only while building
%   the neighbour tables.
% Floor squares never change and never count, so they are dropped now and
% the simulation only ever carries seats.
seat_layout(Grid, layout(Rows, Cols, Coords, Index)) :-
    length(Grid, Rows),
    Grid = [FirstRow|_],
    length(FirstRow, Cols),
    findall(R-C, seat_at(Grid, R, C), Coords),
    length(Coords, N),
    findall(I, between(1, N, I), Ids),
    pairs_keys_values(Pairs, Coords, Ids),
    list_to_assoc(Pairs, Index).

% seat_at(+Grid, -R, -C)
% Enumerate the 1-based coordinates of the non-floor squares, row-major.
% Both nth1/3 calls run in generate mode, so this is one ordered sweep of
% the grid rather than Rows*Cols random accesses.
seat_at(Grid, R, C) :-
    nth1(R, Grid, Row),
    nth1(C, Row, Cell),
    Cell \== '.'.

% direction(-DR, -DC)
% The eight compass steps, as row/column deltas.
direction(-1, -1).
direction(-1,  0).
direction(-1,  1).
direction( 0, -1).
direction( 0,  1).
direction( 1, -1).
direction( 1,  0).
direction( 1,  1).

% ---------------------------------------------------------------------------
% Neighbour tables
% ---------------------------------------------------------------------------
%
% Both tables are a compound term nbrs(L1, ..., LN) whose I-th argument is
% the list of seat ids that seat I watches. A compound term is Prolog's
% array: arg/3 is O(1), where nth1/3 on a list would be O(N) and turn every
% round into a quadratic scan.

% adjacent_table(+Layout, -Table)
% Part 1's rule: the seats among the eight squares touching this one.
adjacent_table(layout(_Rows, _Cols, Coords, Index), Table) :-
    maplist(adjacent_seats(Index), Coords, Lists),
    Table =.. [nbrs|Lists].

% adjacent_seats(+Index, +Coord, -Seats)
% findall over direction/2 collects the neighbours that exist and are
% seats; the get_assoc/3 lookup fails for floor and for off-grid squares
% alike, so no bounds check is needed here.
adjacent_seats(Index, R-C, Seats) :-
    findall(Seat,
            ( direction(DR, DC),
              R1 is R + DR,
              C1 is C + DC,
              get_assoc(R1-C1, Index, Seat)
            ),
            Seats).

% visible_table(+Layout, -Table)
% Part 2's rule: the first seat along each of the eight rays, however much
% floor lies in between.
visible_table(layout(Rows, Cols, Coords, Index), Table) :-
    maplist(visible_seats(Rows, Cols, Index), Coords, Lists),
    Table =.. [nbrs|Lists].

% visible_seats(+Rows, +Cols, +Index, +Coord, -Seats)
visible_seats(Rows, Cols, Index, Coord, Seats) :-
    findall(Seat,
            ( direction(DR, DC),
              first_seat(Rows, Cols, Index, Coord, DR, DC, Seat)
            ),
            Seats).

% first_seat(+Rows, +Cols, +Index, +From, +DR, +DC, -Seat)
% March from From in direction DR-DC and stop at the first seat found.
% Fails if the ray leaves the grid without meeting one, which is exactly
% the "sees no seat that way" case findall/3 should drop.
first_seat(Rows, Cols, Index, R-C, DR, DC, Seat) :-
    R1 is R + DR,
    C1 is C + DC,
    between(1, Rows, R1),
    between(1, Cols, C1),
    (   get_assoc(R1-C1, Index, Found)
    ->  Seat = Found
    ;   first_seat(Rows, Cols, Index, R1-C1, DR, DC, Seat)
    ).

% ---------------------------------------------------------------------------
% The simulation
% ---------------------------------------------------------------------------
%
% A state is a compound term occ(V1, ..., VN) with Vi in 0..1 -- occupancy
% only, since a seat's L/# identity is the whole of its mutable state and
% the floor was discarded during layout. Counting occupied neighbours is
% then a sum of arg/3 lookups, and the round-over-round comparison is one
% ==/2 on the whole term.

% stable_occupancy(+Table, +Tolerance, -Occupied)
% Run the automaton from the all-empty grid to its fixpoint and count the
% occupied seats there.
stable_occupancy(Table, Tolerance, Occupied) :-
    functor(Table, _, N),
    findall(I, between(1, N, I), Ids),
    length(Zeros, N),
    maplist(=(0), Zeros),
    State0 =.. [occ|Zeros],
    fixpoint(Table, Tolerance, Ids, State0, Final),
    occupied_count(Final, Occupied).

% fixpoint(+Table, +Tolerance, +Ids, +State0, -Final)
% Apply rounds until one changes nothing. Note what this does *not* claim:
% a threshold automaton like this can in principle settle into a 2-cycle
% rather than a fixpoint, and this loop would spin forever on one. The
% puzzle promises stabilisation; the function guide has the details.
fixpoint(Table, Tolerance, Ids, State0, Final) :-
    next_state(Table, Tolerance, Ids, State0, State1),
    (   State1 == State0
    ->  Final = State0
    ;   fixpoint(Table, Tolerance, Ids, State1, Final)
    ).

% next_state(+Table, +Tolerance, +Ids, +State0, -State)
% One round. Every seat reads State0 and writes into a fresh term, which
% is the "applied to every seat simultaneously" requirement -- a mutable
% grid updated in place would let a seat see this round's changes.
next_state(Table, Tolerance, Ids, State0, State) :-
    maplist(next_seat(Table, Tolerance, State0), Ids, Cells),
    State =.. [occ|Cells].

% next_seat(+Table, +Tolerance, +State0, +I, -Cell)
next_seat(Table, Tolerance, State0, I, Cell) :-
    arg(I, State0, Cell0),
    arg(I, Table, Neighbours),
    occupied_among(Neighbours, State0, Count),
    seat_rule(Cell0, Count, Tolerance, Cell).

% seat_rule(+Cell0, +Count, +Tolerance, -Cell)
% The statement's three rules, one clause each. Outputs are unified after
% the cut so a pre-bound Cell cannot skip a committed clause.
seat_rule(0, Count, _Tolerance, Cell) :-
    Count =:= 0,
    !,
    Cell = 1.
seat_rule(1, Count, Tolerance, Cell) :-
    Count >= Tolerance,
    !,
    Cell = 0.
seat_rule(Cell0, _Count, _Tolerance, Cell) :-
    Cell = Cell0.

% occupied_among(+Ids, +State, -Count)
% How many of these seats are occupied, by accumulator so the walk is
% tail-recursive and choicepoint-free.
occupied_among(Ids, State, Count) :-
    occupied_among_(Ids, State, 0, Count).

% occupied_among_(+Ids, +State, +Acc0, -Count)
occupied_among_([], _State, Count, Count).
occupied_among_([I|Ids], State, Acc0, Count) :-
    arg(I, State, Value),
    Acc1 is Acc0 + Value,
    occupied_among_(Ids, State, Acc1, Count).

% occupied_count(+State, -Occupied)
occupied_count(State, Occupied) :-
    State =.. [_|Cells],
    sum_list(Cells, Occupied).

% ---------------------------------------------------------------------------
% Parts
% ---------------------------------------------------------------------------

% part1(+Grid, -Occupied)
part1(Grid, Occupied) :-
    seat_layout(Grid, Layout),
    adjacent_table(Layout, Table),
    stable_occupancy(Table, 4, Occupied).

% part2(+Grid, -Occupied)
part2(Grid, Occupied) :-
    seat_layout(Grid, Layout),
    visible_table(Layout, Table),
    stable_occupancy(Table, 5, Occupied).

% solve(+Raw, -Part1, -Part2)
% Both parts index the same layout, so solve builds it once; part1/2 and
% part2/2 stay self-contained for the tests and the bench.
solve(Raw, Part1, Part2) :-
    parse_input(Raw, Grid),
    seat_layout(Grid, Layout),
    adjacent_table(Layout, Adjacent),
    stable_occupancy(Adjacent, 4, Part1),
    visible_table(Layout, Visible),
    stable_occupancy(Visible, 5, Part2).
