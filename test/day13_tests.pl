:- begin_tests(day13).

:- use_module('../src/day13.pl').

% The statement's notes: earliest departure 939, buses 7, 13, 59, 31, 19.
example_input("\
939
7,13,x,x,59,x,31,19
").

% schedule_notes(+Schedule, -Notes)
% Part 2's extra examples give only a bus list, so pin a dummy first line.
schedule_notes(Schedule, Notes) :-
    format(string(Raw), "0\n~w\n", [Schedule]),
    parse_input(Raw, Notes).

% --- Parsing ---

% Offsets are list positions, so the dropped `x` entries still count:
% 59 sits at index 4, not index 2.
test(parse_keeps_positions) :-
    example_input(Raw),
    parse_input(Raw, notes(Earliest, Buses)),
    assertion(Earliest == 939),
    assertion(Buses == [0-7, 1-13, 4-59, 6-31, 7-19]).

% An all-`x` tail contributes nothing but does not upset the indices.
test(parse_trailing_out_of_service) :-
    parse_input("100\n3,x,x\n", notes(Earliest, Buses)),
    assertion(Earliest == 100),
    assertion(Buses == [0-3]).

% --- Waiting for a bus ---

% Departures are the multiples of the ID, so 939 waits 6 minutes for the
% 7 (938 and 945 bracket it) and 5 for the 59 (that is the winner).
test(wait_table, forall(member(Id-Wait, [7-6, 13-10, 59-5, 31-22, 19-11]))) :-
    wait_for(939, Id, Wait).

% Standing at a departure minute means no wait at all -- the `mod` must
% return 0 here rather than a whole period.
test(no_wait_on_a_departure) :-
    wait_for(945, 7, Wait),
    assertion(Wait == 0).

% The wait is always a proper offset into the period, never negative:
% floored `mod` is what makes (-Earliest) mod Id correct without a fixup.
test(wait_is_in_range, forall(member(Earliest, [0, 1, 939, 1000053]))) :-
    forall(member(Id, [7, 13, 19, 523]),
           ( wait_for(Earliest, Id, Wait),
             Wait >= 0,
             Wait < Id,
             (Earliest + Wait) mod Id =:= 0
           )).

% --- Part One ---

test(part1_example) :-
    example_input(Raw),
    solve(Raw, Part1, _Part2),
    assertion(Part1 == 295).

% The answer multiplies the *winning* bus by its own wait, so the
% selection has to be on the wait and not on the product: bus 59 waits 5
% (product 295) while bus 7 waits 6 and scores only 42.
test(part1_picks_the_soonest_not_the_smallest_product) :-
    example_input(Raw),
    parse_input(Raw, notes(Earliest, Buses)),
    earliest_bus(Earliest, Buses, Answer),
    assertion(Answer == 295),
    findall(Product,
            ( member(_-Id, Buses),
              wait_for(Earliest, Id, Wait),
              Product is Id * Wait
            ),
            Products),
    min_member(Smallest, Products),
    assertion(Smallest == 42).

% --- Part Two ---

test(part2_example) :-
    example_input(Raw),
    solve(Raw, _Part1, Part2),
    assertion(Part2 == 1068781).

% The four extra schedules the statement lists.
test(part2_extra_examples,
     forall(member(Schedule-Expected,
                   ["17,x,13,19"-3417,
                    "67,7,59,61"-754018,
                    "67,x,7,59,61"-779210,
                    "67,7,x,59,61"-1261476,
                    "1789,37,47,1889"-1202161486]))) :-
    schedule_notes(Schedule, Notes),
    part2(Notes, Timestamp),
    assertion(Timestamp == Expected).

% Moving one bus by one position changes the answer -- the two middle
% examples differ only in where the `x` sits, which is the whole point of
% carrying offsets rather than a bare bus list.
test(part2_offsets_matter) :-
    schedule_notes("67,x,7,59,61", A),
    schedule_notes("67,7,x,59,61", B),
    part2(A, TimestampA),
    part2(B, TimestampB),
    assertion(TimestampA \== TimestampB).

% What the answer means: every listed bus departs at its own offset.
test(part2_satisfies_every_congruence) :-
    example_input(Raw),
    parse_input(Raw, notes(_, Buses)),
    part2(notes(0, Buses), Timestamp),
    forall(member(Offset-Id, Buses),
           (Timestamp + Offset) mod Id =:= 0).

% And it is the *earliest* such minute: brute force finds nothing below
% it. (Only viable on the small example; the real answer is ~3.3e14.)
test(part2_example_is_minimal) :-
    example_input(Raw),
    parse_input(Raw, notes(_, Buses)),
    part2(notes(0, Buses), Timestamp),
    \+ ( between(0, Timestamp, T),
         T < Timestamp,
         forall(member(Offset-Id, Buses),
                (T + Offset) mod Id =:= 0)
       ).

% --- The CRT sieve itself ---

% A timestamp that already satisfies the new congruence is returned
% unchanged: align/5 must not stride past a solution it is standing on.
test(align_is_idempotent) :-
    align(3417, 1, 0, 17, T),
    assertion(T == 3417),
    align(0, 1, 0, 7, Zero),
    assertion(Zero == 0).

% align/5 only ever returns members of the progression it was given, and
% it returns the first one that fits.
test(align_stays_on_the_progression) :-
    align(7, 7, 1, 13, T),
    assertion(T mod 7 =:= 0),
    assertion((T + 1) mod 13 =:= 0),
    assertion(T == 77).

% One bus at offset 0 is solved by timestamp 0 -- the degenerate case the
% fold starts from.
test(single_bus_at_offset_zero) :-
    schedule_notes("13", Notes),
    part2(Notes, Timestamp),
    assertion(Timestamp == 0).

% Folding the same congruences in a different order lands on the same
% timestamp: CRT solutions are unique modulo the product of the IDs.
test(crt_is_order_independent) :-
    example_input(Raw),
    parse_input(Raw, notes(_, Buses)),
    reverse(Buses, Reversed),
    crt(Buses, Forward),
    crt(Reversed, Backward),
    assertion(Forward == Backward).

% --- Real-input answer locks ---

real_notes(Notes) :-
    read_file_to_string('inputs/day13.txt', Raw, []),
    parse_input(Raw, Notes).

test(part1_real) :-
    real_notes(Notes),
    part1(Notes, Answer),
    assertion(Answer == 102).

test(part2_real) :-
    real_notes(Notes),
    part2(Notes, Timestamp),
    assertion(Timestamp == 327300950120029).

% The real answer clears the bound the statement promises, and satisfies
% all nine congruences.
test(part2_real_is_a_valid_schedule) :-
    real_notes(notes(_, Buses)),
    crt(Buses, Timestamp),
    assertion(Timestamp > 100000000000000),
    forall(member(Offset-Id, Buses),
           (Timestamp + Offset) mod Id =:= 0).

:- end_tests(day13).
