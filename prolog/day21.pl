% Day 21: Allergen Assessment -- a Prolog companion to python/day21.py.
%
% This is not a return to Prolog and not part of the frozen src/ tree.  The
% maintained solution is the Python one; this file exists because the puzzle
% is a constraint satisfaction problem and the Python `assign` -- rounds of
% singleton peeling, a strike step, a refuse-to-guess branch -- is hand-written
% search control that Prolog supplies as the language.  Part 2 here is the
% three-clause assign/3 below and nothing else.  See the function guide,
% Problem_Statements/days/day21_function_guide.md, section 8.
%
% Run from anywhere (the input path is resolved relative to this file):
%
%     swipl prolog/day21.pl                 # real input -> part1=... part2=...
%     swipl prolog/day21.pl some/other.txt  # any foods file
%
% python/tests/test_day21.py runs it through swipl when one is on PATH and
% checks the answers against the Python module's; without swipl that test
% skips.

:- use_module(library(readutil)).
:- use_module(library(ordsets)).
:- use_module(library(apply)).
:- use_module(library(aggregate)).
:- use_module(library(pairs)).

:- initialization(main, main).

% ---- parse ------------------------------------------------------------------
% food(Ingredients, Allergens): ingredients as written (a list, so repeated
% appearances would count), allergens an ordset.  split_string's pad chars
% include \r, which is the CRLF guard.

foods(File, Foods) :-
    read_file_to_string(File, Raw, []),
    split_string(Raw, "\n", "\r ", Lines0),
    exclude(==(""), Lines0, Lines),
    maplist(food, Lines, Foods).

food(String, food(Ingredients, Allergens)) :-
    atom_string(Line, String),
    (   atomic_list_concat([Head, Tail0], ' (contains ', Line)
    ->  sub_atom(Tail0, 0, _, 1, Tail),                 % drop the closing ')'
        atomic_list_concat(Names, ', ', Tail),
        list_to_ord_set(Names, Allergens)
    ;   Head = Line,
        Allergens = []
    ),
    atomic_list_concat(Words, ' ', Head),
    exclude(==(''), Words, Ingredients).

% ---- rule 3: an allergen's holder is in every food that lists it ------------
% candidates(+Foods, +Allergen, -Allergen-Candidates)

candidates(Foods, Allergen, Allergen-Candidates) :-
    findall(Set,
            ( member(food(Ingredients, Allergens), Foods),
              memberchk(Allergen, Allergens),
              list_to_ord_set(Ingredients, Set) ),
            [First|Rest]),
    foldl(ord_intersection, Rest, First, Candidates).

% allergen_candidates(+Foods, -Pairs): one Allergen-Candidates pair per
% allergen, in allergen order (setof sorts), which is also part 2's order.

allergen_candidates(Foods, Pairs) :-
    setof(A, Is^As^(member(food(Is, As), Foods), member(A, As)), Allergens),
    maplist(candidates(Foods), Allergens, Pairs).

% ---- rules 1 and 2 as a search ----------------------------------------------
% assign(+Pairs, -Solution, +Used): pick one candidate per allergen (rule 1)
% such that no ingredient is picked twice (rule 2).  Backtracking is the
% elimination; there are no rounds and nothing to strike.  On the real input
% the first solution is found in 63 inferences and it is the only one:
%
%     ?- foods(F, Fs), allergen_candidates(Fs, Ps),
%        aggregate_all(count, assign(Ps, _, []), N).
%     N = 1.

assign([], [], _).
assign([Allergen-Candidates|More], [Allergen-Ingredient|Solution], Used) :-
    member(Ingredient, Candidates),
    \+ memberchk(Ingredient, Used),
    assign(More, Solution, [Ingredient|Used]).

% ---- the parts --------------------------------------------------------------

part1(Foods, Pairs, Count) :-
    pairs_values(Pairs, Sets),
    ord_union(Sets, Suspect),
    aggregate_all(count,
                  ( member(food(Ingredients, _), Foods),
                    member(Ingredient, Ingredients),
                    \+ ord_memberchk(Ingredient, Suspect) ),
                  Count).

part2(Pairs, Answer) :-
    once(assign(Pairs, Solution, [])),
    pairs_values(Solution, Holders),
    atomic_list_concat(Holders, ',', Answer).

solve(File, Part1, Part2) :-
    foods(File, Foods),
    allergen_candidates(Foods, Pairs),
    part1(Foods, Pairs, Part1),
    part2(Pairs, Part2).

% ---- entry point ------------------------------------------------------------

default_input(File) :-
    source_file(solve(_, _, _), Source),
    file_directory_name(Source, Dir),
    atomic_list_concat([Dir, '/../inputs/day21.txt'], File).

main([]) :-
    default_input(File),
    main([File]).
main([File]) :-
    solve(File, Part1, Part2),
    format("part1=~w part2=~w~n", [Part1, Part2]).
