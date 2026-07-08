:- begin_tests(day08).

:- use_module('../src/day08.pl').

% The statement's example boot code. It loops, and the accumulator is 5 the
% instant before an instruction runs a second time (Part 1). Flipping the
% second-to-last jmp to a nop makes it halt with the accumulator at 8 (Part 2).
example_input("\
nop +0
acc +1
jmp +4
acc +3
jmp -3
acc -99
acc +1
jmp -4
acc +6
").

% --- Parser: a line becomes PC -> Op-Arg, indexed from 0, signs and all ---

test(parse_indexes_from_zero) :-
    parse_input("acc +13\njmp -6\nnop +0\n", prog(N, Assoc)),
    assertion(N == 3),
    get_assoc(0, Assoc, Op0-Arg0), assertion(Op0 == acc), assertion(Arg0 == 13),
    get_assoc(1, Assoc, Op1-Arg1), assertion(Op1 == jmp), assertion(Arg1 == -6),
    get_assoc(2, Assoc, Op2-Arg2), assertion(Op2 == nop), assertion(Arg2 == 0).

% --- Interpreter: outcome is loop vs halt, with the accumulator at the stop ---

test(run_loop_stops_before_repeat) :-
    example_input(Raw),
    parse_input(Raw, Prog),
    run(Prog, Outcome, Acc),
    assertion(Outcome == loop),
    assertion(Acc == 5).

test(run_halt_steps_off_end) :-
    % nop +0, then acc +6, then PC steps to 2 == length -> halt with acc 6.
    parse_input("nop +0\nacc +6\n", Prog),
    run(Prog, Outcome, Acc),
    assertion(Outcome == halt),
    assertion(Acc == 6).

% --- Parts on the example ---

test(part1_example) :-
    example_input(Raw),
    solve(Raw, Part1, _),
    assertion(Part1 == 5).

test(part2_example) :-
    example_input(Raw),
    solve(Raw, _, Part2),
    assertion(Part2 == 8).

% --- Real-input answer locks ---

real_input(Raw) :-
    read_file_to_string('inputs/day08.txt', Raw, []).

test(part1_real) :-
    real_input(Raw),
    solve(Raw, P1, _),
    assertion(P1 == 1331).

test(part2_real) :-
    real_input(Raw),
    solve(Raw, _, P2),
    assertion(P2 == 1121).

:- end_tests(day08).
