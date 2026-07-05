:- begin_tests(day05).

:- use_module('../src/day05.pl').

% --- Worked decode examples (part 1 statement) ---
% Each pass pins Row, Col and Id together, exercising seat/4's split.

test(decode, [forall(member(Pass-Row-Col-Id,
                            ['FBFBBFFRLR'-44-5-357,
                             'BFFFBBFRRR'-70-7-567,
                             'FFFBBBFRRR'-14-7-119,
                             'BBFFBBFRLL'-102-4-820]))]) :-
    seat(Pass, R, C, I),
    assertion(R == Row),
    assertion(C == Col),
    assertion(I == Id).

% seat_id/2 is Row*8 + Col by construction — the whole point of reading
% the pass as one 10-bit number.
test(seat_id_is_row_times_8_plus_col) :-
    seat_id("BBFFBBFRLL", Id),
    assertion(Id =:= 102 * 8 + 4).

% --- Parser ---

test(parse_input) :-
    parse_input("BFFFBBFRRR\nFFFBBBFRRR\n", Ids),
    assertion(Ids == [567, 119]).

% --- Part 1: highest seat ID over the three example passes ---

test(part1_example) :-
    parse_input("BFFFBBFRRR\nFFFBBBFRRR\nBBFFBBFRLL\n", Ids),
    part1(Ids, Max),
    assertion(Max == 820).

% --- Part 2: the single gap of width two ---

test(part2_finds_missing_seat) :-
    % Occupied: 1,2,3,5,6 — seat 4 is the hole with both neighbours filled.
    part2([1, 2, 3, 5, 6], Seat),
    assertion(Seat == 4).

% --- Real-input answer locks ---

real_input(Raw) :-
    read_file_to_string('inputs/day05.txt', Raw, []).

test(part1_real) :-
    real_input(Raw),
    solve(Raw, P1, _),
    assertion(P1 == 888).

test(part2_real) :-
    real_input(Raw),
    solve(Raw, _, P2),
    assertion(P2 == 522).

:- end_tests(day05).
