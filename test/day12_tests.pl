:- begin_tests(day12).

:- use_module('../src/day12.pl').

% The statement's five-instruction voyage.
example_input("\
F10
N3
F7
R90
F11
").

% --- Parsing ---

test(parse_action_value_pairs) :-
    example_input(Raw),
    parse_input(Raw, Instructions),
    assertion(Instructions == ['F'-10, 'N'-3, 'F'-7, 'R'-90, 'F'-11]).

% Multi-digit values and every action letter survive the positional split.
test(parse_all_actions) :-
    parse_input("N1\nS22\nE333\nW4\nL180\nR270\nF12\n", Instructions),
    assertion(Instructions == ['N'-1, 'S'-22, 'E'-333, 'W'-4,
                               'L'-180, 'R'-270, 'F'-12]).

% --- Turn normalisation ---

% Left turns are folded onto clockwise quarters, so L and R agree
% wherever they describe the same rotation.
test(left_is_mirrored_right, forall(member(L-R, [90-270, 180-180, 270-90]))) :-
    quarter_turns('L', L, Quarters),
    quarter_turns('R', R, Quarters).

% A full turn is no turn.
test(full_turn_is_identity) :-
    quarter_turns('R', 360, Right),
    quarter_turns('L', 360, Left),
    assertion(Right == 0),
    assertion(Left == 0).

% The guard: a turn that is not a multiple of 90 has no representation
% here and must fail rather than truncate toward zero.
test(non_right_angle_rejected, [fail]) :-
    quarter_turns('R', 45, _Quarters).

% --- Rotation ---

% Facing east and turning right walks the compass E -> S -> W -> N.
test(right_turns_walk_the_compass) :-
    findall(VX1-VY1,
            ( between(0, 3, Quarters),
              rotate(Quarters, 1, 0, VX1, VY1)
            ),
            Headings),
    assertion(Headings == [1-0, 0-(-1), -1-0, 0-1]).

% Four right angles return any vector to itself.
test(four_quarters_is_identity, forall(member(VX-VY, [1-0, 10-1, -3-7, 0-0]))) :-
    rotate(1, VX,  VY,  A, B),
    rotate(1, A,   B,   C, D),
    rotate(1, C,   D,   E, F),
    rotate(1, E,   F,   G, H),
    assertion(G-H == VX-VY).

% A half turn is two quarter turns, and L90 is three of them.
test(half_turn_composes) :-
    rotate(1, 10, 1, A, B),
    rotate(1, A, B, C, D),
    rotate(2, 10, 1, E, F),
    assertion(C-D == E-F),
    quarter_turns('L', 90, Quarters),
    rotate(Quarters, 10, 1, G, H),
    assertion(G-H == -1-10).

% --- Part One ---

test(part1_example) :-
    example_input(Raw),
    solve(Raw, Part1, _Part2),
    assertion(Part1 == 25).

% The statement is explicit that a cardinal move does not change the
% facing: after F10, N3, F7 the ship is at east 17, north 3, which only
% holds if N3 left it still pointing east.
test(cardinal_move_leaves_facing_alone) :-
    parse_input("F10\nN3\nF7\n", Instructions),
    part1(Instructions, Distance),
    assertion(Distance == 20).

% --- Part Two ---

test(part2_example) :-
    example_input(Raw),
    solve(Raw, _Part1, Part2),
    assertion(Part2 == 286).

% The waypoint starts 10 east, 1 north, so a bare F1 moves the ship
% exactly there -- and F10 scales that offset rather than repeating a
% single step.
test(waypoint_scales_the_offset) :-
    parse_input("F1\n", One),
    parse_input("F10\n", Ten),
    part2(One, Distance1),
    part2(Ten, Distance10),
    assertion(Distance1 == 11),
    assertion(Distance10 == 110).

% Rotating the waypoint moves the ship nowhere by itself; the turn only
% shows up in the next F. R90 sends (10, 1) to (1, -10), so F1 lands the
% ship at east 1, south 10.
test(rotation_alone_does_not_move_the_ship) :-
    parse_input("R90\n", Turn),
    parse_input("R90\nF1\n", TurnThenGo),
    part2(Turn, Distance0),
    part2(TurnThenGo, Distance1),
    assertion(Distance0 == 0),
    assertion(Distance1 == 11).

% --- Degenerate input ---

% An empty program leaves the ship at the origin in both readings.
test(empty_program_goes_nowhere) :-
    parse_input("", Instructions),
    assertion(Instructions == []),
    part1(Instructions, Distance1),
    part2(Instructions, Distance2),
    assertion(Distance1 == 0),
    assertion(Distance2 == 0).

% Manhattan distance is unsigned: sailing west and south is as far from
% the origin as sailing east and north.
test(distance_ignores_sign) :-
    parse_input("W17\nS8\n", Instructions),
    part1(Instructions, Distance),
    assertion(Distance == 25).

% --- Real-input answer locks ---

real_instructions(Instructions) :-
    read_file_to_string('inputs/day12.txt', Raw, []),
    parse_input(Raw, Instructions).

test(part1_real) :-
    real_instructions(Instructions),
    part1(Instructions, Distance),
    assertion(Distance == 1956).

test(part2_real) :-
    real_instructions(Instructions),
    part2(Instructions, Distance),
    assertion(Distance == 126797).

:- end_tests(day12).
