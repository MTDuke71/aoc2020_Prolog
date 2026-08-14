# Day 07 Function Guide — Handy Haversacks

> **Written during this repo's Prolog era.** The solution it describes lives
> in the frozen `src/` tree. The maintained solution for this day is
> `python/day07.py`, tested by `python/tests/test_day07.py`. This guide is
> kept for its problem framing and algorithm reasoning, which did not change
> with the language; it will be rewritten Python-first when this day is next
> touched. See the README for what "frozen" means here.

---

> This is the day the puzzle input *is* a knowledge base. Every line is a
> **rule** — "a light red bag contains 1 bright white and 2 muted yellow
> bags" — and the whole file is a directed, edge-weighted graph over bag
> colours. The two parts are the two classic graph questions: **Part 1 is
> reachability** (which nodes can reach `shiny gold`?) and **Part 2 is a
> recursive weighted node count** (how many bags nest inside one `shiny
> gold`?). The Prolog-native reading of "can X eventually contain Y" is a
> two-line recursive relation with backtracking — `can_contain/3` — but
> the day's real lesson is knowing when the *elegant* relation is the
> wrong tool for the *aggregate* question, and reversing the graph
> instead.

## The puzzle in one paragraph

594 rules like `light red bags contain 1 bright white bag, 2 muted yellow
bags.` define, for each colour, the counted list of colours it must
contain (`... contain no other bags.` for leaves). **Part 1:** how many
colours can *eventually* contain at least one `shiny gold` bag? (Example:
`4`.) **Part 2:** how many individual bags are required *inside* one
`shiny gold` bag? (Example: `32`; a second chain example gives `126`.)

---

## Representation: rules as an assoc of weighted edges

