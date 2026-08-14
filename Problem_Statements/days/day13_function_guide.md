# Day 13 Function Guide — Shuttle Search

> **Written during this repo's Prolog era.** The solution it describes lives
> in the frozen `src/` tree. The maintained solution for this day is
> `python/day13.py`, tested by `python/tests/test_day13.py`. This guide is
> kept for its problem framing and algorithm reasoning, which did not change
> with the language; it will be rewritten Python-first when this day is next
> touched. See the README for what "frozen" means here.

---

> Two lines of input and the shortest source file since [Day
> 5](day05_function_guide.md) — and the first day whose part 2 is
> **unreachable by search**. Bus *N* departs at every timestamp divisible
> by *N*. Part 1 asks when the next bus leaves after a given minute: one
> `mod`, no search. Part 2 asks for the earliest minute `t` at which
> every listed bus departs at *its own offset in the list* — and the
> answer is `327300950120029`, so a loop that counts minutes would need
> 3.3 × 10¹⁴ iterations. The move is to stop reading part 2 as a search
> at all and read it as a **system of simultaneous congruences**, which
> the **Chinese Remainder Theorem** says has exactly one solution modulo
> the product of the bus IDs. The code walks to it in **911 steps**. The
> secondary lesson is the same floored-`mod` fact [Day
> 12](day12_function_guide.md) leaned on, used harder: nearly every line
> of arithmetic in this file is a `mod`, and in C or Rust one of them
> would be wrong.

## The puzzle in one paragraph

Line one is a timestamp; line two is a comma-separated schedule where
each field is either a bus ID or `x` for "out of service". A bus with ID
*N* departs at timestamps `0, N, 2N, 3N, …`. **Part 1:** find the bus
that departs soonest at or after the timestamp, and report *ID × minutes
waited*. Example (`939`, `7,13,x,x,59,x,31,19`) → bus 59 departs at 944,
waiting 5 → **295**. **Part 2:** the first line is discarded; find the
earliest `t` such that the bus at list position *i* departs at `t + i`.
Same example → **1068781**. The `x` entries carry no constraint but
**still occupy a position**, which is why the parse must keep indices
rather than just the bus list.

Real input: earliest `1000053`, nine buses in service —

| Offset                | 0  | 13 | 19  | 37 | 42 | 48 | 50  | 60 | 67          |
| --------------------- | -- | -- | --- | -- | -- | -- | --- | -- | ----------- |
| **Bus ID**      | 19 | 37 | 523 | 13 | 23 | 29 | 547 | 41 | 17          |
| **Part 1 wait** | 12 | 20 | 446 | 11 | 10 | 12 | 410 | 19 | **6** |

Part 1's winner is the last bus in the list: **17 × 6 = 102**. Part 2 is
**327300950120029**, sitting inside a schedule that repeats every
`19·37·523·13·23·29·547·41·17 = 1215475766514841` minutes — about 1.2
quadrillion, or 2.3 billion years of bus service.

---

## The one identity both parts run on

Everything in this day follows from a single sentence in the statement:

> the bus with ID `5` departs from the sea port at timestamps `0`, `5`,
> `10`, `15`, and so on

That is: **bus `Id` departs at time `T` exactly when `T mod Id =:= 0`.**
No schedule needs to be built and no departure times enumerated. Both
parts are questions about divisibility, and they differ only in how many
divisibility facts must hold at once:

|        | Constraint                                            | Count                      |
| ------ | ----------------------------------------------------- | -------------------------- |
| Part 1 | `(Earliest + Wait) mod Id =:= 0`, minimise `Wait` | one bus at a time          |
| Part 2 | `(T + Offset) mod Id =:= 0`                         | **all nine at once** |

Part 1 minimises over independent one-bus problems; part 2 must satisfy
nine coupled ones simultaneously. That is the entire difficulty jump, and
it is the difference between arithmetic and number theory.

---

## Part 1: the wait is a single `mod`

The next departure of bus `Id` at or after minute `E` is

```text
next = Id * ceil(E / Id)
wait = next - E
```

Written that way it needs a division, a ceiling, and a multiply. Written
the other way it needs one operation:

```prolog
Wait is (-E) mod Id.
```

