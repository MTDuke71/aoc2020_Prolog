:- begin_tests(day9).
:- use_module('./day9.pl').

test(sort_vs_msort) :-
    dedup_sorted([3,1,3,2], A),
    stable_sorted([3,1,3,2], B),
    assertion(A == [1,2,3]),
    assertion(B == [1,2,3,3]).

test(run_lengths) :-
    run_lengths([b,a,b,a,a], Runs),
    assertion(Runs == [(a,3),(b,2)]).

:- end_tests(day9).
:- initialization(main, main).
main(_) :- ( run_tests -> halt(0) ; halt(1) ).
