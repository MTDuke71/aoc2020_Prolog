:- module(day2, [len_rec/2, sum_rec/2, reverse_rec/2, count_even/2]).

len_rec([], 0).
len_rec([_|T], N) :-
    len_rec(T, N0),
    N is N0 + 1.

sum_rec([], 0).
sum_rec([X|T], Sum) :-
    sum_rec(T, Tail),
    Sum is X + Tail.

reverse_rec([], []).
reverse_rec([X|T], R) :-
    reverse_rec(T, RT),
    append(RT, [X], R).

count_even([], 0).
count_even([X|T], N) :-
    count_even(T, N0),
    ( 0 is X mod 2 -> N is N0 + 1 ; N = N0 ).