Why they agree: `wait` is the unique value in `0 .. Id-1` with
`E + wait ≡ 0 (mod Id)`, i.e. `wait ≡ -E (mod Id)`. The canonical
representative of `-E` modulo `Id` **is** `(-E) mod Id` — provided `mod`
returns a non-negative result for a negative left operand, which in SWI
it does:

```prolog
?- X is (-939) mod 7.
X = 6.
```

SWI's `mod/2` is **floored**: the result takes the sign of the *divisor*,
so with a positive bus ID the answer always lands in `0 .. Id-1`. C's
`%`, Rust's `%`, Java's and Go's all **truncate** toward zero, so
`-939 % 7 == -6` in those languages and this line silently produces a
negative wait. [Day 12](day12_function_guide.md) hit the same fork when
folding left turns onto right ones with `-(D//90) mod 4`; there the
symptom was a missing clause and a loud failure, here it is a wrong
number and a quiet one. Rust's fix is `rem_euclid`; see the bridge
section.

The zero case falls out for free. If `E` is already a departure minute,
`(-E) mod Id` is `0` and the bus is caught with no wait — no special
case, no `if`.

---

## Part 2: from "search" to congruences

The naive reading of part 2 is a loop: try `t = 0, 1, 2, …` and test all
nine buses. The statement pre-empts it —

> surely the actual earliest timestamp will be larger than
> `100000000000000`

— and the real answer is 3.27 × 10¹⁴. At a generous 10⁸ iterations per
second that loop finishes in about five weeks. It is not a slow solution;
it is not a solution.

Restate the requirement instead. Bus `Id` at list offset `Offset` must
depart at `t + Offset`, so by the identity above:

```text
(t + Offset) ≡ 0        (mod Id)
        t    ≡ -Offset  (mod Id)
```

Nine buses give nine of those, one per bus. Concretely, for the example:

```text
t ≡  0 (mod 7)     t ≡ -1 ≡ 12 (mod 13)     t ≡ -4 ≡ 55 (mod 59)
t ≡ -6 ≡ 25 (mod 31)                        t ≡ -7 ≡ 12 (mod 19)
```

This is a **simultaneous congruence system**, the exact object the
Chinese Remainder Theorem is about. Nothing about "buses" survives the
translation, and that is the point: the puzzle is a story wrapped around
a textbook problem, and recognising which one is the whole day.

---

## The Chinese Remainder Theorem, and the sieve that stands in for it

**The theorem.** Let `m₁, …, mₖ` be **pairwise coprime** moduli and
`a₁, …, aₖ` any residues. Then the system `t ≡ aᵢ (mod mᵢ)` has a
solution, and it is **unique modulo `M = m₁·m₂·…·mₖ`**.

Both halves matter here. *Existence* says an answer exists at all — worth
knowing before writing a loop that might never terminate. *Uniqueness
mod M* is what makes "the earliest such timestamp" a well-posed question
with a computable answer: the solution set is one arithmetic progression
`t₀, t₀+M, t₀+2M, …`, so "earliest non-negative" picks out exactly one
element.

**Do the moduli qualify?** The theorem needs pairwise coprimality, and
AoC hands it over: every bus ID in this input is **prime** — 19, 37, 523,
13, 23, 29, 547, 41, 17 — and they are distinct, so any two share no
factor. This is a property of the puzzle input, not of the problem
statement, and it is the one assumption in this file that the code does
not check. Repeated or composite IDs could make the system unsolvable
(`t ≡ 0 mod 4` together with `t ≡ 1 mod 6` has no solution) and the sieve
below would then walk its progression forever — see the correctness
notes.

**The sieve.** The textbook CRT construction computes modular inverses
and sums `Σ aᵢ · (M/mᵢ) · inv(M/mᵢ, mᵢ)`. This code does something
simpler that needs no inverses at all: add the congruences **one at a
time**, keeping the full solution set of the ones handled so far.

Carry a pair `T-Step` meaning:

> *the timestamps satisfying every congruence folded in so far are
> exactly `T, T+Step, T+2·Step, …`*

- Start at `0-1`: with no constraints every integer qualifies, and "every
  non-negative integer" is the progression starting at 0 with stride 1.
