:- begin_tests(day4).
:- use_module('./day4.pl').

test(parse_lines) :-
    parse_lines("a\nb\n\n", L),
    assertion(L == ["a", "b"]).

test(parse_int_lines) :-
    parse_int_lines("10\n20\n30\n", Ns),
    assertion(Ns == [10,20,30]).

test(parse_csv_ints) :-
    parse_csv_ints("1, 2,3", Ns),
    assertion(Ns == [1,2,3]).

:- end_tests(day4).
:- initialization(main, main).
main(_) :- ( run_tests -> halt(0) ; halt(1) ).
