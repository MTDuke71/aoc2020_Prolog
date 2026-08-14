# Day 04 Function Guide — Passport Processing

> **Written during this repo's Prolog era.** The solution it describes lives
> in the frozen `src/` tree. The maintained solution for this day is
> `python/day04.py`, tested by `python/tests/test_day04.py`. This guide is
> kept for its problem framing and algorithm reasoning, which did not change
> with the language; it will be rewritten Python-first when this day is next
> touched. See the README for what "frozen" means here.

---

> [Day 02](day02_function_guide.md) parsed one record per line;
> Day 4 breaks the line-per-record assumption two ways: records span
> *multiple* lines (blank lines separate them), and fields arrive in *any
> order* with some optional. That forces the repo's first key-value
> representation — Prolog's stand-in for a dict — and its first
> **rule-table predicate**: `valid_field/1`, one clause per field kind,
> where clause selection *is* the dispatch. It's also the first `src/` use
> of `forall/2`, and the day plunit's choice-point warning caught a real
> wart (see the `once/1` note).

## The puzzle in one paragraph

The batch file holds 282 passports, each a bag of `key:value` fields
separated by spaces or newlines, with blank lines between passports.
**Part 1:** count passports that carry all seven required fields (`byr`,
`iyr`, `eyr`, `hgt`, `hcl`, `ecl`, `pid` — `cid` is optional). **Part 2:**
same, but every field value must also satisfy its rule (year ranges,
`cm`/`in` height ranges, `#`+6 lowercase hex, an eye-color enum, exactly
nine digits). No algorithm to speak of — this is a **data-validation**
day, and the interest is in how cleanly the rules transcribe.

---

## Reading Prolog: pairs-as-dict, `forall/2`, and clause-table dispatch

**1. A "dict" is a list of pairs until proven otherwise.** Each passport
parses to `[ecl-"gry", pid-"860033327", ...]` — a list of `Key-Value`
pairs (Day 3 introduced the pair term; here it earns its keep). Lookup is
`memberchk(Key-Value, Passport)`: unification does the matching, first hit
wins, `O(fields)` per lookup. With at most eight fields that beats any
real dictionary; when a later day needs thousands of keys, `library(assoc)`
(AVL trees) or SWI's native dicts (`_{byr: ...}`) take over. The lesson is
the default: **small mapping = pair list + `memberchk`**.

**2. `forall/2` is universal quantification.**
`forall(member(Key, [byr, ...]), memberchk(Key-_, Passport))` reads as
math: *for every required key, some pair with that key is present*.
Operationally it's double negation — `\+ (Cond, \+ Action)` — "there is no
counterexample." Two consequences worth internalizing: it never leaves
choice points (negation is deterministic), and **no bindings escape** —
you can't use `forall/2` to collect anything (that's `findall/3`'s job,
Day 1). Pure check, no data out.

**3. A predicate can *be* the lookup table.** The whole of part 2's rule
set is:

```prolog
valid_field(byr-V) :- year_range(V, 1920, 2002).
valid_field(iyr-V) :- year_range(V, 2010, 2020).
...
valid_field(cid-_).
```

No `if key == "byr"` chain — the clause *heads* do the dispatch, by
unification. Adding a field kind is adding a clause; removing one is
deleting a clause; `cid`'s "always fine" rule is a fact with an anonymous
value. This clause-per-case style is the Prolog analogue of a `match` on
the key, and SWI's argument indexing picks the right clause without a
linear scan. When the rules live in clauses, the code *is* the statement's
bullet list — compare them side by side.

**4. `0'c` is a character-code literal, and it pattern-matches.**
`string_codes(V, [0'#|Hex])` does three things at once: converts the value
to codes, *requires* the first code to be `#`, and names the rest `Hex` —
parse, guard, and destructure in one unification. `0'#` is the code (35)
of `#`; Day 3's Rust bridge already met its twin, `b'#'`.

