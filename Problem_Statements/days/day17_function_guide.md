# Day 17 Function Guide — Conway Cubes

> Conway's Game of Life with the plane taken away. The rule is the one
> from 1970 — survive on 2 or 3 neighbours, be born on exactly 3 — but the
> grid is 3-dimensional in part 1 and 4-dimensional in part 2, and it is
> infinite. The whole day comes down to two representation decisions:
> store only the active cells (so "infinite" costs nothing), and count
> neighbours by *scattering* from the active cells rather than *gathering*
> at every candidate (so there is no candidate list to build). With those
> two in place the dimension is a parameter and part 2 is a one-character
> change to part 1.

Source: [`python/day17.py`](../../python/day17.py) ·
Tests: [`python/tests/test_day17.py`](../../python/tests/test_day17.py)

---

## 1. The problem

The input is a small flat picture:

```text
.#.
..#
###
```

That is a 2-D slice of a pocket dimension where every integer coordinate
holds a cube, active (`#`) or inactive (`.`). Everything outside the slice
starts inactive. Six cycles run; in each, **every** cube simultaneously
looks at its neighbours — every cube whose coordinates each differ from
its own by at most 1 — and:

- an active cube with exactly 2 or 3 active neighbours stays active,
  otherwise it turns inactive;
- an inactive cube with exactly 3 active neighbours turns active,
  otherwise it stays inactive.

**Part 1.** The pocket dimension is 3-D, so a cube has 26 neighbours. How
many cubes are active after six cycles? The example ends at 112.

**Part 2.** The pocket dimension is actually 4-D — a cube has 80
neighbours. Same slice, same rule, same six cycles. The example ends
at 848.

The real input is an 8×8 slice with 31 active cells. Anyone who has seen
Life will recognise the example: it is the **glider**, and the engine
here with `dims=2` is plain Life, in which the glider moves one cell
diagonally every four generations. That is a test, because it is the
cheapest possible check that the rule is implemented right.

## 2. Representation

`parse_input` returns a `frozenset[tuple[int, int]]` — the `(x, y)`
coordinates of the active cells, x across, y down, nothing else. The
example parses to `{(1,0), (2,1), (0,2), (1,2), (2,2)}`.

The simulation state is a `set` of coordinate tuples of whatever
dimension is being run: `(x, y, z)` in part 1, `(x, y, z, w)` in part 2.
Three things follow from that choice, and they are the reason it wins
over an array:

- **The grid is infinite for free.** An inactive cell is one that is not
  in the set. There is no boundary, no padding, no "did the pattern reach
  the edge" check.
- **Growth is bounded but never has to be computed.** Because a cell can
  only be born next to an active one, the occupied box grows by at most
  one cell per axis per cycle. From an 8×8 slice that is at most 20×20
  in x and y and 13 wide on each extra axis after six cycles —
  20·20·13·13 = 67,600 cells in 4-D. An array implementation has to size
  itself to that box up front; the set never thinks about it. (The bound
  is pinned as a test on the example.)
- **Dimension is a number, not a type.** `(x, y) + (0,)` is a 3-D cell,
  `(x, y) + (0, 0)` is a 4-D one, and every function below takes `dims`
  rather than knowing.

The machine framing: this is a **sparse** representation of a bitmap
whose density is very low. On the real input, after six cycles in 4-D,
2,228 of the 67,600 cells in the bounding box are active — 3.3%. A dense
bitmap would touch all 67,600 every cycle; the set touches the active
ones times 80 neighbours. Section 7 discusses when the dense version wins
anyway.

## 3. Function walkthrough

### `parse_input(raw) -> frozenset[tuple[int, int]]`

```python
return frozenset(
    (x, y)
    for y, line in enumerate(raw.splitlines())
    for x, char in enumerate(line.strip())
    if char == "#"
)
```

`splitlines()` handles CRLF, and the per-line `strip()` is belt and
braces: a surviving `\r` would sit past the last column and never equal
`#`, so it would be harmless here — but the day 6 rule is not to rely on
that. `test_crlf_input` pins it.

### `neighbour_offsets(dims) -> tuple[Cell, ...]`

Every tuple of `dims` values from `{-1, 0, 1}`, minus the all-zero one:
`itertools.product((-1, 0, 1), repeat=dims)` filtered by `any(offset)`.
That is 3<sup>dims</sup> − 1 offsets — 8, 26, 80 for 2, 3, 4 dimensions,
matching the statement's numbers, each a test. The function is
`@cache`d because `step` calls it once per active cell and the tuple is
the same every time.

### `embed(slice2d, dims) -> set[Cell]`

`(x, y)` becomes `(x, y, 0, …, 0)`. The slice sits at zero on every extra
axis, which is what "a small flat region" means and is also the source of
the symmetry in section 4.

### `step(active, dims) -> set[Cell]`

