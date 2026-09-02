# Day 15 Function Guide — Rambunctious Recitation

> The shortest solution in the repo, and the first day where the cost is
> not the algorithm but the *iteration count*: there is no part-2 insight
> to find, just the same loop run 14,851× longer. The interesting
> engineering question shifts from "what's the trick?" to "what does one
> loop iteration cost, and where does the time actually go?" — which makes
> this the repo's first day that is really a benchmark of the language.

Source: [`python/day15.py`](../../python/day15.py) ·
Tests: [`python/tests/test_day15.py`](../../python/tests/test_day15.py)

---

## 1. The problem

The Elves play a memory game. Starting from a short list of seed numbers
(the input — `0,1,4,13,15,12,16` here), each subsequent turn looks at the
most recently spoken number:

- if it had never been spoken before that, say **0**;
- otherwise say its **age**: how many turns apart its last two
  occurrences are.

Part 1 asks for the 2,020th number spoken; part 2 asks for the
30,000,000th. Same game, different stopping point — the parts share every
line of logic and differ only in one constant.

This sequence has a name: for seed `0` it is **Van Eck's sequence**,
OEIS [A181391](https://oeis.org/A181391). What is known about it is mostly
negative — no closed form, no known way to jump to term *n* without
generating terms 1 through *n* − 1. That is the puzzle's quiet joke: part 2
looks like it demands a day-13-style number-theory shortcut, and the actual
answer is "there isn't one; walk the sequence."

## 2. Representation: one table plus one register

The naive state is the full history of every number spoken. The game never
needs that. Each turn consults exactly one fact — *when was the current
number previously spoken?* — so the whole state is:

- `last_seen: dict` — number → the turn it was most recently spoken;
- `current: int` — the number spoken on the turn just finished.

The load-bearing choice is what `last_seen` **excludes**: the current
number's own latest occurrence. At the top of each iteration, `current`
was spoken on turn `turn`, but the table still points at the time *before*
that. "How many turns apart are its last two occurrences" is then a single
lookup and a subtraction. Update the table afterwards and the same
property holds for the next iteration.

In machine terms: a tag store plus one register, with a
read-before-write discipline per cycle — read the old tag, then let this
turn's write land.

## 3. Function walkthrough

### `parse_input(raw) -> list[int]`

One line, comma-separated: `raw.strip().split(",")` mapped through `int`.
The `strip()` swallows the trailing newline in either flavour, so a CRLF
input costs nothing (day 6's `\r` bug, guarded by test as always).

### `play(starting, final_turn) -> int` — the engine

```python
if final_turn <= len(starting):
    return starting[final_turn - 1]

last_seen = {number: turn for turn, number in enumerate(starting[:-1], start=1)}
current = starting[-1]
for turn in range(len(starting), final_turn):
    previous = last_seen.get(current)
    last_seen[current] = turn
    current = 0 if previous is None else turn - previous
return current
```

The seeding puts every starting number *except the last* into the table —
the last one is the game's first `current`, and per section 2 its own turn
deliberately stays out of the table until the loop processes it.

Trace on the statement's `0,3,6`. After seeding: table `{0:1, 3:2}`,
current `6`.

| `turn` | `current` in | table says | speaks | table after |
|---:|---:|---|---:|---|
| 3 | 6 | never seen | 0 | `{0:1, 3:2, 6:3}` |
| 4 | 0 | turn 1 | 4−1 = 3 | `{0:4, 3:2, 6:3}` |
| 5 | 3 | turn 2 | 5−2 = 3 | `{0:4, 3:5, 6:3}` |
| 6 | 3 | turn 5 | 6−5 = 1 | `{0:4, 3:6, 6:3}` |
| 7 | 1 | never seen | 0 | … `1:7` |
| 8 | 0 | turn 4 | 8−4 = 4 | … `0:8` |
| 9 | 4 | never seen | 0 | … `4:9` |

Reading the "speaks" column downward from turn 3: 0, 3, 3, 1, 0, 4, 0 —
turns 4 through 10 of the statement's walkthrough, exactly. (Turn 5 is the
row to stare at: 0 was spoken on turn 4, but the table still said turn 1,
which is precisely why the age came out 3.)

Note the loop variable is offset by one from the row it produces: iteration
`turn` computes the number spoken on turn `turn + 1`. The loop therefore
runs to `final_turn` *exclusive*, and `current` on exit is the
`final_turn`-th number. Off-by-one country — which is why the tests pin the
whole 10-turn trace rather than just the 2,020th endpoint.

The early return handles `final_turn` inside the seed list (read it off
directly), and the dict-comprehension seeding handles a repeated starting
number for free: later occurrences overwrite earlier, which is exactly
"most recently spoken".

### `part1` / `part2` / `solve`

`play(starting, 2_020)` and `play(starting, 30_000_000)`. Nothing else —
the constants `PART1_TURNS` / `PART2_TURNS` are the entire difference
between the parts.

## 4. Why it is correct

The invariant, stated once: **at the top of iteration `turn`, `current`
was spoken on turn `turn`, and `last_seen[n]` holds the most recent turn
`n` was spoken on, counting only turns before `turn`.**

- It holds on entry: seeding records turns 1 … len−1, and `current` is the
  number from turn len, absent from the table.
- Each iteration preserves it: `previous` is read under the invariant (so
  it is the occurrence *before* the current one — the exact quantity "how
  many turns apart" refers to), then `last_seen[current] = turn` restores
  the table for the now-complete turn, and the new `current` is the number
  the rules say turn `turn + 1` speaks: 0 if `previous` was absent, else
  `turn - previous`.

Everything else is the statement transcribed. The tests carry the burden
per the repo rule: the full 10-turn trace, all seven 2,020th-number
examples, the repeated-seed edge, and the 30,000,000th-number example
(175594 for `0,3,6`).

## 5. Complexity

O(*n*) time for *n* turns — one dict lookup, one dict store, one subtract
per turn. Space is the number of *distinct* values spoken, which is where
the measured shape gets interesting (real input, `0,1,4,13,15,12,16`):

| turns | distinct numbers spoken | largest number spoken |
|---:|---:|---:|
| 2,020 | 387 | 1,841 |
| 30,000,000 | 3,611,898 | 29,419,548 |

Two things worth noticing in that table:

- About **12% of turns speak a brand-new number**, even 30M turns in
  (3,611,892 of the 30M turns said 0 for that reason). The table keeps
  growing; there is no steady state to converge to.
- Every number spoken is either a seed or an age, and an age is a gap
  between two turns ≤ *n*, so **every spoken value is < n**. The largest
  actually seen, 29,419,548, sits just under the 30M ceiling. That bound
  is what licenses the flat-array variant in the sidebar.

Measured (`python\bench.py 15 -n 5`, best/median of 5):

| phase | best | median |
|---|---:|---:|
| parse | 0.001 ms | 0.001 ms |
| part 1 | 0.106 ms | 0.114 ms |
| part 2 | 3,562 ms | 3,619 ms |

Part 2 is ~34,000× part 1 for 14,851× the turns — the extra factor is the
table outgrowing the caches. And at 3.6 s this is the new slowest day in
the repo by a factor of ~6 (day 11's cellular automaton, at 574 ms total
on the same bench run, was the previous holder), with nothing to show for
it algorithmically: ~120 ns per iteration is simply what a dict probe, a
dict store, and interpreter dispatch cost.

## 6. If I were writing this in Rust

This day is the language-cost benchmark, so it is the day Rust changes
the experience most. The function below was compiled (`rustc -O`, 1.93.1)
and run on the real input while writing this guide: part 2 in
**272–339 ms** across three runs — the same answers, ~13× faster — and
the interesting choices are all about memory.

**The table becomes a `Vec<u32>`, not a HashMap.** The bound from
section 5 — every spoken value < *n* — means the table can be a flat
vector indexed by the number itself, with 0 as the "never spoken"
sentinel (turns are 1-based, so 0 is free):

```rust
fn play(starting: &[u32], final_turn: u32) -> u32 {
    let mut last_seen = vec![0u32; final_turn as usize];
    for (i, &n) in starting[..starting.len() - 1].iter().enumerate() {
        last_seen[n as usize] = i as u32 + 1;
    }
    let mut current = *starting.last().unwrap();
    for turn in starting.len() as u32..final_turn {
        let previous = last_seen[current as usize];
        last_seen[current as usize] = turn;
        current = if previous == 0 { 0 } else { turn - previous };
    }
    current
}
```

`u32` everywhere is deliberate: 30M turns fit comfortably, and the table
is then 120 MB — of which the 3.61M entries actually touched
(section 5's distinct count) are ~14 MB, still far past L2. This loop is
a *memory latency* benchmark — each iteration's `last_seen[current]` is a
data-dependent read at an unpredictable index, so the CPU spends much of
its time waiting on cache misses, not computing. That is also why the
Python/Rust gap here (~13×) is smaller than a pure-compute loop would
show: both languages stall on the same misses; Rust just stops paying
interpreter overhead in between.

**`FxHashMap` is the wrong call this time.** Day 14's guide reached for
it; here the direct-indexed `Vec` beats any hash map — the "hash" is the
identity function and the collision rate is zero. The EE framing: it's a
direct-mapped tag RAM with a 25-bit index, and you never build a CAM when
the index fits in the address lines.

**The sentinel merges two branches.** Python distinguishes `None` from
turn numbers; the Rust version overloads 0 as "never seen", which works
only because turns are 1-based. That is exactly the kind of implicit
invariant worth a `debug_assert!` — or a comment — because a refactor to
0-based turns silently corrupts it.

## 7. Possible optimization

**Flat array in Python** (measured, single runs on the real input): the
same direct-indexed table via `array("i", bytes(4 * final_turn))` runs
part 2 in **2.4 s vs the dict's 3.6 s** — a 1.5× win from skipping the
hashing, kept to the sidebar because `last_seen.get(current)` says what
the algorithm *means* while the array version says how it's stored. One
trap for the porting reader: size the table by
`max(final_turn, max(starting) + 1)`, or a seed larger than a small
`final_turn` indexes out of bounds (the dict never cares).

**Numpy does not apply.** Each turn's read depends on the previous turn's
write — a serial recurrence with a data-dependent index. There is no
vectorization to be had; this is the same reason there's no closed form.

**Stop early, sometimes.** Nothing here — both parts want a fixed turn
count, and since ~12% of turns still speak new numbers at 30M there is no
cycle to detect. The honest optimizations are a faster runtime (PyPy runs
this style of loop well) or a faster language, which is section 6.

---

## Tests

`python/tests/test_day15.py`, 23 tests:

- **The statement trace** — turns 1–10 of `0,3,6`, parametrized. This is
  the test that pins the invariant's bookkeeping; every later test would
  still pass with an off-by-one that shifted the whole sequence, but this
  one fails loudly.
- **All seven 2,020th-number examples** from the statement.
- **The part-2 example** — `0,3,6` → 175594 at 30M turns. One of the
  seven, not all: each costs ~4 s of looping and the short examples
  already pin the mechanism; one at full scale catches anything that only
  breaks at size.
- **Edges** — a `final_turn` inside the seed list, and a repeated seed
  (`0,0`: turn 3 must speak an age, not 0).
- **CRLF** — the standard Windows-download guard.

`LOCKED = (1665, 16439)` — both submitted and accepted, so the suite
asserts them. A refactor that changes either answer fails.

[`day15.md`](day15.md) now carries both parts. The Part Two text was
re-checked against sections 1 and 4 after the backfill: the target is the
30,000,000th number, and `0,3,6` → 175594 is the statement's first
example, the one the test module pins at full scale (its other six
part-2 examples stay unpinned by choice — each costs ~4 s, and one at
scale plus all seven at 2,020 already covers the mechanism).
