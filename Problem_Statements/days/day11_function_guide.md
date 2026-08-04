# Day 11 Function Guide — Seating System

> The first **cellular automaton** of the year, and the first day where
> the naive representation is fast enough to look fine on the example and
> hopeless on the real input. Both parts run the *same* simulation — empty
> seat with no occupied neighbours fills, occupied seat with `Tolerance`
> or more occupied neighbours empties, repeat until a round changes
> nothing. They differ in exactly two constants: **what counts as a
> neighbour** (the 8 touching squares vs. the first seat visible along
> each of the 8 rays) and **the tolerance** (4 vs. 5). So the day's real
> content is a **representation** decision: stop thinking of the grid as a
> grid. Number the seats `1..N`, precompute each seat's neighbour list
> once, and the automaton becomes a flat array of bits with a static
> adjacency table — no coordinates, no bounds checks, no floor, and no
> ray-walking inside the hot loop. In Prolog that array is a **compound
> term** indexed with `arg/3`, which is the single most transferable trick
> in this guide. Grid parsing is [Day 3](day03_function_guide.md)'s
> list-of-char-lists reused verbatim; the "precompute a table, then run a
> cheap loop over it" shape is [Day 7](day07_function_guide.md)'s reversed
> edge index seen again.

## The puzzle in one paragraph

The input is a 99 × 92 seat map: floor (`.`), empty seat (`L`), occupied
seat (`#`). Every round, **all seats update simultaneously** from the
previous round's state: an empty seat with zero occupied neighbours
becomes occupied; an occupied seat with at least `Tolerance` occupied
neighbours becomes empty; everything else holds. Floor never changes.
Run to stabilisation and count the occupied seats. **Part 1:** neighbours
are the eight adjacent squares, tolerance 4 (example → `37`). **Part 2:**
neighbours are the first seat *visible* along each of the eight rays, no
matter how much floor intervenes, tolerance 5 (example → `26`).

Real input: 9,108 squares, of which **7,423 are seats**. Part 1 settles
after **86 rounds** with **2321** occupied; part 2 after **87 rounds**
with **2102**.

---

## Representation: seats are a numbered array, not a grid

This is the whole day. Write down the obvious representation first, so
the cost is visible:

> *A grid is a list of rows, each a list of chars. To find a seat's
> neighbours, look at the eight surrounding coordinates.*

Under that model, one neighbour lookup is `nth0(R, Grid, Row),
nth0(C, Row, Cell)` — **O(rows + cols)**, because a Prolog list is a
linked list and `nth0/3` walks it. One round is 7,423 seats × 8
neighbours × ~190 cells of walking ≈ **11 million cons-cell steps**, and
there are 86 rounds. That is the version that finishes the example
instantly and then appears to hang on the real input. Part 2 is worse
still: each ray re-walks the grid from scratch, every round.

Three observations collapse it:

1. **Floor is not state.** A `.` never changes and never counts toward
   anybody's total. It exists only to be *skipped*. Drop it and 9,108
   squares become 7,423.
2. **Neighbours never change.** The seat map is static — only occupancy
   moves. Whatever "neighbour" means, seat *i*'s neighbour list is the
   same in round 1 and round 86. Compute it once.
3. **Once neighbours are precomputed, coordinates are dead.** Nothing in
   the update rule needs to know *where* a seat is, only which other
   seats it watches. So seats can be renumbered `1..N` and the geometry
   thrown away.

What survives is:

```prolog
% Layout: the static geometry, used only while building tables.
layout(Rows, Cols, Coords, Index)     % Coords: seat i's R-C, row-major
                                      % Index : assoc R-C -> i

% Neighbour table: nbrs(L1, ..., LN), Li = ids seat i watches.
% State:           occ(V1, ..., VN),  Vi in 0..1.
```

**Why a compound term and not a list.** The state is read at random —
seat 4,000 needs its neighbour's bit, which might be seat 12. `arg/3` on
a compound term is **O(1)**: SWI lays a term out as a functor header
followed by contiguous argument words, so `arg(I, T, X)` is pointer
arithmetic, the same machine operation as `v[i]` in C. `nth1/3` on a list
is **O(i)**. Same interface, different asymptotics, and here it is the
difference between a second and several minutes. SWI's `max_arity` flag
is `unbounded`, so a 7,423-argument term is legal and unremarkable.

