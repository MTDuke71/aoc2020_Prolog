:- begin_tests(day22).

:- use_module('../src/day22.pl').

example_input("\
line1
line2
").

test(parse_input_nonempty) :-
    example_input(Raw),
    parse_input(Raw, Parsed),
    assertion(Parsed == ["line1", "line2"]).

test(part1_example) :-
    example_input(Raw),
    solve(Raw, Part1, _Part2),
    assertion(Part1 == 2).

:- end_tests(day22).
