:- begin_tests(day02).

:- use_module('../src/day02.pl').

% --- Puzzle example (from the problem statement) ---

example_input("1-3 a: abcde\n1-3 b: cdefg\n2-9 c: ccccccccc\n").

test(parse_input) :-
    parse_input("1-3 a: abcde\n", Entries),
    assertion(Entries == [entry(1, 3, a, [a, b, c, d, e])]).

test(part1_example) :-
    example_input(Raw),
    parse_input(Raw, Entries),
    part1(Entries, P1),
    assertion(P1 == 2).

test(part2_example) :-
    example_input(Raw),
    parse_input(Raw, Entries),
    part2(Entries, P2),
    assertion(P2 == 1).

% --- Policy predicates, line by line ---

% Part 1: "1-3 b: cdefg" contains no b at all — below the minimum.
test(count_policy_rejects_missing_letter, [fail]) :-
    valid_count(entry(1, 3, b, [c, d, e, f, g])).

% Part 1: the Lo and Hi bounds are both inclusive.
test(count_policy_inclusive_bounds) :-
    valid_count(entry(1, 3, a, [a])),
    valid_count(entry(1, 3, a, [a, a, a])).

% Part 1: one occurrence above the maximum fails.
test(count_policy_rejects_excess, [fail]) :-
    valid_count(entry(1, 3, a, [a, a, a, a])).

% Part 2: "1-3 a: abcde" — position 1 is a, position 3 is not: valid.
test(position_policy_exactly_one) :-
    valid_position(entry(1, 3, a, [a, b, c, d, e])).

% Part 2: "2-9 c: ccccccccc" — both positions hold c: invalid (XOR, not OR).
test(position_policy_rejects_both, [fail]) :-
    valid_position(entry(2, 9, c, [c, c, c, c, c, c, c, c, c])).

% Part 2: neither position holding the letter is invalid too.
test(position_policy_rejects_neither, [fail]) :-
    valid_position(entry(1, 3, b, [c, d, e, f, g])).

% --- Real-input answer locks ---

real_input(Raw) :-
    read_file_to_string('inputs/day02.txt', Raw, []).

test(part1_real) :-
    real_input(Raw),
    solve(Raw, P1, _),
    assertion(P1 == 460).

test(part2_real) :-
    real_input(Raw),
    solve(Raw, _, P2),
    assertion(P2 == 251).

:- end_tests(day02).
