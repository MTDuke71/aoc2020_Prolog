# Day 09 Function Guide — Encoding Error

> Two small classics wearing a cipher's costume. **Part 1 is a sliding
> window**: slide a fixed-size frame down a list and, at each new value,
> ask a **2-SUM** question of the frame behind it — "are there two
> *distinct* values here that add to me?" The first value that answers
> *no* is the break. **Part 2 is a contiguous-subarray-sum search**: find
> a run of consecutive values that totals that broken number, then add the
> run's smallest and largest. What makes both cheap is a single structural
> fact — every value in the input is **positive** — which turns the
> pair-check into a bounded scan and lets the range search stop the moment
> a growing window overshoots. The 2-SUM half is the same shape as
> [Day 1](day01_function_guide.md)'s Report Repair, now pinned to a moving
> 25-wide window instead of the whole report.

## The puzzle in one paragraph

The input is 1000 positive integers, one per line (XMAS cipher output).
The first 25 are a **preamble**; from there on, every value must equal the
sum of **two different** values among the immediately preceding 25.
**Part 1:** report the first value that has no such pair (example, with a
5-number preamble, → `127`). **Part 2:** find a contiguous run of **at
least two** numbers, somewhere before that invalid value, whose sum *is*
the invalid value; report `min(run) + max(run)`, the "encryption
weakness" (example → `62`, from the run `15 25 47 40`: `15 + 47`).

The statement's worked example uses a preamble of 5. The shipped
`part1/2` and `part2/2` hard-wire the real size of 25, while
`part1_with_preamble/3` and `part2_with_preamble/3` expose the size so the
five-number example stays directly testable.

---

## Representation: a plain list, and why that's the right call

`parse_input/2` produces a flat `list` of integers — nothing fancier. That
is the correct data structure here, and it's worth saying *why*, because
[Day 8](day08_function_guide.md) just spent its whole representation
section arguing *against* a plain list:

- **The access pattern is sequential, not random.** Day 8's interpreter
  did `jmp -20` — random access — so a list's `O(n)` walk hurt and an
  `assoc` earned its keep. Day 9 only ever looks at *the window behind the
  cursor* and *contiguous slices*. Both are consumed left-to-right, which
  is exactly what a cons list is good at.
- **Nothing is mutated.** The window "slides" by building a new list
  (drop the oldest, append the newest); the range "grows" by consing one
  more element. Prolog lists are immutable and structure-sharing, so this
  is cheap and pure.
- **No keying is needed.** There's no identity to look up (Day 7's
  colours, Day 8's PCs). A value's only relevant property is its position
  relative to the cursor, and position *is* list order.

The one non-obvious modeling choice is in Part 1's scan: alongside the
25-wide window it also threads a **reverse prefix** — every value seen
*before* the current candidate, newest-first. When the break is found,
reversing that prefix hands Part 2 exactly the data that precedes the
invalid value. That matters for correctness (below) and costs nothing: a
prepend per step, one reverse at the end.

---

## Reading Prolog: the four forms this day turns on

**1. Splitting off a fixed-size prefix with `length/2` + `append/3`.**
The initial window is "the first 25 values." Prolog spells that without an
index or a loop:

```prolog
length(Window, PreambleSize),      % Window := 25 fresh, unbound variables
append(Window, Remaining, Numbers) % bind them to the first 25; rest -> Remaining
```

`length(Window, 25)` with `Window` unbound *generates a list of 25 fresh
variables* — a template of the right shape but no content. `append/3` then
unifies that template against `Numbers`, forcing `Window` to be the first
25 elements and `Remaining` to be everything after. This "make a
skeleton, then unify it into place" idiom is the declarative replacement
for `take(25)` and shows up any time you need a fixed-size chunk.

**2. Distinct-pair enumeration: `select/3`, then `member/2`, guarded by
`=\=`.** The 2-SUM check has to enumerate *ordered choices of two
different entries*:

```prolog
select(First, Window, Remaining),  % pick one entry, Remaining = window minus it
member(Second, Remaining),         % pick a second from what's left
First =\= Second,                  % the puzzle: the two values must differ
Target =:= First + Second
```

