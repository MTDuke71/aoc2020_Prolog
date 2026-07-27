:- begin_tests(day10).

:- use_module('../src/day10.pl').

% The statement's first example: 11 adapters, deliberately unsorted.
small_input("\
16
10
15
5
1
11
7
19
6
12
4
").

small_ratings([16, 10, 15, 5, 1, 11, 7, 19, 6, 12, 4]).

% The statement's larger example: 31 adapters.
large_input("\
28
33
18
42
31
14
46
20
48
47
24
23
49
45
19
38
39
11
1
32
25
35
8
17
7
9
4
2
34
10
3
").

test(parse_ratings) :-
    small_input(Raw),
    parse_input(Raw, Ratings),
    small_ratings(Expected),
    assertion(Ratings == Expected).

test(full_chain_sorts_and_caps) :-
    small_ratings(Ratings),
    full_chain(Ratings, Chain),
    assertion(Chain == [0, 1, 4, 5, 6, 7, 10, 11, 12, 15, 16, 19, 22]).

test(differences_of_small_chain) :-
    small_ratings(Ratings),
    full_chain(Ratings, Chain),
    differences(Chain, Diffs),
    assertion(Diffs == [1, 3, 1, 1, 1, 3, 1, 1, 3, 1, 3, 3]).

test(difference_counts_small) :-
    small_ratings(Ratings),
    full_chain(Ratings, Chain),
    differences(Chain, Diffs),
    difference_counts(Diffs, Ones, Threes),
    assertion(Ones-Threes == 7-5).

test(part1_small_example) :-
    small_input(Raw),
    solve(Raw, Part1, _),
    assertion(Part1 == 35).

test(part2_small_example) :-
    small_input(Raw),
    solve(Raw, _, Part2),
    assertion(Part2 == 8).

test(part1_large_example) :-
    large_input(Raw),
    solve(Raw, Part1, _),
    assertion(Part1 == 220).

test(part2_large_example) :-
    large_input(Raw),
    solve(Raw, _, Part2),
    assertion(Part2 == 19208).

% A single adapter: outlet 0 -> 3 -> device 6, two 3-jolt steps, one chain.
test(single_adapter_chain) :-
    part1([3], Product),
    part2([3], Count),
    assertion(Product == 0),
    assertion(Count == 1).

% --- Real-input answer locks ---

real_input(Raw) :-
    read_file_to_string('inputs/day10.txt', Raw, []).

test(part1_real) :-
    real_input(Raw),
    solve(Raw, Part1, _),
    assertion(Part1 == 2482).

test(part2_real) :-
    real_input(Raw),
    solve(Raw, _, Part2),
    assertion(Part2 == 96717311574016).

:- end_tests(day10).
