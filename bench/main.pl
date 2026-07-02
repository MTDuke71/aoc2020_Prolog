:- initialization(main, main).

% Load each day without importing its predicates (every day exports the
% same parse_input/part1/part2/solve names); bench clauses call them
% module-qualified instead.
:- use_module('../src/day00.pl', []).
:- use_module('../src/day01.pl', []).

% Run:  swipl bench/main.pl day00
% Times parse / part1 / part2 for the requested day against its real input.

main([]) :-
    format("Usage: swipl bench/main.pl <day>   e.g. day00~n").
main([Day|_]) :-
    atom_string(Day, DayS),
    format(string(Path), "inputs/~w.txt", [DayS]),
    read_file_to_string(Path, Raw, []),
    bench(Day, Raw).

% bench(+Day, +Raw)
% Per-day dispatch. Add a clause as each day is solved.
bench(day00, Raw) :- !,
    time_call("parse", day00:parse_input(Raw, Parsed)),
    time_call("part1", day00:part1(Parsed, A1)),
    time_call("part2", day00:part2(Parsed, A2)),
    format("day00  part1=~w  part2=~w~n", [A1, A2]).
bench(day01, Raw) :- !,
    time_call("parse", day01:parse_input(Raw, Parsed)),
    time_call("part1", day01:part1(Parsed, A1)),
    time_call("part2", day01:part2(Parsed, A2)),
    format("day01  part1=~w  part2=~w~n", [A1, A2]).
bench(Day, _) :-
    format("No bench wired for ~w yet.~n", [Day]).

% time_call(+Label, :Goal)
% Run Goal under wall-clock timing and report milliseconds.
time_call(Label, Goal) :-
    statistics(walltime, [Start|_]),
    call(Goal),
    statistics(walltime, [End|_]),
    Ms is End - Start,
    format("  ~w~t~16|~3d ms~n", [Label, Ms]).
