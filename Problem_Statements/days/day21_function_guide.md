# Day 21 Function Guide — Allergen Assessment

> Thirty-eight foods, each an ingredients list in a language I cannot
> read followed by some of its allergens in one I can. Two rules: every
> allergen lives in exactly one ingredient, and when a food lists an
> allergen, the ingredient holding it is somewhere in that food's list.
> Part 1 wants how many times the ingredients that *cannot* hold any
> allergen appear across all the lists; part 2 wants each allergen's
> ingredient, sorted by allergen name and joined with commas — a string,
> the only non-numeric answer in the year. The shipping solution is one
> set intersection per allergen (its candidates are the ingredients
> common to every food that lists it) followed by day 16's singleton
> peeling to resolve the candidates to one ingredient each. The whole
> day runs in a quarter of a millisecond; the interesting content is
> why the intersection is exactly what the two rules say, and why the
> set part 1 excludes turns out to be exactly the set part 2 assigns.

Source: [`python/day21.py`](../../python/day21.py) ·
Tests: [`python/tests/test_day21.py`](../../python/tests/test_day21.py) ·
Prolog companion: [`prolog/day21.pl`](../../prolog/day21.pl), section 8

---

## 1. The problem

Each input line is a food:

```text
mxmxvkd kfcds sqjhc nhms (contains dairy, fish)
trh fvjkl sbzzf mxmxvkd (contains dairy)
sqjhc fvjkl (contains soy)
sqjhc mxmxvkd sbzzf (contains fish)
```

Ingredient names are gibberish; allergen names are English. The
statement's rules, restated as constraints:

1. **Each allergen is in exactly one ingredient.** So `dairy` names a
   single unknown ingredient, and so does `fish`, and so on.
2. **Each ingredient holds zero or one allergen.** Two allergens never
   share an ingredient.
3. **If a food lists allergen A, A's ingredient is in that food's
   list.** This is the only positive evidence there is.
4. **Allergens are not always listed.** A food that does *not* mention
   A may still contain A's ingredient. So the absence of a label says
   nothing, and the rule cannot be run backwards.

Part 1: which ingredients can hold no allergen at all, and how many
times do they appear over all the lists? In the sample, `kfcds`,
`nhms`, `sbzzf` and `trh` are inert; they appear once each except
`sbzzf`, which appears twice, so the answer is 5.

Part 2: which ingredient holds which allergen? In the sample `mxmxvkd`
is dairy, `sqjhc` is fish, `fvjkl` is soy. Sort by allergen (dairy,
fish, soy) and join the ingredients with commas:
`mxmxvkd,sqjhc,fvjkl`.

The real input has 38 foods, 200 distinct ingredients, 2,338 ingredient
appearances (39 to 84 per food), and 8 allergens, each listed by 7 to
13 foods. Every food lists at least one allergen, though the statement
permits a food listing none and the parser accepts one.

## 2. Representation

**A `Food` is a `NamedTuple` of two tuples of strings**: `ingredients`
as written, in order, and `allergens` (empty when the line has no
`(contains ...)`). The ingredients stay a tuple rather than becoming a
set because part 1 counts *appearances*: if an ingredient were ever
written twice on one line it should count twice, and a set would
silently collapse that. (On the real input no line repeats an
ingredient — checked while writing this — but the representation should
not depend on it.) `candidates` builds a set from the tuple per food
when it needs one.

**The parsed input is `list[Food]`.** Order never matters, but a list
is the honest shape of "one per line".

**Candidates are `dict[str, set[str]]`**, allergen name to the
ingredients that could still hold it. This is the structure both parts
work from, and the one the elimination mutates (on a private copy).

**The assignment is `dict[str, str]`**, allergen to ingredient. Part 2
sorts its keys and joins its values.

**Part 2's answer is a `str`**, so `part2` returns `str` and `solve`
returns `tuple[int, str]`. The repo's `check_locked` fixture compares
tuples and does not care about the element types, so the day fits the
convention without a special case; it is just the one day whose
`LOCKED` will hold a string.

## 3. Function walkthrough

### `parse_input(raw) -> list[Food]`

