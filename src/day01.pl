:- module(day01, [parse_input/2, part1/2, part2/2, solve/3,
                  k_sum/4]).

% Day 1: Report Repair.
% Input is one integer expense entry per line. Find the two (part 1) and
% then three (part 2) entries that sum to 2020; the answer is their product.

% parse_input(+Raw, -Entries)
% Split on newlines, drop blanks, read each line as an integer.
parse_input(Raw, Entries) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(number_string, Entries, Lines).

% k_sum(+K, +Target, +Entries, -Combo)
% Combo is a K-element combination of Entries (order preserved) whose sum
% is exactly Target. Nondeterministic: backtracking enumerates every such
% combination. Entries should be ascending and non-negative so the
% `X =< Target` guard can prune doomed branches early.
k_sum(0, 0, _, []).
k_sum(K, Target, [X|Xs], [X|Combo]) :-
    K > 0,
    X =< Target,
    K1 is K - 1,
    T1 is Target - X,
    k_sum(K1, T1, Xs, Combo).
k_sum(K, Target, [_|Xs], Combo) :-
    K > 0,
    k_sum(K, Target, Xs, Combo).

% entry_product(+K, +Entries, -Product)
% Product of the first K-combination of Entries summing to 2020.
% msort/2 (not sort/2!) keeps duplicates, so a report containing 1010
% twice is still handled correctly.
entry_product(K, Entries, Product) :-
    msort(Entries, Sorted),
    once(k_sum(K, 2020, Sorted, Combo)),
    foldl([X, Acc0, Acc]>>(Acc is Acc0 * X), Combo, 1, Product).

% part1(+Entries, -Answer)
part1(Entries, Answer) :-
    entry_product(2, Entries, Answer).

% part2(+Entries, -Answer)
part2(Entries, Answer) :-
    entry_product(3, Entries, Answer).

% solve(+Raw, -Part1, -Part2)
solve(Raw, Part1, Part2) :-
    parse_input(Raw, Entries),
    part1(Entries, Part1),
    part2(Entries, Part2).