`select/3` is `member/2`'s "and remove it" cousin: it binds `First` to an
entry *and* gives back the window with that one occurrence deleted, so
`Second` is drawn from a genuinely different slot. The `=\=` guard is the
one enforcing the puzzle's "two numbers of different values" rule — it
rejects `25 + 25` even when two 25s sit in the window. (With the value
guard in place, `select`'s slot-distinctness is belt-and-suspenders, but
it keeps the intent legible.) Note `=\=` / `=:=` are the *arithmetic*
comparison operators — they evaluate both sides — as distinct from `\==`
(term inequality) and `=` (unification); mixing these up is a classic
early-Prolog trap.

**3. Negation as failure as the invalidity test.** "Is this value
invalid?" is literally "can I *not* prove a valid pair?":

```prolog
\+ valid_sum(Candidate, Window)
```

`\+ Goal` succeeds exactly when `Goal` has no proof. It's safe here
because `valid_sum/2` is called fully ground (bound candidate, bound
window), so there's nothing to bind and the closed-world reading is
exactly what we mean.

**4. Chained if-then-else terminated by `fail`.** The range-grower makes a
three-way decision each step:

```prolog
(   NewSum =:= Target -> reverse([Next|ReverseRange], Range)   % exact hit: done
;   NewSum <  Target  -> extend_range(Rest, NewSum, Target, [Next|ReverseRange], Range)
;   fail                                                       % overshoot: give up
)
```

`( C1 -> T1 ; C2 -> T2 ; E )` commits to the *first* condition that
succeeds (a soft cut) and runs its arm; if none do, `E`. Here the final
arm is an explicit `fail`, which is the load-bearing move: on an
overshoot, `extend_range` fails, which makes the enclosing "start the
range here" clause fail, which backtracks the search to the *next* start.
Positivity is what makes that `fail` sound — see correctness.

---

## The Day 9 code, predicate by predicate

### `parse_input/2`

```prolog
parse_input(Raw, Numbers) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(number_string, Numbers, Lines).
```

The repo's standard split-and-clean opener, unchanged since
[Day 0](day00_function_guide.md): split on newlines, trim `" \t\r"` from
each piece (the `\r` trim is what survives Windows CRLF), drop the
trailing empty line, and read each remaining line with `number_string/2`.
SWI integers are arbitrary precision, so the ten-digit values near the end
(`1930745883`, sums well past 2³¹) need no special handling — they're just
integers.

### `valid_sum/2` — the 2-SUM oracle

```prolog
valid_sum(Target, Window) :-
    select(First, Window, Remaining),
    member(Second, Remaining),
    First =\= Second,
    Target =:= First + Second,
    !.
```

Nondeterministically pick two distinct entries whose values differ and sum
to `Target`; the trailing `!` **commits after the first witness**, turning
what would be a generator of all pairs into a semi-deterministic (semidet)
yes/no oracle.
That cut matters two ways: it stops `valid_sum` leaving choice points
behind (so `\+ valid_sum/…` and the Part 1 scan stay deterministic), and
it means the common case — a pair found early — costs far less than the
`P²` worst case.

### `invalid_and_prefix/4` and `first_invalid/5` — the sliding scan

```prolog
invalid_and_prefix(Numbers, PreambleSize, Invalid, BeforeInvalid) :-
    length(Window, PreambleSize),
    append(Window, Remaining, Numbers),
    reverse(Window, BeforeRev),
    first_invalid(Remaining, Window, BeforeRev, Invalid, BeforeInvalid).

first_invalid([Candidate|_], Window, BeforeRev, Candidate, Before) :-
    \+ valid_sum(Candidate, Window),
    !,
    reverse(BeforeRev, Before).
first_invalid([Candidate|Rest], Window0, BeforeRev, Invalid, Before) :-
    valid_sum(Candidate, Window0),
    slide_window(Window0, Candidate, Window1),
    first_invalid(Rest, Window1, [Candidate|BeforeRev], Invalid, Before).
```

`invalid_and_prefix/4` seeds the state: `Window` is the first 25 values,
`Remaining` is the candidates to test, and `BeforeRev` is the reversed
preamble (the prefix so far). `first_invalid/5` is then a two-clause scan
over the candidates:

- **Clause 1 — the break.** If the candidate has no valid pair, it *is*
  the answer. The `!` commits to this first offender (Part 1 wants the
  *earliest* violation), and only then does `reverse(BeforeRev, Before)`
  reconstruct the forward prefix for Part 2. Doing the reverse after the
  cut means we pay for it exactly once, at the finish line.