- To add bus `Id` at `Offset`: the answer must still be in the current
  progression, so walk it — `T, T+Step, T+2·Step, …` — until a member
  also satisfies `(T + Offset) mod Id =:= 0`.
- The new stride is `Step · Id`, because the solutions of the enlarged
  system are spaced by `lcm(Step, Id)`, and for coprime moduli the lcm
  *is* the product.

**Why the walk is short.** `Step` is a product of bus IDs all coprime to
`Id`, so `Step` is invertible mod `Id`, so the sequence

```text
(T + Offset), (T + Offset + Step), (T + Offset + 2·Step), …   (mod Id)
```

steps by a nonzero invertible amount and therefore **cycles through all
`Id` residues before repeating any**. Exactly one of the first `Id`
candidates hits `0`. So folding in bus `Id` costs fewer than `Id`
iterations, and the whole of part 2 costs fewer than `Σ Idᵢ = 1249`
steps — against 3.27 × 10¹⁴ for the naive loop.

Measured on the real input, the fold is cheaper still:

| Bus     | 19 | 37 | 523 | 13 | 23 | 29 | 547 | 41 | 17 | **total** |
| ------- | -- | -- | --- | -- | -- | -- | --- | -- | -- | --------------- |
| Strides | 0  | 11 | 452 | 10 | 17 | 19 | 375 | 23 | 4  | **911**   |

**911 steps.** The two big primes (523, 547) account for 91% of them,
which is the `< Id` bound showing through: the cost of a congruence is
the size of its modulus, not the size of the answer.

---

## Reading Prolog: the four forms this day turns on

**1. `findall/3` over a nondeterministic generator — the comprehension.**

```prolog
findall(Offset-Id, in_service(Fields, Offset, Id), Buses)
```

reads as *collect one `Offset-Id` term for every way `in_service/3` can
succeed*. It is a list comprehension whose "iterable" is a **predicate
with more than one solution** rather than a data structure. The generator
here is `nth0/3` called with an **unbound index**:

```prolog
?- nth0(I, ["7","13","x"], F).
I = 0, F = "7" ;
I = 1, F = "13" ;
I = 2, F = "x".
```

Same predicate that indexes a list when the index is bound, *enumerating*
it when the index is free — one of Prolog's genuinely different offerings
versus Rust, where indexing and iterating are separate APIs (`v[i]` vs
`v.iter().enumerate()`). Because the index comes out of the enumeration,
there is no counter to thread and no way for the `x`-skipping to
desynchronise the offsets. The filter is just a goal that fails:
`Field \== "x"` removes that solution from the collection.

**2. `min_member/2` and the standard order of terms.**

```prolog
min_member(Wait-Id, Waits)
```

finds the smallest element of a list under the **standard order of
terms** — Prolog's total order over *all* terms, which for two compounds
of the same name and arity compares arguments left to right. So building
the list as `Wait-Id` (and not `Id-Wait`) makes `min_member/2` compare
waits first and use the ID only to break ties. This is the
"decorate with a sort key" trick, working because the order is built into
the language rather than supplied by a comparator. The Rust equivalent is
`min_by_key(|&(wait, _)| wait)`, or ordering a tuple — same idea, more
typing.

**3. `foldl/4` with a *pair* accumulator.**

```prolog
foldl(crt_step, Buses, 0-1, Timestamp-_Period)
```

Prolog has no tuple type; a pair is just the term `-(A, B)`, written
infix. Folding two values through a list means folding one term that
holds both, and **unifying the final term against a pattern** pulls the
pieces back out — including discarding one as `_Period`. Compare [Day
10](day10_function_guide.md), which folded a three-element frontier the
same way, and [Day 12](day12_function_guide.md), which folded a
four-argument `nav/4` state. The accumulator's *shape* is the design
decision in every one of these; here `T-Step` is the algorithm written
down.

**4. Guard-clause recursion with a steadfast cut — the `while` loop.**

```prolog
align(T0, _Step, Offset, Id, T) :-
    (T0 + Offset) mod Id =:= 0,
    !,
    T = T0.
align(T0, Step, Offset, Id, T) :-
    T1 is T0 + Step,
    align(T1, Step, Offset, Id, T).
```

