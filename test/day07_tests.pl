:- begin_tests(day07).

:- use_module('../src/day07.pl').

% The statement's part-1 example: 4 colours can reach shiny gold, and one
% shiny gold bag contains 32 other bags.
example_input("\
light red bags contain 1 bright white bag, 2 muted yellow bags.
dark orange bags contain 3 bright white bags, 4 muted yellow bags.
bright white bags contain 1 shiny gold bag.
muted yellow bags contain 2 shiny gold bags, 9 faded blue bags.
shiny gold bags contain 1 dark olive bag, 2 vibrant plum bags.
dark olive bags contain 3 faded blue bags, 4 dotted black bags.
vibrant plum bags contain 5 faded blue bags, 6 dotted black bags.
faded blue bags contain no other bags.
dotted black bags contain no other bags.
").

% The part-2 example: a linear chain where one shiny gold bag holds 126.
chain_input("\
shiny gold bags contain 2 dark red bags.
dark red bags contain 2 dark orange bags.
dark orange bags contain 2 dark yellow bags.
dark yellow bags contain 2 dark green bags.
dark green bags contain 2 dark blue bags.
dark blue bags contain 2 dark violet bags.
dark violet bags contain no other bags.
").

% --- Parser: a rule becomes Colour -> [Count-Child, ...] ---

test(parse_weighted_edges) :-
    parse_input("light red bags contain 1 bright white bag, 2 muted yellow bags.\n",
                Rules),
    get_assoc('light red', Rules, Children),
    assertion(Children == [1-'bright white', 2-'muted yellow']).

test(parse_leaf_is_empty) :-
    parse_input("faded blue bags contain no other bags.\n", Rules),
    get_assoc('faded blue', Rules, Children),
    assertion(Children == []).

% --- Reachability relation (single queries show the backtracking) ---

test(can_contain_direct_and_indirect) :-
    example_input(Raw),
    parse_input(Raw, Rules),
    % can_contain/3 is nondet (a colour may reach the target by several
    % paths); as a yes/no query, once/1 is the right reading.
    assertion(once(can_contain(Rules, 'bright white', 'shiny gold'))),  % direct
    assertion(once(can_contain(Rules, 'dark orange', 'shiny gold'))).   % two hops

test(cannot_contain_when_no_path, [fail]) :-
    example_input(Raw),
    parse_input(Raw, Rules),
    can_contain(Rules, 'faded blue', 'shiny gold').  % a leaf holds nothing

% --- Recursive weighted count in isolation ---

test(contained_count_subtrees) :-
    example_input(Raw),
    parse_input(Raw, Rules),
    contained_count(Rules, 'dark olive', N1),   % 3 + 4 empties
    contained_count(Rules, 'vibrant plum', N2), % 5 + 6 empties
    assertion(N1 == 7),
    assertion(N2 == 11).

% --- Parts on the examples ---

test(part1_example) :-
    example_input(Raw),
    solve(Raw, Part1, _),
    assertion(Part1 == 4).

test(part2_example) :-
    example_input(Raw),
    solve(Raw, _, Part2),
    assertion(Part2 == 32).

test(part2_chain_example) :-
    chain_input(Raw),
    solve(Raw, _, Part2),
    assertion(Part2 == 126).

% --- Real-input answer locks ---

real_input(Raw) :-
    read_file_to_string('inputs/day07.txt', Raw, []).

test(part1_real) :-
    real_input(Raw),
    solve(Raw, P1, _),
    assertion(P1 == 370).

test(part2_real) :-
    real_input(Raw),
    solve(Raw, _, P2),
    assertion(P2 == 29547).

:- end_tests(day07).
