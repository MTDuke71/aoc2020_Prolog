# Tutorial Day 8: Maps and Lookup Structures

## Why this day matters
So far your lookups have been **linear**: `member/2` walks a list front to back, O(n)
every time. That's fine for a handful of elements and a disaster the moment a puzzle
asks "how many times did each value appear?" or "what's the count for *this* key?"
over thousands of items — you'd be scanning the whole list once per query. Today
introduces **key-value maps**: data structures that find, insert, and update a key in
**O(log n)** instead of O(n). Prolog gives you two flavors. `library(assoc)` is the
portable, standard one — a balanced binary tree you thread through your computation.
SWI **dicts** are a newer, ergonomic record/JSON-style structure with `.key` access.
The canonical use both serve is the **frequency table** — tally how often each thing
occurs — which is the single most common aggregation in all of AoC. Build it once by
hand and every "count the things" puzzle becomes a three-line fold.

## Focus Topics
- **`library(assoc)`** — balanced-tree maps: `empty_assoc/1`, `get_assoc/3`,
  `put_assoc/4` (load the library before any of them work)
- **Persistence / immutability** — `put_assoc/4` returns a **new** map; you *thread*
  it, you don't mutate it (the accumulator pattern from Day 5, applied to a map)
- **SWI dicts** — `_{}` empty dict, `get_dict/3`, the `.put/2` functional update, and
  `Dict.key` dot access
- **The get-or-default idiom** — `( get_assoc(K,M,V) -> ... ; Default )` for "look up,
  or start fresh"
- **Building a frequency table** from a list of tokens — the bread-and-butter tally
- assoc vs dict: when to pick which

## Learning Goals
- Build a frequency table two ways — with an assoc and with a dict — and read the
  counts back out.
- Explain why `put_assoc/4` takes the old map and *returns* a new one (no mutation).
- State the get-or-default idiom and why it's needed for "first time I've seen this
  key."
- Compare assoc and dict on portability, ergonomics, and key restrictions.

## Files
- `day8.pl`: `freq_assoc/2` (frequency table via `library(assoc)`) and `freq_dict/2`
  (the same table via a dict), each with a private accumulator helper.
- `day8_tests.pl`: `plunit` tests reading counts back out of both structures.

```prolog
:- module(day8, [freq_assoc/2, freq_dict/2]).
:- use_module(library(assoc)).
```

## Run the tests
From repo root:

```bash
swipl -q -s tutorial/day8/day8_tests.pl
```

## Start the REPL

```bash
swipl
```
```prolog
?- ['tutorial/day8/day8.pl'].
```

## The whole program

```prolog
freq_assoc(List, AssocOut) :-
    empty_assoc(A0),
    freq_assoc_(List, A0, AssocOut).

freq_assoc_([], A, A).
freq_assoc_([X|Xs], A0, AOut) :-
    ( get_assoc(X, A0, N0) -> N1 is N0 + 1 ; N1 = 1 ),
    put_assoc(X, A0, N1, A1),
    freq_assoc_(Xs, A1, AOut).

freq_dict(List, Dict) :-
    freq_dict_(List, _{}, Dict).

freq_dict_([], D, D).
freq_dict_([X|Xs], D0, DOut) :-
    ( get_dict(X, D0, N0) -> N1 is N0 + 1 ; N1 = 1 ),
    D1 = D0.put(X, N1),
    freq_dict_(Xs, D1, DOut).
```

Two builders that compute the *exact same answer* — a count for every distinct element
— through two different map types. Reading them side by side is the whole lesson:
notice how structurally identical they are.

## The frequency-table pattern

Both builders are a **fold with an accumulator** (Day 5), where the accumulator is a
*map* instead of a number:

```prolog
freq_assoc(List, AssocOut) :-
    empty_assoc(A0),                    % start with an empty map...
    freq_assoc_(List, A0, AssocOut).    % ...and fold the list into it

freq_assoc_([], A, A).                  % list done: the map IS the answer
freq_assoc_([X|Xs], A0, AOut) :-
    ( get_assoc(X, A0, N0) -> N1 is N0 + 1 ; N1 = 1 ),   % look up, or default to 0+1
    put_assoc(X, A0, N1, A1),           % write the new count into a NEW map A1
    freq_assoc_(Xs, A1, AOut).          % recurse carrying A1 forward
```

