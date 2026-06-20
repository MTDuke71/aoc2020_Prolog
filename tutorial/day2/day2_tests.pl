:- begin_tests(day2).
:- use_module('./day2.pl').

test(len_empty) :- len_rec([], N), assertion(N == 0).
test(len_three) :- len_rec([a,b,c], N), assertion(N == 3).
test(sum_list) :- sum_rec([1,2,3,4], S), assertion(S == 10).
test(reverse_list) :- reverse_rec([1,2,3], R), assertion(R == [3,2,1]).
test(count_even) :- count_even([1,2,3,4,6], N), assertion(N == 3).

:- end_tests(day2).
:- initialization(main, main).
main(_) :- ( run_tests -> halt(0) ; halt(1) ).
