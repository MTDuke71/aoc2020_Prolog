:- module(day10, [parse_input/2, part1/2, part2/2, solve/3,
                  full_chain/2, differences/2, difference_counts/3,
                  arrangements/2]).

% Day 10: Adapter Array.
% Every adapter must be used, and each accepts an input 1-3 jolts below its
% rating, so sorting the ratings fixes the one chain that uses them all.
% Part 1 multiplies the count of 1-jolt steps by the count of 3-jolt steps.
% Part 2 counts the distinct sub-chains that still connect outlet to device.

% ---------------------------------------------------------------------------
% Parsing and the full chain
% ---------------------------------------------------------------------------

% parse_input(+Raw, -Ratings)
% One adapter rating per non-empty line, in the order given.
parse_input(Raw, Ratings) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(number_string, Ratings, Lines).

% full_chain(+Ratings, -Chain)
% The chain both parts reason over: the outlet at 0, every adapter in
% ascending order, and the device's built-in adapter at highest + 3.
full_chain(Ratings, Chain) :-
    msort(Ratings, Sorted),
    last(Sorted, Highest),
    Device is Highest + 3,
    append([0|Sorted], [Device], Chain).

% ---------------------------------------------------------------------------
% Part 1: the difference histogram
% ---------------------------------------------------------------------------

% part1(+Ratings, -Product)
part1(Ratings, Product) :-
    full_chain(Ratings, Chain),
    chain_part1(Chain, Product).

% chain_part1(+Chain, -Product)
chain_part1(Chain, Product) :-
    differences(Chain, Diffs),
    difference_counts(Diffs, Ones, Threes),
    Product is Ones * Threes.

% differences(+Chain, -Diffs)
% Gaps between consecutive links; a chain of N links yields N-1 gaps. The
% previous link travels in an accumulator rather than being re-matched as a
% second head argument, so the recursive clauses split on `[]` vs `[_|_]` and
% first-argument indexing keeps the walk deterministic without a cut.
differences([Lower|Rest], Diffs) :-
    differences_from(Rest, Lower, Diffs).

% differences_from(+Rest, +Lower, -Diffs)
differences_from([], _Lower, []).
differences_from([Upper|Rest], Lower, [Diff|Diffs]) :-
    Diff is Upper - Lower,
    differences_from(Rest, Upper, Diffs).

% difference_counts(+Diffs, -Ones, -Threes)
% Only 1- and 3-jolt steps are scored. A well-formed puzzle input has no
% other gap size, but nothing here depends on that.
difference_counts(Diffs, Ones, Threes) :-
    include(=(1), Diffs, OneSteps),
    include(=(3), Diffs, ThreeSteps),
    length(OneSteps, Ones),
    length(ThreeSteps, Threes).

% ---------------------------------------------------------------------------
% Part 2: counting distinct arrangements
% ---------------------------------------------------------------------------

% part2(+Ratings, -Count)
part2(Ratings, Count) :-
    full_chain(Ratings, Chain),
    arrangements(Chain, Count).

% arrangements(+Chain, -Count)
% Count the paths from outlet to device that only ever step up by 1-3 jolts.
% The number of paths reaching a link is the sum over its admissible
% predecessors, so one ascending sweep with running totals suffices.
%
% State is `Recent`: up to three `Value-Ways` pairs, newest first. Three is
% enough because consecutive links differ by at least 1 jolt, so anything
% further back than three links is already more than 3 jolts below.
arrangements([Outlet|Rest], Count) :-
    foldl(place_adapter, Rest, [Outlet-1], Recent),
    Recent = [_Device-Count|_].

% place_adapter(+Value, +Recent0, -Recent)
place_adapter(Value, Recent0, Recent) :-
    reachable_ways(Recent0, Value, Ways),
    recent_three([Value-Ways|Recent0], Recent).

% reachable_ways(+Recent, +Value, -Ways)
% Sum the path counts of the links Value can plug into: those no more than
% 3 jolts below it. Sums here run into the trillions; SWI integers are
% arbitrary precision, so no overflow guard is needed.
reachable_ways(Recent, Value, Ways) :-
    include(within_reach(Value), Recent, Reachable),
    pairs_values(Reachable, Counts),
    sum_list(Counts, Ways).

% within_reach(+Value, +Pair)
within_reach(Value, Lower-_Ways) :-
    Value - Lower =< 3.

% recent_three(+Pairs, -Recent)
% Keep the window bounded at three, so each step costs O(1).
recent_three([A, B, C|_], Recent) :-
    !,
    Recent = [A, B, C].
recent_three(Pairs, Recent) :-
    Recent = Pairs.

% ---------------------------------------------------------------------------
% Combined entry point
% ---------------------------------------------------------------------------

% solve(+Raw, -Product, -Count)
% Both parts sweep the same sorted chain, so solve builds it once. The
% standalone part1/2 and part2/2 each build their own, keeping them usable
% as independent entry points for tests and the bench.
solve(Raw, Product, Count) :-
    parse_input(Raw, Ratings),
    full_chain(Ratings, Chain),
    chain_part1(Chain, Product),
    arrangements(Chain, Count).