Three moves per element, the universal tally recipe:

1. **Look up** the current count for `X` (`get_assoc/3`).
2. **Increment** it — or **default to 1** if this is the first sighting.
3. **Write** the new count back and **carry the updated map forward** to the next
   element.

The base case `freq_assoc_([], A, A)` says "when the list is exhausted, the
accumulated map is the result." `freq_dict_/3` is the byte-for-byte same shape with
dict operations swapped in — same fold, same get-or-default, same threading.

## The two ideas that trip people up

### 1. The get-or-default idiom

```prolog
( get_assoc(X, A0, N0) -> N1 is N0 + 1 ; N1 = 1 )
```

This `( Cond -> Then ; Else )` is an **if-then-else** (Day 3). It matters because
`get_assoc/3` **fails** (it does not throw) when the key is absent. So:

- **Key present** → `get_assoc` succeeds, binds `N0` to the old count, and we set
  `N1 = N0 + 1`.
- **Key absent** (first time we've seen `X`) → `get_assoc` fails, the `->` falls to the
  `;` branch, and we seed the count with `N1 = 1`.

Without the else-branch, the *very first* occurrence of every key would fail the whole
predicate. "Look up, or start fresh" is the heartbeat of every map-building loop.

### 2. Maps are persistent — you thread, you don't mutate

This is the deep Prolog point. `put_assoc(X, A0, N1, A1)` does **not** modify `A0`. It
*constructs a new map* `A1` that is `A0` plus the binding `X→N1`, and leaves `A0`
untouched. That's why the predicate has **two map arguments** (`A0` in, `A1` out) and
why the recursion **carries `A1` forward**:

```prolog
    put_assoc(X, A0, N1, A1),      % A1 is the OLD map + one change; A0 still exists
    freq_assoc_(Xs, A1, AOut).     % pass the NEW map to the next step
```

If you wrote `put_assoc(X, A0, N1, A0)` it would simply fail (you can't unify the old
map with a different new one). Prolog data is **immutable**; "updating" a structure
means *deriving a new one and threading it through* — exactly the accumulator
discipline from Day 5, now over a tree instead of a list or counter. (Dicts behave the
same way: `D1 = D0.put(X, N1)` builds a new dict `D1`; `D0` is unchanged.)

## assoc vs dict, side by side

| | `library(assoc)` | SWI dict |
|---|---|---|
| **Portability** | ISO-ish, works across Prologs | **SWI-specific** |
| **Under the hood** | balanced **AVL tree**, keyed by **standard order of terms** | hash-like, tagged |
| **Empty value** | `empty_assoc(A)` | `_{}` (literal) |
| **Read** | `get_assoc(K, M, V)` — **fails** if absent | `get_dict(K, D, V)` fails if absent; `D.K` **throws** if absent |
| **Write** | `put_assoc(K, M0, V, M1)` (4 args, threaded) | `D1 = D0.put(K, V)` (functional) |
| **Allowed keys** | **any term** | **only atoms or small integers** |
| **Best for** | arbitrary/compound keys, portable code, large dynamic maps | record-style data with known atom keys, readable `.field` access |

The standout practical difference: **dict keys must be atoms or small integers** — you
cannot key a dict on a compound like `point(3,4)`, but an assoc handles it fine
(grids-as-coordinate-maps is exactly that case). Conversely, dicts read beautifully
when keys are known field names. The fact that assoc orders keys by **standard order of
terms** (the same total order Day 9 sorts by) is why `assoc_to_keys/2` hands them back
sorted for free.

## Trace: `freq_assoc([a,b,a,c,a], A)`

```text
start          empty
X=a  get fails -> N1=1   put a->1   {a:1}
X=b  get fails -> N1=1   put b->1   {a:1, b:1}
X=a  get a=1   -> N1=2   put a->2   {a:2, b:1}
X=c  get fails -> N1=1   put c->1   {a:2, b:1, c:1}
X=a  get a=2   -> N1=3   put a->3   {a:3, b:1, c:1}
[]             -> result  {a:3, b:1, c:1}
```

Three `a`s, one `b`, one `c`. The first test reads `get_assoc(a, A, 3)` and
`get_assoc(b, A, 1)` back out of exactly this map.

## The Tests, One by One

```prolog
:- begin_tests(day8).
:- use_module('./day8.pl').
:- use_module(library(assoc)).

test(freq_assoc) :-
    freq_assoc([a,b,a,c,a], A),
    get_assoc(a, A, Na),
    get_assoc(b, A, Nb),
    assertion(Na == 3),
    assertion(Nb == 1).

test(freq_dict) :-
    freq_dict([x,y,x], D),
    assertion(D.x == 2),
    assertion(D.y == 1).

:- end_tests(day8).
```

| Test | What it pins down |
|---|---|
| `freq_assoc` | Build the table, then **read it back with `get_assoc/3`**: `a` counted 3 times, `b` once. Note the test must itself `use_module(library(assoc))` to call `get_assoc/3`. |
| `freq_dict` | The dict builder gives the same kind of result, read with **dot access** `D.x == 2`, `D.y == 1`. The `.x` syntax is the dict's signature ergonomic win. |

Both use `==/2` (structural identity on bound integers), the right check for "is this
exactly the count I expect?".

## REPL Drills

```prolog
?- empty_assoc(A0), put_assoc(a, A0, 1, A1), get_assoc(a, A1, V).   % V = 1
?- empty_assoc(A0), get_assoc(missing, A0, V).                      % FAILS (no throw)
?- freq_assoc([a,b,a,c,a], A), get_assoc(a, A, N).                  % N = 3
?- freq_assoc([a,b,a], A), assoc_to_list(A, Pairs).                 % Pairs = [a-2, b-1]
?- freq_assoc([a,b,a], A), assoc_to_keys(A, Ks).                    % Ks = [a, b]  (sorted)
?- D0 = _{}, D = D0.put(foo, 42), V = D.foo.                        % V = 42
?- freq_dict([x,y,x], D), V = D.x.                                  % V = 2
?- D = _{a:1}, ( get_dict(missing, D, V) -> true ; writeln(absent) ). % absent (get_dict fails)
?- list_to_assoc([a-1, b-2], A), get_assoc(b, A, V).               % V = 2  (bulk build)
```

The drills worth feeling: `get_assoc` on a missing key **fails** (drill 2) — pair that
with the get-or-default idiom and it clicks. And `assoc_to_keys/2` returns keys in
**sorted** order (drill 5), the free consequence of the AVL tree's standard-order
keying — a direct bridge to Day 9.

## The assoc & dict toolbox (reference)

| Operation | `library(assoc)` | dict |
|---|---|---|
| empty | `empty_assoc(-A)` | `_{}` |
| insert/update | `put_assoc(+K, +A0, +V, -A1)` | `D1 = D0.put(K, V)` |
| lookup | `get_assoc(+K, +A, -V)` (fails if absent) | `get_dict(K, D, V)` / `D.K` |
| bulk build | `list_to_assoc(+Pairs, -A)` | `dict_pairs(D, Tag, Pairs)` |
| to list | `assoc_to_list(+A, -Pairs)` (sorted) | `dict_pairs(D, _, Pairs)` |
| just keys / values | `assoc_to_keys/2`, `assoc_to_values/2` | `dict_keys/2`, `D.Key` |

For one-shot counting you'll also meet `aggregate_all(count, ...)` (Day 9), but a map
is what you want whenever you need the counts **kept around** for later lookup, or
you're updating incrementally as you stream input.

## Verification (maps to the checklist)
- **Repeated-key increment:** `freq_assoc([a,b,a,c,a], A)` gives `a→3` — the same key
  seen three times accumulates, not overwrites.
- **Missing-key default:** the first sighting of any key produces count `1` via the
  else-branch; `get_assoc` on a never-seen key **fails** rather than throwing.
- **Both structures agree:** assoc and dict builders produce the same logical table;
  the tests read it back through each structure's native accessor.
- **Persistence:** intermediate maps are independent — `put_assoc` never mutates its
  input, so threading is mandatory.

## Common Gotchas
- **Forgetting `:- use_module(library(assoc)).`** Without it, `empty_assoc`,
  `get_assoc`, and `put_assoc` are undefined. It's the second line of `day8.pl` — and
  the *test* file needs its own copy to call `get_assoc/3`.
- **Expecting `put_assoc` to mutate.** It returns a **new** map in its 4th argument;
  the old one is unchanged. You must capture and thread the result — `put_assoc(K, A0,
  V, A1)` then use `A1`. This is the #1 "my map is empty / unchanged" bug.
- **Assuming `get_assoc` throws on a missing key.** It **fails**. That's *why* the
  get-or-default `( ... -> ... ; ... )` works — but it also means a bare
  `get_assoc(K, M, V)` in the wrong place silently fails your clause instead of erroring.
- **Dict keys that aren't atoms/small ints.** `_{}.put(point(3,4), 1)` is illegal —
  dict keys must be atoms or small integers. Need compound keys (grid coordinates)? Use
  an **assoc**, which keys on any term.
- **`D.key` vs `get_dict/3` on a missing key.** Dot access `D.missing` **throws**;
  `get_dict(missing, D, V)` **fails** (usable in a condition). Pick `get_dict/3` when
  absence is normal and you want to branch on it.
- **Not threading the dict either.** `D0.put(X, N1)` returns a new dict — you must bind
  it (`D1 = D0.put(X, N1)`) and pass `D1` on, exactly like the assoc.

## The AoC Payoff: maps are everywhere

Three recurring AoC shapes are all this same map:

```prolog
% 1. Frequency / histogram: how many of each? (you just built it)
%    answer "most common" by reading counts back out.

% 2. Sparse grid as a coordinate map (assoc, because keys are compounds):
set_cell(P, V, G0, G1) :- put_assoc(P, G0, V, G1).      % P = X-Y or point(X,Y)
cell(P, G, V) :- ( get_assoc(P, G, V) -> true ; V = '.' ). % default for unset cells

% 3. Seen-set / visited map for search (Day 6), O(log n) membership:
mark_seen(N, S0, S1) :- put_assoc(N, S0, true, S1).
seen(N, S) :- get_assoc(N, S, _).
```

The grid case is why assoc earns its keep: a 2020 puzzle with a huge but *sparse* grid
is far better as a `point(X,Y)→value` map than a list of lists, and the compound-key
freedom is exactly what dicts can't give you. The seen-set replaces the O(n) `member/2`
guard you used in Day 6's search with an O(log n) lookup. The judgment call: **dict**
for record-shaped data with known atom fields and readable `.field` access; **assoc**
for arbitrary/compound keys, portability, or big dynamic maps.

## Rust bridge

This is the most direct Rust mapping of any tutorial day — `library(assoc)` is a
`BTreeMap` (ordered, tree-backed) and a dict is closest to a `HashMap`:

```rust
use std::collections::HashMap;

// freq_assoc / freq_dict  ->  the classic entry-API tally
fn frequencies(items: &[char]) -> HashMap<char, u32> {
    let mut counts = HashMap::new();
    for &x in items {
        *counts.entry(x).or_insert(0) += 1;   // get-or-default, then increment
    }
    counts                                    // {'a':3, 'b':1, 'c':1}
}
```

`entry(x).or_insert(0)` **is** the get-or-default idiom: "give me the slot for `x`,
creating it as `0` if absent," then `+= 1`. One line in Rust because the map is
*mutable in place*; in Prolog the same logic splits into look-up, default, write-new,
thread-forward because the map is **immutable** — that threading is the only real
difference. Swap `HashMap` for `BTreeMap` and you get `library(assoc)`'s sorted-key
behavior (`assoc_to_keys/2` ↔ iterating a `BTreeMap`). Same data structure, same tally
pattern; Prolog just makes the "new map each step" explicit instead of hiding it behind
mutation.

## Exit Criteria
- You can build a frequency table with both `library(assoc)` and a dict, and read the
  counts back with `get_assoc/3` and `.key`.
- You can explain why `put_assoc/4` returns a new map and why you must thread it.
- You can state the get-or-default idiom and why `get_assoc/3` *failing* on a missing
  key is what makes it work.
- You can choose assoc vs dict for a given task, and name the key-type restriction that
  often forces the choice.

## Next Step
Day 9 turns these tallies into **ordered aggregates** with **sorting, grouping, and
counting**:
- `sort/2` (drops duplicates) vs `msort/2` (keeps them) — the distinction that makes or
  breaks a count
- **run-length encoding**: sort, then pack equal neighbors into `(Value, Count)` pairs —
  the same histogram you built today, arrived at by sorting instead of a map
- choosing between a hand-rolled group-and-count, `sort/4`, and `aggregate_all/3`
