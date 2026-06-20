:- initialization(main, main).

main(_) :-
    load_test_files(['test']),
    run_tests,
    halt.
