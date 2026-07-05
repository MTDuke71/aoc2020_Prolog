:- module(day02, [parse_input/2, part1/2, part2/2, solve/3,
                  valid_count/1, valid_position/1]).

:- use_module(library(dcg/basics)).

% Day 2: Password Philosophy.
% Each input line is "Lo-Hi L: Password" — a policy plus a password.
% Part 1: the password is valid when letter L appears between Lo and Hi
% times (inclusive). Part 2: the password is valid when exactly one of
% the 1-indexed positions Lo and Hi holds L. Both answers count valid lines.

% parse_input(+Raw, -Entries)
% One entry(Lo, Hi, Letter, Password) term per line. Letter is a char
% atom; Password is a list of char atoms (so positions and counting both
% work on the same representation).
parse_input(Raw, Entries) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(parse_line, Lines, Entries).

parse_line(Line, Entry) :-
    string_codes(Line, Codes),
    phrase(entry(Entry), Codes).

% entry(-Entry)//
% Grammar for one line: "Lo-Hi L: Password". integer//1 and remainder//1
% come from library(dcg/basics); [C] consumes the single policy letter.
entry(entry(Lo, Hi, Letter, Password)) -->
    integer(Lo), "-", integer(Hi), " ",
    [C], { char_code(Letter, C) },
    ": ",
    remainder(Cs), { maplist(char_code, Password, Cs) }.

% valid_count(+Entry)
% Part-1 policy: Letter occurs between Lo and Hi times in Password.
% between/3 with all arguments bound acts as a range check.
valid_count(entry(Lo, Hi, Letter, Password)) :-
    include(==(Letter), Password, Hits),
    length(Hits, N),
    between(Lo, Hi, N).

% valid_position(+Entry)
% Part-2 policy: exactly one of positions Lo and Hi (1-indexed) is Letter.
% The if-then-else spells out XOR deterministically: if position Lo holds
% Letter then position Hi must not, otherwise position Hi must.
valid_position(entry(Lo, Hi, Letter, Password)) :-
    nth1(Lo, Password, A),
    nth1(Hi, Password, B),
    (   A == Letter
    ->  B \== Letter
    ;   B == Letter
    ).

% count_valid(:Policy, +Entries, -N)
% N is how many Entries satisfy Policy.
count_valid(Policy, Entries, N) :-
    include(Policy, Entries, Valid),
    length(Valid, N).

% part1(+Entries, -Answer)
part1(Entries, Answer) :-
    count_valid(valid_count, Entries, Answer).

% part2(+Entries, -Answer)
part2(Entries, Answer) :-
    count_valid(valid_position, Entries, Answer).

% solve(+Raw, -Part1, -Part2)
solve(Raw, Part1, Part2) :-
    parse_input(Raw, Entries),
    part1(Entries, Part1),
    part2(Entries, Part2).
