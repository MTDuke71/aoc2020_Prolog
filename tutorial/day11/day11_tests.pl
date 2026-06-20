:- begin_tests(day11).
:- use_module('./day11.pl').

example_input("\
3
7
2
5
").

test(parse_input) :-
    example_input(Raw),
    parse_input(Raw, Nums),
    assertion(Nums == [3,7,2,5]).

test(part1_example) :-
    example_input(Raw),
    solve(Raw, P1, _),
    assertion(P1 == 17).

test(part2_example) :-
    example_input(Raw),
    solve(Raw, _, P2),
    assertion(P2 == 35).

:- end_tests(day11).
:- initialization(main, main).
main(_) :- ( run_tests -> halt(0) ; halt(1) ).
