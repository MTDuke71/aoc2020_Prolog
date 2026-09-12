# Day 23 Function Guide — Crab Cups

> Nine cups in a circle, labelled 1 to 9 in some order, and a crab that
> shuffles them by rule: lift the three cups after the current one, drop
> them back in after the cup labelled one less than the current one
> (skipping cups in hand, wrapping from 1 to 9), then step to the next
> cup. Part 1 is 100 moves and reads the circle from cup 1. Part 2 pads
> the circle to a **million** cups and makes **ten million** moves, and
> that scale is the whole puzzle: a list that shifts on every move would
> take seventeen hours. The shipping solution stores the circle as a
> **successor table**, `nxt[label]` = the cup clockwise of `label`, so a
> cup never moves and a move is three loads and three stores. One
> engine, `play(cups, moves, total)`, does both parts; part 2 runs in
> 1.9 s, the year's second slowest phase after day 15's 30-million-turn
> recitation, and for the same reason: it is ten million dependent
> random reads into a table, which no language makes free. The pinned
> content is the statement's ten-move trace line by line, a literal
> list-shuffling oracle that the table must agree with on random
> circles, the invariant that the table is always one cycle, and one
> identity the trace does not show: through fresh padding the current
> cup strides four labels per move, which on the real input makes the
> first 250,000 moves a straight walk.

Source: [`python/day23.py`](../../python/day23.py) ·
Tests: [`python/tests/test_day23.py`](../../python/tests/test_day23.py)

---

## 1. The problem

The input is one line, `496138527`: nine cups, clockwise, the first one
the *current cup*. A **move**:

1. Lift the three cups immediately clockwise of the current cup out of
   the circle.
2. Pick the **destination**: the cup labelled one less than the current
   cup. If that label is in hand, subtract one again; below 1, wrap to
   the highest label. (Only three cups are in hand, so at most three
   labels are skipped.)
3. Drop the three cups back in immediately clockwise of the
   destination, in the order they were lifted.
4. The new current cup is the one now immediately clockwise of the old
   current cup.

The statement traces ten moves on `389125467`. Move 1: current 3, lift
8 9 1, destination 2, circle becomes `3 (2) 8 9 1 5 4 6 7`. Move 2 is
the interesting one for the destination rule: current 2, lift 8 9 1,
count down to 1 (in hand), wrap to 9 (in hand), 8 (in hand), land on 7.
After 10 moves the cups clockwise from 1 read `92658374`; after 100,
`67384529`, which is the part 1 answer format: the circle read from cup
1 with cup 1 itself left out.

Part 2 changes the numbers and nothing else. The circle is the nine
input cups followed by 10, 11, ... up to **1,000,000**, clockwise, and
the crab makes **10,000,000** moves. The answer is the product of the
two cups clockwise of cup 1: on the sample they are 934001 and 159792,
product 149245887792.

## 2. Representation

**The circle is a list `nxt` of length n + 1 with `nxt[label]` = the
label of the cup clockwise of `label`.** Index 0 is unused so that a
label is its own index. The sample's starting circle is:

```text
label   1  2  3  4  5  6  7  8  9
nxt     2  5  8  6  4  7  3  9  1
```

Read it as a register file of *next* pointers. It is a singly linked
list with the nodes stored in an array indexed by their payload, and
since the payloads are exactly 1..n, the array has no gaps. Every
operation the crab makes is a pointer operation:

- "the three cups after the current cup" is `nxt[cur]`, `nxt[a]`,
  `nxt[b]`: three dependent loads;
- "remove them from the circle" is one store, `nxt[cur] = nxt[c]`;
- "the cup labelled `dest`" is the index `dest`, no search;
- "put them after `dest`" is two stores.

Nothing shifts, and the cost of a move does not depend on how many cups
there are or where the destination happens to be. That is the entire
difference between a solution and no solution here; section 7 measures
the alternative.