**Why not an assoc.** [Day 7](day07_function_guide.md) and
[Day 8](day08_function_guide.md) both reached for `library(assoc)` (an
AVL tree) for their index. It would work here too, at **O(log N)** per
lookup — about 13 comparisons per read instead of one pointer add. With
~7,400 seats × ~7 neighbours × 86 rounds ≈ 4.5 million reads per part,
that is a ~13× multiplier on the innermost operation. An assoc is right
when keys are sparse, structured, or unknown up front (`R-C` pairs while
*building* the tables — which is exactly where this code still uses one).
Dense integer keys `1..N` want an array.

**Why the state is bits, not chars.** Once floor is gone, a seat has two
states, so `0`/`1` beats `'L'`/`'#'`: counting occupied neighbours
becomes `Acc1 is Acc0 + Value` rather than a comparison per neighbour,
and the final tally is one `sum_list/2`.

---

## Reading Prolog: the five forms this day turns on

**1. `Term =.. List` — "univ", the term/list bridge.** The one piece of
syntax people forget between Prolog sessions. It relates a compound term
to the list of its functor and arguments, in either direction:

```prolog
?- occ(1,0,1) =.. L.
L = [occ, 1, 0, 1].

?- T =.. [occ, 1, 0, 1].
T = occ(1, 0, 1).
```

This day uses both directions for the same reason: **lists are the
natural thing to *build*, terms are the natural thing to *read*.**
`maplist/3` produces a list of new cell values, univ freezes it into an
array; `occupied_count/2` thaws the array back into a list so `sum_list/2`
can total it. Think of `=..` as the cast between "sequence I'm
constructing" and "array I'm indexing."

**2. `functor/3` and `arg/3` — the rest of the array API.**

```prolog
functor(Table, Name, N)     % N is the arity: how many seats
arg(I, State, Value)        % Value is the I-th argument, 1-based, O(1)
```

`functor/3` here recovers `N` from the table rather than threading a
separate seat count through every predicate — the table *is* the source
of truth about how many seats exist. `arg/3` is 1-based, matching
`nth1/3` and the `1..N` ids, so there is no off-by-one anywhere in the
file. (Contrast the Python reference, which is 0-based throughout; both
are internally consistent, which is what matters.)

**3. `findall/3` over a generator, as a comprehension.** Two different
jobs in this file, both worth recognising:

```prolog
findall(R-C, seat_at(Grid, R, C), Coords).
```

`seat_at/3` is written to be **nondeterministic on purpose**:

```prolog
seat_at(Grid, R, C) :-
    nth1(R, Grid, Row),
    nth1(C, Row, Cell),
    Cell \== '.'.
```

Called with `R` and `C` unbound, `nth1/3` *enumerates* — it yields row 1,
then row 2, and so on, with the column loop nested inside. So this is a
double `for` loop with a filter, written as a relation, and `findall/3`
collects the results in generation order. That ordering is load-bearing:
it is what makes the ids row-major and the `Coords` list agree with them
positionally. The other job:

```prolog
findall(Seat,
        ( direction(DR, DC),
          R1 is R + DR, C1 is C + DC,
          get_assoc(R1-C1, Index, Seat)
        ),
        Seats).
```

`direction/2` is eight facts, so the goal backtracks through eight
directions; `get_assoc/3` **fails** for a coordinate that is off-grid or
is floor, and a failed branch contributes nothing. So "keep the
directions that land on a seat" needs no filtering step and no bounds
check — failure *is* the filter. This is the idiom that
[Day 4](day04_function_guide.md)'s validation table leans on, used for
collection instead of checking.

**4. Building a fresh term per round = simultaneous update.** The
statement says the rules "are applied to every seat simultaneously," and
that is a real constraint, not flavour text: if seat 5 could see seat
4's *new* value, the automaton would be a different one (a Gauss–Seidel
sweep instead of a Jacobi one, in numerical-methods terms) and would give
wrong answers. Immutability makes this free:

```prolog
next_state(Table, Tolerance, Ids, State0, State) :-
    maplist(next_seat(Table, Tolerance, State0), Ids, Cells),
    State =.. [occ|Cells].
```