Two clauses tried in order: *if the test passes, stop; otherwise take one
stride and recurse.* That is a `while` loop, and the second clause is
tail-recursive, so SWI runs it in constant stack — iteration, not
recursion, at the machine level.

The `!` commits: once the test succeeds the second clause is dead and the
predicate leaves no choicepoint. Note where the output is unified —
**after** the cut, as `T = T0`, not in the clause head. That is the
repo's [steadfastness](day03_function_guide.md) convention: if the head
read `align(T0, _, Offset, Id, T0)` and a caller passed a *bound* `T`
that happened to differ, head unification would fail and execution would
fall through into clause two, striding forward forever after a `T` it can
never match. Unifying after the cut lets the guard, not the caller's
binding, decide which clause runs.

---

## The Day 13 code, predicate by predicate

### `parse_input/2` and `in_service/3`

```prolog
parse_input(Raw, notes(Earliest, Buses)) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, [EarliestS, ScheduleS|_]),
    number_string(Earliest, EarliestS),
    split_string(ScheduleS, ",", " \t\r", Fields),
    findall(Offset-Id, in_service(Fields, Offset, Id), Buses).

in_service(Fields, Offset, Id) :-
    nth0(Offset, Fields, Field),
    Field \== "x",
    number_string(Id, Field).
```

The parsed form is `notes(Earliest, Buses)` with `Buses` a list of
`Offset-Id` pairs. Two decisions are worth naming.

**The offset is stored, not the position in the output list.** After
dropping `x` entries, list positions no longer match schedule positions —
in the example, 59 is the third *bus* but the fifth *field*, and part 2
needs the five. Carrying the index as data means the `x` entries can be
discarded entirely rather than kept as placeholders, and nothing
downstream has to know they existed.

**The whole parse is `exclude/3` plus a comprehension.** The
`exclude(=(""), Lines0, [EarliestS, ScheduleS|_])` line does double duty:
it drops blank lines *and* destructures the result into exactly the two
lines the format promises, in the same unification. Given a one-line
input the clause fails outright rather than proceeding with garbage. The
trailing `|_` tolerates extra lines the format does not promise are
absent.

`number_string/2` throws on unparseable input rather than failing, which
is why the `x` test is an explicit `\==` and not an attempt to parse and
recover.

### `wait_for/3`

```prolog
wait_for(Earliest, Id, Wait) :-
    Wait is (-Earliest) mod Id.
```

One line, discussed at length above. It is a separate predicate for two
reasons: it is the single place a sign error can enter part 1, so it is
the single place the tests can pin (`wait_is_in_range` checks
`0 ≤ Wait < Id` and `(Earliest + Wait) mod Id =:= 0` as a property, over
several timestamps), and naming it lets `earliest_bus/3` read as
selection logic with no arithmetic in it.

### `earliest_bus/3`

```prolog
earliest_bus(Earliest, Buses, Answer) :-
    findall(Wait-Id,
            ( member(_Offset-Id, Buses),
              wait_for(Earliest, Id, Wait)
            ),
            Waits),
    min_member(Wait-Id, Waits),
    Answer is Id * Wait.
```

Decorate, minimise, combine. `member/2` as the generator inside
`findall/3` is the standard "for each element" idiom — with the offset
explicitly discarded as `_Offset`, since part 1 is the half of this
puzzle that does not care where a bus sits in the list.

The subtlety the suite pins: the minimisation is on **wait**, not on the
answer. In the example, bus 7 waits 6 minutes and scores 42, smaller than
the correct answer of 295 — a version that minimised the product would be
right about nothing, but it is a natural slip when the code and the
answer both end in a multiplication. Building the pair as `Wait-Id` makes
the correct choice the default one.

### `crt/2`

```prolog
crt(Buses, Timestamp) :-
    foldl(crt_step, Buses, 0-1, Timestamp-_Period).
```

The sieve, in one line, with the interesting content in the seed and the
discard. `0-1` is the empty system: every integer solves it. The
discarded `_Period` is the product of all bus IDs — the schedule's repeat
interval, `1215475766514841` for the real input. It is not part of the
answer, but it is the CRT's uniqueness modulus, so the code that computes
the answer also computes the bound within which the answer is unique.

