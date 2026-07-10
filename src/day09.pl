:- module(day09, [parse_input/2, part1/2, part2/2, solve/3,
                  part1_with_preamble/3, part2_with_preamble/3,
                  invalid_number/3, valid_sum/2, contiguous_range/3]).

% Day 9: Encoding Error.
% After a fixed-size preamble, every number must be the sum of two distinct
% values from the immediately preceding window. Part 1 finds the first
% number that breaks that rule. Part 2 finds a contiguous range before that
% number whose sum is it, then adds the range's minimum and maximum.

% ---------------------------------------------------------------------------
% Parsing and configuration
% ---------------------------------------------------------------------------

% parse_input(+Raw, -Numbers)
% Each non-empty input line is one arbitrary-precision Prolog integer.
parse_input(Raw, Numbers) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(number_string, Numbers, Lines).

preamble_size(25).

% part1(+Numbers, -Invalid)
part1(Numbers, Invalid) :-
    preamble_size(PreambleSize),
    invalid_number(Numbers, PreambleSize, Invalid).

% part1_with_preamble(+Numbers, +PreambleSize, -Invalid)
% The public puzzle uses 25; this variant also makes the statement's
% five-number example directly testable.
part1_with_preamble(Numbers, PreambleSize, Invalid) :-
    invalid_number(Numbers, PreambleSize, Invalid).

% part2(+Numbers, -Weakness)
part2(Numbers, Weakness) :-
    preamble_size(PreambleSize),
    part2_with_preamble(Numbers, PreambleSize, Weakness).

% part2_with_preamble(+Numbers, +PreambleSize, -Weakness)
part2_with_preamble(Numbers, PreambleSize, Weakness) :-
    invalid_and_prefix(Numbers, PreambleSize, Invalid, BeforeInvalid),
    weakness(Invalid, BeforeInvalid, Weakness).

% weakness(+Invalid, +BeforeInvalid, -Weakness)
% The encryption weakness: smallest plus largest of a contiguous range
% (length >= 2, drawn from the values before Invalid) that sums to Invalid.
weakness(Invalid, BeforeInvalid, Weakness) :-
    contiguous_range(BeforeInvalid, Invalid, Range),
    min_list(Range, Smallest),
    max_list(Range, Largest),
    Weakness is Smallest + Largest.

% solve(+Raw, -Invalid, -Weakness)
% Both parts need the first invalid value, so solve finds it (and the
% prefix before it) exactly once and shares it. Calling part1/2 and part2/2
% separately would rescan for the invalid value twice; keeping them as
% independent entry points is deliberate, but solve avoids the double scan.
solve(Raw, Invalid, Weakness) :-
    parse_input(Raw, Numbers),
    preamble_size(PreambleSize),
    invalid_and_prefix(Numbers, PreambleSize, Invalid, BeforeInvalid),
    weakness(Invalid, BeforeInvalid, Weakness).

% ---------------------------------------------------------------------------
% Part 1: the first invalid number
% ---------------------------------------------------------------------------

% invalid_number(+Numbers, +PreambleSize, -Invalid)
invalid_number(Numbers, PreambleSize, Invalid) :-
    invalid_and_prefix(Numbers, PreambleSize, Invalid, _BeforeInvalid).

% invalid_and_prefix(+Numbers, +PreambleSize, -Invalid, -BeforeInvalid)
% Keep the values before the current candidate in reverse order. This lets
% Part 2 search only the data preceding the invalid number, even if the same
% numeric value appeared earlier in the input.
invalid_and_prefix(Numbers, PreambleSize, Invalid, BeforeInvalid) :-
    length(Window, PreambleSize),
    append(Window, Remaining, Numbers),
    reverse(Window, BeforeRev),
    first_invalid(Remaining, Window, BeforeRev, Invalid, BeforeInvalid).

% first_invalid(+Candidates, +Window, +BeforeRev, -Invalid, -Before)
first_invalid([Candidate|_], Window, BeforeRev, Candidate, Before) :-
    \+ valid_sum(Candidate, Window),
    !,
    reverse(BeforeRev, Before).
first_invalid([Candidate|Rest], Window0, BeforeRev, Invalid, Before) :-
    valid_sum(Candidate, Window0),
    slide_window(Window0, Candidate, Window1),
    first_invalid(Rest, Window1, [Candidate|BeforeRev], Invalid, Before).

% slide_window(+Window0, +NewValue, -Window1)
% The input window is kept oldest-to-newest. Its first (oldest) value is
% discarded, and the new value becomes the newest member.
slide_window([_|Tail], NewValue, Window1) :-
    append(Tail, [NewValue], Window1).

% valid_sum(+Target, +Window)
% The two addends must be different values, not merely two positions. select/3
% removes the first addend's occurrence, so the two values also come from
% different entries in the window.
valid_sum(Target, Window) :-
    select(First, Window, Remaining),
    member(Second, Remaining),
    First =\= Second,
    Target =:= First + Second,
    !.

% ---------------------------------------------------------------------------
% Part 2: a contiguous range with the invalid sum
% ---------------------------------------------------------------------------

% contiguous_range(+PositiveNumbers, +Target, -Range)
% Search starts from each position. Since the puzzle numbers are positive,
% extending a range can only increase its sum, so an overshoot lets us stop
% that start and move to the next one. At least one extension is required,
% which excludes a one-element range.
contiguous_range(Numbers, Target, Range) :-
    contiguous_from_start(Numbers, Target, Range),
    !.

contiguous_from_start([First|Rest], Target, Range) :-
    extend_range(Rest, First, Target, [First], Range).
contiguous_from_start([_|Rest], Target, Range) :-
    contiguous_from_start(Rest, Target, Range).

extend_range([Next|Rest], CurrentSum, Target, ReverseRange, Range) :-
    NewSum is CurrentSum + Next,
    (   NewSum =:= Target
    ->  reverse([Next|ReverseRange], Range)
    ;   NewSum < Target
    ->  extend_range(Rest, NewSum, Target, [Next|ReverseRange], Range)
    ;   fail
    ).
