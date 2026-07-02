:- initialization(main, main).

% Run from the repo root:  swipl test/run_tests.pl
% Consults every test/dayNN_tests.pl and runs all plunit suites.
% (Answer-lock tests read inputs/ relative to the repo root.)

main(_) :-
    expand_file_name('test/day*_tests.pl', Files),
    maplist(consult, Files),
    (   run_tests
    ->  halt
    ;   halt(1)
    ).
