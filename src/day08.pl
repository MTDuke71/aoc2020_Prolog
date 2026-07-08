:- module(day08, [parse_input/2, part1/2, part2/2, solve/3, run/3]).

:- use_module(library(assoc)).

% Day 8: Handheld Halting.
% The puzzle input *is* a program for a tiny accumulator machine with three
% opcodes — acc (add to the accumulator), jmp (relative branch), nop (fall
% through). We build an interpreter. The parsed program is a fixed array of
% instructions indexed by program counter (PC); running it is the classic
% fetch/decode/execute loop, and the only extra machinery is a "seen" set of
% PCs so we can detect when control revisits an instruction.
%
% Part 1: the boot code loops forever; report the accumulator at the instant
% control is about to run an instruction a second time.
% Part 2: exactly one jmp<->nop is corrupted. Flip candidates one at a time
% until the program halts (PC steps off the end); report the halting acc.

% ---------------------------------------------------------------------------
% Representation
% ---------------------------------------------------------------------------
% A parsed program is  prog(N, Assoc)  where N is the instruction count and
% Assoc maps PC (0..N-1) to Op-Arg (Op an atom in {acc,jmp,nop}, Arg an int).
% An assoc — not a plain list — because Part 2 needs random access (fetch the
% instruction at any PC) *and* a cheap, pure single-cell update (the flipped
% program), which put_assoc/4 gives in O(log N) while sharing structure with
% the original. Halting is PC =:= N: "the instruction immediately after the
% last instruction in the file."

% parse_input(+Raw, -Prog)
parse_input(Raw, prog(N, Assoc)) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(parse_instr, Lines, Instrs),
    length(Instrs, N),
    N1 is N - 1,
    numlist(0, N1, Idxs),
    pairs_keys_values(Pairs, Idxs, Instrs),
    list_to_assoc(Pairs, Assoc).

% parse_instr(+Line, -(Op-Arg))
% "jmp +140" -> jmp - 140. number_string/2 accepts the signed +N / -N form
% directly, so no manual sign handling is needed.
parse_instr(Line, Op-Arg) :-
    split_string(Line, " ", "", [OpS, ArgS]),
    atom_string(Op, OpS),
    number_string(Arg, ArgS).

% ---------------------------------------------------------------------------
% The interpreter
% ---------------------------------------------------------------------------

% run(+Prog, -Outcome, -Acc)
% Execute from PC=0, accumulator=0. Outcome is `loop` if control is about to
% re-enter an already-executed PC, or `halt` if PC steps to exactly N (off the
% end). Acc is the accumulator at that stopping instant.
run(prog(N, Assoc), Outcome, Acc) :-
    empty_assoc(Seen0),
    step(N, Assoc, 0, 0, Seen0, Outcome, Acc).

% step(+N, +Assoc, +PC, +Acc0, +Seen, -Outcome, -Acc)
% Three mutually exclusive cases, committed with cuts (outputs unified after
% the cut, per the repo's steadfast-cut style):
%   1. PC is off the end  -> halt with the current accumulator;
%   2. PC already visited  -> loop with the current accumulator;
%   3. otherwise           -> mark PC seen, execute one instruction, recurse.
step(N, _Assoc, PC, Acc0, _Seen, Outcome, Acc) :-
    PC =:= N, !,
    Outcome = halt, Acc = Acc0.
step(_N, _Assoc, PC, Acc0, Seen, Outcome, Acc) :-
    get_assoc(PC, Seen, true), !,
    Outcome = loop, Acc = Acc0.
step(N, Assoc, PC, Acc0, Seen0, Outcome, Acc) :-
    get_assoc(PC, Assoc, Op-Arg),
    put_assoc(PC, Seen0, true, Seen1),
    exec(Op, Arg, PC, Acc0, PC1, Acc1),
    step(N, Assoc, PC1, Acc1, Seen1, Outcome, Acc).

% exec(+Op, +Arg, +PC, +Acc0, -PC1, -Acc1)
% One instruction's effect on (PC, accumulator). First-argument indexed on the
% opcode atom, so the dispatch is deterministic with no choice points.
exec(acc, Arg, PC, Acc0, PC1, Acc1) :- PC1 is PC + 1,   Acc1 is Acc0 + Arg.
exec(jmp, Arg, PC, Acc,  PC1, Acc)  :- PC1 is PC + Arg.
exec(nop, _,   PC, Acc,  PC1, Acc)  :- PC1 is PC + 1.

% ---------------------------------------------------------------------------
% Parts
% ---------------------------------------------------------------------------

% part1(+Prog, -Acc)
% The boot code is an infinite loop; run it and read off the accumulator at
% the moment before the first repeat. Constraining Outcome to `loop` documents
% (and checks) that expectation.
part1(Prog, Acc) :-
    run(Prog, loop, Acc).

% part2(+Prog, -Acc)
% Exactly one jmp<->nop flip makes the program halt. Walk PCs in order; for the
% first candidate whose flipped program halts, that halting accumulator is the
% answer. flipped/2 fails on acc, so between/3 backtracks past acc lines; a
% flip that still loops fails the `halt` constraint and backtracks too.
part2(prog(N, Assoc), Acc) :-
    N1 is N - 1,
    between(0, N1, PC),
    get_assoc(PC, Assoc, Op-Arg),
    flipped(Op, Op2),
    put_assoc(PC, Assoc, Op2-Arg, Assoc2),
    run(prog(N, Assoc2), halt, Acc),
    !.

% flipped(+Op, -Op2): the jmp<->nop corruption. Undefined for acc (no clause),
% which is exactly the "no acc instructions were harmed" rule.
flipped(jmp, nop).
flipped(nop, jmp).

% solve(+Raw, -Part1, -Part2)
solve(Raw, Part1, Part2) :-
    parse_input(Raw, Prog),
    part1(Prog, Part1),
    part2(Prog, Part2).
