# Day 14 Function Guide — Docking Data

> The first day written after this repo went Python-only, and a good one to
> land on: it is an **emulator**, so it rhymes with
> [Day 08](day08_function_guide.md)'s accumulator machine, but the twist in
> Part Two is not a new algorithm — it is the *same instruction stream read
> under different semantics*, exactly the reparameterisation trick from
> [Day 12](day12_function_guide.md).

Source: [`python/day14.py`](../../python/day14.py) ·
Tests: [`python/tests/test_day14.py`](../../python/tests/test_day14.py)

---

## 1. The problem

The input is a program for a 36-bit machine with two instructions:

```text
mask = XXXXXXXXXXXXXXXXXXXXXXXXXXXXX1XXXX0X
mem[8] = 11
```

A `mask` line loads a 36-character mask, which stays in force until the
next `mask` line. A `mem[a] = v` line performs a store. The answer to both
parts is the sum of all values left in memory at the end.

The two parts apply the mask to different things:

| Mask char | Part 1 — applies to the **value** | Part 2 — applies to the **address** |
|---|---|---|
| `0` | overwrite the bit with 0 | leave the bit unchanged |
| `1` | overwrite the bit with 1 | overwrite the bit with 1 |
| `X` | leave the bit unchanged | **floating** — write to both |

Read that table twice. `0` and `X` swap roles between the parts, and `X`
stops being "do nothing" and becomes "do everything". Part 1 performs one
store per instruction; part 2 performs 2^k, where k is the number of `X`
bits in the current mask.

## 2. Representation choices

### Memory is a dict, not an array

The address space is 2^36 words — 68 billion. Allocating it is out of the
question, and unnecessary: the real input touches **71,385** distinct
addresses. A `dict[int, int]` holds exactly what was written.

The statement's aside that "the entire address space begins initialized to
`0`" turns out to cost nothing. Addresses never written are absent from
the dict, and absent addresses contribute 0 to a sum, which is the same
thing. No initialization step is needed anywhere.

### The parse groups writes under their governing mask

`parse_input` returns `list[tuple[str, list[tuple[int, int]]]]` — a list of
`(mask, [(address, value), ...])` blocks:

```python
[("XXXXXXXXXXXXXXXXXXXXXXXXXXXXX1XXXX0X", [(8, 11), (7, 101), (8, 0)])]
```

A flat instruction list would force both parts to carry a "current mask"
variable and branch on instruction type in their main loop. Since the mask
is *stated* to govern everything until the next mask line, that structure
is in the input already — the parse just makes it explicit. Both parts then
read as a plain nested loop with no state of their own.

This is the repo's [full-parse rule](../../CLAUDE.md) doing real work:
`parse_input` is not a line splitter.

### The mask stays a string

`parse_input` deliberately does *not* decode the mask into integers, even
though both parts want integers. The two parts want **different**
integers — part 1 wants an OR mask and an AND mask, part 2 wants a list of
bit positions — so decoding in the parser would mean computing the wrong
one, or computing both and wasting one. The string is the common form; each
part decodes it its own way.

## 3. Part One: two integers per mask

The whole of part 1 is this identity:

```python
def value_masks(mask):
    return int(mask.replace("X", "0"), 2), int(mask.replace("X", "1"), 2)
```

Call them `ones` and `zeros`. Then a masked value is:

```python
value & zeros | ones
```

Why that works, bit by bit:

| Mask char | bit in `ones` | bit in `zeros` | `& zeros` does | `\| ones` does | net |
|---|---|---|---|---|---|
| `1` | 1 | 1 | nothing | forces 1 | **1** |
| `0` | 0 | 0 | forces 0 | nothing | **0** |
| `X` | 0 | 1 | nothing | nothing | **unchanged** |

The `X` row is the load-bearing one: an `X` position is 0 in `ones` and 1
in `zeros`, so it is the identity element for *both* operations. That is
why one AND and one OR suffice, with no third "which bits are floating"
mask to consult.

Trace the statement's first write. Mask
`XXXXXXXXXXXXXXXXXXXXXXXXXXXXX1XXXX0X`, value 11:

```text
value   000000000000000000000000000000001011   11
zeros   111111111111111111111111111111111101   X->1, 0->0
& zeros 000000000000000000000000000000001001    9   (the 2s bit forced off)
ones    000000000000000000000000000001000000   X->0, 1->1
| ones  000000000000000000000000000001001001   73  (the 64s bit forced on)
```