**5. `once/1` around a grammar — a warning made real.** `height//2` has
two clauses:

```prolog
height(H, cm) --> integer(H), "cm".
height(H, in) --> integer(H), "in".
```

Parsing `"190cm"` succeeds in the first clause — but the second is still
*untried*, so the success carries a dangling choice point. Harmless here
(any backtrack would just fail), but plunit flagged it: *"Test succeeded
with choicepoint."* The fix is Day 1's tool at Day 2's layer:
`once(phrase(height(H, Unit), Codes))` — a value has one parse; commit to
it. Day 2 solved the same problem *inside* the code with if-then-else;
`once/1` solves it *around* a goal you'd rather not contort. Both are the
same discipline: don't ship choice points you don't mean.

**6. plunit's `forall` option = parameterized tests.**

```prolog
test(field_valid, [forall(member(Field, [byr-"2002", hgt-"60in", ...]))]) :-
    valid_field(Field).
```

runs the body once per binding and reports each separately (`38-1`,
`38-2`, ...). One test clause pins all thirteen of the statement's worked
field values — table-driven tests for a table-driven predicate.

---

## The Day 4 code, predicate by predicate

### `parse_input/2`, `blocks/2`, `block_rest/3`

```prolog
parse_input(Raw, Passports) :-
    split_string(Raw, "\n", " \t\r", Lines),
    blocks(Lines, Blocks),
    maplist(block_passport, Blocks, Passports).

blocks([], []).
blocks([""|Rest], Blocks) :- !,
    blocks(Rest, Blocks).
blocks([Line|Rest], [[Line|More]|Blocks]) :-
    block_rest(Rest, More, Tail),
    blocks(Tail, Blocks).

block_rest([], [], []).
block_rest([""|Rest], [], Rest) :- !.
block_rest([Line|Rest], [Line|More], Tail) :-
    block_rest(Rest, More, Tail).
```

The usual line-splitter feeds `blocks/2`, which groups consecutive
non-blank lines: skip leading blanks, then let `block_rest/3` peel off the
non-blank prefix (`More`) and hand back the remainder (`Tail`) for the
recursion. `block_rest/3` is Haskell's `break`/`span` shape — one walk
returning both the prefix and the rest — and the pair of green cuts is
Day 3's `drop/3` story again: clauses made explicitly mutually exclusive
so no choice points survive. **Blank-line-separated blocks recur in AoC
(Day 6's answer groups, Day 22's decks) — `blocks/2` is written to be
lifted into `src/common/` the day it's needed twice.**

### `block_passport/2` and `token_field/2`

```prolog
block_passport(Lines, Passport) :-
    atomic_list_concat(Lines, ' ', Joined),
    split_string(Joined, " ", "", Tokens0),
    exclude(=(""), Tokens0, Tokens),
    maplist(token_field, Tokens, Passport).

token_field(Token, Key-Value) :-
    split_string(Token, ":", "", [KeyS, Value]),
    atom_string(Key, KeyS).
```