Every `next_seat/5` call reads `State0` and writes into a brand-new
`State`. There is no way to express the bug. In a mutable language this
is the double-buffer you have to remember to write; here, forgetting is
not an option. (The flip side is allocation: a fresh 7,423-argument term
every round, 86 times. See the optimization sidebar.)

**5. Partial application under `maplist/3`.** Note the shape of

```prolog
maplist(next_seat(Table, Tolerance, State0), Ids, Cells)
```

`next_seat/5` is called with three arguments pre-supplied; `maplist/3`
appends the two it varies (`I` from `Ids`, `Cell` into `Cells`). This is
currying by argument order, and it dictates predicate signatures across
this repo: **fixed context first, varying data last.** Every predicate in
this file that gets mapped over — `adjacent_seats/3`, `visible_seats/5`,
`next_seat/5` — is ordered for it. It is also why `seat_rule/4` takes
`Tolerance` in the middle rather than last.

---

## The Day 11 code, predicate by predicate

### `parse_input/2`

```prolog
parse_input(Raw, Grid) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(string_chars, Lines, Grid).
```

Unchanged from [Day 3](day03_function_guide.md): split on newlines, pad
characters stripped, drop the trailing empty line, each row to a list of
char atoms. Grid parsing has been identical every time it has come up, so
it is worth reading once and never again. The output is deliberately the
*raw* grid, not the layout — `part1/2` and `part2/2` receive what the
bench harness calls `Parsed`, and the layout is derived from it.

### `seat_layout/2`

```prolog
seat_layout(Grid, layout(Rows, Cols, Coords, Index)) :-
    length(Grid, Rows),
    Grid = [FirstRow|_],
    length(FirstRow, Cols),
    findall(R-C, seat_at(Grid, R, C), Coords),
    length(Coords, N),
    findall(I, between(1, N, I), Ids),
    pairs_keys_values(Pairs, Coords, Ids),
    list_to_assoc(Pairs, Index).
```

