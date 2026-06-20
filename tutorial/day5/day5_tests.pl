:- begin_tests(day5).
:- use_module('./day5.pl').

test(sum_acc) :- sum_acc([1,2,3,4], S), assertion(S == 10).
test(sum_acc_empty) :- sum_acc([], S), assertion(S == 0).
test(reverse_acc) :- reverse_acc([1,2,3], R), assertion(R == [3,2,1]).

:- end_tests(day5).
:- initialization(main, main).
main(_) :- ( run_tests -> halt(0) ; halt(1) ).
