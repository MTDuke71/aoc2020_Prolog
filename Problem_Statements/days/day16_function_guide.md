# Day 16 Function Guide — Ticket Translation

> The puzzle is really two filters in series: first, reject invalid nearby
> tickets by checking whether each value falls inside at least one field
> range; then, among the surviving tickets, deduce which field name belongs
> to each column and multiply the values from the fields that start with
> `departure`.

Source: [`python/day16.py`](../../python/day16.py) ·
Tests: [`python/tests/test_day16.py`](../../python/tests/test_day16.py)

---

## 1. The problem

Each ticket has a fixed ordering of fields, but the labels are scrambled. The
input gives:

- a set of field rules like `class: 1-3 or 5-7`
- your ticket
- nearby tickets from the same train service

A value is valid if it sits in at least one range for at least one field.
Part 1 asks for the sum of all invalid values in the nearby tickets. Part 2
asks which field occupies which column, then multiplies the values for the
columns whose names begin with `departure`.

The shape of the challenge is therefore:

1. parse the notes into rules and ticket data,
2. identify invalid values,
3. remove invalid tickets,
4. deduce a unique field-to-column mapping,
5. apply the departure product.

## 2. Representation

The cleanest parse is a dictionary with three pieces of data:

- `rules`: `name -> [(lo, hi), ...]`
- `my_ticket`: a list of ints
- `nearby_tickets`: a list of lists of ints

That preserves the original problem structure directly: every rule is a set of
inclusive intervals, and every ticket is a sequence of positions. The code does
not try to build a more abstract model; it keeps the exact objects the
statement describes.

A single helper does the heavy lifting:

```python
value_matches_rule(value, ranges)
```

It answers exactly the question we need over and over: "is this integer valid
for this rule?"

## 3. Function walkthrough

### `parse_input(raw) -> dict`

The input is block-structured: rules, then `your ticket:`, then `nearby
tickets:`. The parser walks the stripped lines in order and accumulates:

- each field name and its interval list,
- the player's ticket as a list of ints,
- every nearby ticket as a list of ints.

CRLF is tolerated by `splitlines()` and `strip()` on each line; a stray `\r`
that survives a raw `split("\n")` is not a problem here.

### `value_matches_rule(value, ranges) -> bool`

This is a direct translation of the statement: a value is valid if any range
contains it.

### `field_matches_any(value, rules) -> bool`

A ticket value must match at least one field somewhere in the whole notes set.
This is the part-1 invalidity test, and it is also the filter used for valid
nearby tickets in part 2.

### `part1(parsed) -> int`

The function sums every value from every nearby ticket that is not valid for any
field.

```python
for ticket in nearby_tickets:
    for value in ticket:
        if not field_matches_any(value, rules):
            total += value
```

This is exactly the puzzle's "ticket scanning error rate".

### `part2(parsed) -> int`

This is the deduction phase:

1. Keep only tickets where every value is valid for at least one field.
2. For each column index, compute the set of field names whose ranges accept
   every value in that column across the valid tickets.
3. Eliminate fields that have already been assigned to other columns.
4. Once each column has exactly one candidate left, resolve the mapping.
5. Multiply the player's values on every column whose field name starts with
   `departure`.

The candidate-set elimination is the key detail. If a field is already known to
occupy one column, remove it from all other columns; repeated elimination yields
one unique field per column.

## 4. Why it is correct

Part 1 is a direct reading of the rules:

- a value is invalid exactly when it matches no rule anywhere,
- so summing those invalid values is the ticket scanning error rate.

Part 2 is correct because each field name is retained as a candidate for a
position only if it matches all valid tickets at that position. Any candidate
that appears in a different already-solved position is removed. When every
column has exactly one candidate, the mapping is unique and consistent with all
valid tickets.

The algorithm does not guess: it filters by the rule sets verified on every
valid ticket. A field that does not fit a specific column can never survive the
elimination step, and the remaining one-to-one mapping is exactly the field
ordering the puzzle asks for.

## 5. Complexity

Let:

- `n` = number of nearby tickets
- `m` = number of fields
- `k` = number of values per ticket

Then:

- part 1 is O(n · k · m) in the worst case, because each value is checked
  against the union of all field ranges,
- part 2 is dominated by the column-candidate scan across valid tickets, also
  O(n · k · m), plus the elimination pass, which is at most a few passes over
  the columns.

The input sizes are small enough that the straightforward set-and-filter
approach is both clear and fast.

## 6. If I were writing this in Rust

The direct Rust translation keeps the same structure:

```rust
fn value_matches_rule(value: i32, ranges: &[(i32, i32)]) -> bool {
    ranges.iter().any(|(lo, hi)| *lo <= value && value <= *hi)
}
```

Rules live in a `HashMap<String, Vec<(i32, i32)>>`, the player's ticket is a
`Vec<i32>`, and nearby tickets are `Vec<Vec<i32>>`. This mirrors the Python
model exactly: the code is an interval checker first, then a candidate-elimination
problem.

The language difference is mostly about data layout and iteration speed, not
algorithmic structure. A Rust `HashMap` for the rules is easy and clear, and the
candidate sets are naturally `HashSet<String>` or `BTreeSet<String>` for
elimination. The algorithmic shape stays the same as the Python version: first
filter invalid tickets, then solve a unique mapping by removing impossible
candidates.

## 7. Possible optimization

The obvious optimization is to precompute each field's valid intervals and
check them by position rather than re-scanning all rules for each value. In a
larger problem, a vector of valid-column masks (bitsets) would make the
candidate elimination faster and more compact. That would be a micro-optimization,
not a rewrite: the current version is already simple, readable, and fast enough
for the task size.