"Fields separated by spaces *or newlines*" is normalized in one move: glue
the block's lines back together with spaces (`atomic_list_concat/3`), then
split on spaces — newline separators are now space separators. Each token
splits at the colon; the two-element list pattern `[KeyS, Value]` doubles
as a format check (a token with zero or two colons fails loudly). Keys
become atoms (they're a closed vocabulary for clause dispatch); values
stay strings (they're data to validate).

### `has_required_fields/1` and `valid_passport/1`

```prolog
has_required_fields(Passport) :-
    forall(member(Key, [byr, iyr, eyr, hgt, hcl, ecl, pid]),
           memberchk(Key-_, Passport)).

valid_passport(Passport) :-
    has_required_fields(Passport),
    forall(member(Field, Passport), valid_field(Field)).
```

Two quantifiers, two directions: part 1 quantifies over the *required
keys* ("each must appear in the passport"), part 2 additionally
quantifies over the *present fields* ("each must satisfy its rule").
`cid` threads the needle by appearing in neither the required list nor
any restrictive rule — `valid_field(cid-_)` accepts anything, which is
exactly "ignored, missing or not."

### `valid_field/1` and its helpers

```prolog
valid_field(hgt-V) :-
    string_codes(V, Codes),
    once(phrase(height(H, Unit), Codes)),
    (   Unit == cm
    ->  between(150, 193, H)
    ;   between(59, 76, H)
    ).
valid_field(hcl-V) :-
    string_codes(V, [0'#|Hex]),
    length(Hex, 6),
    maplist(hex_lower, Hex).
valid_field(pid-V) :-
    string_codes(V, Codes),
    length(Codes, 9),
    maplist(digit_code, Codes).

year_range(Value, Lo, Hi) :-
    string_codes(Value, Codes),
    length(Codes, 4),
    maplist(digit_code, Codes),
    number_codes(Year, Codes),
    between(Lo, Hi, Year).
```

Every textual rule gets the same treatment: convert to codes, constrain
the *shape* (length, digit-ness, leading `#`), then constrain the *value*
(`between/3`, Day 2's all-bound range check). Shape-before-value matters:
`year_range/3` demands *exactly four digits* before converting, so
`"02e2"` (a number! `number_codes` would read it as 200.0) or `"+200"`
never sneak through — the validation is strictly stricter than "parses as
a number in range." The height rule reuses Day 2's grammar machinery for
the only field with real structure; `ecl` is a one-liner `memberchk` on
the enum; `pid`'s `length(Codes, 9)` is the whole leading-zeroes story —
digits are checked as *text*, never converted.

### `part1/2`, `part2/2`, `solve/3`

```prolog
part1(Passports, Answer) :-
    include(has_required_fields, Passports, Valid),
    length(Valid, Answer).
```

Day 2's filter-count shape verbatim, with the two validity predicates
slotted in. `solve/3` is the standard parse-once-answer-both.

---

## Correctness notes

- **Grouping:** `blocks/2` produces exactly the maximal runs of non-blank
  lines — leading, trailing, and repeated blank lines all vanish into
  separators, so CRLF debris or a trailing newline can't create ghost
  passports.
- **Part 1** is the statement's rule by direct quantification: all seven
  required keys present, `cid` never consulted. The four example
  passports classify valid/invalid/valid/invalid = 2, matching.
- **Part 2** adds per-field validation over *present* fields. All
  thirteen worked field values classify as stated; the four
  known-invalid passports score 0 and the four known-valid score 4.
- **Strictness:** every rule checks textual shape before numeric value
  (see `year_range/3` above), so float notation, signs, or wrong lengths
  fail even when the numeric value would be in range.
- **Determinism:** `forall/2` never leaves choice points; the one
  grammar-induced choice point (`height//2`) is closed with `once/1` —
  found by plunit's warning, not by luck.
- Locked real-input answers: **Part 1 = 250**, **Part 2 = 158**,
  cross-validated by [python/day04.py](../../python/day04.py).

## Tests — what's pinned and why

[test/day04_tests.pl](../../test/day04_tests.pl) pins four layers, **10
tests + 11 forall sub-tests green** (85/85 repo-wide):

1. **Parser** — a two-passport mini-input parses to exact pair lists,
   pinning key order, atom keys, and string values.
2. **Field rules** — the statement's 6 valid and 7 invalid worked values,
   run as two `forall`-parameterized tests against `valid_field/1`
   directly (each value reported as its own sub-test).
3. **Whole passports** — the statement's four invalid passports must
   score `part2 = 0` and the four valid ones `part2 = 4`, with a
   `length/2` guard proving the blank-line grouping saw four passports
   in each batch.
4. **Real answers** — `250` / `158` locked against `inputs/day04.txt`.

Run: `swipl test/run_tests.pl` from the repo root (runs every day's suite).

## Complexity & benchmarks

Let `n` = total input size (~19 KB), `P` = 282 passports, `F` ≤ 8 fields
each.

- **Parse:** `O(n)` — each character is split/joined a constant number of
  times.
- **Part 1:** per passport, 7 required keys × `O(F)` `memberchk` — call it
  `O(P·7·F)`, comfortably tiny.
- **Part 2:** part 1's check plus `O(F)` rule applications of `O(len)`
  each — still linear in input size.

Inferences are exact and reproducible (`swipl bench/main.pl day04` reports
the same counts every run); the times are the mean of 1,000 iterations:

| Phase | Inferences | Time (ms) |
|-------|-----------:|----------:|
| parse | 19,054 | 1.340 |
| part1 | 7,153 | 0.405 |
| part2 | 37,437 | 1.521 |

Day 2's profile again — string-slicing parse work dominating trivial
logic — at a slightly larger scale. Part 2 costs ~3.8× part 1: same
required-fields check plus a codes conversion and rule per field.

## If I were writing this in Rust

```rust
struct Passport(HashMap<String, String>);

fn valid_field(key: &str, value: &str) -> bool {
    match key {
        "byr" => valid_year(value, 1920, 2002),
        "iyr" => valid_year(value, 2010, 2020),
        "eyr" => valid_year(value, 2020, 2030),
        "hgt" => valid_height(value), // strip_suffix("cm")/("in"), parse, range-check
        "hcl" => value.strip_prefix('#')
            .is_some_and(|h| h.len() == 6
                && h.bytes().all(|b| b.is_ascii_hexdigit() && !b.is_ascii_uppercase())),
        "ecl" => ["amb","blu","brn","gry","grn","hzl","oth"].contains(&value),
        "pid" => value.len() == 9 && value.bytes().all(|b| b.is_ascii_digit()),
        "cid" => true,
        _ => false,
    }
}
```

- The `valid_field/1` clause table ↔ a `match` on `&str` — the closest
  Rust gets to clause-head dispatch. One honest difference: Prolog's
  version has no `_ => false` arm; an unknown key just *fails to match
  any clause* and the call fails. Failure-as-falsehood replaces the
  explicit default.
- Pair-list-as-dict ↔ `HashMap<String, String>` — Rust reaches for the
  hash map by reflex; the pair list is Prolog being honest that `F ≤ 8`.
  (`memberchk` ↔ `map.get(key)`, `O(F)` vs `O(1)`, irrelevant at this
  size.)
- `forall(member(...), ...)` ↔ `.iter().all(...)` — universal
  quantification as a fold over booleans instead of double negation.
- `string_codes(V, [0'#|Hex])` ↔ `value.strip_prefix('#')` returning
  `Option` — unification failure and `None` are the same control flow.
- `blocks/2` ↔ `raw.split("\n\n")` — Rust (like Python's
  `re.split(r"\n\s*\n")` in [python/day04.py](../../python/day04.py))
  splits the raw string; the Prolog version groups *lines*, which is why
  it shrugs off `\r\n` and trailing blanks without regex help.

## Possible optimization

- **Sorted-fields subset check:** `msort/2` each passport's keys once,
  then `ord_subset/2` against the sorted required list — replaces
  7×`memberchk` with one linear merge. The classic set-operations move;
  invisible below thousands of passports.
- **SWI dicts:** parse each passport to `passport{byr: "1937", ...}` and
  test with `get_dict/3` — native `O(log F)` lookup and prettier syntax,
  at the cost of SWI-only code. Worth knowing the option exists; the repo
  stays portable-flavored.
- **Validate during parse:** `token_field/2` could call `valid_field/1`
  and tag each field valid/invalid once, letting both parts count tags —
  saves re-walking values, muddies the parse/part boundary the bench
  depends on. Declined, same as Day 3's fused-slopes idea.
- All of it is sidebar material at 1.5 ms; the shipped shape follows the
  repo's optimization policy.