### `crt_step/3`

```prolog
crt_step(Offset-Id, T0-Step0, T-Step) :-
    align(T0, Step0, Offset, Id, T),
    Step is Step0 * Id.
```

One congruence folded in: find the first surviving timestamp, then widen
the stride. The two lines are the two halves of the invariant —
`align/5` maintains "T is the smallest solution so far", `Step is Step0 * Id` maintains "Step is the spacing between solutions".

### `align/5`

```prolog
align(T0, _Step, Offset, Id, T) :-
    (T0 + Offset) mod Id =:= 0,
    !,
    T = T0.
align(T0, Step, Offset, Id, T) :-
    T1 is T0 + Step,
    align(T1, Step, Offset, Id, T).
```

The loop. Note what it does **not** do: it never searches all timestamps,
only the ones already known to satisfy every earlier congruence. Each
fold step therefore searches a set `Step0` times sparser than the last,
which is why nine nested "searches" cost 911 iterations in total. The
progression is the memo.

`=:=` and not `=`: this is arithmetic comparison (evaluate both sides,
compare numbers), where `=` would try to unify the *term*
`(T0+Offset) mod Id` with the integer `0` and fail every time. The
distinction bites every Prolog newcomer once; the symptom here would be a
loop that never terminates rather than a wrong answer.

### `part1/2`, `part2/2`, `solve/3`

```prolog
part1(notes(Earliest, Buses), Answer) :-
    earliest_bus(Earliest, Buses, Answer).

part2(notes(_Earliest, Buses), Timestamp) :-
    crt(Buses, Timestamp).
```

Destructuring in the head, one call in the body. `part2/2`'s `_Earliest`
is the statement's "(The first line in your input is no longer
relevant.)" written as code — the underscore prefix tells both the reader
and SWI's singleton check that the omission is deliberate.

---

## Correctness notes

**The fold's invariant, stated precisely.** After folding buses `b₁ … bₖ`
(IDs `m₁ … mₖ`, offsets `a₁ … aₖ`), the accumulator `T-Step` satisfies:

1. `Step = m₁ · m₂ · … · mₖ`;
2. `T` is the **smallest non-negative** integer with
   `(T + aᵢ) ≡ 0 (mod mᵢ)` for all `i ≤ k`;
3. the set of *all* non-negative solutions of those `k` congruences is
   `{ T + n·Step : n ≥ 0 }`.

*Base case:* `0-1` — the empty system's solution set is every
non-negative integer, which is `{0 + n·1}`, and `0` is its smallest
member. *Inductive step:* adding `mₖ₊₁`. By (3), any solution of the
enlarged system already lies in `{T + n·Step}`, so scanning that
progression in increasing order and stopping at the first hit yields the
smallest solution — property (2). Since `gcd(Step, mₖ₊₁) = 1` (the IDs
are distinct primes), the values `T + n·Step` cover every residue class
mod `mₖ₊₁` as `n` runs over `0 … mₖ₊₁-1`, so the scan **terminates**
within `mₖ₊₁` steps, and the hits recur exactly every `mₖ₊₁` strides —
spacing `Step · mₖ₊₁`, which is property (3) and the new `Step`.

Property (2) at `k = 9` is the puzzle's "earliest timestamp". The
algorithm does not find *a* solution and hope it is minimal; minimality
is maintained at every step, which is why no final search is needed.

**Termination.** Each `align/5` call terminates by the coprimality
argument above — within `Id` iterations. `foldl/4` runs over a
nine-element list. So part 2 terminates, and unlike [Day
11](day11_function_guide.md)'s fixpoint this is a proof rather than a
promise from the puzzle-setter. The proof's dependence on coprimality is
real, though, and coprimality is an input property: a schedule listing
bus 7 twice at incompatible offsets would send `align/5` around its
progression forever. See the optimization section for what a defensive
version costs.

