:- begin_tests(day09).

:- use_module('../src/day09.pl').

example_numbers([35, 20, 15, 25, 47,
                 40, 62, 55, 65, 95,
                 102, 117, 150, 182, 127,
                 219, 299, 277, 309, 576]).

example_input("\
35
20
15
25
47
40
62
55
65
95
102
117
150
182
127
219
299
277
309
576
").

test(parse_numbers) :-
    example_input(Raw),
    parse_input(Raw, Numbers),
    example_numbers(Expected),
    assertion(Numbers == Expected).

test(valid_sum_requires_different_values, [fail]) :-
    valid_sum(50, [25, 25]).

test(part1_example) :-
    example_numbers(Numbers),
    part1_with_preamble(Numbers, 5, Invalid),
    assertion(Invalid == 127).

test(contiguous_range_example) :-
    example_numbers(Numbers),
    contiguous_range(Numbers, 127, Range),
    assertion(Range == [15, 25, 47, 40]).

test(part2_example) :-
    example_numbers(Numbers),
    part2_with_preamble(Numbers, 5, Weakness),
    assertion(Weakness == 62).

% --- Real-input answer locks ---

real_input(Raw) :-
    read_file_to_string('inputs/day09.txt', Raw, []).

test(part1_real) :-
    real_input(Raw),
    solve(Raw, Part1, _),
    assertion(Part1 == 1930745883).

test(part2_real) :-
    real_input(Raw),
    solve(Raw, _, Part2),
    assertion(Part2 == 268878261).

:- end_tests(day09).
