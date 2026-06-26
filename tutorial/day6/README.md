# Tutorial Day 6: Search and State Modeling

## Why this day matters
A huge fraction of AoC is "get from a start state to a goal state, one legal move
at a time": walk a grid, follow a graph of rules, explore a maze, chain bag-in-bag
containment. Prolog is unusually good at this because **search is the language's
native control flow** — you don't write an explicit stack or queue, you write the
*rules of a legal move* and let backtracking enumerate the reachable states for
you. The whole day is one small graph and one predicate, `path/3`, but it contains
the entire pattern: model states and moves as facts/rules, recurse along moves,
and carry a **visited set** so a cyclic graph can't trap you in an infinite loop.
That visited set is a Day 5 accumulator wearing a different hat — the habit
transfers directly.

## Focus Topics
- **Modeling state as data**: nodes and moves as `edge/2` facts
- **Depth-first search via backtracking** — recursion *is* the search
- **The visited set** as an accumulator that keeps search finite on cycles
- **`\+ member(...)`** (negation as failure) as the "don't revisit" guard
- **Build-reversed-then-`reverse`** to report the path in travel order
- Forcing **determinism** at the call site with `once/1` when you want *a* path,
  not *all* paths

## Learning Goals
- Read `path/3` and narrate the DFS it performs, step by step.
- Explain precisely why the visited set prevents infinite recursion on the cycle.
- State why the path is accumulated *backwards* and reversed at the end.
- Choose between "find one path" (`once/1`) and "find all paths" (backtracking).

## Files
- `day6.pl`: a 6-edge directed graph plus `path/3`, a cycle-safe DFS.
- `day6_tests.pl`: `plunit` tests pinning one reachable path and one dead end.

```prolog
:- module(day6, [edge/2, path/3]).
```

## Run the tests
From repo root:

```bash
swipl -q -s tutorial/day6/day6_tests.pl
```

## Start the REPL

```bash
swipl
```
```prolog
?- ['tutorial/day6/day6.pl'].
```

## First, the model: the graph is just facts

```prolog
edge(a, b).
edge(b, c).
edge(c, d).
edge(a, e).
edge(e, d).
edge(c, a). % cycle
```

There is no graph *object* here — the relation `edge/2` **is** the graph. Each
fact is one directed move "you may step from X to Y." Drawn out:

```text
        a ──▶ b ──▶ c ──▶ d
        │           │     ▲
        │           ▼     │
        └────▶ e ───┴─────┘     (e ──▶ d)

   c ──▶ a   is a back-edge: a ▶ b ▶ c ▶ a forms a cycle
```

Two things to notice. `d` has **no outgoing edge** — it's a *sink* (dead end).
And `c ──▶ a` closes a **cycle** `a → b → c → a`. A naive walker that just follows
edges would loop around that cycle forever. Keeping search finite in the presence
of that cycle is the entire job of the visited set below.

> **Why facts and not an adjacency list?** Because `edge/2` is a *queryable
> relation*. `edge(a, X)` enumerates a's neighbors on backtracking; `edge(X, d)`
> enumerates d's predecessors. The same data is indexed both ways for free. In a
> real AoC solution you'd usually `assertz/1` these facts from the parsed input (or
> pass an `assoc` — Day 8), but the access pattern is identical.

## The search: `path/3` and its accumulator helper

```prolog
path(Start, Goal, Path) :-
    path_(Start, Goal, [Start], Rev),
    reverse(Rev, Path).

path_(Goal, Goal, Visited, Visited).
path_(Node, Goal, Visited, Path) :-
    edge(Node, Next),
    \+ member(Next, Visited),
    path_(Next, Goal, [Next|Visited], Path).
```

This is the **same public/helper split** from Day 5. The wrapper `path/3` seeds
the accumulator — here the visited set, seeded with `[Start]` because you start
*already standing on* `Start` — and reverses the result at the end. The worker
`path_/4` does the recursion. Read its two clauses as **base case** and
**recursive move**:

- **`path_(Goal, Goal, Visited, Visited).`** — When the current node *is* the goal
  (both head arguments unify to the same term), we're done. The accumulated
  `Visited` list *is* the path (reversed); hand it straight back through the 4th
  argument. This is exactly Day 5's `..._([], Acc, Acc)` base case — "the finished
  accumulator is the answer."

- **The recursive clause makes one legal move:**
  1. `edge(Node, Next)` — pick a neighbor `Next`. On backtracking this tries
     *every* neighbor, which is what makes the search exhaustive.
  2. `\+ member(Next, Visited)` — **only if we haven't already been there.** This
     is the cycle guard. `\+` is *negation as failure*: it succeeds exactly when
     `member(Next, Visited)` fails, i.e. `Next` is new.
  3. `path_(Next, Goal, [Next|Visited], Path)` — step to `Next`, **prepending** it
     to the visited set (O(1), Day 5), and recurse. This is the last goal — a tail
     call.

## Trace it: depth-first, with backtracking

Ask for a path from `a` to `d`:

