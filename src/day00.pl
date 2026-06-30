:- module(day00, [parse_input/2, part1/2, part2/2, solve/3,
                  fuel/2, total_fuel/2]).

% Day 0: The Tyranny of the Rocket Equation (tutorial dry run).
% Input is one integer module mass per line.

% parse_input(+Raw, -Masses)
% Split on newlines, drop blanks, read each line as an integer.
parse_input(Raw, Masses) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(number_string, Masses, Lines).

% fuel(+Mass, -Fuel)
% Fuel for a single mass: floor(Mass / 3) - 2.
fuel(Mass, Fuel) :-
    Fuel is Mass // 3 - 2.

% total_fuel(+Mass, -Fuel)
% Part-two fuel: the fuel for a mass, plus fuel for that fuel, and so on,
% stopping once a step would call for zero or negative fuel.
total_fuel(Mass, Fuel) :-
    fuel(Mass, Step),
    (   Step =< 0
    ->  Fuel = 0
    ;   total_fuel(Step, Rest),
        Fuel is Step + Rest
    ).

% part1(+Masses, -Answer)
% Sum of per-module fuel.
part1(Masses, Answer) :-
    maplist(fuel, Masses, Fuels),
    sum_list(Fuels, Answer).

% part2(+Masses, -Answer)
% Sum of per-module total fuel (fuel for fuel included).
part2(Masses, Answer) :-
    maplist(total_fuel, Masses, Fuels),
    sum_list(Fuels, Answer).

% solve(+Raw, -Part1, -Part2)
solve(Raw, Part1, Part2) :-
    parse_input(Raw, Masses),
    part1(Masses, Part1),
    part2(Masses, Part2).
