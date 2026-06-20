:- begin_tests(day3).
:- use_module('./day3.pl').

test(classify_negative) :- classify_num(-4, C), assertion(C == negative).
test(classify_zero) :- classify_num(0, C), assertion(C == zero).
test(classify_positive) :- classify_num(9, C), assertion(C == positive).
test(first_even) :- first_even([1,3,4,6], X), assertion(X == 4).
test(maybe_member_backtracks, all(X == [a,b,c])) :- maybe_member(X, [a,b,c]).

:- end_tests(day3).
:- initialization(main, main).
main(_) :- ( run_tests -> halt(0) ; halt(1) ).
