:- module(day07, [parse_input/2, part1/2, part2/2, solve/3,
                  can_contain/3, contained_count/3]).

:- use_module(library(assoc)).

% Day 7: Handy Haversacks.
% The rules are a directed, edge-weighted graph over bag colours: a line
% "light red bags contain 1 bright white bag, 2 muted yellow bags." is the
% node `light red` with weighted edges 1->bright white, 2->muted yellow.
% Part 1: how many colours can *eventually* contain a shiny gold bag —
% reachability of `shiny gold` from each node (a graph search). Part 2:
% how many bags are inside one shiny gold bag — a recursive weighted count
% of its descendants.

target('shiny gold').

% parse_input(+Raw, -Rules)
% Rules is an assoc mapping each colour (an atom) to its contents: a list
% of Count-Colour pairs (Count an integer, Colour an atom). Every colour
% that appears as a container has exactly one rule, so keys are unique and
% list_to_assoc/2 is well-defined; leaf bags map to [].
parse_input(Raw, Rules) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(parse_rule, Lines, Pairs),
    list_to_assoc(Pairs, Rules).

% parse_rule(+Line, -(Colour-Contents))
% "<colour> bags contain <contents>." -> Colour-[Count-Child, ...].
% Strip the trailing period, split at the fixed phrase " bags contain " —
% everything before it is the container colour, everything after is the
% contents clause.
parse_rule(Line, Colour-Contents) :-
    split_string(Line, "", ".", [Clean]),            % strip trailing '.'
    sub_string(Clean, Before, Len, _, " bags contain "),
    !,
    sub_string(Clean, 0, Before, _, ColourS),
    atom_string(Colour, ColourS),
    Start is Before + Len,
    sub_string(Clean, Start, _, 0, RestS),
    parse_contents(RestS, Contents).

% parse_contents(+Rest, -Contents)
% "no other bags" -> []; otherwise a comma-separated list of items.
parse_contents("no other bags", []) :- !.
parse_contents(Rest, Contents) :-
    split_string(Rest, ",", " ", Items),
    maplist(parse_item, Items, Contents).

% parse_item(+Item, -(Count-Colour))
% "2 muted yellow bags" -> 2-'muted yellow'. The last word is always
% "bag"/"bags"; the count is the first token; the colour is what's between.
parse_item(Item, Count-Colour) :-
    split_string(Item, " ", "", [CountS|Words0]),
    number_string(Count, CountS),
    once(append(ColourWords, [_BagWord], Words0)),   % peel trailing bag/bags
    atomic_list_concat(ColourWords, ' ', Colour).

% can_contain(+Rules, +Colour, +Target)
% The declarative reading of reachability: a Colour bag can eventually hold
% a Target bag if some direct child is the target, or some direct child can
% itself contain it. member/2 backtracks over the children, so this is
% nondet — a colour with several paths to the target proves true once per
% path. It is the natural single-query form ("can dark orange hold gold?");
% part1 does *not* iterate it over all colours (that re-explores shared
% subgraphs) but reverses the graph instead — see below.
can_contain(Rules, Colour, Target) :-
    get_assoc(Colour, Rules, Children),
    member(_-Child, Children),
    (   Child == Target
    ->  true
    ;   can_contain(Rules, Child, Target)
    ).

% part1(+Rules, -Count)
% Count the colours from which shiny gold is reachable. Instead of running
% can_contain/3 forward from all 594 colours (which re-explores shared
% subgraphs and is ~exponential on the misses), reverse the edges once and
% search *outward from the target*: build a Child -> [Parent,...] index and
% take the transitive closure of the target's parents. Every colour that
% can reach the target is visited exactly once — O(V + E).
part1(Rules, Count) :-
    target(Target),
    parents_index(Rules, Parents),
    ( get_assoc(Target, Parents, Seed) -> true ; Seed = [] ),
    close_ancestors(Parents, Seed, [], Ancestors),
    length(Ancestors, Count).

% parents_index(+Rules, -Parents)
% Invert the containment graph: Parents maps each Child colour to the list
% of colours that directly contain it.
parents_index(Rules, Parents) :-
    assoc_to_list(Rules, Pairs),
    empty_assoc(Empty),
    foldl(index_rule, Pairs, Empty, Parents).

index_rule(Colour-Children, A0, A) :-
    foldl(index_edge(Colour), Children, A0, A).

index_edge(Colour, _Count-Child, A0, A) :-
    ( get_assoc(Child, A0, Ps) -> true ; Ps = [] ),
    put_assoc(Child, A0, [Colour|Ps], A).

% close_ancestors(+Parents, +Queue, +Visited, -Ancestors)
% Breadth-first transitive closure with a visited set: pop a colour, and
% if unseen, mark it and enqueue its parents. Visited never holds the
% target (it is not its own parent), so it is exactly the ancestor set.
close_ancestors(_, [], Visited, Visited).
close_ancestors(Parents, [C|Queue], Visited, Result) :-
    (   memberchk(C, Visited)
    ->  close_ancestors(Parents, Queue, Visited, Result)
    ;   ( get_assoc(C, Parents, Ps) -> true ; Ps = [] ),
        append(Ps, Queue, Queue1),
        close_ancestors(Parents, Queue1, [C|Visited], Result)
    ).

% contained_count(+Rules, +Colour, -Total)
% Total number of bags strictly inside one Colour bag: for each edge
% Count-Child, that subtree contributes Count * (1 + bags inside a Child).
contained_count(Rules, Colour, Total) :-
    get_assoc(Colour, Rules, Children),
    foldl(add_child(Rules), Children, 0, Total).

add_child(Rules, Count-Child, Acc0, Acc) :-
    contained_count(Rules, Child, Sub),
    Acc is Acc0 + Count * (1 + Sub).

% part2(+Rules, -Total)
% How many bags are required inside a single shiny gold bag.
part2(Rules, Total) :-
    target(Target),
    contained_count(Rules, Target, Total).

% solve(+Raw, -Part1, -Part2)
solve(Raw, Part1, Part2) :-
    parse_input(Raw, Rules),
    part1(Rules, Part1),
    part2(Rules, Part2).