- **Clause 2 — advance.** Otherwise the candidate is valid: slide the
  window forward and recurse, prepending the candidate to the reverse
  prefix in `O(1)` (`[Candidate|BeforeRev]`).

`invalid_number/3` is the thin Part 1 wrapper that calls this and discards
the prefix.

### `slide_window/3`

```prolog
slide_window([_|Tail], NewValue, Window1) :-
    append(Tail, [NewValue], Window1).
```

The window is kept oldest-to-newest. Drop the head (the oldest value) and
append the new value at the tail — a pure `O(P)` rebuild that keeps the
frame exactly `P` wide and correctly ordered for the next step.

### `contiguous_range/3` — the range search

```prolog
contiguous_range(Numbers, Target, Range) :-
    contiguous_from_start(Numbers, Target, Range),
    !.

contiguous_from_start([First|Rest], Target, Range) :-
    extend_range(Rest, First, Target, [First], Range).
contiguous_from_start([_|Rest], Target, Range) :-
    contiguous_from_start(Rest, Target, Range).

extend_range([Next|Rest], CurrentSum, Target, ReverseRange, Range) :-
    NewSum is CurrentSum + Next,
    (   NewSum =:= Target
    ->  reverse([Next|ReverseRange], Range)
    ;   NewSum <  Target
    ->  extend_range(Rest, NewSum, Target, [Next|ReverseRange], Range)
    ;   fail
    ).
```

Read this as two nested loops made of backtracking. `contiguous_from_start/3`
is the **outer loop over start positions**: clause 1 says "begin the range
at the current head"; clause 2 says "or skip this head and start later."
`extend_range/5` is the **inner loop that grows one range** from a fixed
start, carrying the running sum and the range so far (built reversed for
`O(1)` cons, reversed once on success). Its three-way test is the whole
algorithm: exact hit → succeed; still short → extend; overshoot → `fail`,
which backtracks the outer loop to the next start. Because `extend_range`
seeds the sum with `First` and must consume at least one `Next` before it
can report equality, every range it returns has **length ≥ 2**, satisfying
the puzzle's "at least two numbers." The outer `!` commits to the first
range found. (There's deliberately no `extend_range([], …)` clause: a start
that runs off the end without hitting `Target` simply fails and backtracks —
absence of a clause *is* the base case.)

### `part1/2`, `part2/2`, `weakness/3`, `solve/3`

```prolog
part1(Numbers, Invalid) :-
    preamble_size(PreambleSize),
    invalid_number(Numbers, PreambleSize, Invalid).

part2_with_preamble(Numbers, PreambleSize, Weakness) :-
    invalid_and_prefix(Numbers, PreambleSize, Invalid, BeforeInvalid),
    weakness(Invalid, BeforeInvalid, Weakness).

weakness(Invalid, BeforeInvalid, Weakness) :-
    contiguous_range(BeforeInvalid, Invalid, Range),
    min_list(Range, Smallest),
    max_list(Range, Largest),
    Weakness is Smallest + Largest.

solve(Raw, Invalid, Weakness) :-
    parse_input(Raw, Numbers),
    preamble_size(PreambleSize),
    invalid_and_prefix(Numbers, PreambleSize, Invalid, BeforeInvalid),
    weakness(Invalid, BeforeInvalid, Weakness).
```

`preamble_size(25)` is the single fact pinning the real size; the
`_with_preamble` variants take it as an argument for the example.
`weakness/3` is the shared fold — given the invalid value and the data
before it, it finds the contiguous range and returns `min + max`.

The two public parts are deliberately **self-contained**: `part1/2` scans
for the invalid value, and `part2/2` scans for it again (via
`invalid_and_prefix/4`) before searching for the range — so each can be
called, tested, and benchmarked in isolation. `solve/3`, however, is the
*combined* entry point: since both parts need the same invalid value, it
runs `invalid_and_prefix/4` **once**, uses the invalid value directly as
Part 1, and hands the invalid value plus its prefix to `weakness/3` for
Part 2. That saves one full Part 1 scan versus calling `part1/2` and
`part2/2` back to back — ~300k inferences, dropping the end-to-end cost
from ~1.33M to ~1.04M (see benchmarks).

---

## Correctness notes

