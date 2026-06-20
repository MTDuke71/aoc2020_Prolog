:- module(day11, [parse_input/2, part1/2, part2/2, solve/3]).

parse_input(Raw, Nums) :-
    split_string(Raw, "\n", " \t\r", Lines),
    exclude(=(""), Lines, Clean),
    maplist(number_string, Nums, Clean).

part1(Nums, Sum) :-
    sum_list(Nums, Sum).

part2(Nums, ProductTop2) :-
    msort(Nums, Sorted),
    reverse(Sorted, Desc),
    Desc = [A,B|_],
    ProductTop2 is A * B.

solve(Raw, P1, P2) :-
    parse_input(Raw, Nums),
    part1(Nums, P1),
    part2(Nums, P2).