73, as the statement says. The other two worked examples — 101 masking to
itself, and 0 masking to 64 — are in the test module as a parametrized
table.

That "leaves X alone" claim is not left as prose. `test_value_masks_leave_x_positions_alone`
pins it directly: under an all-`X` mask every value must survive intact,
under all-`0` everything must flatten to 0, and under all-`1` everything
must saturate. A guide sentence can rot; that test cannot.

## 4. Part Two: enumerating floating addresses

Part 2 needs every address reachable from `address` under `mask`. Three
steps in `floating_addresses`:

1. **Force the 1 bits on**: `address | ones`, reusing the same `ones` trick.
2. **Clear the floating bits**: they must not carry their original value
   into the enumeration, since they are about to be set from scratch.
3. **Re-set them from every subset**.

Step 3 is the only interesting part, and it is done by **counting**:

```python
for counter in range(1 << len(floats)):
    candidate = base
    for j, bit in enumerate(floats):
        if counter >> j & 1:
            candidate |= 1 << bit
    addresses.append(candidate)
```

The counter runs 0 .. 2^k − 1. Bit *j* of the counter selects the *j*-th
floating position. So the counter's k contiguous low bits are **scattered**
out to the k arbitrary positions the mask marked with `X`. Counting through
every k-bit integer visits every subset of those positions exactly once —
no recursion, no string building, no `itertools.product` over `"01"`.

Worked, on the statement's example. Mask `...X1001X`, address 42:

```text
address 101010                       42
ones    010010                       X->0, 1->1
|ones   111010                       58
floats  [0, 5]                       the X positions, LSB-first
clear   011010                       26   <- base
counter 00 -> base                   26
counter 01 -> base | 1<<0            27
counter 10 -> base | 1<<5            58
counter 11 -> base | 1<<5 | 1<<0     59
```

26, 27, 58, 59 — the four addresses the statement lists.

Note `floating_bits` indexes **from the least significant end**
(`enumerate(reversed(mask))`). The mask is written most-significant-first,
so the last character is bit 0. Getting this backwards produces addresses
that are wrong by a bit-reversal and still look plausible, so it has its own
test.

## 5. Why it is correct

**Part 1.** Each store writes `memory[address]`, unconditionally
overwriting. Since the dict keeps only the last write per address, and the
statement asks for values *left* in memory, last-write-wins is exactly the
required semantics. The example writes address 8 twice and the answer is
101 + 64 = 165, not 73 + 101 + 64 — `test_a_later_write_overwrites_an_earlier_one`
pins that the earlier 73 does not survive.

**Part 2.** Same argument, applied per expanded address: a store to a
floating mask is 2^k independent stores, each last-write-wins. The
enumeration is exhaustive (every subset of floating positions) and
duplicate-free (distinct counters differ in some bit *j*, which scatters to
a distinct position, so the resulting addresses differ). That
distinctness matters — it is why the store count is exact rather than an
upper bound — and it is checked by
`test_floating_addresses_are_distinct_and_count_two_to_the_k`.

**Both.** Python's integers are arbitrary precision, so nothing here can
silently wrap at 36 or 64 bits. The statement's parenthetical — "do not
truncate the sum to 36 bits" — is a trap only for fixed-width languages.

## 6. Complexity

Let *n* be the number of store instructions and *k* the floating-bit count
of the governing mask.

- **Part 1** — O(n), two integer ops per store. On the real input, n = 460.
- **Part 2** — O(Σ 2^k) stores. On the real input the masks carry 4 to 9
  `X` bits, distributed:

  | X bits | 4 | 5 | 6 | 7 | 8 | 9 |
  |---|---|---|---|---|---|---|
  | masks | 15 | 18 | 15 | 22 | 17 | 13 |

  which works out to **75,328** stores landing on **71,385** distinct
  addresses. The near-equality is worth noticing: overlap between blocks is
  slight, so almost every store is to a fresh address.

Measured on this machine, best and median of 15 runs
(`python\bench.py 14 -n 15`):

| phase | best | median |
|---|---:|---:|
| parse | 0.281 ms | 0.307 ms |
| part 1 | 0.073 ms | 0.081 ms |
| part 2 | 67.495 ms | 72.962 ms |

Part 2 is ~900× part 1, which is just 2^k showing up in the wall clock. It
is also the second-slowest day in the repo so far, behind
[Day 11](day11_function_guide.md)'s cellular automaton.

