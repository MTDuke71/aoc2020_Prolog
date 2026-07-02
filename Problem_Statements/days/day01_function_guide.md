# Day 01 Function Guide — Report Repair

> First real day of AoC 2020, and the first day where **backtracking does the
> work**. [Day 00](day00_function_guide.md) was deliberately deterministic —
> every predicate had exactly one solution. Day 1 is the opposite: the whole
> solution is one nondeterministic predicate, `k_sum/4`, whose alternative
> clauses *are* the search. If Day 0 taught `is/2` vs `=/2`, Day 1 teaches
> choice points.

## The puzzle in one paragraph

Input is an expense report: one positive integer per line (200 lines in the
real input). **Part 1:** find the two entries that sum to `2020` and multiply
them. **Part 2:** same, but three entries. Both parts are instances of the
classic **k-SUM** problem with `k = 2` and `k = 3`.

---

## Reading Prolog: backtracking, choice points, and `once/1`

**1. Multiple clauses are a decision, not an override.** In Rust, a `match`
picks exactly one arm. In Prolog, when a goal like `k_sum(2, 2020, [1721|Xs], C)`
is called, *every* clause whose head unifies is a live alternative. The engine
tries them top-to-bottom and leaves a **choice point** at each untried one; on
failure it rewinds (undoing unifications) and resumes at the most recent choice
point. `k_sum/4` has two recursive clauses — "take the head" and "skip the
head" — and that pair of alternatives, applied at every list position, *is* a
depth-first search over subsets. No loop, no stack data structure: the clause
order is the search order.

**2. `once/1` = "first solution only."** `once(G)` runs `G`, commits to its
first solution, and discards the remaining choice points. The puzzle promises a
unique answer, so `entry_product/3` wraps the search in `once/1` — otherwise a
later `findall` or a stray backtrack could re-enter the search. It's the
disciplined version of a cut: scoped, and readable at the call site.

**3. `msort/2` vs `sort/2` — a real trap.** `sort/2` sorts *and removes
duplicates*. If the report contained `1010` twice, `sort/2` would silently
delete the pair whose product is the answer. `msort/2` sorts and keeps
duplicates. (Tested explicitly — see the test section.)

**4. `findall/3` reaps all solutions.** `findall(C, k_sum(...), Combos)` drives
the nondeterministic goal to exhaustion and collects every binding of `C`. It's
how the tests pin the *enumeration* behavior, not just the first hit.

**5. Lambdas via `yall`.** `foldl([X, Acc0, Acc]>>(Acc is Acc0 * X), Combo, 1, P)`
is SWI's inline-lambda fold: `[Params]>>Body` builds an anonymous predicate.
`foldl/4` threads the accumulator left-to-right, so this is exactly
`combo.iter().fold(1, |acc, x| acc * x)`.

---

## The Day 1 code, predicate by predicate

### `parse_input/2`

```prolog
parse_input(Raw, Entries) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(number_string, Entries, Lines).
```

Byte-for-byte the [Day 00 parser](day00_function_guide.md) — split on
newlines, trim CRLF debris, drop blanks, read integers. This
lines-of-integers shape will recur (Day 9, Day 10 at least), so it's worth
recognizing on sight.

### `k_sum/4` — the whole algorithm

```prolog
% k_sum(+K, +Target, +Entries, -Combo)
k_sum(0, 0, _, []).
k_sum(K, Target, [X|Xs], [X|Combo]) :-
    K > 0,
    X =< Target,
    K1 is K - 1,
    T1 is Target - X,
    k_sum(K1, T1, Xs, Combo).
k_sum(K, Target, [_|Xs], Combo) :-
    K > 0,
    k_sum(K, Target, Xs, Combo).
```

Read the three clauses as the three cases of a recursive enumeration:

- **Clause 1 (base):** we've taken exactly `K` elements (`K` counted down to
  `0`) and they consumed the target exactly (`Target` reached `0`). The empty
  combination completes the answer.
- **Clause 2 (take):** put the head `X` into the combination, then find `K-1`
  more elements summing to `Target - X` *in the tail* `Xs`.
- **Clause 3 (skip):** don't use `X`; search the tail with `K` and `Target`
  unchanged.

Two structural points make this correct and duplicate-free:

- **Recursing on the tail in both clauses** means each element is considered
  once, at its own position, and combinations come out in input order —
  `[1721, 299]` can be found but `[299, 1721]` can never be generated
  separately. This is the standard "combinations, not permutations" DFS shape.
- **The `X =< Target` guard prunes.** Entries are positive, so once the head
  alone exceeds the remaining target, clause 2 cannot possibly succeed —
  failing early kills that branch before recursing. This only works because
  `entry_product/3` sorts first: on an ascending list, a too-big head also
  means every deeper `take` from this prefix is too big.

**In algorithm-literature terms:** this is **k-SUM solved by depth-first
enumeration of k-combinations with prefix-sum pruning** — a small instance of
branch-and-bound over the subset tree. The same take/skip clause pair is the
skeleton for subset-sum, knapsack enumeration, and the combination generators
in later AoC days.

**Why it terminates:** every recursive call is on the strict tail of the list,
so the third argument shrinks on every step and bottoms out at `[]`, where
only clause 1 (if `K = 0, Target = 0`) or nothing can apply.

### `entry_product/3`, `part1/2`, `part2/2`, `solve/3`

