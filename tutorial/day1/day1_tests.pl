:- begin_tests(day1_basics).

:- use_module('./basics.pl').

test(parent_fact_true) :-
    parent(alice, bob).

test(parent_fact_false, [fail]) :-
    parent(bob, alice).

test(ancestor_direct) :-
    once(ancestor(alice, bob)).

test(ancestor_transitive) :-
    once(ancestor(alice, diana)).

test(member_of_backtracking, all(X == [10, 20, 30])) :-
    member_of(X, [10, 20, 30]).

test(sum_list_rec) :-
    sum_list_rec([1, 2, 3, 4], Sum),
    assertion(Sum == 10).

:- end_tests(day1_basics).

:- initialization(main, main).

main(_) :-
    ( run_tests -> halt(0) ; halt(1) ).