`splitlines()`, then per line `.strip()` and `partition(" (contains ")`.
The head splits on whitespace into ingredients; the tail, if there was
a separator, has its closing `)` removed and splits on `", "` into
allergens. A line with no separator gets `allergens=()`.

The CRLF hazard is specific. With `\r\n` endings and no strip, the
tail of every line would end in `)\r`, `removesuffix(")")` would see
the `\r` last and remove nothing, and every line's final allergen would
come out as a string like `fish)\r`. No two lines would then agree on
any allergen, and every candidate set would be a single food's whole
ingredient list. The per-line strip happens before the partition, so
none of that arises; the CRLF test runs the sample with `\r\n` endings
through and asserts the same `Food`s come out.

### `candidates(foods) -> dict[str, set[str]]`

For each food and each allergen it lists, intersect the allergen's
running candidate set with the food's ingredients; the first food to
mention an allergen seeds its set. Foods that list no allergen
contribute nothing, and a food that lists `dairy` says nothing about
`fish`. On the sample:

```text
food 1 lists dairy, fish: dairy = {mxmxvkd, kfcds, sqjhc, nhms}
                          fish  = {mxmxvkd, kfcds, sqjhc, nhms}
food 2 lists dairy:       dairy ∩= {trh, fvjkl, sbzzf, mxmxvkd} = {mxmxvkd}
food 3 lists soy:         soy   = {sqjhc, fvjkl}
food 4 lists fish:        fish  ∩= {sqjhc, mxmxvkd, sbzzf}      = {mxmxvkd, sqjhc}
```

Result: `dairy → {mxmxvkd}`, `fish → {mxmxvkd, sqjhc}`,
`soy → {sqjhc, fvjkl}` — pinned as a test, as is the fact that
appending an *unlabelled* food containing `sqjhc` changes none of it.

On the real input the eight sets come out with sizes 4, 2, 3, 4, 1, 3,
2, 2 (dairy, eggs, fish, peanuts, sesame, shellfish, soy, wheat), and
their union has exactly 8 members. Eight allergens, eight suspects.

### `assign(possible) -> dict[str, str]`

Day 16's `assign_fields`, on a dict instead of a list. Copy the sets,
then loop: every allergen whose set has one member is *forced* to it;
pop those, strike their ingredients from every remaining set, repeat.
If a round forces nothing, the sets admit more than one matching and
the function raises rather than pick one. A final check that no two
allergens landed on the same ingredient guards rule 2.

On the sample, three rounds:

```text
round 1: dairy {mxmxvkd}        fish {mxmxvkd, sqjhc}  soy {sqjhc, fvjkl}
         → dairy = mxmxvkd; strike mxmxvkd
round 2:                        fish {sqjhc}           soy {sqjhc, fvjkl}
         → fish = sqjhc; strike sqjhc
round 3:                                               soy {fvjkl}
         → soy = fvjkl
```

On the real input, six rounds. The sizes at the start of each round,
and what that round forces:

| round | dairy | eggs | fish | peanuts | sesame | shellfish | soy | wheat | forced |
| ----: | ----: | ---: | ---: | ------: | -----: | --------: | --: | ----: | ------ |
| 1 | 4 | 2 | 3 | 4 | **1** | 3 | 2 | 2 | sesame = kfgln |
| 2 | 4 | **1** | 3 | 3 | | 2 | 2 | 2 | eggs = jmvxx |
| 3 | 3 | | 2 | 3 | | **1** | 2 | 2 | shellfish = pqqks |
| 4 | 2 | | **1** | 2 | | | 2 | 2 | fish = lkv |
| 5 | **1** | | | **1** | | | **1** | 2 | dairy, peanuts, soy |
| 6 | | | | | | | | **1** | wheat = lclnj |

This is *not* day 16's staircase. There, the twenty sets had sizes
exactly 1..20 and were nested, so each round forced exactly one column.
Here the starting sizes are `[1, 2, 2, 2, 3, 3, 4, 4]`, two allergens
tie at four, and round 5 forces three at once. The elimination does
not need the staircase; it needs only that *some* set is a singleton
at every round, and the tests pin that this input has that property
(by asserting `assign` returns all eight) without pinning a shape it
does not have.