- **The window is always the preceding `P` values.** The initial `Window`
  is exactly the first `P`. Every advancing step drops the oldest and
  appends the accepted candidate, so when candidate *k* is tested the
  window holds precisely values *k−P … k−1* — the puzzle's "immediately
  preceding 25."
- **The pair check is faithful.** `select/3` + `member/2` enumerates every
  ordered choice of two distinct entries; `First =\= Second` enforces the
  "different values" rule (rejecting `25 + 25`). So a value is declared
  invalid iff no admissible pair sums to it.
- **Part 1 returns the earliest violation.** Clause 1 of `first_invalid/5`
  fires — and cuts — at the first candidate with no valid pair, so no later
  offender can be returned instead.
- **Part 2 searches the right data.** It runs over `BeforeInvalid`, the
  values strictly *before* the invalid one, reconstructed from the reverse
  prefix. This both matches the puzzle's "in your list, prior to the
  weakness" framing and dodges a subtle trap: if the invalid number's
  numeric value also appeared *earlier* in the input, searching the whole
  list could latch onto the wrong occurrence. Restricting to the true
  prefix removes the ambiguity.
- **The overshoot cutoff is sound because the values are positive.** Once a
  growing range from a fixed start exceeds `Target`, every longer range
  from that same start is strictly larger too, so it can never come back
  down to `Target` — abandoning that start loses no solution. Trying all
  starts and stopping only on exact equality therefore finds a valid
  contiguous range whenever one exists.
- **Determinism.** `valid_sum/2` commits with a cut; `first_invalid/5`'s
  break clause cuts; `contiguous_range/3` cuts on the first range. The
  suite runs clean with no "succeeded with choicepoint" warnings — the
  repo's determinism bar since [Day 5](day05_function_guide.md).
- Locked real-input answers: **Part 1 = 1930745883**, **Part 2 =
  268878261**, cross-validated by [python/day09.py](../../python/day09.py).

## Tests — what's pinned and why

[test/day09_tests.pl](../../test/day09_tests.pl) pins four layers, **7/7
green** (run `swipl test/run_tests.pl` from the repo root, or
`swipl -g "consult('test/day09_tests.pl'), run_tests(day09), halt"` for
this day alone):

1. **Parser** — the 20-line example string parses to the exact integer
   list, locking the blank-line drop and string→int conversion.
2. **The distinct-values rule** — `valid_sum(50, [25, 25])` is asserted to
   **fail**, pinning the one subtlety a naive "any two entries" check would
   get wrong.
3. **Parts on the example** — with preamble 5: `part1 = 127`,
   `contiguous_range(…, 127) = [15, 25, 47, 40]` (the intermediate range is
   pinned directly, not just the final weakness), and `part2 = 62`.
4. **Real answers** — `1930745883` / `268878261` locked against
   `inputs/day09.txt`, so any refactor that changes a result fails loudly.

## Complexity & benchmarks

Let `N` be the input length (1000) and `P` the preamble size (25).

- **Parse:** `O(N)` time and space — one linear pass.
- **Part 1:** each candidate tests up to `P²` pairs and slides an `O(P)`
  window, so `O(N · P²)` time, `O(N + P)` space. With `P` fixed at 25 this
  is *linear in `N`* with a modest constant.
- **Part 2 (standalone `part2/2`):** `O(N²)` worst case for the
  restart-per-start range scan, `O(N)` space, **plus** a second Part 1 scan
  (it recomputes the invalid value so it can stand alone), which is why its
  inference count below is more than Part 1's.

The benchmark drives the *self-contained* `part1/2` and `part2/2`. Inferences
are exact and reproducible (`swipl bench/main.pl day09` reports the same
counts every run); times are representative single runs:

| Phase | Inferences | Time (ms) |
|-------|-----------:|----------:|
| parse | 6,061 | 0.9 |
| part1 | 299,502 | 9.7 |
| part2 | 1,032,354 | 25.8 |

Standalone Part 2 does ~3.4× Part 1's work: roughly one Part 1 scan (~300k)
to re-find the invalid value (which sits at line 666, so Part 1 tests ~640
candidates), then ~700k more for the contiguous search over the
~665-element prefix. `solve/3` avoids that duplicated scan — it shares one
`invalid_and_prefix/4` call across both parts, so end-to-end it costs
~1.04M inferences rather than the ~1.33M of `part1` + `part2` run
separately. At ~26 ms the whole day is comfortably fast either way, so the
shipped code keeps the readable restart-per-start range form (the repo's
correctness-and-clarity-first policy); the linear alternatives are in the
sidebar.