A rule is a node plus its out-edges. The parsed value is an **assoc**
(SWI's AVL-tree map, `library(assoc)`) from colour → contents:

```
'light red'   -> [1-'bright white', 2-'muted yellow']
'shiny gold'  -> [1-'dark olive', 2-'vibrant plum']
'faded blue'  -> []
```

Keys are colour **atoms**; each value is a list of `Count-Colour` pairs —
the weighted out-edges. Why an assoc rather than a list of `rule/2`
facts or a `:- dynamic` database?

- **Every colour that is ever a container has exactly one rule**, so the
  keys are unique and `list_to_assoc/2` is well-defined; child lookup is
  `get_assoc/3` in `O(log n)`.
- It keeps the solution **pure**: `parse_input/2` returns a value the
  parts consume, with no global database state to assert/retract between
  test runs — the same parse-once contract as every day since Day 4.

The database form (`assert(contains('light red', 1, 'bright white'))`,
then `setof`/backtracking) is the *other* idiomatic Prolog encoding and
is discussed in the optimization sidebar; the assoc keeps determinism and
testability without giving up the graph reading.

---

## Reading Prolog: a recursive relation, graph reversal, a weighted fold

**1. `can_contain/3` — reachability as a two-line relation.** "A colour
can eventually contain the target" is naturally recursive:

```prolog
can_contain(Rules, Colour, Target) :-
    get_assoc(Colour, Rules, Children),
    member(_-Child, Children),
    (   Child == Target
    ->  true
    ;   can_contain(Rules, Child, Target)
    ).
```

`member(_-Child, Children)` **backtracks over the out-edges** (the count
is ignored with `_`); for each child we either hit the target or recurse
into it. This is the declarative core of the whole puzzle and reads like
its English statement. It is **nondet**: a colour with several paths to
the target proves `true` once per path — perfectly fine for a single
yes/no query (`once(can_contain(...))`), which is why the test wraps it
in `once/1`.

**2. Why Part 1 does *not* iterate `can_contain/3`.** The obvious Part 1
is `include(can_contain-over-all-594-colours)`. It gives the right answer
— and measured **~47 ms**, an order of magnitude slower than anything
else in the repo. The reason is algorithmic: a colour that *cannot* reach
the target explores its entire reachable subgraph, and because there is
no memo, subgraphs shared by many colours are re-explored again and
again — roughly exponential on the misses. The fix is the textbook one:
**reverse the edges and search once, outward from the target.**

```prolog
part1(Rules, Count) :-
    target(Target),
    parents_index(Rules, Parents),          % Child -> [Parent, ...]
    ( get_assoc(Target, Parents, Seed) -> true ; Seed = [] ),
    close_ancestors(Parents, Seed, [], Ancestors),
    length(Ancestors, Count).
```

`parents_index/2` inverts the graph (for each edge `Colour -> Child`, add
`Colour` to `Parents[Child]`); `close_ancestors/4` is a **breadth-first
transitive closure with a visited set** — pop a colour, and if unseen,
mark it and enqueue its parents:

```prolog
close_ancestors(_, [], Visited, Visited).
close_ancestors(Parents, [C|Queue], Visited, Result) :-
    (   memberchk(C, Visited)
    ->  close_ancestors(Parents, Queue, Visited, Result)
    ;   ( get_assoc(C, Parents, Ps) -> true ; Ps = [] ),
        append(Ps, Queue, Queue1),
        close_ancestors(Parents, Queue1, [C|Visited], Result)
    ).
```

Every colour that can reach the target enters `Visited` exactly once, so
this is `O(V + E)` and drops Part 1 to **~3.9 ms**. The `Visited` set is
what turns a potentially exponential walk into a linear one — the same
idea as marking nodes in a BFS/DFS.

**3. Part 2 — a recursive *weighted* count.** "How many bags inside one
`shiny gold`" is a fold over the out-edges where each edge contributes
its count times one-plus-the-subtree:

```prolog
contained_count(Rules, Colour, Total) :-
    get_assoc(Colour, Rules, Children),
    foldl(add_child(Rules), Children, 0, Total).

add_child(Rules, Count-Child, Acc0, Acc) :-
    contained_count(Rules, Child, Sub),
    Acc is Acc0 + Count * (1 + Sub).
```

The recurrence is `inside(B) = Σ nᵢ · (1 + inside(Cᵢ))` over B's edges:
each of the `nᵢ` child bags is itself one bag (`+1`) plus whatever nests
inside it (`inside(Cᵢ)`). A leaf's `Children` is `[]`, so `foldl` returns
`0` and the recursion bottoms out. On the example: `inside(dark olive) =
3·1 + 4·1 = 7`, `inside(vibrant plum) = 5·1 + 6·1 = 11`, so
`inside(shiny gold) = 1·(1+7) + 2·(1+11) = 8 + 24 = 32`. Because bag
rules form a DAG, this always terminates; unlike Part 1 the target's
subtree is small, so the un-memoized recursion is already **~0.04 ms**.

---

## The Day 7 code, predicate by predicate

### `parse_input/2`, `parse_rule/2`, `parse_contents/2`, `parse_item/2`

```prolog
parse_input(Raw, Rules) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(parse_rule, Lines, Pairs),
    list_to_assoc(Pairs, Rules).
```

The repo's split-and-clean opener, then one `Colour-Contents` pair per
line, assembled into the assoc. `parse_rule/2` strips the trailing period
(`split_string(Line, "", ".", [Clean])` — empty separator, `"."` as pad,
trims the dot), locates the fixed phrase `" bags contain "` with
`sub_string/5`, and cuts: everything before is the container colour,
everything after is the contents clause. `parse_contents/2` special-cases
the leaf string `"no other bags"` to `[]`, else splits on `", "` and maps
`parse_item/2` over the items. `parse_item/2` splits `"2 muted yellow
bags"` on spaces, reads the leading count, and peels the trailing
`bag`/`bags` word:

```prolog
once(append(ColourWords, [_BagWord], Words0))
```

`append(Front, [Last], List)` is the idiomatic "split off the last
element," but with a bound `List` it leaves a spurious choice point
(append doesn't know the list won't extend); `once/1` commits to the
single solution and keeps the whole parse deterministic — the repo's
no-choicepoint-warnings bar (see [Day 5](day05_function_guide.md)).

### `can_contain/3`

The declarative reachability relation (above). Exported and tested as the
natural single-query form, but not used by Part 1.

### `part1/2` and helpers `parents_index/2`, `close_ancestors/4`

Graph reversal + BFS closure (above). `parents_index/2` uses nested
`foldl` — outer over rules, inner over each rule's edges — to accumulate
the inverted adjacency into an assoc of parent-lists. `close_ancestors/4`
is the visited-set closure; its two clauses are mutually exclusive on the
queue (`[]` vs `[C|Queue]`), so it runs deterministically.

### `contained_count/3`, `part2/2`, `solve/3`

The weighted recursive count (above). `part2/2` seeds it at the target;
`solve/3` is the standard parse-once-answer-both.

---

## Correctness notes

- **Parse:** each rule yields one `Colour-[Count-Child,...]` pair; the
  leaf phrase maps to `[]`. Colours are two-word atoms in this input, but
  `parse_item/2` peels only the trailing `bag`/`bags` token, so any
  word-count colour parses correctly.
- **Part 1** counts colours that can reach `shiny gold`. Reversing the
  graph makes this the ancestor set of the target; the visited set
  guarantees each ancestor is counted once and guarantees termination
  even though the forward graph could otherwise be re-walked
  exponentially. The target itself is never its own parent, so it is
  excluded from the count. Example → `4`, real → **370**.
- **Part 2** applies `inside(B) = Σ nᵢ·(1 + inside(Cᵢ))`. The DAG
  structure guarantees termination; leaves contribute `0`. Example →
  `32`, chain example → `126`, real → **29547**.
- **Determinism:** the parser commits with cuts / `once/1`;
  `close_ancestors/4` and `parse_contents/2` have mutually exclusive
  clauses; `get_assoc`, `foldl`, `memberchk`, `length` are deterministic.
  `can_contain/3` is *intentionally* nondet and is only ever called under
  `once/1`. The suite runs with **no "succeeded with choicepoint"
  warnings**.
- Locked real-input answers: **Part 1 = 370**, **Part 2 = 29547**,
  cross-validated by [python/day07.py](../../python/day07.py).

## Tests — what's pinned and why

[test/day07_tests.pl](../../test/day07_tests.pl) pins five layers, **10
tests green** (run `swipl test/run_tests.pl` from the repo root):

1. **Parser** — a multi-edge rule parses to
   `[1-'bright white', 2-'muted yellow']` (counts *and* colours, so a bug
   swapping either is caught); a leaf parses to `[]`.
2. **Reachability relation** — `can_contain/3` is true for a direct
   container and a two-hop one, and *fails* for a leaf (`[fail]` test).
3. **Weighted count in isolation** — `contained_count` on `dark olive`
   is `7` and on `vibrant plum` is `11`, pinning the subtree arithmetic
   before it feeds the top-level total.
4. **Parts on examples** — `part1 = 4`, `part2 = 32` on the main example,
   and `part2 = 126` on the linear chain (the deep-nesting case).
5. **Real answers** — `370` / `29547` locked against `inputs/day07.txt`.

## Complexity & benchmarks

Let `V` = colours (594), `E` = total edges.

- **Parse:** `O(total input size)` — one pass, per-line splitting.
- **Part 1:** `O(V + E)` — build the reverse index, then one BFS closure.
  (The naive forward `include(can_contain)` is worst-case exponential: it
  runs **348,175 inferences** to the closure's **62,456** — a stable 5.6×
  more work. The wall gap is even wider, ~47 ms vs ~3.9 ms, because the
  naive version also churns choicepoints and bindings the inference count
  doesn't see. Either way, it's why the shipped code reverses the graph.)
- **Part 2:** `O(size of the shiny-gold subtree)` — a DAG recursion; tiny
  here.

Inferences are exact and reproducible (`swipl bench/main.pl day07` reports
the same counts every run); the times are the mean of 2,000 iterations:

| Phase | Inferences | Time (ms) |
|-------|-----------:|----------:|
| parse | 25,457 | 2.66 |
| part1 | 62,456 | 3.88 |
| part2 | 1,051 | 0.04 |

Parsing and the Part 1 closure are the two real costs (string work over
594 lines; index + BFS over the graph); Part 2 is a handful of
multiplications.

## If I were writing this in Rust

```rust
use std::collections::{HashMap, HashSet};

type Rules = HashMap<String, Vec<(u64, String)>>;

fn part1(rules: &Rules) -> usize {
    let mut parents: HashMap<&str, Vec<&str>> = HashMap::new();
    for (c, kids) in rules {
        for (_, child) in kids {
            parents.entry(child).or_default().push(c);
        }
    }
    let mut seen = HashSet::new();
    let mut stack: Vec<&str> = parents.get("shiny gold").cloned().unwrap_or_default();
    while let Some(c) = stack.pop() {
        if seen.insert(c) {
            stack.extend(parents.get(c).into_iter().flatten().copied());
        }
    }
    seen.len()
}

fn inside(rules: &Rules, colour: &str) -> u64 {
    rules[colour].iter().map(|(n, c)| n * (1 + inside(rules, c))).sum()
}
```

- **assoc ↔ `HashMap`.** Prolog's `get_assoc/put_assoc` are the AVL-tree
  analog of Rust's hash map; both are the "colour → contents" index.
- **`close_ancestors/4` ↔ the `while let Some` stack loop.** The Prolog
  visited list plus queue *is* Rust's `HashSet` + `Vec` worklist;
  `seen.insert(c)` returning `false` on a repeat is exactly `memberchk(C,
  Visited)` short-circuiting. Both take the transitive closure of the
  target's parents over the reversed graph.
- **`contained_count/3` ↔ `inside`.** The `foldl(add_child, …)` weighted
  fold is Rust's `.map(|(n,c)| n*(1+inside(..))).sum()` — the same
  recurrence, recursion mirroring recursion.
- **`can_contain/3` has no direct Rust analog** because Rust doesn't
  backtrack; you'd write the reachability test as its own DFS. That
  asymmetry is the point of the day — Prolog *gives* you the relational
  search for free, and the skill is choosing when to use it (single
  query) versus when to reverse the graph (the aggregate).

The Python reference
([python/day07.py](../../python/day07.py)) is the same two algorithms —
a reverse-BFS `set`/`list` worklist for Part 1 and a recursive `sum` for
Part 2 — and re-confirms `370` / `29547`.

## Possible optimization

- **The `:- dynamic` database form.** Assert `edge(Container, N, Child)`
  facts and let Prolog's clause indexing be the graph:
  `can_contain(X, gold) :- edge(X, _, gold).`
  `can_contain(X, T) :- edge(X, _, M), can_contain(M, T).`
  then `aggregate_all(count, distinct(X, can_contain(X, gold)), N)` for
  Part 1. It is the most "textbook Prolog" encoding and very compact, but
  it (a) reintroduces global state that must be retracted between runs —
  awkward for the pure `solve/3` contract and the test suite — and (b)
  still needs `distinct`/memoing to avoid the same re-exploration blow-up.
  Declined for the pure assoc, which keeps determinism and testability.
- **Memoize Part 1's forward search** with an assoc of `Colour -> bool`
  results instead of reversing the graph. Same `O(V+E)`, but threading a
  memo through pure Prolog is clunkier than reversing the edges once, and
  the reversed-BFS reads as a standard algorithm.
- **Memoize `contained_count/3`** for pathological deep-sharing inputs.
  Invisible here (subtree is small), so left as plain recursion.
- Sidebar material only; the shipped shape follows the repo's
  correctness-and-clarity-first policy.