### `part1(foods) -> int`

Union the candidate sets into one *suspect* set, then count the
ingredient appearances not in it:

```python
suspect = set().union(*candidates(foods).values())
return sum(ingredient not in suspect for food in foods for ingredient in food.ingredients)
```

`sum` over booleans counts the `True`s. On the real input, 2,338
appearances of which 266 are suspects, so 2,072.

Part 1 does **not** resolve the allergens. It does not need to, and
there is a test in which it cannot: two allergens whose candidates are
both `{a, b}` can never be told apart, `part2` raises on them, but an
ingredient `d` in neither set is inert regardless, and `part1` says so.

### `part2(foods) -> str`

`assign(candidates(foods))`, then the holders in allergen order,
comma-joined. The sort is by *allergen*, which the sample demonstrates
(alphabetically `fvjkl` would be first; by its allergen `soy` it is
last) and a test pins along with the no-spaces rule.

## 4. Why it is correct

**The intersection is exactly rule 3.** For allergen A, let h(A) be
its ingredient (rule 1 says there is exactly one). Every food F that
lists A has h(A) ∈ F.ingredients (rule 3). So h(A) is in the
intersection of those foods' ingredient sets — the candidate set
contains the true holder. Nothing else is claimed: the candidate set
may hold impostors, ingredients that happen to ride along in every
A-labelled food, and the sample's `fish → {mxmxvkd, sqjhc}` has one
(`mxmxvkd`, which is really dairy).

**Rule 4 is why only labelled foods are intersected.** A food not
listing A may or may not contain h(A). If it does not, and we wrongly
intersected with it, we would strike h(A) and the true holder would be
gone. Only foods that *positively* list A are evidence, and the code
touches only those. The unlabelled-food test is this argument as an
assertion.

**Part 1 is sound.** An ingredient in no candidate set is not the
holder of any allergen, since every holder is in its allergen's
candidate set. "Cannot possibly contain any allergen" is therefore
decided correctly for every ingredient the code calls inert. Could an
ingredient *in* some candidate set also be inert (an impostor for every
allergen it is a candidate for)? In general yes, and then part 1 would
undercount — but see the identity below: on any input the peeling can
resolve, there are no such ingredients.

**Peeling is sound.** If A's set is `{x}`, then h(A) ∈ {x} forces
h(A) = x. Striking x from B's set is rule 2: x already holds A, so it
does not hold B. Each step preserves "the true holder is in the set",
so whatever the loop assigns is forced by the rules, never a guess.
When a round forces nothing the sets genuinely admit more than one
matching, and the code raises. Day 16 had the same argument.

**The identity the two parts share: when peeling completes, the union
of the candidate sets equals the set of assigned ingredients.** One
direction is trivial (every assigned ingredient came out of a set).
The other: suppose ingredient u is in some allergen's candidate set S
but is never assigned. S ends the loop as a singleton `{v}` with v ≠ u,
so u was struck from S at some round. But an ingredient is struck only
when it has just been *assigned* to some allergen. Contradiction. So
every suspect is a holder, part 1's "suspect" set is precisely part 2's
holders, and part 1 equals total appearances minus the holders'
appearances. This is pinned on the real input as
`test_real_every_suspect_ingredient_holds_an_allergen`. It is what
makes the union-of-candidates reading of part 1 not merely sound but
exact on every input the puzzle actually poses.

## 5. Complexity

With F foods, I ingredient appearances in total, and A allergens:
parsing is O(I). `candidates` is O(I) set construction plus one
intersection per (food, listed allergen) pair, each bounded by the
food's size — O(I · a) where a is the most allergens on one line
(3 here). `assign` is at most A rounds of A set differences over sets
of size ≤ the largest candidate set, so O(A² · c) with c ≤ 4; it is
8 allergens and negligible. Part 1 is I set-membership tests. The day
is linear in the input, dominated by the 2,338 membership tests.

Measured on the real input (`python\bench.py 21 -n 20`, best / median):

