:- begin_tests(day06).

:- use_module('../src/day06.pl').

% The statement's five-group example. Group sizes:
%   anyone   : 3 3 3 1 1  -> sum 11
%   everyone : 3 0 1 1 1  -> sum  6
example_input("abc\n\na\nb\nc\n\nab\nac\n\na\na\na\na\n\nb\n").

% --- Parser: groups of per-person letter sets ---

test(parse_groups_structure) :-
    parse_input("abcx\nabcy\nabcz\n", Groups),
    % one group of three people, each an ordset of their letters
    assertion(Groups == [[[a,b,c,x], [a,b,c,y], [a,b,c,z]]]).

test(parse_group_count) :-
    example_input(Raw),
    parse_input(Raw, Groups),
    assertion(length(Groups, 5)).

% --- Per-group set ops ---

test(anyone_is_union) :-
    % union of {a,b,c,x},{a,b,c,y},{a,b,c,z} = {a,b,c,x,y,z} -> 6
    group_anyone([[a,b,c,x], [a,b,c,y], [a,b,c,z]], N),
    assertion(N == 6).

test(everyone_is_intersection) :-
    % intersection of {a,b},{a,c} = {a} -> 1
    group_everyone([[a,b], [a,c]], N),
    assertion(N == 1).

test(single_person_anyone_equals_everyone) :-
    % A lone person: union and intersection are both their own set.
    group_anyone([[a,b,c]], Nany),
    group_everyone([[a,b,c]], Nall),
    assertion(Nany == 3),
    assertion(Nall == 3).

% --- Parts on the statement example ---

test(part1_example) :-
    example_input(Raw),
    solve(Raw, Part1, _),
    assertion(Part1 == 11).

test(part2_example) :-
    example_input(Raw),
    solve(Raw, _, Part2),
    assertion(Part2 == 6).

% --- Real-input answer locks ---

real_input(Raw) :-
    read_file_to_string('inputs/day06.txt', Raw, []).

test(part1_real) :-
    real_input(Raw),
    solve(Raw, P1, _),
    assertion(P1 == 6683).

test(part2_real) :-
    real_input(Raw),
    solve(Raw, _, P2),
    assertion(P2 == 3122).

:- end_tests(day06).