```text
path(a, d, P)
  path_(a, d, [a], Rev)
    edge(a, b)        b ∉ [a] ✓
    path_(b, d, [b,a], Rev)
      edge(b, c)      c ∉ [b,a] ✓
      path_(c, d, [c,b,a], Rev)
        edge(c, d)    d ∉ [c,b,a] ✓
        path_(d, d, [d,c,b,a], Rev)   <- base case: Goal=Goal, Rev = [d,c,b,a]
  reverse([d,c,b,a], P)  ->  P = [a,b,c,d]
```

The search dives **depth-first**: it commits to `a→b→c→d` all the way down before
considering any alternative. The path comes back **reversed** (`[d,c,b,a]`) because
each move prepends to the front of the accumulator — newest node first, exactly
like Day 5's `reverse_acc`. The wrapper's `reverse/2` flips it into travel order
`[a,b,c,d]`.

Now watch the **cycle guard earn its keep**. Back at node `c`, after `d`, Prolog
backtracks and tries the *other* edge out of `c`:

```text
      edge(c, a)      a ∈ [c,b,a]  ✗  -- \+ member fails, this move is pruned
```

`c ──▶ a` would re-enter the cycle, but `a` is already in `Visited`, so
`\+ member(a, Visited)` **fails** and that branch is abandoned. Without that one
line the search would loop `a→b→c→a→b→c→…` forever. *With* it, every node can
appear at most once on the current path, so the recursion depth is bounded by the
number of nodes — search **terminates**.

Because `edge/2` and the two clauses leave choicepoints open, `path/3` will, on
backtracking, also find the **second** path:

```prolog
?- path(a, d, P).
P = [a, b, c, d] ;
P = [a, e, d].
```

## Why `path(d, a, _)` fails — and what the test really checks

```prolog
?- path(d, a, P).
false.
```

`d` is a sink: there is no `edge(d, _)` fact at all. So in `path_(d, a, ...)` the
base clause needs `d = a` (false) and the recursive clause's first goal
`edge(d, Next)` finds no neighbor — both clauses fail, the query fails. The test
named `path_cycle_safe` asserts this `fail`. Read it honestly: it confirms `a` is
**unreachable from `d`** (the edges are directed and `d` is terminal). It's not a
direct demonstration of cycle-breaking — but it *is* the same machinery
(directedness + bounded search) that makes the cyclic graph safe, and it proves the
predicate **fails cleanly** instead of looping or erroring when no path exists.

## The Tests, One by One

```prolog
:- begin_tests(day6).
:- use_module('./day6.pl').

test(path_exists) :-
    once(path(a, d, P)),
    assertion(memberchk(P, [[a,b,c,d], [a,e,d]])).

test(path_cycle_safe, [fail]) :-
    path(d, a, _).

:- end_tests(day6).
```

| Test | What it pins down |
|---|---|
| `path_exists` | A path from `a` to `d` is found, and it's *one of the two* legal ones. `once/1` takes the **first** solution; `memberchk/2` accepts either `[a,b,c,d]` or `[a,e,d]` so the test doesn't over-specify DFS's search order. |
| `path_cycle_safe` (`[fail]`) | `path(d, a, _)` must **fail**, not loop and not error. The `[fail]` option *expects* the goal to fail — that's the test passing. Proof that an unreachable goal terminates. |

Two idioms worth lifting straight into AoC solutions:

- **`once/1`** wraps a goal and keeps only its first solution, discarding the
  choicepoints. Use it when *a* path/answer is wanted, not the whole enumeration —
  it also makes the call deterministic (Day 3).
- **`memberchk/2`** is `member/2` committed to its first match — a deterministic
  "is X in this list?" check. Using it in the assertion keeps the test robust to
  whichever valid path DFS returns first.

## REPL Drills

```prolog
?- edge(a, X).                       % X = b ; X = e   -- enumerate a's neighbors
?- edge(X, d).                       % X = c ; X = e   -- enumerate d's predecessors
?- path(a, d, P).                    % P = [a,b,c,d] ; P = [a,e,d]  -- all paths, backtracking
?- once(path(a, d, P)).              % P = [a,b,c,d]   -- just the first
?- findall(P, path(a, d, P), Ps).    % Ps = [[a,b,c,d],[a,e,d]]  -- collect them all
?- path(d, a, P).                    % false           -- unreachable, fails cleanly
?- aggregate_all(count, path(a, d, _), N).  % N = 2     -- count distinct paths
```

`findall/3` and `aggregate_all/3` are how you turn Prolog's "one solution at a
time" search into the *set* or *count* that an AoC part usually asks for. The
backtracking engine enumerates; these collect.

## Verification (maps to the checklist)
- **Reachable goal:** `path(a, d, P)` yields a valid path; `findall/3` shows
  exactly two and no duplicates.
- **Cyclic safety:** despite `c ──▶ a` closing a loop, every query **terminates** —
  the visited set bounds depth to the node count.
- **Unreachable goal:** `path(d, a, _)` fails cleanly (sink node, no outgoing
  edges) rather than looping or throwing.