The natural first representation, a Python list of labels in circle
order, does exactly what the statement says and is fine for part 1
(0.05 ms). It fails part 2 on two counts per move: finding the
destination is a linear `index`, and the splice shifts everything after
it. The test module keeps that version as the oracle, `literal_moves`,
because "does the table agree with the literal statement" is the
question worth asking, and the literal version is short enough to
trust.

**The current cup lives outside the table**, as a plain integer, and
`play` returns both. The tests need the current cup to read the circle
the way the statement prints it (from the current cup); the parts do
not, since both read from cup 1.

**Padding is construction, not representation.** Part 2's circle is
the input's cups, then `len(cups)+1 .. total`, then back to the first
input cup. `nxt` is initialised to `range(1, n + 2)`, i.e. every label
followed by the next integer, which is already right for all of the
padding except its last cup; then the input's cups and the closing link
are written over the top.

## 3. Function walkthrough

### `parse_input(raw) -> Cups`

`raw.strip()` takes the newline (and a Windows `\r`) off, then each
character is one cup. The CRLF case is one assertion: `"389125467\r\n"`
parses to the same nine cups. Two rejections: anything that is not all
digits, and any set of digits that is not exactly `1..n` once each
(a `0`, a repeat, a missing label). The destination rule counts down
through the labels, so it needs them contiguous; the check makes that a
parse error rather than a wrong answer.

### `play(cups, moves, total=None) -> (nxt, cur)`

The engine. Build the table as described, then:

```python
cur = cups[0]
for _ in range(moves):
    a = nxt[cur]
    b = nxt[a]
    c = nxt[b]
    nxt[cur] = nxt[c]

    dest = cur - 1 if cur > 1 else n
    while dest == a or dest == b or dest == c:
        dest = dest - 1 if dest > 1 else n

    nxt[c] = nxt[dest]
    nxt[dest] = a
    cur = nxt[cur]
return nxt, cur
```

Move 1 of the sample on the table. Start with the table above and
`cur = 3`:

```text
a, b, c = nxt[3], nxt[8], nxt[9]  = 8, 9, 1
nxt[3]  = nxt[1] = 2                      3 now points past the three
dest    = 2                               not in hand, no wrap
nxt[1]  = nxt[2] = 5                      last lifted cup points at what followed dest
nxt[2]  = 8                               dest points at the first lifted cup
cur     = nxt[3] = 2

label   1  2  3  4  5  6  7  8  9
nxt     5  8  2  6  4  7  3  9  1         read from 3: 3 2 8 9 1 5 4 6 7
```

That is the statement's `3 (2) 8 9 1 5 4 6 7`. Three entries changed
(`nxt[3]`, `nxt[1]`, `nxt[2]`); six did not.

Move 2 is the countdown case. `cur = 2`, `a, b, c = 8, 9, 1`,
`nxt[2] = nxt[1] = 5`. `dest` starts at 1, which is `c`; down to 0,
wrap to 9, which is `b`; 8 is `a`; 7 is free. Then `nxt[1] = nxt[7] =
3`, `nxt[7] = 8`, `cur = nxt[2] = 5`, and the circle from 3 reads
`3 2 5 4 6 7 8 9 1`, the statement's move 3 line.

Two details of the loop:

- The `while` compares against `a`, `b`, `c` separately rather than
  `dest in (a, b, c)`. Both were timed (section 7); they are the same
  speed, and the separate form was kept because it does not build a
  tuple ten million times for no reason.
- `cur = nxt[cur]` after the splice is right because `dest` is never
  `cur` (the countdown starts at `cur - 1` and only goes down, and it
  cannot wrap all the way back up to `cur` since it stops within three
  steps), so `nxt[cur]` is still the cup that was after the three
  lifted ones.

### `clockwise_from(nxt, label, count) -> list[int]`

Walk `count` steps from `label` and collect the cups, `label` itself
excluded. Part 1 uses it with `count = n - 1` to read the whole circle
after cup 1; part 2 with `count = 2`.

### `part1(cups)` and `part2(cups)`

`play(cups, 100)` and the eight labels after 1 joined as a number;
`play(cups, 10_000_000, total=1_000_000)` and the product of the two
labels after 1.

## 4. Why it is correct

