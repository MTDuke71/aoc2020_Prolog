# Tutorial Day 4: Parsing Input Text

## Why this day matters
Most AoC bugs happen in **parsing and normalization**, not in the core algorithm.
A puzzle input is just a blob of text with a trailing newline; before you can
solve anything you have to turn it into typed Prolog data — lists of integers,
grids, records. Get the parser right *once*, deterministically, and both Part 1
and Part 2 reuse it. This day builds the small parsing toolkit the real
`src/dayNN.pl` files will lean on, and confronts the thing that surprises everyone
coming from Rust: **SWI-Prolog has several different "string" types**, and picking
the wrong one is the #1 source of parsing confusion.

## Focus Topics
- The SWI text types: **string** vs. **atom** vs. **code list** vs. **char list**
- `split_string/4` — the parsing workhorse (separators *and* padding)
- Dropping empty segments with `exclude/3` and the `=("")` idiom
- Converting text to numbers with `number_string/2` + `maplist/3`
- Keeping the parser **deterministic** and structuring data for part1/part2 reuse

## Learning Goals
- Build a robust line parser that survives trailing/blank lines.
- Convert line-oriented text into typed structures (lists of integers).
- Know which text type you're holding and how to convert between them.
- Understand how a malformed line behaves (it **fails**, it doesn't throw — see
  Gotchas).

## Files
- `day4.pl`: three parsers — lines, integer-lines, and CSV integers.
- `day4_tests.pl`: `plunit` tests pinning the exact output shape of each.

```prolog
:- module(day4, [parse_lines/2, parse_int_lines/2, parse_csv_ints/2]).
```

## Run the tests
From repo root:

```bash
swipl -q -s tutorial/day4/day4_tests.pl
```

## Start the REPL

```bash
swipl
```
```prolog
?- ['tutorial/day4/day4.pl'].
```

## First, the thing that trips everyone up: SWI text types

In Rust there's basically `String`/`&str` and you're done. In SWI-Prolog a piece
of text can be **four different kinds of term**, and they do **not** unify with
each other even when they "look the same":

| Type | Literal | What it is | `?- X == ...` |
|---|---|---|---|
| **string** | `"abc"` (default) | an opaque string object | `"abc"` |
| **atom** | `abc` or `'abc'` | an interned symbol | `abc` |
| **code list** | `` `abc` `` or `[97,98,99]` | list of character *codes* (ints) | `[97,98,99]` |
| **char list** | `[a,b,c]` | list of one-char atoms | `[a,b,c]` |

The literal `"abc"` is a **string** because SWI's `double_quotes` flag defaults to
`string`. That's why the tests assert `L == ["a","b"]` (strings), not `[a,b]`
(atoms) — `"a" == a` is **false**. This matters constantly: `split_string/4`
*produces strings*, so everything downstream stays in string-land until you
deliberately convert.

Conversions you'll actually use (all bidirectional):

```prolog
?- atom_string(abc, S).        S = "abc".          % atom  <-> string
?- number_string(42, S).       S = "42".           % number <-> string
?- atom_number('42', N).       N = 42.             % atom  <-> number
?- string_chars("abc", Cs).    Cs = [a,b,c].       % string <-> char list
?- string_codes("abc", Cs).    Cs = [97,98,99].    % string <-> code list
```

Rust analogy: think of it as `String` vs. an *interned* `&'static str` (atom) vs.
`Vec<u8>` (codes) vs. `Vec<char>` (chars) — same text, genuinely different types,
explicit conversions required.

## The workhorse: `split_string/4`

```prolog
split_string(+String, +SepChars, +PadChars, -SubStrings)
```

- **String** — the text to cut up.
- **SepChars** — every character in this string is a separator. `"\n"` splits on
  newlines; `",;"` would split on commas *and* semicolons.
- **PadChars** — characters stripped from **both ends of each piece** after
  splitting. `" \t\r"` trims spaces, tabs, and carriage returns — handy for
  Windows `\r\n` line endings and stray indentation.
- **SubStrings** — the resulting list of **strings**.

Watch what it does with a trailing/blank-laden input:

```prolog
?- split_string("a\nb\n\n", "\n", " \t\r", S).
S = ["a", "b", "", ""].
```

Two empty strings appear at the end — one for the gap before the final newline,
one after it. **This is the single most common parsing surprise:** a trailing
newline (which every AoC input has) yields a trailing `""`. We don't fight it; we
filter it out in the next step.

> Edge note: when `SepChars` and `PadChars` share characters, `split_string`
> collapses adjacent separators (useful for "split on runs of whitespace"). We
> don't rely on that here, but it's why the argument exists.

## Dropping the empties: `exclude/3` and the `=("")` idiom

```prolog
exclude(=(""), Split, Lines)
```