**Bignums are load-bearing, and invisible.** The final `Step` is
`1215475766514841` ≈ 2⁵⁰ and the answer ≈ 2⁴⁸. Both fit a signed 64-bit
integer with roughly four orders of magnitude to spare, so nothing
dramatic happens here — but **two more buses of this size would overflow
`i64`**, and the failure would be a silent wraparound rather than an
error. SWI's integers are arbitrary-precision, so the Prolog is correct
for any number of buses; the Rust sketch below has to pick a width and
think about it. Same non-event as [Day
10](day10_function_guide.md)'s 97-trillion path count, one order of
magnitude closer to mattering.

**Where a wrong answer would come from**, ranked by ease of shipping:

1. **Dropping the `x` entries before recording offsets.** Then 59 gets
   offset 2 instead of 4, and part 2 returns a perfectly valid solution
   to the wrong system. The statement's `67,x,7,59,61` and `67,7,x,59,61`
   pair exists precisely to catch this; the suite runs both.
2. **A truncating `mod` in part 1.** Negative waits, a nonsense minimum,
   no error message. Language-dependent: correct in SWI and Python, wrong
   in C, C++, Rust, Java, and Go.
3. **`t ≡ +Offset` instead of `t ≡ -Offset`.** Sign inversion on the
   congruence, giving a timestamp where the buses depart in the wrong
   order — and note it still satisfies any check of the form "some bus
   departs then".
4. **Minimising the product rather than the wait in part 1.**
5. **Generalising the stride to `lcm` and getting the gcd path wrong.**
   Only reachable if you extend the code to non-coprime moduli, which is
   the one change to this file that requires redoing the proof above.

---

## Tests — what's pinned and why

Nineteen tests plus fourteen `forall` sub-tests in
[`test/day13_tests.pl`](../../test/day13_tests.pl).

- `parse_keeps_positions` — the statement's schedule parses to
  `[0-7, 1-13, 4-59, 6-31, 7-19]`. Pins the offsets *by value*, so the
  `x`-skipping bug above cannot survive.
  `parse_trailing_out_of_service` covers `3,x,x`, where the dropped
  fields are at the end and an off-by-one would otherwise go unnoticed.
- `wait_table` (`forall` over five ID-wait pairs at minute 939) — the
  part-1 arithmetic against numbers read off the statement's own
  departure chart. `no_wait_on_a_departure` pins the boundary: standing
  at minute 945 waits **0** for bus 7, not 7.
- `wait_is_in_range` (`forall` over four timestamps, each checking four
  buses) — a **property test** rather than a value test: in every case
  `0 ≤ Wait < Id` *and* `(Earliest + Wait) mod Id =:= 0`. Those two
  conditions uniquely characterise the answer, so the test passes only
  for a correct `wait_for/3` and needs no precomputed expectations. It
  includes `Earliest = 0`, the one case a truncating `%` gets right.
- `part1_picks_the_soonest_not_the_smallest_product` — computes all five
  products for the example and asserts the smallest is **42** while the
  answer is **295**. The one test that separates the correct selection
  rule from the plausible wrong one.
- `part2_extra_examples` (`forall` over all five statement schedules,
  including the pair differing only in `x` placement) and
  `part2_offsets_matter`, which asserts those two give *different*
  answers. Between them, offset handling is nailed down.
- `part2_satisfies_every_congruence` and `part2_example_is_minimal` — the
  two halves of the specification, checked separately. The first verifies
  the answer *is* a solution (`forall` over the buses); the second
  brute-forces every minute below `1068781` and asserts none qualifies.
  That brute force is the puzzle's definition run directly — viable only
  because the example is small (0.27 s, the slowest test in the file and
  still the cheapest possible proof of minimality).
- `align_is_idempotent` — a timestamp already satisfying the new
  congruence comes back unchanged. This is the steadfastness case: it
  fails if the guard clause strides before it tests.
  `align_stays_on_the_progression` pins that `align(7, 7, 1, 13, T)`
  gives **77**, still a multiple of 7 — the invariant that earlier
  congruences are never broken by a later one.
- `single_bus_at_offset_zero` → **0**. The degenerate fold, and a
  reminder that the answer is allowed to be zero.
- `crt_is_order_independent` — folds the example's congruences forwards
  and reversed and asserts the same timestamp. CRT uniqueness as an
  executable claim; the sieve's *intermediate* states differ completely
  between the two orders.
