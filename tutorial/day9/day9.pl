:- module(day9, [dedup_sorted/2, stable_sorted/2, run_lengths/2]).

dedup_sorted(List, Sorted) :- sort(List, Sorted).
stable_sorted(List, Sorted) :- msort(List, Sorted).

run_lengths(List, Runs) :-
    msort(List, Sorted),
    pack_runs(Sorted, Runs).

pack_runs([], []).
pack_runs([X|Xs], [(X,N)|Runs]) :-
    take_same(X, Xs, 1, N, Rest),
    pack_runs(Rest, Runs).

take_same(_, [], N, N, []).
take_same(X, [Y|Ys], Acc, N, Rest) :-
    ( X == Y ->
        Acc1 is Acc + 1,
        take_same(X, Ys, Acc1, N, Rest)
    ;
        N = Acc,
        Rest = [Y|Ys]
    ).
