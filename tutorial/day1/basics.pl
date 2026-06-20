:- module(day1_basics, [
    parent/2,
    ancestor/2,
    member_of/2,
    sum_list_rec/2
]).

% Small family graph for rule and backtracking practice.
parent(alice, bob).
parent(bob, carol).
parent(carol, diana).
parent(alice, erin).

ancestor(X, Y) :-
    parent(X, Y).
ancestor(X, Y) :-
    parent(X, Z),
    ancestor(Z, Y).

member_of(X, [X|_]).
member_of(X, [_|Xs]) :-
    member_of(X, Xs).

sum_list_rec([], 0).
sum_list_rec([X|Xs], Sum) :-
    sum_list_rec(Xs, TailSum),
    Sum is X + TailSum.