| phase  |     best |   median |
| ------ | -------: | -------: |
| parse  | 0.077 ms | 0.079 ms |
| part 1 | 0.140 ms | 0.149 ms |
| part 2 | 0.055 ms | 0.064 ms |

A scratch script taking the best of 200 runs per phase (the regime
sections 6 and 7 use, so their numbers compare like with like) gives
0.070–0.074 / 0.122–0.123 / 0.053–0.054 ms over three repeats: the
same picture with the noise floor shaved. Inside part 1, `candidates`
alone is about 0.047 ms and the 2,338 membership tests are the rest.
Inside part 2, `assign` is 0.005 ms — the six rounds cost less than
building the sets they peel. In the repo-wide `python\bench.py -n 3`
day 21's total is eighth fastest of the 22 solved days, between day 12
and day 2; nothing here is worth optimising, and section 7 measures
what happens if you try.

## 6. If I were writing this in Rust

The same algorithm with one representation change that is the natural
one for an embedded engineer: **an ingredients list is a bitset.**
Intern each ingredient name to an index the first time it is seen (a
`HashMap<&str, usize>` and a `Vec<&str>` for the reverse map); with 200
ingredients a food's list is a `[u64; 4]`, and intersection, union,
complement and "is this a singleton" are word-wise `&`, `|`, `!` and
`count_ones() == 1`. The candidate map is `HashMap<&str, [u64; 4]>`,
`assign` is the same loop with `retain` and a `taken` mask, and part 1
is one `|`-fold over the candidate masks followed by a bit test per
appearance:

```rust
type Mask = [u64; 4]; // 200 ingredients fit in 256 bits

fn candidates<'a>(menu: &Menu<'a>) -> HashMap<&'a str, Mask> {
    let mut possible: HashMap<&str, Mask> = HashMap::new();
    for food in &menu.foods {
        for &allergen in &food.allergens {
            possible
                .entry(allergen)
                .and_modify(|m| *m = and(*m, food.mask))
                .or_insert(food.mask);
        }
    }
    possible
}

fn part1(menu: &Menu) -> usize {
    let suspect = candidates(menu).values().fold([0u64; 4], |acc, m| or(acc, *m));
    menu.foods
        .iter()
        .flat_map(|f| f.ingredients.iter())
        .filter(|&&i| suspect[i / 64] >> (i % 64) & 1 == 0)
        .count()
}
```

The `Food` keeps both the `Vec<usize>` of indices (for counting
appearances faithfully) and the mask (for the set algebra). Lifetimes
are the only Rust-specific noise: the `Food`s borrow their allergen
names from the input string, so `Menu<'a>` and `candidates<'a>` carry
the lifetime through to the returned map's keys.

The port was compiled with `rustc -O` (1.93.1) and run three times on
the real input while writing this guide, best of 200 inside each run.
Same two answers; parse **0.066–0.077 ms**, part 1 **0.0025–0.0026 ms**,
part 2 **0.0021 ms**. Part 1 and part 2 are about 50× and 25× faster,
which is what bit operations on four words buy against Python sets of
strings. The parse is **not faster at all** — 0.066–0.077 ms against
Python's 0.070–0.074 under the same regime — and that is the
instructive number: Python's `str.split` is a C loop, and the Rust
parse does strictly more work, interning 2,338 names through a SipHash
`HashMap`. Python's parse does no hashing until the parts build sets.
This is day 18's ratio on the parts (per-element overhead *is* the
cost) and parity on the parse, so the day's honest speed-up is about
3.5× overall, from 0.25 ms to 0.07 ms — and the Rust version is then
entirely parse-bound.

## 7. Possible optimization

Three things measured on the real input from a scratch script (best of
200 runs; same answers as shipping in every case):

| variant                                             | shipping | variant |
| --------------------------------------------------- | -------: | ------: |
| one `candidates()` shared by both parts             | 0.176 ms (part 1 + part 2) | 0.129 ms |
| part 1 via `Counter`: total − holders' appearances  | 0.122 ms | 0.157 ms |
| ingredients interned to bit positions, `int` masks: parse | 0.070 ms | 0.273 ms |
| … part 1                                            | 0.122 ms | 0.010 ms |
| … part 2                                            | 0.053 ms | 0.012 ms |
| … parse + part 1 + part 2                           | 0.245 ms | 0.295 ms |