The 5 ms gap between best and median is the reason the bench reports both.
At day 13's scale (0.005 ms parse) a single measurement would be mostly
noise; best-of-N estimates the floor, since interference only ever adds.

## 7. If I were writing this in Rust

Close to a transliteration, with three differences worth flagging.

**Integer width is now yours to get right.** Values and addresses are 36
bits, so `u64` throughout. The `!` on the clear step is a genuine hazard:

```rust
for &bit in &floats {
    base &= !(1u64 << bit);
}
```

Written as `!(1 << bit)` without the `u64` suffix, inference may land on
`i32` and the shift panics for `bit >= 32` in debug (and is UB-adjacent
nonsense in release). Days 12 and 13 had the floored-`%` trap; this is the
same genre — an arithmetic assumption Python makes silently that Rust makes
you state.

**Parse to a real enum.** Rust would want the instruction stream typed:

```rust
enum Instr { Mask(Mask), Store { addr: u64, value: u64 } }
```

and the block grouping falls out of a `Vec<(Mask, Vec<(u64, u64)>)>` just
as it does here. A `struct Mask { ones: u64, zeros: u64, floats: Vec<u8> }`
computed once at parse time is the natural Rust shape — cheaper than
Python's re-`replace` per block, and there is no reason not to, since both
representations are small.

**The memory dict.** `HashMap<u64, u64>` works, but `FxHashMap` from
`rustc-hash` is a large win here: 75k inserts of small integer keys is
precisely the workload where SipHash's DoS resistance is dead weight. Sum
with `.values().sum::<u64>()`.

An idiomatic subset enumeration is worth a look too:

```rust
(0..1u64 << floats.len()).map(|counter| {
    floats.iter().enumerate().fold(base, |acc, (j, &bit)| {
        if counter >> j & 1 == 1 { acc | 1 << bit } else { acc }
    })
})
```

— a lazy iterator, so the addresses never have to be collected into a
`Vec` at all. Which brings us to:

## 8. Possible optimization

**Do not materialize the address list.** `floating_addresses` returns a
`list`, so part 2 builds up to 512 integers per store just to iterate them
once. Making it a generator (`yield` instead of `addresses.append`) removes
75,328 list slots without changing a line of the caller. The reason it is
written as a list in the shipped source is that the tests want to `sorted()`
it and check `len(set(...))` — a generator would need `list()` at every call
site in the test module, which is a readability tax paid in the wrong place.

**Skip the scatter loop with Gray codes.** Consecutive Gray-code counters
differ in exactly one bit, so each successive address is one XOR away from
the previous one, replacing the inner O(k) scatter with O(1):

```python
prev = 0
for counter in range(1 << k):
    gray = counter ^ (counter >> 1)
    candidate ^= (gray ^ prev) mapped through floats   # one bit changes
    prev = gray
```

That turns part 2 from O(k · 2^k) into O(2^k). With k ≤ 9 the constant
factor saved is under 10×, on a phase that is already the bulk of a 68 ms
day — real, but not worth the loss of the "counter bit j selects float j"
one-liner that makes the current version explainable in a sentence.

**Cache by (address, mask).** Only if the input repeated address/mask
pairs, which this one does not — 460 stores across 100 masks, essentially
all distinct. Measured before assumed.

---

## Tests

`python/tests/test_day14.py`, 19 tests plus one skip:

- **Statement examples** — both worked value-masks and both worked address
  decodes, parametrized.
- **Parser** — grouping under masks, and four rejection cases (short mask,
  write before any mask, malformed line, bad syntax).
- **The identities** — that `X` is the identity for both value operations,
  and that floating addresses are distinct and number exactly 2^k. These
  are the two claims the solution actually rests on, so per the repo rule
  they are tests, not sentences in this file.
- **Part disambiguation** — `test_the_two_parts_read_the_same_mask_differently`
  runs both parts over the *same* parsed blocks and asserts they disagree,
  which is the one-line statement of what makes this puzzle a pair.
- **CRLF** — a Windows-downloaded input carries `\r`; the parse must not
  keep it.

`LOCKED = (3059488894985, 2900994392308)` — both submitted and accepted, so
the suite asserts them. A refactor that changes either answer fails.

[`day14.md`](day14.md) now carries both parts. The Part Two rules and both
worked address decodes in section 4 were re-checked against it after the
backfill: `0` unchanged, `1` overwritten with 1, `X` floating; 42 under
`X1001X` decoding to 26/27/58/59, and 26 under `X0XX` to the eight addresses
16-19 and 24-27, summing to 208.