The floor-elimination and numbering step. `Coords` is the id → coordinate
map (position *i* holds seat *i*'s `R-C`); `Index` is the inverse,
coordinate → id, as an assoc. Both directions are needed *while building
tables* — the tables are indexed by id, but neighbour-finding is
geometric — and neither is needed afterwards.

Two small things:

- `findall(I, between(1, N, I), Ids)` rather than `numlist(1, N, Ids)`,
  because `numlist/3` **fails** when `N` is 0 while `between/3` simply
  yields nothing, so a seatless grid produces `[]` instead of failing the
  whole solve. The floor-only test pins that.
- `pairs_keys_values/3` builds `Coord-Id` pairs from two parallel lists
  in one call; it runs in any mode, which is why it reads as a
  declarative zip rather than a loop.

`list_to_assoc/2` requires distinct keys. Coordinates are distinct by
construction, so this is safe — and if it ever were not, the predicate
would throw rather than silently drop a seat.

### The neighbour tables — `adjacent_table/2` and `visible_table/2`

Both have the same two-line shape: map a per-seat neighbour-finder over
`Coords`, freeze the resulting list of lists into a term.

```prolog
adjacent_table(layout(_Rows, _Cols, Coords, Index), Table) :-
    maplist(adjacent_seats(Index), Coords, Lists),
    Table =.. [nbrs|Lists].
```

The **part 1** finder is one `findall/3` over `direction/2`, shown above:
step one square, look it up, keep it if it is a seat. Off-grid needs no
special handling because `get_assoc/3` fails on absent keys and there are
no seats outside the grid.

The **part 2** finder marches:

```prolog
first_seat(Rows, Cols, Index, R-C, DR, DC, Seat) :-
    R1 is R + DR,
    C1 is C + DC,
    between(1, Rows, R1),
    between(1, Cols, C1),
    (   get_assoc(R1-C1, Index, Found)
    ->  Seat = Found
    ;   first_seat(Rows, Cols, Index, R1-C1, DR, DC, Seat)
    ).
```

Here bounds *are* checked, and this is the one place they must be:
without them the recursion would walk off the grid forever, since "no
seat here" and "not on the grid" are both just a failed `get_assoc/3`.
`between(1, Rows, R1)` with `R1` **bound** is a test, not a generator —
the same predicate used in generate mode two predicates earlier. Reading
`between/3` correctly means checking whether its third argument is bound.

The if-then-else is a **committed choice**: the first seat found ends the
ray. Without it, `first_seat/7` would backtrack into the recursive branch
and offer the *second* seat along the ray as an alternative solution, and
the enclosing `findall/3` would happily collect every seat on the line.
That is the bug this day is most likely to hide, because it still gives
the right answer on the small vignettes where each ray holds at most one
seat.

### The simulation — `stable_occupancy/3`, `fixpoint/5`, `next_state/5`

```prolog
stable_occupancy(Table, Tolerance, Occupied) :-
    functor(Table, _, N),
    findall(I, between(1, N, I), Ids),
    length(Zeros, N),
    maplist(=(0), Zeros),
    State0 =.. [occ|Zeros],
    fixpoint(Table, Tolerance, Ids, State0, Final),
    occupied_count(Final, Occupied).
```

`length(Zeros, N), maplist(=(0), Zeros)` is the standard "list of N
copies" idiom: `length/2` with an unbound list and a bound length builds
`N` fresh variables, then `maplist(=(0), …)` binds them all. `Ids` is
built once here and threaded through every round rather than
reconstructed 86 times.

The initial state is all-empty because the puzzle's input is all-`L` —
worth noting that the code *assumes* this rather than reading the initial
occupancy out of the grid. Every AoC input is all-empty, but it is an
assumption, and it is the one thing in this file that would need changing
to run the automaton from an arbitrary start.

```prolog
fixpoint(Table, Tolerance, Ids, State0, Final) :-
    next_state(Table, Tolerance, Ids, State0, State1),
    (   State1 == State0
    ->  Final = State0
    ;   fixpoint(Table, Tolerance, Ids, State1, Final)
    ).
```

`==/2` is **structural identity**, not unification: it compares two
ground terms without binding anything. On a 7,423-argument term of small
integers that is a linear word-by-word walk — cheap next to the round
that produced it. Using `=/2` here would be a real bug: it would *unify*
the states, succeeding by binding variables rather than by finding them
equal. (They are ground, so it would happen to work — but `==/2` says
what is meant, and this repo's rule is to use the comparison that cannot
be misread. Compare [Day 8](day08_function_guide.md)'s use of `==/2` for
its halt/loop test.)

### `seat_rule/4`

```prolog
seat_rule(0, Count, _Tolerance, Cell) :- Count =:= 0, !, Cell = 1.
seat_rule(1, Count, Tolerance, Cell)  :- Count >= Tolerance, !, Cell = 0.
seat_rule(Cell0, _Count, _Tolerance, Cell) :- Cell = Cell0.
```

The statement's three bullets, one clause each, in the statement's order,
with the catch-all last. Two style points that are house rules by now:

- **Outputs unified after the cut.** `Cell` never appears in a clause
  head. The cut commits on the *inputs* alone, so a caller that passes a
  pre-bound `Cell` cannot fail the head match and slide into a later
  clause — the trap that makes cut-carrying predicates
  non-**steadfast**. This is the same discipline as
  [Day 3](day03_function_guide.md)'s `drop/3`.
- **First-argument indexing does most of the work.** Clauses 1 and 2 have
  distinct first arguments (`0` and `1`), so SWI jumps straight to the
  relevant one; the cuts exist to skip the catch-all, not to choose
  between the first two.

`=:=` is **arithmetic** equality (evaluates both sides) where `==` above
was structural. `Count =:= 0` and `Count == 0` both work on an integer;
`=:=` states that this is a number being compared numerically.

### `occupied_among/3` and `occupied_count/2`

```prolog
occupied_among_([], _State, Count, Count).
occupied_among_([I|Ids], State, Acc0, Count) :-
    arg(I, State, Value),
    Acc1 is Acc0 + Value,
    occupied_among_(Ids, State, Acc1, Count).
```

The innermost loop of the program — roughly 4.5 million iterations per
part — so it is written as a tail-recursive accumulator walk with clauses
split on `[]` versus `[_|_]`, which is what lets first-argument indexing
keep it choicepoint-free. [Day 10](day10_function_guide.md) has the long
version of why the accumulator matters. Summing `0`/`1` values rather
than counting matches is what makes the body two goals.

`occupied_count/2` totals the final state with univ + `sum_list/2` —
called once, so clarity wins over the `arg/3` walk that would avoid
building the intermediate list.

### `part1/2`, `part2/2`, `solve/3`

```prolog
part1(Grid, Occupied) :-
    seat_layout(Grid, Layout),
    adjacent_table(Layout, Table),
    stable_occupancy(Table, 4, Occupied).
```

Three lines, and the only difference in `part2/2` is `visible_table` and
`5`. That symmetry is the deliverable — everything above exists so that
the two parts can differ by exactly the two things the statement says
they differ by. `solve/3` shares the one `seat_layout/2` between them (a
sub-millisecond saving, but it keeps the "parse once" contract the other
days follow), while `part1/2` and `part2/2` stay self-contained for the
tests and the bench harness.

---

## Correctness notes

**Floor elimination is safe.** A floor square is never a seat (it cannot
hold a value the rules read), and it is never *counted* — part 1 counts
occupied seats among adjacent squares, and floor is not an occupied seat;
part 2 explicitly looks *past* floor. So removing floor from the state
changes nothing observable. It does mean floor must still be represented
in the *geometry* while tables are built, which is why `visible_table/2`
gets `Rows`/`Cols` and walks coordinates rather than seats.

**Simultaneous update is enforced structurally**, as described above:
`next_state/5` reads only `State0`.

**Both neighbour relations are symmetric.** If seat *a* is adjacent to
*b*, then *b* is adjacent to *a* — obvious. Less obvious: if *a* *sees*
*b* along a ray, then *b* sees *a* along the reverse ray, because
"sees" means *no seat lies strictly between them on that line*, which is
a symmetric condition. (Verified on the real input: every id in seat
*i*'s list has *i* in its own.) This matters for the next point.

**Termination is not proved by this code, and the guide should not
pretend otherwise.** `fixpoint/5` stops when a round changes nothing; on
a 2-cycle it would spin forever. Here is the honest state of the
argument:

- For a **pure** threshold rule — one where the new state depends only on
  the neighbour count, not on the seat's own previous state — the update
  map `F` is **antitone**: more occupation now means no more occupation
  next round (`A ⊆ B ⟹ F(B) ⊆ F(A)`). Then `F²` is *monotone*, and
  starting from `S₀ = ∅` (the minimum) the even-indexed states form an
  increasing chain and the odd-indexed states a decreasing one. Two
  monotone chains in a finite lattice must both stabilise, so the system
  reaches period 1 or 2. That is the standard argument, and the general
  theorem for symmetric-weight threshold networks under parallel update —
  **eventual period 1 or 2** — is **Goles and Olivos (1980)**.
- This rule is *not* a pure threshold: it has **hysteresis**. A seat fills
  only at count 0 and empties only at count ≥ `Tolerance`; in the band
  between, it holds its current value. That state-dependence breaks
  antitonicity (take a seat that is empty in `A`, occupied in `B`, with a
  count in the middle band), so the clean proof does not transfer.
- Empirically, on this input, the two parity chains *are* monotone and
  both parts reach a genuine fixpoint (86 and 87 rounds). The puzzle
  guarantees stabilisation, and the code takes that promise at face
  value.

If robustness mattered more than clarity, the fix is a round cap or a
two-back comparison that detects the 2-cycle and reports it. That is a
deliberate omission, not an oversight.

**No cut escapes into the answer.** The only cuts are in `seat_rule/4`,
after the input tests, with outputs unified afterwards.

---

## Tests — what's pinned and why

Thirteen tests in [`test/day11_tests.pl`](../../test/day11_tests.pl).
The interesting ones are not the answers:

- `layout_keeps_only_seats` — 10 × 10 grid, **71** seats. Pins the
  floor-elimination step and the row-major ordering (`Coords` starts
  `1-1, 1-3`, i.e. the floor at `1-2` is gone and ids are not
  coordinates).
- `adjacent_table_corner` / `visible_table_corner` — the *same* seat
  (top-left) under both rules: adjacency gives `[2-1, 2-2]`, visibility
  gives `[1-3, 2-1, 2-2]`. One extra seat, seen past the floor square at
  `1-2`. This pair is the clearest statement of what part 2 changed, and
  it is the test that fails first if the ray-walk is wrong.
- The three **sight-line vignettes** from the Part Two statement, which
  exist precisely because they are hard cases: eight visible seats
  through floor; a nearer *empty* seat blocking the view of occupied ones
  (blocking is by seat, not by occupancy — the single most common
  misreading of part 2); and a seat walled in so it sees nothing, whose
  neighbour list must be `[]`.
- `floor_only_layout_is_stable` and `single_seat_fills` — degenerate
  shapes. The first exercises `N = 0`, where the state term degenerates
  to the *atom* `occ` and the table to the atom `nbrs`; `functor/3`
  reports arity 0 and everything downstream still works. The second pins
  that a seat with no neighbours fills and then stays filled.
- Answer locks: **2321** and **2102**. These call `part1/2` and `part2/2`
  directly rather than `solve/3`, so the suite runs two simulations
  instead of four — about 0.8 s instead of 1.6 s.

The tests resolve neighbour ids back to `R-C` coordinates through a
helper, so expectations read as grid positions. Asserting raw ids would
pin an internal numbering nothing else guarantees.

Cross-validated against [`python/day11.py`](../../python/day11.py), which
is the same algorithm with lists and a dict, and independently prints
`part1=2321 part2=2102`.

---

## Complexity & benchmarks

Let *N* be the seat count (7,423) and *d* the average neighbour count
(6.47 adjacent, 7.85 visible), *R* the rounds (86, 87).

| Phase | Cost |
|---|---|
| Parse | O(squares) |
| Layout | O(squares) sweep + O(N log N) assoc build |
| Adjacent table | O(8N log N) — eight assoc lookups per seat |
| Visible table | O(8N log N + total ray length) |
| One round | O(N·d) — one `arg/3` per neighbour |
| Simulation | **O(R·N·d)** ≈ 4.1M / 5.1M neighbour reads |

Measured (`swipl bench/main.pl day11`):

```text
  parse          1,557 inf      0.869 ms
  part1     12,617,177 inf    396.556 ms
  part2     14,830,878 inf    447.074 ms
```

Read the inference counts against the model: part 1 does ~4.1M neighbour
reads and reports 12.6M inferences — about three inferences per
neighbour (`arg/3`, the addition, the recursive call), plus per-seat and
per-round overhead. The numbers say the constant factor is small and
nothing unexpected is happening. Part 2's 18% premium over part 1 is
almost exactly its 21% larger average neighbourhood; the extra round and
the ray-marching table build are noise beside that.

Table construction does not appear as a separate line, but it is inside
those figures and is a small fraction: ~60k assoc lookups against
millions of round-reads. **Precomputation is essentially free and buys
back a factor of hundreds** — the day's whole lesson in one ratio.

---

## If I were writing this in Rust

The design maps over almost unchanged, because the Prolog version already
converged on the array-of-bits-plus-adjacency-table shape that Rust would
force:

```rust
struct Layout {
    rows: usize,
    cols: usize,
    coords: Vec<(usize, usize)>,          // id -> position
    index: HashMap<(usize, usize), u32>,  // position -> id
}

fn stable_occupancy(table: &[Vec<u32>], tolerance: u32) -> usize {
    let mut state = vec![0u8; table.len()];
    let mut next = vec![0u8; table.len()];
    loop {
        for (i, neighbours) in table.iter().enumerate() {
            let count: u32 = neighbours.iter()
                .map(|&j| state[j as usize] as u32)
                .sum();
            next[i] = match (state[i], count) {
                (0, 0) => 1,
                (1, c) if c >= tolerance => 0,
                (s, _) => s,
            };
        }
        if next == state { return state.iter().filter(|&&v| v == 1).count(); }
        std::mem::swap(&mut state, &mut next);
    }
}
```

Correspondences worth noting:

| Prolog | Rust | Note |
|---|---|---|
| `occ(V1,…,VN)` + `arg/3` | `Vec<u8>` + `state[i]` | Same O(1) indexed read; the compound term *is* the vector |
| `nbrs(L1,…,LN)` | `Vec<Vec<u32>>` | Rust would flatten this — see below |
| fresh term per round | `mem::swap` of two buffers | Rust reuses two allocations; Prolog allocates one per round |
| `State1 == State0` | `next == state` | `PartialEq` on slices, same linear compare |
| `seat_rule/4` clauses | `match (state[i], count)` | Guarded match arms are Prolog clause heads with tests |
| `get_assoc/3` fails | `HashMap::get` → `Option` | Failure vs. `None`; `filter_map` is `findall/3`'s filtering |

Three genuine differences:

1. **The double-buffer is manual and therefore fallible.** `mem::swap`
   with two buffers is the standard Jacobi pattern; write `state[i] = …`
   inside the loop instead and you have silently switched to
   Gauss–Seidel and get a wrong answer that still looks plausible. The
   Prolog version cannot express that bug. This is the clearest case
   this year of immutability preventing a class of error rather than just
   costing allocations.
2. **`Vec<Vec<u32>>` is a pointer chase per seat.** The idiomatic
   optimization is a **CSR / flattened adjacency**: one `Vec<u32>` of all
   neighbour ids plus a `Vec<u32>` of start offsets, giving
   `&flat[starts[i]..starts[i+1]]`. Cache-friendly and about as fast as
   this gets without SIMD. The Prolog term-of-lists has the same shape as
   `Vec<Vec<_>>` and the same locality problem — but at SWI's abstraction
   level, chasing it is not worth the readability.
3. **`u8` state, `bool` state, or a bitset.** With a bitset, counting
   neighbours becomes popcount over masks, and the whole automaton
   vectorises. That is the direction a serious Rust version would go, and
   it is exactly the direction that would make the Prolog unreadable.

The parse would be `input.lines().map(str::as_bytes)`, and the eight
directions a `const DIRECTIONS: [(i32, i32); 8]` — the Rust equivalent of
the eight `direction/2` facts, though Prolog's version gets to *be* a
generator rather than something you iterate.

---

## Possible optimization

Shipping code stays as written. Four things a faster version would do,
roughly in order of payoff:

**1. Skip seats that cannot change.** The classic CA optimization: a seat
whose neighbourhood was unchanged last round has the same outcome this
round. Maintain a *frontier* of seats adjacent to something that changed
and only recompute those. By round 40 the frontier is tiny and the last
~40 rounds are nearly free. This is where the big constant-factor win is
— potentially 5–10× — but it needs a change-set per round and a
neighbour-of-neighbour table, roughly doubling the file. Not worth it for
0.4 s.

**2. Early-exit the neighbour count.** `occupied_among/3` always sums the
whole list, but an occupied seat only needs to know whether the count
*reaches* `Tolerance`, and an empty seat only whether it is *nonzero* —
which the first occupied neighbour settles. In a stable-ish grid most
seats are occupied with several occupied neighbours, so a short-circuit
count would skip a good fraction of the reads. Costs a threshold
parameter in the innermost predicate and a second clause; a measurable
win for a modest clarity hit, and the cheapest of the four to write.

**3. Fixpoint detection without the full compare.** `State1 == State0`
walks all *N* arguments every round. `next_state/5` could instead report
whether any cell changed, folding the test into the round it already
performs. Small (the compare is ~1% of a round) but nearly free.

**4. `setarg/3` into a reused buffer.** Two pre-allocated state terms,
destructively updated and swapped — the Rust `mem::swap` pattern, giving
up the "fresh term per round" guarantee and with it the structural
enforcement of simultaneous update. Saves 86 allocations of a
7,423-argument term. Given that SWI's allocation is a pointer bump and
the GC handles short-lived terms well, this buys the least of the four
while costing the most safety. Mentioned because it is the
transliteration of the Rust code, and it is the wrong move here.

A different axis entirely: **both parts are independent** and could run
concurrently with `concurrent_maplist/3` or explicit threads, halving
wall-clock on any multi-core machine. The repo has not needed concurrency
yet, and introducing it for 0.4 s would be the wrong first use — but Day
11 is the first day where the two parts are genuinely separate,
equal-cost computations over shared read-only data, which is the ideal
case for it.