`exclude(Goal, List, Kept)` (from `library(apply)`) keeps every element for which
`Goal` **fails**. The clever part is `=("")`:

- `=/2` is unification. `=("")` is a **partially applied** goal — it's `=` with
  its first argument fixed to `""`, still missing one.
- `exclude` supplies each list element as that missing argument, so for element
  `E` it runs `=("" , E)`, i.e. `"" = E`.
- That succeeds exactly when `E` is the empty string — so `exclude` **drops** the
  empty strings and keeps the real lines.

This partial-application trick (a goal missing its last argument, completed by the
higher-order predicate) is everywhere in idiomatic Prolog — the same shape as
`maplist(number_string, ...)` below.

## Converting with `maplist/3`

```prolog
maplist(number_string, Ints, Lines)
```

`maplist/3` applies a 2-argument goal across two lists in lockstep — it's Rust's
`.iter().map()` / `.zip()` rolled into one relation. Here it calls
`number_string(I, L)` for each `Int`/`Line` pair.

The argument order looks backwards but isn't: `number_string(?Number, ?String)`
puts the *number* first, so `maplist(number_string, Ints, Lines)` reads
"`Ints` are the numbers of the `Lines`." Because `number_string` is bidirectional,
the *same* code would render numbers back to strings if you bound `Ints` instead —
a recurring Prolog theme (one relation, multiple modes).

## Predicate Walkthroughs (line by line)

### `parse_lines/2` — text blob → clean list of line strings

```prolog
parse_lines(Raw, Lines) :-
    split_string(Raw, "\n", " \t\r", Split),
    exclude(=(""), Split, Lines).
```

Two steps: split on newlines (trimming whitespace/`\r` from each piece), then drop
the empty strings that blank/trailing lines produce.

Trace of `parse_lines("a\nb\n\n", L)`:

```text
split_string("a\nb\n\n", "\n", " \t\r", Split)
    Split = ["a", "b", "", ""]        % note the two trailing empties
exclude(=(""), ["a","b","",""], L)
    L = ["a", "b"]                    % empties removed
```

This is the canonical `parse_input/2` skeleton: **split, then clean.** It's robust
to trailing newlines, blank separator lines, and Windows `\r\n`.

### `parse_int_lines/2` — one integer per line

```prolog
parse_int_lines(Raw, Ints) :-
    parse_lines(Raw, Lines),
    maplist(number_string, Ints, Lines).
```

Reuse `parse_lines/2` to get clean line strings, then map each to a number. This
*composition* — a general parser feeding a typed one — is exactly the reuse the
exit criteria asks for.

```prolog
?- parse_int_lines("10\n20\n30\n", Ns).
Ns = [10, 20, 30].
```

### `parse_csv_ints/2` — one comma-separated line → integers

```prolog
parse_csv_ints(Line, Ints) :-
    split_string(Line, ",", " \t\r", Pieces),
    exclude(=(""), Pieces, Clean),
    maplist(number_string, Ints, Clean).
```

Same shape as the other two, but the separator is `","` instead of `"\n"`. The
`" \t\r"` padding is what lets `"1, 2,3"` (note the space after the first comma)
parse cleanly — each piece is trimmed before conversion.

```prolog
?- parse_csv_ints("1, 2,3", Ns).
Ns = [1, 2, 3].
```

Trace:

```text
split_string("1, 2,3", ",", " \t\r", Pieces)
    Pieces = ["1", "2", "3"]          % the space in " 2" is trimmed by padding
exclude(=(""), ["1","2","3"], Clean)
    Clean = ["1", "2", "3"]           % nothing to drop here
maplist(number_string, Ints, ["1","2","3"])
    Ints = [1, 2, 3]
```

### The shared recipe

All three parsers are the same three-beat pattern:

| Step | `parse_lines` | `parse_int_lines` | `parse_csv_ints` |
|---|---|---|---|
| 1. split | on `"\n"` | (via `parse_lines`) | on `","` |
| 2. clean | drop `""` | (via `parse_lines`) | drop `""` |
| 3. convert | — | `maplist number_string` | `maplist number_string` |

Learn the recipe once and most AoC parsing is a variation on it: change the
separator, change (or add) the conversion.

## The Tests, One by One

```prolog
:- begin_tests(day4).
:- use_module('./day4.pl').

test(parse_lines)     :- parse_lines("a\nb\n\n", L),       assertion(L == ["a","b"]).
test(parse_int_lines) :- parse_int_lines("10\n20\n30\n", Ns), assertion(Ns == [10,20,30]).
test(parse_csv_ints)  :- parse_csv_ints("1, 2,3", Ns),     assertion(Ns == [1,2,3]).

:- end_tests(day4).
```