**The statement's trace is pinned line by line.** `TRACE` in the test
module is the ten `cups:` lines, each with its `pick up` and
`destination`, transcribed from the statement. For each move k in
0..9, `play(sample, k)` must give the circle read from the current cup
equal to line k+1, the three cups after the current cup equal to that
line's pick-up, and after one more move the destination must point at
the first lifted cup. Then the `final` line, the current cup 8 after
ten moves, `92658374` after ten, `67384529` after a hundred. A wrong
splice order, a wrong wrap, a wrong new-current rule: each changes a
line.

**The literal oracle agrees with the table on circles the statement
does not show.** `literal_moves` is the statement on a list: pop three,
count down, `index` the destination, splice, rotate. It is first
checked against the same trace, and then it and the table are compared
after every one of 200 moves on five shuffled nine-cup circles, and
after every one of 300 moves on the sample padded to 40 cups. The
padded run is long enough for the current cup to leave the nine input
cups, cross the padding, wrap round the top and come back, so the
padding construction and the wrap-to-`total` rule are both covered by
something independent of the table.

**The table is always a single cycle.** A successor table is a
permutation of 1..n; the crab's circle is that permutation having
exactly one cycle. The test walks the table from the current cup after
each of the first 100 moves and checks it visits all nine labels and
returns. On the real part 2 table the same walk after ten million
moves visits all 1,000,000. A splice that dropped a cup (say, writing
`nxt[dest] = a` before reading `nxt[dest]`) would break the cycle into
two, and this catches it.

**The countdown is bounded by three skips**, since only three cups are
ever in hand. Move 2 of the trace is the worst case (skip, wrap, skip,
skip) and is its own test. On the real input's ten million moves the
countdown skipped nothing on 9,881,450, once on 114,019, twice on
4,529, three times on **2**, and wrapped at 1 on 10 moves. The
destination is almost always simply `cur - 1`.

**Through fresh padding the current cup strides four labels per move.**
While the current cup `k` is inside padding that no move has touched
yet, the three cups after it are `k+1, k+2, k+3`, the destination is
`k-1` (not in hand, and no wrap since `k-1 >= 10`), so the three are
dropped *behind* the current cup and the new current cup is `k+4`. On
the sample padded to 200 the current cup goes `3, 2, 5, 10, 14, 18,
22, ...` and the test walks the whole stride. On the real million-cup
circle the walk runs from move 5 (current cup 12) to move 250,002
(current cup 1,000,000); the first 2.5 % of the game is a straight
line through memory, and the interesting mixing is the other 97.5 %.
The identity is pinned as a test on the small circle, and the
real-input numbers are stated here because they were measured, not
because anything depends on them.

## 5. Complexity

A move is O(1): three loads, three stores, and a countdown of at most
four steps. `play` is O(moves) time on top of O(n) to build the table,
and O(n) space for the table, which is the input to part 2 (a million
entries) rather than anything the algorithm accumulates.

| | part 1 | part 2 |
| --- | ---: | ---: |
| cups | 9 | 1,000,000 |
| moves | 100 | 10,000,000 |
| countdown skips (0 / 1 / 2 / 3) | 65 / 28 / 7 / 0 | 9,881,450 / 114,019 / 4,529 / 2 |
| wraps | 18 | 10 |
| stride-4 phase | – | moves 5 to 250,002 |
| cups after 1 | `69425837` | 843145, 259603 |

Reading the rows: a *countdown skip* is one step of the destination
search that landed on a cup in hand and had to continue (at most three,
since three cups are in hand; the four counts are moves needing 0, 1, 2
and 3 of them). A *wrap* is a move whose countdown fell below label 1
and jumped to the top label, 9 or 1,000,000. The *stride-4 phase* is the
walk through untouched padding from section 4, where the current cup
advances four labels per move; part 1 has no padding. *Cups after 1* is
what the answer is read from: all eight labels clockwise of cup 1 in
part 1, the two whose product is asked for in part 2.

Measured on the real input (`python\bench.py 23 -n 5`, best / median):