**Sharing `candidates`** saves the 0.05 ms of building the sets twice.
It is the day 20 argument again: `part1(parsed)` and `part2(parsed)`
are independent by convention, and 50 µs does not buy a special case.

**Counting with a `Counter`** is the identity from section 4 turned
into code — total appearances minus the holders' appearances — and it
is slower, because building the `Counter` is 2,338 dict increments
where the shipping version does 2,338 set lookups and nothing else.
It is the right shape for a *test* (where it is) and the wrong shape
for the solver.

**Bitmask ints** are the Rust port's representation done in Python:
intern each ingredient to a bit, a food is one `int`, and candidates
are `&`. Parts 1 and 2 get 12× and 4× faster — Python's big-int `&`
and `bit_count()` are C loops over a few words — but the parse gets
4× *slower*, because interning 2,338 names is a Python-level loop with
a dict lookup each, where the shipping parse is `str.split` and a
tuple. The total is worse. The lesson is the section 6 one from the
other side: the machine framing pays only when the interning is
amortised over work that dwarfs it, and here the parse *is* most of
the work. Shipping code stays `set[str]`, which is also what the
statement is written in.

## 8. The Prolog companion

This repo's Prolog era is over and `src/` is frozen, but Matt's rule
from this day is that where a puzzle genuinely fits Prolog, a companion
should exist. Day 21 is the first: [`prolog/day21.pl`](../../prolog/day21.pl),
in a new `prolog/` directory so the frozen tree stays frozen. It is not
the maintained solution and it is not a port of the Python; it is the
same puzzle written in a language whose execution model *is* the
algorithm.

The reason it fits is section 3's `assign`. In Python, resolving the
candidates is hand-written search control: rounds, a forced set, a
strike step, a "refuse to guess" branch, a duplicate-holder check. In
Prolog, part 2 is three clauses and nothing else:

```prolog
assign([], [], _).
assign([Allergen-Candidates|More], [Allergen-Ingredient|Solution], Used) :-
    member(Ingredient, Candidates),
    \+ memberchk(Ingredient, Used),
    assign(More, Solution, [Ingredient|Used]).
```

Read against the statement: `member(Ingredient, Candidates)` is rule 1,
one ingredient per allergen; `\+ memberchk(Ingredient, Used)` is rule
2, no ingredient holds two. Backtracking supplies the elimination. When
`dairy` picks an impostor and a later allergen finds every candidate
already used, Prolog backs up and `dairy` picks again. There are no
rounds because nothing is being peeled; the search simply does not
return until every allergen has a distinct holder.

The part that is *better* than the Python, rather than merely shorter,
is section 4's uniqueness argument. The Python guide had to prove in
prose that peeling never leaves an unassigned suspect and raise on
ambiguity. In Prolog "is the assignment unique" is a question the
program can be asked:

```prolog
?- foods('inputs/day21.txt', Fs), allergen_candidates(Fs, Ps),
   aggregate_all(count, assign(Ps, _, []), N).
N = 1.
```

Measured (SWI-Prolog 10.0.2, real input): the first solution of
`assign/3` costs **63 inferences**; the whole of `solve/3`, parsing
included, **36,892**. The search is 0.2% of the work; the rest is
`split_string`, `atomic_list_concat` and eight `ord_intersection`s,
the same parse-dominated shape as the Python and the Rust.

One honest caveat, the same one from the Rust and bitmask sections
turned around: generate-and-test is exponential in the worst case where
singleton peeling is polynomial. Over eight allergens with candidate
sets of size 1 to 4 the difference does not exist, but the Python
version's guarantee is the stronger one on a hostile input, and that,
plus the repo's direction, is why it is the one that ships.

The companion runs standalone from anywhere (`swipl prolog/day21.pl`,
input resolved relative to the file; an optional path argument
substitutes another foods file), and `test_day21.py` runs it through
`swipl` on the sample, a CRLF sample and the real input, checking the
answers against the Python module's. Without `swipl` on PATH those
three tests skip, so a machine without SWI-Prolog stays green.
