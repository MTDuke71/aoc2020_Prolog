:- module(day06, [parse_input/2, part1/2, part2/2, solve/3,
                  group_anyone/2, group_everyone/2]).

:- use_module(library(ordsets)).

% Day 6: Custom Customs.
% The form has 26 yes/no questions (a..z). Groups of people are separated
% by blank lines; within a group, each line is one person's "yes" letters.
% Treat every person as a *set* of letters. Part 1: for each group count
% the questions ANYONE answered yes — the union of the group's sets —
% and sum those counts. Part 2: count the questions EVERYONE answered —
% the intersection — and sum. "Anyone" = ∪, "everyone" = ∩; the two parts
% are the same fold over the same parsed groups with the set op swapped.

% parse_input(+Raw, -Groups)
% Groups is a list of groups; each group is a list of people, and each
% person is an ordset (sorted, duplicate-free list) of the letter atoms
% they answered yes to. Blank lines separate groups. Same block-splitting
% opener as Day 4 (Passport Processing) — blocks/2 + block_rest/2 are
% reused verbatim; only the per-line mapping differs.
parse_input(Raw, Groups) :-
    split_string(Raw, "\n", " \t\r", Lines),
    blocks(Lines, Blocks),
    maplist(block_group, Blocks, Groups).

% blocks(+Lines, -Blocks)
% Group consecutive non-blank Lines into Blocks; blank lines separate
% blocks and never appear in one. (Identical to Day 4's blocks/2.)
blocks([], []).
blocks([""|Rest], Blocks) :- !,
    blocks(Rest, Blocks).
blocks([Line|Rest], [[Line|More]|Blocks]) :-
    block_rest(Rest, More, Tail),
    blocks(Tail, Blocks).

% block_rest(+Lines, -More, -Tail)
% More is the non-blank prefix of Lines; Tail is everything after the
% blank line (or []) that ended it.
block_rest([], [], []).
block_rest([""|Rest], [], Rest) :- !.
block_rest([Line|Rest], [Line|More], Tail) :-
    block_rest(Rest, More, Tail).

% block_group(+Lines, -People)
% One group's lines become a list of per-person letter sets.
block_group(Lines, People) :-
    maplist(person_set, Lines, People).

% person_set(+Line, -Set)
% A person's answer line becomes the ordset of its letters. Reading it as
% a set drops any accidental duplicates and makes ord_union / ord_intersection
% directly applicable.
person_set(Line, Set) :-
    string_chars(Line, Chars),
    list_to_ord_set(Chars, Set).

% group_anyone(+People, -Count)
% Part-1 per-group score: how many questions ANYONE answered yes — the
% size of the union of the group's sets. ord_union/2 folds a list of
% ordsets into their union (empty set is the identity, so a lone person
% just gives their own letters).
group_anyone(People, Count) :-
    ord_union(People, Union),
    length(Union, Count).

% group_everyone(+People, -Count)
% Part-2 per-group score: how many questions EVERYONE answered — the size
% of the intersection. ord_intersection/2 folds a list of ordsets into
% their common elements; for a single-person group that is that person's
% own set.
group_everyone(People, Count) :-
    ord_intersection(People, Inter),
    length(Inter, Count).

% part1(+Groups, -Answer)
% Sum of each group's "anyone" count.
part1(Groups, Answer) :-
    maplist(group_anyone, Groups, Counts),
    sum_list(Counts, Answer).

% part2(+Groups, -Answer)
% Sum of each group's "everyone" count.
part2(Groups, Answer) :-
    maplist(group_everyone, Groups, Counts),
    sum_list(Counts, Answer).

% solve(+Raw, -Part1, -Part2)
solve(Raw, Part1, Part2) :-
    parse_input(Raw, Groups),
    part1(Groups, Part1),
    part2(Groups, Part2).