```prolog
entry_product(K, Entries, Product) :-
    msort(Entries, Sorted),
    once(k_sum(K, 2020, Sorted, Combo)),
    foldl([X, Acc0, Acc]>>(Acc is Acc0 * X), Combo, 1, Product).

part1(Entries, Answer) :- entry_product(2, Entries, Answer).
part2(Entries, Answer) :- entry_product(3, Entries, Answer).
```

Both parts are one predicate with a different `K` — the payoff of writing
`k_sum/4` generically instead of hard-coding a pair search. `msort/2` (not
`sort/2`; see trap above) enables the pruning guard; `once/1` commits to the
puzzle's unique solution; `foldl` multiplies the combination out. `solve/3`
is the standard parse-once-answer-both shape from Day 0.

---

## Correctness notes

- **Soundness:** clause 1 only succeeds when exactly `K` elements were taken
  totaling exactly `Target`, so any `Combo` produced is a valid answer.
- **Completeness:** at every list position the search tries both *take* and
  *skip*, so every K-combination is reachable; pruning only cuts branches
  whose prefix already exceeds `Target`, which (entries being positive) can
  never contain a solution.
- Example verified: part 1 finds `1721 × 299 = 514579`, part 2 finds
  `979 × 366 × 675 = 241861950` — both match the problem statement.
- Locked real-input answers: **Part 1 = 902451**, **Part 2 = 85555470**,
  cross-validated by [python/day01.py](../../python/day01.py).

## Tests — what's pinned and why

[test/day01_tests.pl](../../test/day01_tests.pl) pins four layers, **8/8
green** (63/63 repo-wide):

1. **Parser** — the example block parses to the six integers.
2. **Both worked examples** — asserted as products (`1721 * 299`,
   `979 * 366 * 675`), so the test text mirrors the puzzle text.
3. **Search semantics** — `k_sum_enumerates_all` uses `findall/3` to check
   the *full* solution set on a hand-built case (order and count, not just
   membership); `duplicate_entries` locks the `msort` decision by requiring
   `1010 + 1010` to be found; `no_solution_fails` uses plunit's `[fail]`
   option to assert the search fails cleanly rather than erroring.
4. **Real answers** — `902451` / `85555470` locked against
   `inputs/day01.txt`.

Run: `swipl test/run_tests.pl` from the repo root (runs every day's suite).

## Complexity & benchmarks

- Sorting: `O(n log n)`, once.
- Worst case the DFS visits every K-combination: `O(C(n, k))` — `O(n²)` for
  part 1, `O(n³)` for part 2. At `n = 200` that's at most 2·10⁴ / 1.3·10⁶
  nodes, and pruning cuts well below that.
- Space: `O(n)` for the list, `O(k)` recursion depth beyond the list walk.

Mean of 10,000 iterations (`swipl bench/main.pl day01` is the single-shot
version):

| Phase | Time (ms) |
|-------|----------:|
| parse | 0.042 |
| part1 | 0.189 |
| part2 | 1.731 |

First day where the *search* visibly dominates: part 2 is ~9× part 1, which
tracks the extra factor of `n` in the combination count. Still under 2 ms —
comfortably inside the "no optimization needed" zone.

## If I were writing this in Rust

```rust
fn k_sum(k: usize, target: i64, entries: &[i64]) -> Option<Vec<i64>> {
    if k == 0 {
        return (target == 0).then(Vec::new);
    }
    for (i, &x) in entries.iter().enumerate() {
        if x > target { break; }               // ascending ⇒ prune the rest
        if let Some(mut combo) = k_sum(k - 1, target - x, &entries[i + 1..]) {
            combo.push(x);
            return Some(combo);
        }
    }
    None
}
```

- Prolog's two recursive clauses collapse into one `for` loop: iterating `i`
  *is* the skip clause, the recursive call at each `i` *is* the take clause.
  What Prolog gets from the engine (resume-at-last-choice-point), Rust spells
  as explicit control flow.
- `once/1` ↔ returning `Option` and short-circuiting with `return Some(...)`
  instead of collecting all solutions.
- `msort/2` ↔ `sort_unstable()` on a `Vec<i64>` (Rust's sort never dedups, so
  the `sort/2` trap has no Rust analogue — one of the rare places Prolog has
  the sharper edge).
- `foldl` with a `yall` lambda ↔ `combo.iter().product::<i64>()`.
- See [python/day01.py](../../python/day01.py) for the same DFS as a recursive
  *generator* — Python's `yield` is a readable halfway point between Prolog's
  choice points and Rust's explicit loop.

## Possible optimization

- **Hash-set two-sum:** put entries in a set; for each `X` check membership of
  `2020 - X`. `O(n)` for part 1, and `O(n²)` for part 2 by fixing one element
  and two-summing the rest. In SWI the "set" could be a `library(assoc)` AVL
  tree (`O(n log n)`) or tabled facts. This is the textbook answer to k-SUM,
  and the right move if `n` were 10⁵ instead of 200.
- **Two-pointer scan** on the sorted list: `O(n)` per two-sum after sorting,
  `O(n²)` for 3SUM — the standard competitive-programming shape, but it
  translates awkwardly to lists (needs indexed access to be worth it).
- Neither is warranted at `n = 200` / 1.7 ms; the nondeterministic `k_sum/4`
  is the idiomatic Prolog and stays per the repo's optimization policy.
