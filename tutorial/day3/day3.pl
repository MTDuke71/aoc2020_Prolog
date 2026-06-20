:- module(day3, [classify_num/2, first_even/2, maybe_member/2]).

classify_num(N, negative) :- N < 0, !.
classify_num(0, zero) :- !.
classify_num(_, positive).

first_even([X|_], X) :- 0 is X mod 2, !.
first_even([_|T], X) :- first_even(T, X).

maybe_member(X, [X|_]).
maybe_member(X, [_|T]) :- maybe_member(X, T).
