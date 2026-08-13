:- module(day13, [parse_input/2, part1/2, part2/2, solve/3,
                  wait_for/3, earliest_bus/3, align/5, crt/2]).

% Day 13: Shuttle Search.
% Bus N departs at every timestamp divisible by N. Part 1 asks for the
% first departure at or after a given minute; part 2 asks for the first
% minute T at which every listed bus departs at its own offset in the
% list.
%
% Both parts are modular arithmetic on the same parsed notes, and both
% turn on one identity: bus Id departs at T exactly when T mod Id =:= 0.
%   Part 1: the wait for bus Id is (-Earliest) mod Id, minimised over
%           the buses. One pass, no search.
%   Part 2: bus Id at list offset Offset must depart at T + Offset, i.e.
%           T = -Offset (mod Id). That is a simultaneous congruence
%           system -- the Chinese Remainder Theorem -- solved here by an
%           incremental sieve that folds one congruence in at a time.
%
% Sizes are why part 2 cannot be searched directly: the real answer is
% near 10^15, so counting to it one minute at a time is hopeless, while
% the sieve gets there in a few thousand steps.
%
% Every `mod` below relies on SWI's *floored* mod, which returns a value
% with the sign of the divisor: (-Earliest) mod Id lands in 0..Id-1 with
% no correction. C and Rust's `%` truncates and would hand back a
% negative here -- the same trap day12's left-turn folding walked around.

% ---------------------------------------------------------------------------
% Parsing
% ---------------------------------------------------------------------------

% parse_input(+Raw, -Notes)
% Notes is notes(Earliest, Buses) where Buses is a list of Offset-Id
% pairs: Offset is the bus's *position in the comma list*, which is the
% only thing part 2 cares about, and out-of-service `x` entries are
% dropped while still consuming a position.
parse_input(Raw, notes(Earliest, Buses)) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, [EarliestS, ScheduleS|_]),
    number_string(Earliest, EarliestS),
    split_string(ScheduleS, ",", " \t\r", Fields),
    findall(Offset-Id, in_service(Fields, Offset, Id), Buses).

% in_service(+Fields, -Offset, -Id)
% Nondeterministically yield each running bus with its index. nth0/3 with
% an unbound index is a generator, so the offset comes out of the same
% call that reads the field -- no counter to thread, and the `x` entries
% are skipped by failing the number test rather than by bookkeeping.
in_service(Fields, Offset, Id) :-
    nth0(Offset, Fields, Field),
    Field \== "x",
    number_string(Id, Field).

% ---------------------------------------------------------------------------
% Part 1 -- the first departure at or after Earliest
% ---------------------------------------------------------------------------

% wait_for(+Earliest, +Id, -Wait)
% Minutes from Earliest until bus Id next departs.
%
% Bus Id departs on multiples of Id, so the next departure at or after
% Earliest is Id * ceil(Earliest/Id), and the wait is that minus
% Earliest. Written directly as (-Earliest) mod Id, which is the same
% number: it is 0 when Earliest is already a departure, and otherwise
% the distance up to the next multiple.
wait_for(Earliest, Id, Wait) :-
    Wait is (-Earliest) mod Id.

% earliest_bus(+Earliest, +Buses, -Answer)
% The puzzle answer: Id * Wait for whichever bus comes first. Pairing as
% Wait-Id lets min_member/2 do the selection under the standard order of
% terms, which compares the waits first -- the same trick as sorting on
% a key without building a comparator.
earliest_bus(Earliest, Buses, Answer) :-
    findall(Wait-Id,
            ( member(_Offset-Id, Buses),
              wait_for(Earliest, Id, Wait)
            ),
            Waits),
    min_member(Wait-Id, Waits),
    Answer is Id * Wait.

% ---------------------------------------------------------------------------
% Part 2 -- the Chinese Remainder Theorem, sieved
% ---------------------------------------------------------------------------
%
% Each bus contributes one congruence: bus Id at offset Offset must
% depart at T + Offset, so
%
%     T + Offset = 0  (mod Id)        i.e.   T = -Offset  (mod Id).
%
% The bus IDs in this puzzle are distinct primes, hence pairwise coprime,
% so the CRT says the whole system has exactly one solution modulo the
% product of the IDs. crt/2 builds it one congruence at a time.

% crt(+Buses, -Timestamp)
% Fold the congruences together. The accumulator is T-Step, meaning "the
% solutions found so far are exactly T, T+Step, T+2*Step, ...":
%   - start at 0-1: every integer satisfies the empty system;
%   - after folding in buses with IDs I1..Ik, Step is I1*...*Ik and T is
%     the smallest non-negative solution of those k congruences.
% The final T is the answer; the final Step (the full product) is the
% period at which the whole schedule repeats.
crt(Buses, Timestamp) :-
    foldl(crt_step, Buses, 0-1, Timestamp-_Period).

% crt_step(+Offset-Id, +T0-Step0, -T-Step)
% Add one congruence to the solution set. Only timestamps in the current
% arithmetic progression can survive, so the search walks that
% progression -- T0, T0+Step0, T0+2*Step0, ... -- until it also satisfies
% the new bus. Because Id is coprime to Step0, exactly one of the first
% Id steps works, so this loop runs fewer than Id times.
%
% The new period is Step0*Id: the solutions of the enlarged system are
% spaced by the least common multiple of the old period and Id, which
% for coprime moduli is their product.
crt_step(Offset-Id, T0-Step0, T-Step) :-
    align(T0, Step0, Offset, Id, T),
    Step is Step0 * Id.

% align(+T0, +Step, +Offset, +Id, -T)
% The smallest T >= T0 with T = T0 (mod Step) and (T + Offset) mod Id =:= 0.
% Two clauses, tested in order: stop on the first hit, otherwise take one
% more stride. Output is unified after the cut so a bound T cannot make
% the first clause fail into the second and loop forever.
align(T0, _Step, Offset, Id, T) :-
    (T0 + Offset) mod Id =:= 0,
    !,
    T = T0.
align(T0, Step, Offset, Id, T) :-
    T1 is T0 + Step,
    align(T1, Step, Offset, Id, T).

% ---------------------------------------------------------------------------
% Parts
% ---------------------------------------------------------------------------

% part1(+Notes, -Answer)
part1(notes(Earliest, Buses), Answer) :-
    earliest_bus(Earliest, Buses, Answer).

% part2(+Notes, -Timestamp)
% The first line of the notes is dead here, as the statement says.
part2(notes(_Earliest, Buses), Timestamp) :-
    crt(Buses, Timestamp).

% solve(+Raw, -Part1, -Part2)
solve(Raw, Part1, Part2) :-
    parse_input(Raw, Notes),
    part1(Notes, Part1),
    part2(Notes, Part2).
