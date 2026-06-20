:- module(day05, [parse_input/2, part1/2, part2/2, solve/3]).

% parse_input(+Raw, -Parsed)
parse_input(Raw, Parsed) :-
    split_string(Raw, "\n", " \t\r", Lines),
    exclude(=(""), Lines, Parsed).

% part1(+Parsed, -Answer)
part1(Parsed, Answer) :-
    length(Parsed, Answer).

% part2(+Parsed, -Answer)
part2(Parsed, Answer) :-
    length(Parsed, Answer).

% solve(+Raw, -Part1, -Part2)
solve(Raw, Part1, Part2) :-
    parse_input(Raw, Parsed),
    part1(Parsed, Part1),
    part2(Parsed, Part2).
