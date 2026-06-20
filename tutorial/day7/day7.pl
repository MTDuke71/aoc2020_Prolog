:- module(day7, [pair_sum_10/2, all_pair_sum_10/1]).
:- use_module(library(clpfd)).

pair_sum_10(X, Y) :-
    X in 1..9,
    Y in 1..9,
    X + Y #= 10,
    labeling([], [X, Y]).

all_pair_sum_10(Pairs) :-
    findall((X,Y), pair_sum_10(X, Y), Pairs).
