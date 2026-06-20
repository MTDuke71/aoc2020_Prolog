:- module(day10, [fib_plain/2, fib_memo/2, clear_fib_cache/0]).
:- dynamic fib_cache/2.

fib_plain(0, 0).
fib_plain(1, 1).
fib_plain(N, F) :-
    N > 1,
    N1 is N - 1,
    N2 is N - 2,
    fib_plain(N1, F1),
    fib_plain(N2, F2),
    F is F1 + F2.

fib_memo(N, F) :-
    fib_cache(N, F), !.
fib_memo(0, 0) :-
    ( fib_cache(0, 0) -> true ; assertz(fib_cache(0, 0)) ).
fib_memo(1, 1) :-
    ( fib_cache(1, 1) -> true ; assertz(fib_cache(1, 1)) ).
fib_memo(N, F) :-
    N > 1,
    N1 is N - 1,
    N2 is N - 2,
    fib_memo(N1, F1),
    fib_memo(N2, F2),
    F is F1 + F2,
    ( fib_cache(N, F) -> true ; assertz(fib_cache(N, F)) ).

clear_fib_cache :-
    retractall(fib_cache(_, _)).
