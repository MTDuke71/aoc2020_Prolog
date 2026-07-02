:- begin_tests(day01).

:- use_module('../src/day01.pl').

% --- Puzzle example (from the problem statement) ---

example_entries([1721, 979, 366, 299, 675, 1456]).

test(parse_input) :-
    parse_input("1721\n979\n366\n299\n675\n1456\n", Entries),
    example_entries(Expected),
    assertion(Entries == Expected).

test(part1_example) :-
    example_entries(Entries),
    part1(Entries, P1),
    assertion(P1 =:= 1721 * 299).

test(part2_example) :-
    example_entries(Entries),
    part2(Entries, P2),
    assertion(P2 =:= 979 * 366 * 675).

% --- k_sum/4 behavior ---

% k_sum enumerates every combination on backtracking, not just the first.
test(k_sum_enumerates_all) :-
    findall(C, k_sum(2, 10, [1, 2, 3, 4, 6, 8, 9], C), Combos),
    assertion(Combos == [[1, 9], [2, 8], [4, 6]]).

% Duplicates survive msort, so a pair like 1010 + 1010 is found.
test(duplicate_entries) :-
    part1([5, 1010, 7, 1010], P1),
    assertion(P1 =:= 1010 * 1010).

test(no_solution_fails, [fail]) :-
    part1([1, 2, 3], _).

% --- Real-input answer locks ---

real_input(Raw) :-
    read_file_to_string('inputs/day01.txt', Raw, []).

test(part1_real) :-
    real_input(Raw),
    solve(Raw, P1, _),
    assertion(P1 == 902451).

test(part2_real) :-
    real_input(Raw),
    solve(Raw, _, P2),
    assertion(P2 == 85555470).

:- end_tests(day01).
