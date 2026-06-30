# Day 00 Function Guide — The Tyranny of the Rocket Equation

> Tutorial **dry run** (it's AoC 2019 Day 1, reused). Besides solving the
> puzzle, this day's job is to exercise the whole per-day pipeline —
> `src/day00.pl`, `test/day00_tests.pl`, `bench/main.pl`, this guide, and a
> `python/day00.py` cross-check — once, end to end, before AoC 2020 proper
> begins on July 1. So the guide spends a section on Prolog reading mechanics
> and the rest on the Day 0 code itself.

## The puzzle in one paragraph

Input is a list of module masses, one integer per line. **Part 1:** for each
module, `fuel = floor(mass / 3) - 2`; sum them. **Part 2:** fuel has mass too,
so it needs its own fuel, which needs its own fuel, … Keep applying the same
formula to each newly-added chunk of fuel until a step yields nothing
positive, and sum the whole chain per module.

---

## Reading Prolog: relations, unification, and `is`

Day 0 is deliberately **backtracking-free** — every predicate here has exactly
one solution and is used in one mode. That makes it the right place to pin down
the three mechanics you'll lean on every later day.

**1. Predicates are relations, not functions.** `fuel(Mass, Fuel)` does not
"return"; it *relates* a mass to its fuel. The last argument is conventionally
the output, but that's a convention, not syntax. The mode comment
`fuel(+Mass, -Fuel)` documents how we actually call it: `+` = bound on entry,
`-` = produced.

**2. `=/2` is unification; `is/2` is arithmetic.** This is the single most
common beginner trap coming from Rust:

| Goal | Meaning |
|------|---------|
| `X = 3 + 2` | unify `X` with the **term** `+(3,2)` — `X` is now a 3-element tree, *not* `5` |
| `X is 3 + 2` | evaluate the right side arithmetically, unify `X` with `5` |

`is/2` requires its right side to be fully ground and arithmetic; that's why
`Fuel is Mass // 3 - 2` needs `Mass` already bound. `=/2` never evaluates — it
only matches structure.

**3. `//` vs `div`.** `//` is truncating integer division (toward zero);
`div` is flooring. For non-negative masses they coincide, and both equal the
puzzle's "divide by three and round down." We use `//`; for positive input the
choice is moot, but it's worth knowing they differ on negatives.

**4. If-then-else is `( Cond -> Then ; Else )`.** The `->` commits to the
first solution of `Cond` (a *soft cut*) and then runs `Then`; if `Cond` fails,
`Else` runs. It is the relational spelling of the Part 2 stop condition.

---

## The Day 0 code, predicate by predicate

### `parse_input/2`

```prolog
parse_input(Raw, Masses) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(number_string, Masses, Lines).
```

- `split_string(Raw, "\n", " \t\r", Lines0)` splits on newlines and trims
  `" \t\r"` from each piece. Trimming `\r` is what makes this robust to
  Windows CRLF endings — without it, `number_string/2` would choke on a
  trailing carriage return. (Worth remembering: AoC inputs on Windows
  routinely carry `\r`.)
- `exclude(=(""), Lines0, Lines)` drops the empty string left by the trailing
  newline. `=("")` is a *partial application*: `exclude` calls the goal
  `=("", E)` for each element `E`, dropping those for which it succeeds.
- `maplist(number_string, Masses, Lines)` is the relational map. Note the
  argument order: `number_string(-Number, +String)` reads a string into a
  number, so with `Lines` bound and `Masses` unbound, `maplist` produces the
  integer list. This is the same "first element is the verb" idea as a
  higher-order call in any language — `number_string` is the function, the two
  lists are mapped in lockstep.

- **Rust analogue:** `raw.lines().filter(|l| !l.trim().is_empty()).map(|l| l.trim().parse().unwrap()).collect()`.

### `fuel/2` — the Part 1 kernel

```prolog
fuel(Mass, Fuel) :- Fuel is Mass // 3 - 2.
```

A direct transcription of the spec. The `is/2` is doing real work here —
`Fuel = Mass // 3 - 2` would have left `Fuel` as an unevaluated term.

### `total_fuel/2` — the Part 2 fixed-point iteration

```prolog
total_fuel(Mass, Fuel) :-
    fuel(Mass, Step),
    (   Step =< 0
    ->  Fuel = 0
    ;   total_fuel(Step, Rest),
        Fuel is Step + Rest
    ).
```

This is the **algorithm hiding inside Day 0**: a *fixed-point iteration* (a.k.a.
"iterate to convergence"). You repeatedly apply `fuel` to its own output and
accumulate each positive result, stopping when the map leaves the positive
region. Naming it matters — the same shape recurs whenever you apply a step
function until it stabilizes (Newton's method; the stabilization passes in
later AoC grid puzzles).

**Why it terminates:** the orbit `Mass → fuel(Mass) → fuel(fuel(Mass)) → …`
strictly decreases — each step is roughly `m/3` — so it's a geometric decay
with ratio ≈ 1/3. That same ratio is why Part 2's total is only ~1.5× Part 1's
rather than unbounded (`1 + 1/3 + 1/9 + … = 3/2`).

**A note on tail recursion:** this clause is *not* tail-recursive — the
`Fuel is Step + Rest` runs *after* the recursive call returns, so each level
leaves a frame. An accumulator version (carry the running sum down, return it
at the base case) would be tail-recursive and run in constant stack, mirroring
the Racket guide's named-`let loop`. At `O(log Mass)` ≈ 11 frames deep it makes
no practical difference here, so the readable shape wins — see the optimization
sidebar.

### `part1/2`, `part2/2`, `solve/3`

```prolog
part1(Masses, Answer) :- maplist(fuel, Masses, Fuels), sum_list(Fuels, Answer).
part2(Masses, Answer) :- maplist(total_fuel, Masses, Fuels), sum_list(Fuels, Answer).
solve(Raw, P1, P2) :- parse_input(Raw, Masses), part1(Masses, P1), part2(Masses, P2).
```

`maplist/3` maps the per-module predicate over the list; `sum_list/2` folds
with `+`. `solve/3` parses once, then runs both parts — the same
"parse once, produce both answers" shape every later day reuses.

---

## Correctness notes

- `fuel/2` verified on all four worked examples: `12→2`, `14→2`, `1969→654`,
  `100756→33583`.
- `total_fuel/2` verified on `14→2`, `1969→966`, `100756→50346`; termination
  argued above.
- Locked real-input answers: **Part 1 = 3481005**, **Part 2 = 5218616**.

## Tests — what's pinned and why

[test/day00_tests.pl](../../test/day00_tests.pl) pins three layers, **7/7
green**:

1. **Parser** — `parse_input("12\n14\n1969\n", [12,14,1969])`, locking the
   blank-line drop and string→int conversion.
2. **Every worked example** from the puzzle text, for both `fuel/2` and
   `total_fuel/2`, plus the `part1`/`part2` sums over the example list.
3. **The real answers** — read from `inputs/day00.txt` and asserted to equal
   `3481005` / `5218616`. Pinning the actual answer means any future refactor
   that changes the result fails loudly instead of silently.

Run: `swipl -g "use_module(library(plunit)), consult('test/day00_tests.pl'), run_tests(day00), halt"`.

## Complexity & benchmarks

- Part 1: `O(n)` over `n` modules, each `O(1)`.
- Part 2: `O(n · log Mass)` — each module's fuel chain has `O(log Mass)` steps.
- Space: `O(n)` parsed list; `total_fuel/2` recursion depth `O(log Mass)`.

Mean of 100,000 iterations each (`swipl bench/main.pl day00` does a single
shot; these are the repeated-measure numbers):

| Phase | Time (ms) |
|-------|----------:|
| parse | 0.022 |
| part1 | 0.011 |
| part2 | 0.148 |

Calibration for the cold reader: the whole day is well under a millisecond.
Unlike the Racket port (where parsing dominated), here **Part 2 dominates** —
~13× Part 1 — because the per-module fixed-point recursion is the only
non-trivial work. Anything in later days that is *not* sub-millisecond is doing
real algorithmic work.

## If I were writing this in Rust

```rust
fn fuel(mass: i64) -> i64 { mass / 3 - 2 }

fn total_fuel(mass: i64) -> i64 {
    std::iter::successors(Some(fuel(mass)), |&f| Some(fuel(f)))
        .take_while(|&f| f > 0)   // stop at the first non-positive step
        .sum()
}
```

- Parsed list ↔ `Vec<i64>` from
  `input.lines().map(|l| l.parse().unwrap()).collect()`.
- Rust `/` on `i64` truncates toward zero, matching `//` for non-negative
  masses.
- The interesting correspondence is `total_fuel`: Prolog spells the
  fixed-point iteration as explicit recursion with an `( -> ; )` stop guard;
  Rust says the same thing declaratively — `successors(seed, step)` *is*
  "iterate this function," and `take_while(|&f| f > 0)` *is* the `Step =< 0`
  guard. Two spellings of one idea. `maplist`+`sum_list` ↔ `.map(...).sum()`.
- See [python/day00.py](../../python/day00.py) for the same logic in the
  imperative `while f > 0 { total += f; f = fuel(f); }` shape.

## Possible optimization

- **Accumulator/tail-recursive `total_fuel`** for constant stack — irrelevant
  at depth ≈ 11, documented above only as the transferable technique.
- None of it is needed at `n = 100`; readable Prolog wins here per the repo's
  optimization policy.