- Answer locks **102** and **327300950120029**, plus
  `part2_real_is_a_valid_schedule`, which re-derives the real answer and
  checks it against all nine congruences and the statement's
  `> 100000000000000` promise.

Cross-validated against [`python/day13.py`](../../python/day13.py) — the
same sieve over tuples, relying on Python's `%` being floored like
Prolog's. It independently prints `part1=102 part2=327300950120029`.

---

## Complexity & benchmarks

Let *k* be the number of buses in service (9) and *f* the number of
schedule fields (68).

| Phase                      | Cost                                                                 |
| -------------------------- | -------------------------------------------------------------------- |
| Parse                      | O(f) — one`nth0/3` enumeration, one `number_string/2` per field |
| `wait_for/3`             | O(1)                                                                 |
| `earliest_bus/3`         | O(k)                                                                 |
| `align/5` for bus `Id` | O(`Id`) iterations, worst case                                     |
| `crt/2`                  | **O(Σ Idᵢ)** — at most 1249 iterations; 911 in practice     |

The part-2 bound is worth restating because it is so unlike the naive
one: the cost depends on the **sum** of the moduli while the answer
depends on their **product**. Nine three-digit numbers sum to about a
thousand and multiply to 1.2 quadrillion. That ratio is the whole
algorithmic content of the day.

`nth0/3` with an unbound index would be O(f) *per solution* if it
re-indexed each time, but SWI enumerates by walking the list once and
backtracking into it, so the `findall/3` is a single O(f) pass, not
O(f²).

Measured (`swipl bench/main.pl day13`):

```text
  parse          1,233 inf      0.485 ms
  part1            388 inf      0.081 ms
  part2          2,941 inf      0.165 ms
```

Two readings. First, **part 2 costs 2,941 inferences to produce a
15-digit answer** — about three per `align/5` stride, which is the loop
body (one arithmetic test, one addition, one recursive call) and nothing
else. Second, **parsing dominates again**, as on [Day
12](day12_function_guide.md): 1,233 inferences to read 68 comma-separated
fields against 388 for the entirety of part 1. When the algorithm is this
good, the input format is the program. The whole day runs in under
0.8 ms, and part 2 — the part that is impossible by search — is the
cheapest non-trivial thing in the file.

For scale: the naive part-2 loop needs roughly 10¹⁵ inferences, about
**two years** at the throughput this benchmark shows. That puts the day
alongside [Day 10](day10_function_guide.md)'s
count-don't-enumerate DP and [Day 7](day07_function_guide.md)'s
exponential-to-linear BFS as one of the three places in the repo so far
where choosing the right formulation is the difference between a program
and an impossibility.

---

## If I were writing this in Rust

The sieve transfers verbatim; the interesting differences are the two
places Rust's types and its `%` force a decision.

```rust
fn parse(raw: &str) -> (i64, Vec<(i64, i64)>) {
    let mut lines = raw.lines();
    let earliest: i64 = lines.next().unwrap().trim().parse().unwrap();
    let buses = lines
        .next()
        .unwrap()
        .trim()
        .split(',')
        .enumerate()
        .filter_map(|(i, f)| f.parse::<i64>().ok().map(|id| (i as i64, id)))
        .collect();
    (earliest, buses)
}

fn part1(earliest: i64, buses: &[(i64, i64)]) -> i64 {
    let (wait, id) = buses
        .iter()
        .map(|&(_, id)| ((-earliest).rem_euclid(id), id))
        .min()
        .unwrap();
    id * wait
}

fn part2(buses: &[(i64, i64)]) -> i64 {
    buses
        .iter()
        .fold((0i64, 1i64), |(mut t, step), &(off, id)| {
            while (t + off) % id != 0 {
                t += step;
            }
            (t, step * id)
        })
        .0
}
```

**`rem_euclid`, not `%`.** `(-939) % 7` is `-6` in Rust;
`(-939i64).rem_euclid(7)` is `6`. This is the single line where a direct
transliteration of the Prolog produces a wrong answer, and it generalises
to a rule worth internalising: **whenever a negative value meets `%`,
Rust and Prolog disagree.** Inside `part2` the operands are non-negative
so plain `%` is fine there — but writing `rem_euclid` in both places
costs nothing and removes the need to know that.

