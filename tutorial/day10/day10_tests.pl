:- begin_tests(day10).
:- use_module('./day10.pl').

test(fib_plain_small, [setup(clear_fib_cache), cleanup(clear_fib_cache)]) :-
    once(fib_plain(10, F)),
    assertion(F == 55).

test(fib_memo_small, [setup(clear_fib_cache), cleanup(clear_fib_cache)]) :-
    once(fib_memo(10, F)),
    assertion(F == 55).

test(fib_consistent, [setup(clear_fib_cache), cleanup(clear_fib_cache)]) :-
    once(fib_plain(12, A)),
    clear_fib_cache,
    once(fib_memo(12, B)),
    assertion(A == B).

:- end_tests(day10).
:- initialization(main, main).
main(_) :- ( run_tests -> halt(0) ; halt(1) ).