| Test | What it pins down |
|---|---|
| `parse_lines` | the split-then-clean core; input has a **blank trailing line** so it proves the empties are dropped. Asserts **strings** (`"a"`, not `a`). |
| `parse_int_lines` | composition + conversion; trailing newline survived, output is **integers** |
| `parse_csv_ints` | comma split + padding; the `" 2"` proves whitespace trimming works |

Note the `==` (not `=`): after parsing, the result is fully bound, and `==`
checks it's *exactly* this list — including that the elements are strings vs.
numbers, which is the whole point of the type discussion above.

## REPL Drills

```prolog
?- split_string("a\nb\n", "\n", " \t\r", L).   % L = ["a","b",""]  -- see the trailing ""
?- maplist(number_string, Ns, ["10","20","30"]).% Ns = [10,20,30]
?- exclude(=(""), ["a","","b"], K).            % K = ["a","b"]
?- string_chars("hi", Cs).                      % Cs = [h,i]
?- atom_string(foo, S).                         % S = "foo"   (atom -> string)
?- parse_lines("  x  \n\n y \n", L).            % L = ["x","y"] -- padding trims the spaces
```

## Verification (maps to the checklist)
- **Empty input:** `parse_lines("", L)` gives `L = []` — no crash.
- **Single line:** `parse_lines("a", L)` gives `L = ["a"]`.
- **Whitespace-only lines:** `parse_lines("  \n\t\n", L)` gives `L = []` — padding
  reduces each line to `""`, then `exclude` drops them.
- **Parser shape asserted directly:** each test uses `==` on the full result.

## Common Gotchas
- **The trailing-`""` artifact.** Every real input ends in `\n`, so `split_string`
  always hands you a trailing `""`. Always `exclude(=(""), ...)` (or equivalent)
  after splitting line-oriented text.
- **String ≠ atom.** `"a" == a` is **false**. `split_string` yields strings; if a
  later predicate expects atoms, convert with `atom_string/2` or `maplist`.
- **Malformed numbers *fail*, they don't throw.** `number_string(N, "bad")`
  **fails** (no exception), so `parse_int_lines("10\nbad\n", R)` quietly **fails**
  rather than raising a clear error. If you want a loud failure or a default,
  wrap the conversion (e.g. with `catch/3`, or a clause that maps unparseable
  lines to a sentinel). Don't assume a bad input throws.
- **`number_string` arg order is `(Number, String)`.** The number comes first even
  though it's usually the output — match `maplist(number_string, Ints, Strings)`.
- **`=` vs `=:=` vs `==` (recap).** `exclude(=(""), ...)` uses unification `=`
  (right for "is this the empty string?"); tests use `==` for exact already-bound
  comparison; arithmetic comparison would be `=:=`.

## The AoC Payoff: parse once, reuse in both parts

The reason to invest in a clean parser is that Part 2 almost always reuses Part 1's
parsed data. The shipping `src/dayNN.pl` shape is:

```prolog
solve(File, Part1, Part2) :-
    read_file_to_string(File, Raw, []),  % library(readutil)
    parse_int_lines(Raw, Data),          % <- today's parser, once
    part1(Data, Part1),
    part2(Data, Part2).
```

`Data` is computed a single time and threaded into both parts. Keeping the parser
**deterministic** (one answer, no leftover choicepoints — Day 3's lesson) means
`solve/3` doesn't accidentally backtrack into re-parsing.

## Rust bridge

```rust
fn parse_int_lines(raw: &str) -> Vec<i64> {
    raw.lines()                       // split_string on "\n"
       .map(str::trim)                // the " \t\r" padding
       .filter(|l| !l.is_empty())     // exclude(=(""), ...)
       .map(|l| l.parse().unwrap())   // maplist(number_string, ...)
       .collect()
}
```

Near one-to-one. Two differences worth holding onto: (1) Prolog's
`number_string` is *bidirectional* — the same predicate parses *and* formats,
where Rust needs `.parse()` and `.to_string()` as separate calls; and (2) Rust's
`.parse().unwrap()` **panics** on bad input, whereas Prolog's version **fails** —
a quieter failure mode you have to test for deliberately.

## Exit Criteria
- You can write one `parse_input/2` and reuse the parsed data in both parts.
- You can name the four SWI text types and convert between string/atom/number.
- You can explain why a trailing `""` appears and how `exclude/3` removes it.
- You can read the `=("")` partial-application idiom and the `maplist/3` mapping.
- You know that a malformed numeric line *fails* rather than throwing.

## Next Step
Day 5 builds on parsing with:
- consuming the parsed list safely via **accumulator-passing** recursion
- **tail recursion** and last-call optimization (constant-stack folds)
- the prepend-then-reverse idiom and `foldl/4` as its library form
