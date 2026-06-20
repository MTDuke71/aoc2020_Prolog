:- begin_tests(day7).
:- use_module('./day7.pl').

test(pair_example) :-
    once(pair_sum_10(X, Y)),
    assertion(X + Y =:= 10).

test(all_pairs_count) :-
    all_pair_sum_10(Pairs),
    length(Pairs, N),
    assertion(N == 9).

:- end_tests(day7).
:- initialization(main, main).
main(_) :- ( run_tests -> halt(0) ; halt(1) ).
