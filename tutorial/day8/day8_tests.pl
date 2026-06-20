:- begin_tests(day8).
:- use_module('./day8.pl').
:- use_module(library(assoc)).

test(freq_assoc) :-
    freq_assoc([a,b,a,c,a], A),
    get_assoc(a, A, Na),
    get_assoc(b, A, Nb),
    assertion(Na == 3),
    assertion(Nb == 1).

test(freq_dict) :-
    freq_dict([x,y,x], D),
    assertion(D.x == 2),
    assertion(D.y == 1).

:- end_tests(day8).
:- initialization(main, main).
main(_) :- ( run_tests -> halt(0) ; halt(1) ).