```python
counts: Counter[Cell] = Counter()
for cell in active:
    for offset in neighbour_offsets(dims):
        counts[tuple(a + b for a, b in zip(cell, offset))] += 1
return {cell for cell, n in counts.items() if n == 3 or (n == 2 and cell in active)}
```

This is the whole algorithm. The natural way to state the rule is a
*gather*: for each cell that might be active next cycle, count its active
neighbours. But "each cell that might be active" is itself a set you have
to construct (every active cell plus every neighbour of one), and then
each of those looks at all 26 or 80 neighbours again. The *scatter* skips
the construction: every active cell walks its neighbours and adds one to
a counter there. When the loop ends, `counts[T]` is exactly the number of
active neighbours of `T`, for every `T` that has at least one — and a
cell with zero active neighbours can be neither born nor kept, so the
cells missing from the counter are correctly missing from the result.

The rule then reads straight off the counter. `n == 3` is active next
cycle whether or not it is active now (born, or survives with 3);
`n == 2` survives only if already active; everything else is off. Note
that `active` is only *read* while the new set is built, which is what
makes the update simultaneous.

Traced on the example, 3-D, first cycle. The five glider cells scatter
26 increments each; here is the z=0 plane of the counter with the rule
applied cell by cell (x across 0..2, y down 0..3):

| y | counts | verdicts | next |
|---:|---|---|---|
| 0 | 1 1 2 | (1,0) is active with 1 → dies | `...` |
| 1 | 3 5 3 | (0,1) inactive with 3 → born; (1,1) has 5 → stays off; (2,1) active with 3 → stays | `#.#` |
| 2 | 1 3 2 | (0,2) active with 1 → dies; (1,2) active with 3 → stays; (2,2) active with 2 → stays | `.##` |
| 3 | 2 3 2 | (1,3) inactive with 3 → born | `.#.` |

Read the last column top to bottom, dropping the empty row: `#.#`, `.##`,
`.#.` — the statement's `z=0` layer after one cycle, whose frame has
shifted down a row to follow the cells. The z=1 plane of the same counter
holds only inactive cells, so only its 3s matter: they are at (0,1),
(2,2) and (1,3), which is the statement's `#..` / `..#` / `.#.`; z=−1 is
the mirror image. That the z=0 layer is also what plain 2-D Life does to a
glider in one step is not a coincidence: at cycle 1 the z=0 cells have
exactly their 8 in-plane neighbours to look at.

### `boot(slice2d, dims, cycles=6) -> set[Cell]`

Embed, then `step` six times. Exposed separately from `part1`/`part2` so
tests can ask for one or two or three cycles and compare against the
statement's layer dumps, and so `dims=2` is reachable.

### `part1` / `part2`

`len(boot(slice2d, 3))` and `len(boot(slice2d, 4))`. On the real input,
cycle by cycle:

| cycle | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 3-D active | 31 | 71 | 81 | 197 | 172 | 318 | 359 |
| 4-D active | 31 | 185 | 245 | 1,176 | 592 | 2,556 | 2,228 |

Both sequences saw-tooth — an odd cycle spreads the pattern into fresh
layers, the next one thins it — and 4-D's peak is cycle 5, not 6. The
answers are **359** and **2,228**, both submitted and accepted. The
final 3-D box is x −4..13, y −3..13, z −5..5; the 4-D box has the same x
and y and z, w both −6..6.

## 4. Why it is correct

**Scatter equals gather.** The neighbour relation is symmetric: `T` is a
neighbour of `A` exactly when `A` is a neighbour of `T`, because the offset
set is closed under negation. So "the number of active `A` that are
neighbours of `T`" (the gather the statement describes) equals "the
number of times some active `A` scattered onto `T`" (what the counter
holds). The two are the same sum written in the other order.

**Missing means zero.** A cell that no active cell scattered onto has no
active neighbours. With count 0 it fails both clauses of the rule
whatever its current state, so leaving it out of the counter and hence
out of the next set is right. The `n == 2 and cell in active` clause is
the only place the *current* state is consulted, and that is exactly the
asymmetry the statement's rule has.

**Simultaneity.** Every count is computed from the old set before any
cell of the new set exists. The statement's "all cubes simultaneously
change" is a two-set update, which is what the code is.

**The first 4-D cycle is the first 3-D cycle, replicated.** The
statement's Part Two shows nine 3×3 layers after cycle 1, eight of them
identical to 3-D's `z=1` and the ninth, at `(z,w)=(0,0)`, identical to
3-D's `z=0`. That is forced: after one cycle the only cells that can have
been anyone's neighbour are the initial slice at `z=w=0`, and a cell one
step away from the slice sees the same nine slice cells whether the step
is in z, in w, or in both. `test_first_4d_cycle_is_the_first_3d_cycle_replicated`
checks it layer by layer.

