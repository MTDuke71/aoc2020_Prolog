:- begin_tests(day03).

:- use_module('../src/day03.pl').

% --- Puzzle example (from the problem statement) ---

example_input("\
..##.......
#...#...#..
.#....#..#.
..#.#...#.#
.#...##..#.
..#.##.....
.#.#.#....#
.#........#
#.##...#...
#...##....#
.#..#...#.#
").

test(parse_input) :-
    parse_input("..#\n#..\n", Rows),
    assertion(Rows == [['.', '.', '#'], ['#', '.', '.']]).

test(part1_example) :-
    example_input(Raw),
    parse_input(Raw, Rows),
    part1(Rows, P1),
    assertion(P1 == 7).

% The statement's five slope counts: 2, 7, 3, 4, 2.
test(slope_counts_example) :-
    example_input(Raw),
    parse_input(Raw, Rows),
    maplist([R-D, C]>>slope_trees(Rows, R, D, C),
            [1-1, 3-1, 5-1, 7-1, 1-2], Counts),
    assertion(Counts == [2, 7, 3, 4, 2]).

test(part2_example) :-
    example_input(Raw),
    parse_input(Raw, Rows),
    part2(Rows, P2),
    assertion(P2 =:= 2 * 7 * 3 * 4 * 2).

% --- slope_trees/4 behavior ---

% The pattern repeats to the right: on a 2-wide grid, column 2 wraps
% back to column 0.
test(column_wraps) :-
    slope_trees([['#', '.'], ['.', '#']], 2, 1, Count),
    assertion(Count == 1).

% Down > 1 skips rows entirely: three all-tree rows, down 2, visits
% rows 0 and 2 only.
test(down_skips_rows) :-
    slope_trees([['#'], ['#'], ['#']], 0, 2, Count),
    assertion(Count == 2).

% An empty grid has nothing to hit.
test(empty_grid) :-
    slope_trees([], 3, 1, Count),
    assertion(Count == 0).

% --- Real-input answer locks ---

real_input(Raw) :-
    read_file_to_string('inputs/day03.txt', Raw, []).

test(part1_real) :-
    real_input(Raw),
    solve(Raw, P1, _),
    assertion(P1 == 148).

test(part2_real) :-
    real_input(Raw),
    solve(Raw, _, P2),
    assertion(P2 == 727923200).

:- end_tests(day03).