**`filter_map` + `parse::<i64>().ok()`** replaces the `Field \== "x"`
guard: fields that do not parse are dropped, and `enumerate()` *before*
the filter is what preserves the offsets. It is the closest Rust gets to
the `nth0/3`-as-generator trick — `enumerate` and `filter` are separate
combinators where Prolog uses one predicate with a free variable.

**Integer width is a real choice.** `step` reaches 1.2 × 10¹⁵, safe in
`i64` (max ≈ 9.2 × 10¹⁸) for this input and a silent wraparound in
release mode for an input with two more buses. `i128` costs nothing
measurable at this scale and removes the reasoning entirely; `u64` with
`checked_mul` is the paranoid version. The Prolog needs none of this
deliberation, which is exactly the trade [Day
10](day10_function_guide.md) noted: arbitrary precision buys freedom from
a class of questions.

**`min()` on a tuple** does what `min_member/2` does on a pair —
lexicographic ordering, first field dominant — provided the tuple is
built `(wait, id)` and not `(id, wait)`. Same decoration trick, same
semantics, enforced by `Ord` derivation rather than by the standard order
of terms.

A production Rust version would probably reach for `num::integer` or a
small `crt` helper built on the extended Euclidean algorithm. For nine
congruences and a `while` loop that runs 911 times, the dependency buys
nothing.

---

## Possible optimization

Shipping code stays as written. Part 2 costs 0.165 ms; these are for the
shape of the ideas.

**1. True CRT with modular inverses.** Replace the `align/5` scan with
the closed form: compute `inv(Step, Id)` by the extended Euclidean
algorithm and jump straight to the answer instead of striding to it.

```prolog
crt_step(Offset-Id, T0-Step0, T-Step) :-
    Residue is (-Offset - T0) mod Id,
    Jump is (Residue * modular_inverse(Step0, Id)) mod Id,   % sketch
    T is T0 + Jump * Step0,
    Step is Step0 * Id.
```

That turns each fold step from O(`Id`) into O(log `Id`) — the whole of
part 2 becomes a few dozen operations instead of 911. It is the *right*
algorithm and it is not the shipped one, because extended Euclid is
another twenty lines that must themselves be tested, to save 0.15 ms on a
problem where nothing is waiting. Worth writing when the moduli are large
(cryptographic CRT, where they are hundreds of bits and the scan is
genuinely impossible) — and worth knowing that SWI can shortcut it for
*prime* moduli via Fermat's little theorem: `Inverse is powm(Step0, Id-2, Id)`, since `a^(p-2) ≡ a⁻¹ (mod p)`. That is a one-liner on a
built-in, and the only reason it is not here is that it silently assumes
primality where the scan only needs coprimality.

**2. Fold the largest moduli first.** The scan for bus `Id` costs up to
`Id` strides, so reordering the fold looks like it should help — do the
expensive scans while `Step` is small. It changes nothing: the stride
*count* for a modulus is independent of the stride *size*, and the bound
is `Σ Idᵢ` in every order. Recorded because "process the expensive items
first" is a real heuristic elsewhere and this is a clean case of it being
provably worthless.

**3. Check coprimality, or handle its absence.** The current code assumes
pairwise-coprime moduli and would hang if that failed. A general version
computes `G is gcd(Step0, Id)`, fails cleanly unless `G` divides the
residue difference, and widens by `Step0 * Id // G` instead of
`Step0 * Id`. That is the textbook non-coprime CRT, roughly six extra
lines, and it makes the predicate reusable for any congruence system. Not
shipped because it adds branches no test can exercise — the input's IDs
are prime, and there is no second caller.

**4. Parse to codes rather than strings.** As on [Day
12](day12_function_guide.md), parsing is the largest line in the
benchmark: `split_string/4` allocates a string per field before
`number_string/2` re-reads each one. `phrase_from_file/2` over codes
would cut most of that. Also as on Day 12, it is the only item here that
would move the numbers, and it is a parsing change rather than an
algorithmic one — which is what "the algorithm is already optimal" looks
like in a profile.
