:- begin_tests(day6).
:- use_module('./day6.pl').

test(path_exists) :-
    once(path(a, d, P)),
    assertion(memberchk(P, [[a,b,c,d], [a,e,d]])).

test(path_cycle_safe, [fail]) :-
    path(d, a, _).

:- end_tests(day6).
:- initialization(main, main).
main(_) :- ( run_tests -> halt(0) ; halt(1) ).
