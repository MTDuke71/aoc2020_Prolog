:- module(day05, [parse_input/2, part1/2, part2/2, solve/3,
                  seat_id/2, seat/4]).

% Day 5: Binary Boarding.
% Each boarding pass is a 10-character binary space partition: the first
% 7 characters (F/B) name one of 128 rows, the last 3 (L/R) one of 8
% columns, and the seat ID is Row*8 + Col. Read as bits — F/L = 0 (lower
% half), B/R = 1 (upper half) — the whole pass is a 10-bit number equal
% to its seat ID, so no halving arithmetic is needed. Part 1: the highest
% seat ID. Part 2: the one empty seat whose neighbours are both occupied.

% parse_input(+Raw, -Ids)
% Ids is the list of seat IDs, one per non-blank line.
parse_input(Raw, Ids) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(seat_id, Lines, Ids).

% seat_id(+Pass, -Id)
% Decode a boarding pass to its seat ID by reading its ten characters as
% a binary number (Horner's method), most-significant character first.
seat_id(Pass, Id) :-
    string_chars(Pass, Chars),
    foldl(add_bit, Chars, 0, Id).

% add_bit(+Char, +Acc0, -Acc)
% Shift the accumulator left one bit and add this character's bit.
add_bit(Char, Acc0, Acc) :-
    bit(Char, B),
    Acc is Acc0 * 2 + B.

% bit(?Char, ?Bit)
% The partition alphabet as a lookup table: "lower half" characters are
% 0, "upper half" characters are 1. Clause heads do the dispatch, so
% first-argument indexing makes the mapping deterministic.
bit('F', 0).
bit('B', 1).
bit('L', 0).
bit('R', 1).

% seat(+Pass, -Row, -Col, -Id)
% Full decode: the seat ID split back into its high 7 bits (row) and
% low 3 bits (column) — the inverse of Id = Row*8 + Col.
seat(Pass, Row, Col, Id) :-
    seat_id(Pass, Id),
    Row is Id // 8,
    Col is Id mod 8.

% part1(+Ids, -Max)
% The highest seat ID on any boarding pass.
part1(Ids, Max) :-
    max_list(Ids, Max).

% part2(+Ids, -Seat)
% The missing seat: sort the occupied IDs and find the single gap of
% width two, i.e. consecutive occupied IDs A and A+2. The empty seat
% A+1 is ours. Front-row and back-row missing seats sit outside the
% occupied range, so they leave no internal gap and the first such gap
% is unique.
part2(Ids, Seat) :-
    sort(Ids, Sorted),
    gap(Sorted, Seat).

% gap(+Sorted, -Seat)
% Scan adjacent pairs of a sorted list for the first that skips exactly
% one value; Seat is that skipped value. Output bound after the cut so
% the commit rests on the inputs alone (steadfastness).
gap([A, B|_], Seat) :-
    B =:= A + 2,
    !,
    Seat is A + 1.
gap([_|Rest], Seat) :-
    gap(Rest, Seat).

% solve(+Raw, -Part1, -Part2)
solve(Raw, Part1, Part2) :-
    parse_input(Raw, Ids),
    part1(Ids, Part1),
    part2(Ids, Part2).