- **Trivial path:** `path(a, a, P)` gives `P = [a]` — the base case fires
  immediately, the seeded `[Start]` is the whole answer.

## Common Gotchas
- **Forgetting the visited guard turns a cycle into an infinite loop.** `\+ member(Next, Visited)`
  is not optional decoration — drop it and `path(a, d, P)` will, on backtracking,
  wander `a→b→c→a→…` until the stack blows. The guard is the difference between a
  search and a hang.
- **Seed the visited set with `[Start]`, not `[]`.** You begin *standing on* the
  start node, so it's already visited. Seeding `[]` would let a self-loop or a
  back-edge revisit the start.
- **The path comes out reversed.** Because moves prepend, the accumulator is
  newest-first. If you forget the wrapper's `reverse/2`, you get `[d,c,b,a]`. (Same
  prepend-then-reverse lesson as Day 5.)
- **`\+` is *negation as failure*, not logical negation.** It means "I couldn't
  prove this," which is only sound when its argument is **ground** (fully bound) at
  call time. Here `Next` is bound by `edge/2` before `\+ member(...)` runs — order
  matters. Swap those two goals and the negation would see an unbound `Next` and
  misbehave.
- **`member/2` makes the visited check O(n).** Fine for a tiny graph; on a big AoC
  grid you'd switch the visited set to an `assoc` or a sorted set for O(log n)
  lookup (Day 8). The *algorithm* is identical — only the set's data structure
  changes.
- **DFS finds *a* path, not the *shortest*.** `path/3` returns whatever the
  depth-first order reaches first. For shortest-path you need BFS (a queue) or a
  cost-aware search (Dijkstra/A*) — same state-modeling, different frontier
  strategy.

## The AoC Payoff: this is the skeleton for every traversal day

Grid walks, maze solving, rule-graph reachability, "how many bags eventually
contain a gold bag" — they're all `path/3` with the nouns swapped. The recipe:

```prolog
% 1. Model a state and a legal move.
move(State, Next) :- ...        % e.g. step to an in-bounds, non-wall neighbor cell

% 2. Search with a visited set, exactly like path_/4.
reach(Goal, Goal, _Visited).
reach(State, Goal, Visited) :-
    move(State, Next),
    \+ member(Next, Visited),
    reach(Next, Goal, [Next|Visited]).

% 3. Collect or count with findall/3 or aggregate_all/3.
```

For a 2-D grid, a "state" is a coordinate `R-C`, and `move/2` is "the four
orthogonal neighbors that are in bounds and not walls." Swap `member/2` for an
`assoc`-backed set when the grid is big, swap DFS for a BFS queue when you need the
*shortest* path, and the spine you learned today carries straight through.

## Rust bridge

The Prolog version hides the stack and the backtracking; in Rust you write them
out. An explicit recursive DFS with a `Vec` visited/path is the literal
translation:

```rust
use std::collections::HashMap;

fn path(
    node: char,
    goal: char,
    edges: &HashMap<char, Vec<char>>,
    visited: &mut Vec<char>,        // doubles as the path, in order
) -> bool {
    if node == goal {
        return true;                // base case: path_(Goal, Goal, V, V)
    }
    for &next in edges.get(&node).into_iter().flatten() {
        if !visited.contains(&next) {     // \+ member(Next, Visited)
            visited.push(next);           // [Next | Visited]
            if path(next, goal, edges, visited) {
                return true;
            }
            visited.pop();                // undo on backtrack — Prolog does this for free
        }
    }
    false                            // no move worked: the goal fails
}
```

Three things the bridge makes vivid. (1) Prolog's `edge(Node, Next)` enumerating
neighbors **is** the `for` loop. (2) The `visited.pop()` after a failed branch is
*manual backtracking* — Prolog's engine unwinds bindings automatically, so there's
no `pop` in the Prolog source; that's the single biggest ergonomic win. (3) To get
*all* paths in Rust you'd thread a `results: &mut Vec<Vec<char>>` and never
early-return; in Prolog you just drop `once/1` and let backtracking enumerate, or
wrap it in `findall/3`. Same DFS, but Prolog gives you the search engine for free.

## Exit Criteria
- You can read `path/3` and narrate the depth-first search it performs.
- You can point at `\+ member(Next, Visited)` and explain why it makes a cyclic
  graph safe and bounds the recursion depth.
- You can say why the visited set is seeded with `[Start]` and why the result is
  reversed.
- You can choose `once/1` (one path), backtracking (all paths), or `findall/3`
  (collect them) deliberately.
- You can describe how to retarget this skeleton to a 2-D grid walk.

## Next Step
Day 7 swaps *explicit* search for **declarative constraints** with
`library(clpfd)`:
- state the *relationships* (`X + Y #= 10`, domains via `ins`) and let the solver
  search
- the crucial distinction between `is/2` (evaluate now) and `#=/2` (constrain)
- `labeling/2` to extract concrete solutions — search you *describe* instead of
  *drive*