| phase  |      best |    median |
| ------ | --------: | --------: |
| parse  |  0.001 ms |  0.002 ms |
| part 1 |  0.015 ms |  0.016 ms |
| part 2 | 1,896 ms  | 2,010 ms  |

About 190 ns per move. Second slowest day of the year after day 15
(3.8 s), ahead of day 11 (0.59 s) and day 22 (0.43 s), and it is day
15's shape exactly: a loop whose body is a handful of dependent
indexed reads, where the CPU cannot start the next move's loads until
this move's `cur = nxt[cur]` has come back from memory. The table is
a million CPython `int` objects behind a million pointers; measured,
the list is 8.0 MB of pointers and the integers above 256 are 28 bytes
each, so a move's random reads are walking about 36 MB, not 4.

## 6. If I were writing this in Rust

The same table as `Vec<u32>`, and the loop is the Python loop with
`as usize` on every index:

```rust
fn play(cups: &[u32], moves: usize, total: usize) -> Vec<u32> {
    let n = total as u32;
    let mut nxt: Vec<u32> = (1..=n + 1).collect();
    let order: Vec<u32> = cups.iter().copied().chain(cups.len() as u32 + 1..=n).collect();
    for w in order.windows(2) { nxt[w[0] as usize] = w[1]; }
    nxt[*order.last().unwrap() as usize] = order[0];
    let mut cur = cups[0];
    for _ in 0..moves {
        let a = nxt[cur as usize];
        let b = nxt[a as usize];
        let c = nxt[b as usize];
        nxt[cur as usize] = nxt[c as usize];
        let mut dest = if cur > 1 { cur - 1 } else { n };
        while dest == a || dest == b || dest == c {
            dest = if dest > 1 { dest - 1 } else { n };
        }
        nxt[c as usize] = nxt[dest as usize];
        nxt[dest as usize] = a;
        cur = nxt[cur as usize];
    }
    nxt
}
```

Compiled with `rustc -O` (1.93.1) and run three times on the real
input while writing this guide, best of 5 for part 2. Same two answers,
and the sample's 149245887792. Part 1 0.0005 ms; part 2 **146 ms**,
about 13× the Python. The `u32` is the point: the whole table is 4 MB,
which is inside a modern last-level cache, where Python's 36 MB is
not, and the loop is otherwise identical. There is no borrow-checker
story here at all, one `Vec` mutated in place, and no reason to reach
for a linked list type, which is the Rust lesson of the day: a linked
list *in an array indexed by payload* is what you write when the
payloads are dense integers, and it is what a `LinkedList<u32>` would
never give you, because you could not find node `dest` in O(1).

## 7. Possible optimization

All measured on the real input, best of 3 in a scratch script; every
variant produces 218882971435.

| variant | part 2 |
| --- | ---: |
| shipping (`list`, three comparisons in the countdown) | 1.85 s |
| `dest in (a, b, c)` instead of the three comparisons | 1.83 s |
| wrap by `(dest - 2) % n + 1` instead of a branch | 1.93 s |
| `array('i')` instead of `list` | 2.68 s |
| the literal list (`pop`, `index`, splice) | 6.2 s per **1,000** moves; 17 h projected |

There is no algorithmic shortcut on offer: the crab's rule is a
pseudo-random permutation walk with no known closed form, so ten
million moves means ten million moves, and the question is only how
much each costs. The countdown variants are within noise of each
other, because the countdown almost never runs (section 4).

`array('i')` is the tempting one, since it stores 4-byte integers like
the Rust `Vec<u32>` and would shrink the table nine-fold. It is 45 %
*slower*: every read boxes the value into a fresh `int` object and
every write unboxes, and that per-access cost outweighs the cache
benefit for an interpreter that was already spending most of the move
on bytecode dispatch. NumPy has the same problem for scalar indexing.
The dense table only pays off when the loop itself is compiled, which
is the 13× in section 6, and the honest summary is the one day 15's
guide reached: this is a memory-latency benchmark, and the shipping
Python is the readable statement of the algorithm at the price the
interpreter charges for it.
