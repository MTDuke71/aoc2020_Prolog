:- module(day03, [parse_input/2, part1/2, part2/2, solve/3,
                  slope_trees/4]).

% Day 3: Toboggan Trajectory.
% The map is a grid of open squares (.) and trees (#) whose pattern
% repeats infinitely to the right. Starting at the top-left and stepping
% Right columns / Down rows at a time, count the trees hit before
% falling off the bottom. Part 1: slope right 3, down 1. Part 2: product
% of the counts over five fixed slopes.

% parse_input(+Raw, -Rows)
% Rows is a list of rows, each a list of char atoms ('.' or '#').
parse_input(Raw, Rows) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(string_chars, Lines, Rows).

% slope_trees(+Rows, +Right, +Down, -Count)
% Count is the number of trees on the slope: starting at the top-left,
% visit column I*Right (mod row width — the pattern repeats rightward)
% of every Down-th row, and count the '#' cells.
slope_trees(Rows, Right, Down, Count) :-
    slope_trees_(Rows, Right, Down, 0, 0, Count).

% slope_trees_(+Rows, +Right, +Down, +Col, +Acc, -Count)
% Accumulator walk: check the head row at Col (wrapped), then step to
% the row Down below (drop Down-1 of the remaining rows) at Col+Right.
slope_trees_([], _, _, _, Count, Count).
slope_trees_([Row|Rest], Right, Down, Col, Acc0, Count) :-
    length(Row, Width),
    Index is Col mod Width,
    nth0(Index, Row, Cell),
    (   Cell == '#'
    ->  Acc1 is Acc0 + 1
    ;   Acc1 = Acc0
    ),
    Col1 is Col + Right,
    Skip is Down - 1,
    drop(Skip, Rest, Rest1),
    slope_trees_(Rest1, Right, Down, Col1, Acc1, Count).

% drop(+N, +List, -Rest)
% Rest is List without its first N elements ([] if List is shorter).
drop(0, List, List) :- !.
drop(_, [], []) :- !.
drop(N, [_|Xs], Rest) :-
    N > 0,
    N1 is N - 1,
    drop(N1, Xs, Rest).

% slope_trees_pair(+Rows, +Right-Down, -Count)
% slope_trees/4 with the slope packed as a Right-Down pair, so it can
% be partially applied under maplist/3.
slope_trees_pair(Rows, Right-Down, Count) :-
    slope_trees(Rows, Right, Down, Count).

% part1(+Rows, -Answer)
part1(Rows, Answer) :-
    slope_trees(Rows, 3, 1, Answer).

% part2(+Rows, -Answer)
% Product of the tree counts over the five slopes from the statement.
part2(Rows, Answer) :-
    Slopes = [1-1, 3-1, 5-1, 7-1, 1-2],
    maplist(slope_trees_pair(Rows), Slopes, Counts),
    foldl([X, Acc0, Acc]>>(Acc is Acc0 * X), Counts, 1, Answer).

% solve(+Raw, -Part1, -Part2)
solve(Raw, Part1, Part2) :-
    parse_input(Raw, Rows),
    part1(Rows, Part1),
    part2(Rows, Part2).
