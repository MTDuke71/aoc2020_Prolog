:- initialization(main, main).

% Load each day without importing its predicates (every day exports the
% same parse_input/part1/part2/solve names); bench clauses call them
% module-qualified instead.
:- use_module('../src/day00.pl', []).
:- use_module('../src/day01.pl', []).
:- use_module('../src/day02.pl', []).
:- use_module('../src/day03.pl', []).
:- use_module('../src/day04.pl', []).
:- use_module('../src/day05.pl', []).
:- use_module('../src/day06.pl', []).
:- use_module('../src/day07.pl', []).
:- use_module('../src/day08.pl', []).

% Run:  swipl bench/main.pl day00
% Reports logical inferences (exact, reproducible) and wall time (noisy) for
% parse / part1 / part2 of the requested day against its real input.

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
bench(day02, Raw) :- !,
    time_call("parse", day02:parse_input(Raw, Parsed)),
    time_call("part1", day02:part1(Parsed, A1)),
    time_call("part2", day02:part2(Parsed, A2)),
    format("day02  part1=~w  part2=~w~n", [A1, A2]).
bench(day03, Raw) :- !,
    time_call("parse", day03:parse_input(Raw, Parsed)),
    time_call("part1", day03:part1(Parsed, A1)),
    time_call("part2", day03:part2(Parsed, A2)),
    format("day03  part1=~w  part2=~w~n", [A1, A2]).
bench(day04, Raw) :- !,
    time_call("parse", day04:parse_input(Raw, Parsed)),
    time_call("part1", day04:part1(Parsed, A1)),
    time_call("part2", day04:part2(Parsed, A2)),
    format("day04  part1=~w  part2=~w~n", [A1, A2]).
bench(day05, Raw) :- !,
    time_call("parse", day05:parse_input(Raw, Parsed)),
    time_call("part1", day05:part1(Parsed, A1)),
    time_call("part2", day05:part2(Parsed, A2)),
    format("day05  part1=~w  part2=~w~n", [A1, A2]).
bench(day06, Raw) :- !,
    time_call("parse", day06:parse_input(Raw, Parsed)),
    time_call("part1", day06:part1(Parsed, A1)),
    time_call("part2", day06:part2(Parsed, A2)),
    format("day06  part1=~w  part2=~w~n", [A1, A2]).
bench(day07, Raw) :- !,
    time_call("parse", day07:parse_input(Raw, Parsed)),
    time_call("part1", day07:part1(Parsed, A1)),
    time_call("part2", day07:part2(Parsed, A2)),
    format("day07  part1=~w  part2=~w~n", [A1, A2]).
bench(day08, Raw) :- !,
    time_call("parse", day08:parse_input(Raw, Parsed)),
    time_call("part1", day08:part1(Parsed, A1)),
    time_call("part2", day08:part2(Parsed, A2)),
    format("day08  part1=~w  part2=~w~n", [A1, A2]).
bench(Day, _) :-
    format("No bench wired for ~w yet.~n", [Day]).

% time_call(+Label, :Goal)
% Report two numbers for Goal:
%   - logical inferences: deterministic and machine-independent, the stable
%     signal for comparing algorithms (same input -> same count every run);
%   - wall milliseconds: the noisy real cost, via get_time/1 for sub-ms
%     resolution (a single fast phase is far below statistics(walltime)'s
%     1 ms granularity).
% The harness's own inference cost between the two probes is measured with
% an identical bracket around `true` and subtracted, so the reported count
% is the goal's alone — the same correction time/1 applies internally.
time_call(Label, Goal) :-
    bench_overhead(Base),
    statistics(inferences, I0),
    get_time(T0),
    call(Goal),
    get_time(T1),
    statistics(inferences, I1),
    Infs is I1 - I0 - Base,
    Ms is (T1 - T0) * 1000,
    format("  ~w~t~10|~t~D inf~26|~t~3f ms~40|~n", [Label, Infs, Ms]).

% bench_overhead(-Base)
% The inference count consumed by time_call/2's own probe bracket, measured
% by running that exact bracket around a no-op. Self-calibrating, so no
% magic constant and it stays correct across SWI versions.
bench_overhead(Base) :-
    statistics(inferences, I0),
    get_time(_),
    call(true),
    get_time(_),
    statistics(inferences, I1),
    Base is I1 - I0.