**Mirror symmetry.** The slice sits at z=0, the offset set is symmetric
under z → −z, so the state after any number of cycles is symmetric under
z → −z; likewise w in 4-D, and z ↔ w since the two extra axes start
identical. On the real input after six cycles the 3-D state has 33 cells
in the z=0 layer and 37, 40, 40, 36, 10 in each of z=±1..±5 — the same
count on both sides, and in fact the same cells. This is not something
the shipping code needs, but the optimisation in section 7 leans on it,
and the repo rule is that an identity a shortcut leans on is a test, not a
sentence: `test_real_input_is_mirror_symmetric_in_the_extra_axes` asserts
all three symmetries on the real state, and a parametrized sibling does it
on the example at cycles 1, 2, 3 and 6.

## 5. Complexity

Let *a<sub>c</sub>* be the active count at cycle *c* and *k* = 3<sup>dims</sup> − 1.
One `step` does *a<sub>c</sub>* · *k* tuple constructions and counter
increments, then one pass over the counter, whose size is at most
*a<sub>c</sub>* · *k* and in practice much less (neighbourhoods overlap
heavily). Over six cycles the work is Σ *a<sub>c</sub>* · *k*. Measured on
the real input:

| | cells scattered (Σ *a<sub>c</sub>*, c = 0..5) | × *k* | tuple builds |
|---|---:|---:|---:|
| 3-D | 870 | 26 | 22,620 |
| 4-D | 4,785 | 80 | 382,800 |

Each tuple build in the shipping code is a generator over `zip(cell,
offset)` — the clearest way to write "add these two vectors" in Python
and also the slowest, at roughly half a microsecond each. That is where
the time goes:

| phase | best | median |
|---|---:|---:|
| parse | 0.004 ms | 0.004 ms |
| part 1 | 12.5 ms | 12.6 ms |
| part 2 | 229 ms | 232 ms |

(`python\bench.py 17 -n 20`, best/median of 20.) Part 2 is 18× part 1
for 17× the tuple builds — the cost is linear in the scatter count, as
the model says. At about a quarter of a second this is the third-slowest
day so far, behind day 15 (3.6 s of Van Eck) and day 11 (0.56 s, the
seating automaton, which is also Life-shaped and does more work than this
by scanning a dense 99×92 grid — 9,108 cells, 7,423 of them seats — every round).

Space is the set plus the counter: O(*a* · *k*) at worst, a few tens of
thousands of entries in 4-D. Nothing here is asymptotically interesting;
it is all constant factors, which is the subject of section 7.

## 6. If I were writing this in Rust

The set-of-cells design ports directly, and Rust adds the one thing
Python's tuples lack: a fixed-width coordinate type. `[i32; N]` with a
const generic `N` gives `HashSet<[i32; 3]>` and `HashSet<[i32; 4]>` from
the same source, and the "add these two vectors" that costs a generator
in Python is an unrolled loop over `N` registers. The port below was
compiled (`rustc -O`, 1.93.1) and run three times on the real input
while writing this guide. Same two answers; parse **3.1–3.4 µs**, part 1
**554–576 µs**, part 2 **7.6–7.7 ms** — about 30× the Python for the same
algorithm and the same hash-map traffic.

```rust
fn step<const N: usize>(active: &HashSet<[i32; N]>, offsets: &[[i32; N]]) -> HashSet<[i32; N]> {
    let mut counts: HashMap<[i32; N], u8> = HashMap::with_capacity(active.len() * 8);
    for cell in active {
        for off in offsets {
            let mut target = *cell;
            for d in 0..N {
                target[d] += off[d];
            }
            *counts.entry(target).or_insert(0) += 1;
        }
    }
    counts
        .into_iter()
        .filter(|(cell, n)| *n == 3 || (*n == 2 && active.contains(cell)))
        .map(|(cell, _)| cell)
        .collect()
}
```

Things the types make explicit that Python left implicit:

- **The count fits in a `u8`.** The maximum is *k* = 80. Python's
  `Counter` holds arbitrary ints; here the width is a decision.
- **`offsets` is built by counting in base 3.** `0..3^N` as an integer,
  each base-3 digit minus one is a coordinate; skip the all-zero one.
  That is `itertools.product` done by hand and is the same shape as day
  14's "the counter's bits select the floating positions".
- **`boot::<3>` and `boot::<4>`** are two monomorphised functions. The
  dimension is a compile-time constant, so the inner `for d in 0..N` is
  unrolled and there is no per-cell `zip`. This is the Rust way to get
  what section 7's "unpacked" Python variant gets by writing the 3-D and
  4-D loops out twice.

With the growth bound from section 2, the *dense* version is also natural
in Rust: a `Vec<u8>` of 67,600 cells, 80 shifted adds per cycle, no
hashing at all. It was not measured here, but the hash map is the
dominant cost of the port above (every increment is a hash and a probe),
so it would be the next thing to try.

