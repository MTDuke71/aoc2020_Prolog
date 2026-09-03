# Day 16 Function Guide — Ticket Translation

> Two filters in series. Part 1 is a value-level filter — does *any*
> field accept this number? — and part 2 is a column-level one — which
> fields accept *every* number in this column? The second filter leaves one
> candidate set per column, and the puzzle is built so those sets nest like
> a staircase (sizes 1, 2, …, 20 on the real input), which is exactly the
> shape that lets a peel-the-singleton loop resolve the whole assignment
> without search. The guide's job is to show that shape, say why the loop is
> sound, and be honest about when it would not be enough.

Source: [`python/day16.py`](../../python/day16.py) ·
Tests: [`python/tests/test_day16.py`](../../python/tests/test_day16.py)

---

## 1. The problem

The notes come in three blocks:

```text
class: 1-3 or 5-7          <- one rule per field: a name, two inclusive spans
row: 6-11 or 33-44
seat: 13-40 or 45-50

your ticket:
7,1,14                     <- my ticket: the same columns, unlabelled

nearby tickets:
7,3,47                     <- other people's tickets, same column order
40,4,50
55,2,20
38,6,12
```

Every ticket lists its fields in the same order; nobody knows what that
order is. The real input has 20 fields, 20-column tickets, and 238 nearby
tickets with values from 0 to 999.

**Part 1.** A value that lies in no span of *any* field cannot be a real
field value, so its ticket is corrupt. Sum those values across the nearby
tickets — the "ticket scanning error rate". In the example, 4, 55 and 12
are valid for nothing, so the answer is 71.

**Part 2.** Discard the corrupt tickets. Using the survivors, work out which
field sits in which column, then multiply my ticket's values in the six
columns whose field name begins with `departure`.

## 2. Representation

`parse_input` returns a `Notes` named tuple:

| field | type | contents |
|---|---|---|
| `rules` | `dict[str, Ranges]` | field name → `((lo, hi), (lo, hi))`, in input order |
| `mine` | `list[int]` | my ticket |
| `nearby` | `list[list[int]]` | the nearby tickets, one row each |

`Ranges` is a tuple of inclusive `(lo, hi)` spans. It is left as spans —
not expanded into sets of accepted integers, not turned into a lookup
table — because that is the statement's own vocabulary, and the closure
over them, `accepts(ranges, value)`, is a one-liner.

The part-2 working state is one `set[str]` per column: the fields that
could still live there. Sets rather than bitmasks because the operations
the algorithm needs — "is this a singleton", "remove these names" — read
directly as `len(s) == 1` and `s -= taken`. The bitmask version is real and
much faster; it lives in section 7 and in the Rust bridge.

The machine framing worth carrying: a field's rule is a **decode ROM**.
Values are 10 bits wide (0–999), so "which fields accept value *v*" is one
read of a 1,000-entry table whose word is a 20-bit mask, one bit per
field. Part 1 asks whether the word is zero; part 2 ANDs the words down a
column. The shipping Python does the same work by scanning spans, because
at 238 tickets the ROM is a sidebar, not a necessity.

## 3. Function walkthrough

### `parse_input(raw) -> Notes`

```python
rules_block, mine_block, nearby_block = "\n".join(raw.splitlines()).strip().split("\n\n")
```

The three blocks are separated by blank lines, and on a Windows download a
blank line is `\r\n\r\n`, which `split("\n\n")` would not find. Rejoining
`splitlines()` normalises every line ending to `\n` first, so the split
sees `\n\n` on either flavour and no `\r` survives onto the last value of
a ticket line — the day 6 lesson, pinned by `test_crlf_input`.

A rule line is `name: lo-hi or lo-hi`. Field names contain spaces
(`departure location`), so the split is on the literal `": "` and then on
`" or "`. My ticket is the second line of its block; the nearby tickets are
every line after the header of theirs.

### `accepts(ranges, value) -> bool`

```python
return any(lo <= value <= hi for lo, hi in ranges)
```

Inclusive on both ends, as the statement says explicitly for `1-3 or 5-7`:
3 and 5 are valid, 4 is not. That sentence is a parametrized test.

### `invalid_values(ticket, rules) -> list[int]`

The values on one ticket that **no** field accepts. This is the single
predicate the two parts share: part 1 sums the list, part 2 keeps the
tickets whose list is empty. Traced on the example's four nearby tickets:

| ticket | per-value verdict | `invalid_values` |
|---|---|---|
| `7,3,47` | 7→class, 3→class, 47→seat | `[]` — valid ticket |
| `40,4,50` | 40→row/seat, **4→nothing**, 50→seat | `[4]` |
| `55,2,20` | **55→nothing**, 2→class, 20→seat | `[55]` |
| `38,6,12` | 38→row/seat, 6→class/row, **12→nothing** | `[12]` |

### `part1(notes) -> int`

Sum of `invalid_values` over the nearby tickets: 4 + 55 + 12 = 71. My
ticket is not consulted ("ignore your ticket for now"), and a ticket with
two bad values contributes both — each is a test.

On the real input: 48 invalid values, on 48 distinct tickets (every corrupt
ticket has exactly one bad number), 190 tickets survive. And every bad
value is either below 25 or above 974:

```text
0 2 3 3 4 4 5 6 6 7 11 13 14 14 14 14 15 15 17 19 21 21 21 22 22 23
976 976 977 977 979 980 982 983 984 984 984 984 985 987 987 990 991 993 993 994 995 999
```

That is not a coincidence of this input's bad values; it is a property of
the rules. Each rule is two spans with a small gap between them (e.g.
`class: 40-350 or 372-965`, gap 351–371), and every gap is covered by some
other field's span. The **union** of all twenty rules is the contiguous
window 25…974 with no hole. So "valid for at least one field" collapses to
"25 ≤ *v* ≤ 974" — a two-comparison range check, which is the kind of thing
the decode-ROM view makes visible and the span-scanning code never notices.

### `candidate_fields(rules, tickets) -> list[set[str]]`

For each column of the (already filtered) tickets, the set of fields whose
spans accept **every** value in that column. `zip(*tickets)` transposes
rows into columns; the rest is `all(accepts(...))` per (column, field).

Traced on the statement's Part Two example — rules `class: 0-1 or 4-19`,
`row: 0-5 or 8-19`, `seat: 0-13 or 16-19`; tickets `3,9,18`, `15,1,5`,
`5,14,9`:

| column | values | class? | row? | seat? | candidates |
|---:|---|---|---|---|---|
| 0 | 3, 15, 5 | 3 is in the 2–3 gap → no | yes | 15 is in the 14–15 gap → no | `{row}` |
| 1 | 9, 1, 14 | yes | yes | 14 → no | `{class, row}` |
| 2 | 18, 5, 9 | yes | yes | yes | `{class, row, seat}` |

Sizes 1, 2, 3, and each set contains the one before it. That is the
staircase.

### `assign_fields(rules, tickets) -> list[str]`

```python
while unresolved:
    forced = {column for column in unresolved if len(candidates[column]) == 1}
    if not forced:
        raise ValueError("field order is not forced by elimination alone")
    for column in forced:
        (names[column],) = candidates[column]
    unresolved -= forced
    taken = {names[column] for column in forced}
    for column in unresolved:
        candidates[column] -= taken
```

Each round: every column with exactly one candidate left gets that field;
those fields are struck from every still-open column. On the example:

| round | forced | assignment | remaining sets |
|---:|---|---|---|
| 1 | column 0 `{row}` | 0 = row | 1: `{class}`, 2: `{class, seat}` |
| 2 | column 1 `{class}` | 1 = class | 2: `{seat}` |
| 3 | column 2 `{seat}` | 2 = seat | — |

Order `row, class, seat`, and reading my ticket `11,12,13` through it gives
class = 12, row = 11, seat = 13 — the statement's conclusion, pinned by
`test_my_ticket_reads_through_the_assignment`.

On the real input the same loop runs 20 rounds, one forced column per
round, because the candidate sets are a full staircase — sizes exactly
1 through 20, each nested in the next (`test_real_input_candidates_are_a_full_staircase`).
The first four rungs:

| column | size | candidates |
|---:|---:|---|
| 13 | 1 | route |
| 3 | 2 | route, seat |
| 9 | 3 | route, seat, type |
| 5 | 4 | arrival track, route, seat, type |

Round 1 assigns column 13 = route and strikes `route` everywhere, which
leaves column 3 holding only `seat`; round 2 assigns it, exposes `type`
in column 9; and so on down. The full forced sequence is: route, seat,
type, arrival track, zone, arrival location, row, train, departure
station, departure platform, departure track, departure location,
departure date, departure time, class, price, wagon, arrival station,
duration, arrival platform.

Two deliberate refusals are in the loop. If a round finds no singleton,
the sets are not a chain and elimination alone cannot finish — the code
raises rather than picking. And if two columns are ever forced to the same
field the input contradicts itself; that is checked after the loop.

### `part2(notes) -> int`

Filter by `invalid_values`, assign, then `math.prod` over the columns whose
assigned name starts with `departure`. On the real input the six departure
columns of my ticket are:

| column | field | my value |
|---:|---|---:|
| 2 | departure track | 61 |
| 6 | departure date | 257 |
| 15 | departure platform | 53 |
| 16 | departure time | 89 |
| 17 | departure station | 149 |
| 19 | departure location | 59 |

61 × 257 × 53 × 89 × 149 × 59 = 650,080,463,519. That is what the code
produces; see the Tests section for its verification status.

## 4. Why it is correct

**Part 1** is the statement transcribed: a value is invalid exactly when
no field's spans contain it, and the error rate is the sum of those over
the nearby tickets.

**Part 2** has two claims to separate.

*Candidate sets are necessary conditions.* If field F really occupies
column c, then every valid ticket's value in column c is a legitimate F
value, so F's spans accept all of them and F is in c's candidate set. The
converse is not true — a field can accept a whole column by accident — so
the sets over-approximate, and the elimination is what tightens them.

*Peeling singletons is sound.* The puzzle promises a consistent assignment
exists (a perfect matching of fields to columns inside the candidate
sets). A column whose set has shrunk to one field must, in *every* such
matching, hold that field; striking it from the other columns only removes
options no matching could use. So every assignment the loop makes is
forced, never guessed — hence the `ValueError` when nothing is forced:
that is the loop announcing it has reached the limit of what forcing can
prove, not a bug.

*When is peeling complete?* Whenever the sets form a **chain** (each is a
subset of the next). Then the smallest set is a singleton, striking its
field turns the next-smallest into a singleton, and induction finishes the
job in one round per column. Inputs for this puzzle are generated to have
that shape; the repo does not take that on faith, it pins it on the real
input as a test. Without the chain property the general problem is
bipartite matching — Hall's condition, augmenting paths — and a candidate
set structure like `{a, b}, {a, b}` has no forced move at all. The
`refuses_to_guess` test constructs exactly that and asserts the raise.

## 5. Complexity

With *n* nearby tickets, *k* columns, *m* fields, and 2 spans per rule:

- `part1` is O(*n* · *k* · *m*) span checks in the worst case, but
  `any()` short-circuits at the first accepting field, and the first rule
  in the file (`departure location: 45-535 or 550-961`) accepts most
  values on its own. Measured: **5,683** `accepts` calls for 4,760 values.
- `candidate_fields` is O(*n* · *k* · *m*) with much less short-circuiting:
  a (column, field) pair that *is* a candidate has to scan all 190 values
  before `all()` can say yes, and 210 of the 400 pairs are candidates.
  Measured: **58,045** `accepts` calls — ten times part 1's count, and
  each call spins up a generator over two spans.
- `assign_fields` is O(*k*²) set operations: at most *k* rounds, each
  touching *k* sets. Negligible.

Measured (`python\bench.py 16 -n 20`, best/median of 20):

| phase | best | median |
|---|---:|---:|
| parse | 0.417 ms | 0.437 ms |
| part 1 | 4.308 ms | 4.343 ms |
| part 2 | 32.355 ms | 32.594 ms |

Part 2 is 7.5× part 1 for the same asymptotic bound; that ratio is the
58k-vs-5.7k `accepts` count plus the part-1 filter being run again inside
part 2. Under 40 ms total, this sits between day 14 (49 ms) and the
sub-millisecond days — the algorithm is not the cost, the per-call
overhead of a Python generator inside `any()` is. Section 7 shows what
happens when that overhead is replaced by a table read.

## 6. If I were writing this in Rust

This is a day where the bit-level version *is* the readable version in
Rust, because `u32` masks, `count_ones()` and `trailing_zeros()` are
first-class. The port below was compiled (`rustc -O`, 1.93.1) and run on
the real input three times while writing this guide; it produces the same
two answers, with parse at **138–143 µs**, table build plus part 1 at
**14–15 µs**, and part 2 at **6–7 µs**. Parsing dominates — the actual
puzzle is a few thousand table reads.

**The decode ROM, literally.** One `u32` per possible value, bit *i* set
when field *i* accepts it:

```rust
fn build_lut(rules: &Rules, size: usize) -> Vec<u32> {
    let mut lut = vec![0u32; size];
    for (bit, (_, spans)) in rules.iter().enumerate() {
        for &(lo, hi) in spans {
            for v in lo..=hi {
                lut[v as usize] |= 1 << bit;
            }
        }
    }
    lut
}
```

Part 1 is then `lut[v] == 0`, and a column's candidate set is the AND of
its values' words — the same `all(accepts(...))` as Python, but as 190
bitwise ANDs instead of 190 generator evaluations:

```rust
let mut candidates = vec![all; width];
for ticket in nearby.iter().filter(|t| t.iter().all(|&v| lut[v as usize] != 0)) {
    for (c, &v) in ticket.iter().enumerate() {
        candidates[c] &= lut[v as usize];
    }
}
```

**Peeling is a popcount loop.** "Exactly one candidate" is
`count_ones() == 1`; "which one" is `trailing_zeros()`; "strike it
elsewhere" is `&= !(1 << bit)`:

```rust
while unresolved > 0 {
    let forced = (0..width)
        .find(|&c| field_of[c] == usize::MAX && candidates[c].count_ones() == 1)
        .expect("elimination stalled: candidate sets are not a chain");
    let bit = candidates[forced].trailing_zeros() as usize;
    field_of[forced] = bit;
    unresolved -= 1;
    for c in 0..width {
        if c != forced {
            candidates[c] &= !(1 << bit);
        }
    }
}
```

One difference from the Python loop is worth noticing: this takes the
*first* forced column per round rather than all of them, which is simpler
and, on a chain, identical in effect. The `expect` is the Python
`ValueError` — same refusal to guess, same message.

**Types.** `u32` masks cap the field count at 32; the input has 20. The
product overflows `u32` (the answer is 6.5 × 10¹¹), so the
`.map(|c| mine[c] as u64).product()` widening is not optional — Python's
integers hid that question entirely.

## 7. Possible optimization

**The lookup table in Python** (measured on the real input, best of 20):

| | shipping | table | ratio |
|---|---:|---:|---:|
| part 1 | 4.31 ms | 1.14 ms | 3.8× |
| part 2 | 31.8 ms | 1.50 ms | 21× |

The table itself costs 1.04 ms to build (20 fields × ~900 values of
`lut[v] |= 1 << bit`), and both figures include it. Part 2's 21× is the
58k generator-backed `accepts` calls becoming 3,800 integer ANDs. It stays
in the sidebar because `accepts(ranges, value)` says what the algorithm
*means* while `lut[value] & (1 << bit)` says how it is stored — and at
32 ms nobody is waiting.

**Sort once, peel in order.** Given the chain property, the columns
sorted by candidate-set size *are* the forced order, so the whole
`assign_fields` loop could be a single pass. That bakes the chain
assumption into the control flow instead of checking it each round; the
current loop's `raise` is the more honest shape.

**Skip the second filter.** `part2` recomputes `invalid_values` for all
238 tickets (the 4 ms part-1 cost again). `parse_input` could partition
tickets into valid/invalid once, since the split does not depend on which
part is asking — arguably that is what the "full parse" rule wants. Kept
separate here so `part1` and `part2` each read as the statement's
paragraph; the guide notes it rather than the code doing it.

---

## Tests

`python/tests/test_day16.py`, 25 tests plus the locked check:

- **Parse** — the example's rules, my ticket and nearby tickets; a field
  name with a space; the CRLF round trip (`\r\n\r\n` block separators).
- **Inclusive spans** — 1, 3, 5, 7 accepted and 0, 4, 8 rejected for
  `1-3 or 5-7`, parametrized from the statement's own sentence.
- **Part 1** — per-ticket `invalid_values` for all four example tickets,
  the sum 71, a ticket with two bad values, and my ticket being ignored
  even when it carries a bad value.
- **Part 2** — the staircase `{row} ⊂ {class, row} ⊂ {class, row, seat}`,
  the order `row, class, seat`, my ticket reading as class 12 / row 11 /
  seat 13, the departure product (two fields renamed to `departure …`,
  11 × 13), the empty product when nothing is a departure field, and an
  invalid ticket being discarded before deduction.
- **The refusal** — two interchangeable fields raise `ValueError`.
- **The real-input staircase** — sizes exactly 1…20 and nested; this is
  the identity the elimination leans on, pinned per the repo rule instead
  of asserted in prose. Skips when the gitignored input is absent.

`LOCKED = (21996, 650080463519)` — both submitted and accepted, so the
suite asserts them; a refactor that changes either answer fails. Before
submission, an independent bitmask implementation (the section 7 table,
and the Rust port) had reproduced both numbers, which was consistency, not
acceptance — the distinction the `check_locked` fixture exists to keep.

[`day16.md`](day16.md) carries both parts. The Part Two text was
backfilled from the puzzle rather than fetched from the site, and its
example — rules, tickets, the `row, class, seat` order and the 12/11/13
reading — is exactly what the part-2 tests execute, so the example at
least is verified even if the prose is from memory.