## If I were writing this in Rust

```rust
use std::collections::HashSet;

fn part1(nums: &[i64], preamble: usize) -> i64 {
    nums.windows(preamble + 1)                 // each slice: 25 window + 1 candidate
        .find_map(|w| {
            let (window, cand) = w.split_at(preamble);
            let target = cand[0];
            let seen: HashSet<i64> = window.iter().copied().collect();
            let valid = window.iter().any(|&x| {
                let need = target - x;
                need != x && seen.contains(&need)   // distinct values summing to target
            });
            (!valid).then_some(target)
        })
        .expect("no invalid number")
}

fn contiguous_range(nums: &[i64], target: i64) -> &[i64] {
    let (mut lo, mut sum) = (0, 0i64);          // two-pointer over a positive series
    for hi in 0..nums.len() {
        sum += nums[hi];
        while sum > target { sum -= nums[lo]; lo += 1; }
        if sum == target && hi - lo >= 1 { return &nums[lo..=hi]; }
    }
    unreachable!()
}

fn part2(nums: &[i64], preamble: usize) -> i64 {
    let invalid = part1(nums, preamble);
    let idx = nums.iter().position(|&x| x == invalid).unwrap();
    let run = contiguous_range(&nums[..idx], invalid);
    run.iter().min().unwrap() + run.iter().max().unwrap()
}
```

- **Prolog list ↔ `&[i64]`.** The window slides for free as
  `nums.windows(P + 1)`; `select`+`member`+`=\=` becomes the natural Rust
  optimization — a `HashSet` complement lookup with the `need != x` guard
  standing in for the distinct-values rule (this is the guide's Part 1
  sidebar, made idiomatic).
- **`extend_range`'s overshoot `fail` ↔ the `while sum > target` shrink.**
  Rust reaches for the amortized **two-pointer** (`lo`/`hi`) that the
  positivity guarantee unlocks — `O(N)` instead of the Prolog version's
  restart-per-start `O(N²)`. Same soundness argument, tighter loop; it's
  the Part 2 sidebar below.
- **The reverse-prefix trick disappears.** Rust just slices `&nums[..idx]`
  after `position`; Prolog threads the prefix through the recursion because
  it has no `O(1)` random slice.

The Python reference ([python/day09.py](../../python/day09.py)) is the
middle ground — an explicit `numbers[i-preamble:i]` window and a
grow-from-each-start range scan that mirrors the shipped Prolog — and
re-confirms `1930745883` / `268878261`.

## Possible optimization

- **Part 1 in `O(N·P)` with a windowed multiset.** Keep a hash multiset of
  the current 25 values. To test `Target`, iterate one value `X` and look
  up `Target − X` (respecting the distinct-values rule and multiplicities);
  slide by decrementing the departing value and incrementing the arriving
  one. That drops the per-candidate pair check from `P²` to `O(P)` (near
  `O(1)` expected per probe). Irrelevant at `P = 25` — the bounded scan is
  already sub-10 ms — but it's the technique that matters if the preamble
  grows.
- **Part 2 in `O(N)` with a two-pointer.** For a positive series, maintain
  a window `lo..hi` and a running sum: advance `hi` to grow, advance `lo`
  to shrink whenever the sum overshoots. Each index moves at most once, so
  the whole search is linear instead of the shipped `O(N²)`. This is the
  Rust version above; the Prolog stays with the restart-per-start form
  because it reads closer to the problem's "contiguous range" wording and
  the `O(N²)` cost is invisible at `N = 1000`.
- **Share the invalid-number scan in `solve/3`** — *done.* Both parts need
  the first invalid value, and the naive `solve` (`part1` then `part2`)
  scans for it twice. `solve/3` now runs `invalid_and_prefix/4` once and
  feeds the result to both parts, cutting ~300k inferences (~1.33M → ~1.04M
  end-to-end). The standalone `part1/2` and `part2/2` deliberately keep their
  own scans so they remain independent entry points for tests and the
  bench; only the combined path is deduplicated.
- Sidebar material only; the shipped shape follows the repo's
  correctness-and-clarity-first policy.