## 7. Possible optimization

All measured on the real input, best of 5, six cycles, against the
shipping `step` (`variants.py` in the session scratchpad, not the repo):

| variant | 3-D | 4-D | 4-D speed-up |
|---|---:|---:|---:|
| shipping (`tuple(a + b for a, b in zip(...))`) | 12.6 ms | 232 ms | — |
| `tuple(map(add, cell, offset))` | 7.6 ms | 139 ms | 1.7× |
| unpacked, fixed width | 3.2 ms | 59 ms | 3.9× |
| mirror-folded (on the `map(add)` base) | 7.4 ms | 74 ms | 3.1× |

**`map(add)`.** Same semantics, one C-level call instead of a Python
generator per tuple. A defensible swap for the shipping code; it stays in
the sidebar because the generator says what is happening and the
difference is 90 ms nobody waits for.

**Unpack the tuple.** `for x, y, z, w in active:` then
`counts.update((x + dx, y + dy, z + dz, w + dw) for dx, dy, dz, dw in OFFSETS)`
— four adds and one tuple display, and the `Counter.update` takes the
whole generator in one call. Nearly 4× on part 2, and it is what the Rust
port gets for free from `const N`. The price is that `dims` stops being a
parameter: the 3-D and 4-D loops are two copies, and the `dims=2` Life
test would need a third.

**Fold the mirror symmetry.** Since the state is symmetric under z → −z
(and w → −w), store only cells with z ≥ 0 (and w ≥ 0) and let the mirror
images be implied. Scattering then needs a weight: a stored cell at z=1
has an image at z=−1 that also touches the z=0 targets, so those targets
get 2 from it; a target with z < 0 is dropped. In general the weight is
the product over the folded axes of `2 if cell_axis == 1 and target_axis == 0 else 1`,
and the final count is Σ 2<sup>(number of strictly positive folded
coordinates)</sup> over stored cells. On the real input it stores 196 of
the 359 3-D cells and 682 of the 2,228 4-D ones — 3.3× fewer — but the
weight computation eats most of that in Python, so it lands at 1.9× over
its base. Folding z ↔ w as well (store z ≥ w ≥ 0) would take the 4-D
count down by roughly another half; the bookkeeping gets correspondingly
less obvious. This is the identity `test_real_input_is_mirror_symmetric_in_the_extra_axes`
exists to protect.

**Go dense.** The box is known before the simulation starts (section 2),
so a flat `bytearray` — or a NumPy array with an 80-tap convolution — is
an option: no tuples, no hashing, but 67,600 cells touched per cycle
whether active or not. Not measured here; noted as the route the Rust
port would take next. With the density at 3.3% it is not obvious the
dense version wins in Python, which is why it is a sentence and not a
table.

---

## Tests

`python/tests/test_day17.py`, 31 tests plus the locked check:

- **Parse** — the example's five cells; the CRLF round trip.
- **Neighbourhood** — 8 / 26 / 80 offsets for 2 / 3 / 4 dimensions, all
  distinct, every coordinate in {−1, 0, 1}, the zero offset absent; the
  statement's own "(2,2,2) and (0,2,3) are neighbours of (1,2,3)".
- **The rule, count by count** — a centre cell with 0, 1, 2, 3, 4 axis
  neighbours, active and inactive, parametrized to the statement's two
  sentences; a lone cube dies.
- **The statement's layers** — every 3-D layer it prints after cycles 1,
  2 and 3, parsed from the dump text and compared modulo the frame's
  shift; the nine 4-D layers after cycle 1, and the reason they are what
  they are (replication of the 3-D layers).
- **Both answers on the example** — 112 and 848.
- **Degenerate case** — `dims=2` is Life and the seed is a glider: after
  four generations it is itself shifted by (1, 1).
- **The bounds** — growth of at most one cell per axis per cycle, pinned
  on the example after six cycles.
- **The symmetry** — z-mirror, w-mirror and z ↔ w on the example at
  cycles 1, 2, 3, 6 and on the real input after six; this is the identity
  the folded sidebar leans on. The real-input test skips when the
  gitignored input is absent.

`LOCKED = (359, 2228)` — both submitted and accepted, so the suite
asserts them and a refactor that changes either answer fails. Before
submission the day sat at `LOCKED = None`, with the fixture reporting the
two numbers and skipping; the statement examples and the compiled Rust
port agreed with them, which was consistency, not acceptance.

[`day17.md`](day17.md) carries both parts. The Part Two text was
backfilled from the puzzle rather than fetched from the site. Its
cycle-1 and cycle-2 layer dumps were generated by this code, so they are
consistent with the 848 the same code reproduces rather than
independently verified; the cycle-1 layers agree with the replication
argument in section 4, which is independent of the code.
