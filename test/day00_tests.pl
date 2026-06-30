:- begin_tests(day00).

:- use_module('../src/day00.pl').

% --- Puzzle examples (from the problem statement) ---

test(parse_input) :-
    parse_input("12\n14\n1969\n", Masses),
    assertion(Masses == [12, 14, 1969]).

test(fuel_examples) :-
    assertion(\+ ( member(M-F, [12-2, 14-2, 1969-654, 100756-33583]),
                   \+ fuel(M, F) )).

test(total_fuel_examples) :-
    assertion(\+ ( member(M-F, [14-2, 1969-966, 100756-50346]),
                   \+ total_fuel(M, F) )).

test(part1_example) :-
    part1([12, 14, 1969, 100756], P1),
    assertion(P1 =:= 2 + 2 + 654 + 33583).

test(part2_example) :-
    part2([14, 1969, 100756], P2),
    assertion(P2 =:= 2 + 966 + 50346).

% --- Real-input answer locks ---

real_input(Raw) :-
    read_file_to_string('inputs/day00.txt', Raw, []).

test(part1_real) :-
    real_input(Raw),
    solve(Raw, P1, _),
    assertion(P1 == 3481005).

test(part2_real) :-
    real_input(Raw),
    solve(Raw, _, P2),
    assertion(P2 == 5218616).

:- end_tests(day00).
