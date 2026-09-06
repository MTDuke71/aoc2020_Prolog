# Day 18 Function Guide — Operation Order

> A page of arithmetic homework with the precedence rules changed: in
> part 1 `+` and `*` rank equally and go left to right, in part 2 `+`
> outranks `*`. Parentheses still mean parentheses. This is the puzzle
> where every calculator, compiler and spreadsheet begins — turn a string
> of numbers and operators into a value — and the classic answer is a
> machine with two stacks, one for values not yet used and one for
> operators not yet applied. Its only knob is a precedence table, so part 2
> is part 1 with a different table passed in. The same 10,528 tokens, the
> same loop, two different answers.

Source: [`python/day18.py`](../../python/day18.py) ·
Tests: [`python/tests/test_day18.py`](../../python/tests/test_day18.py)

---

## 1. The problem

Each line of the input is an expression over non-negative integers, `+`,
`*` and parentheses:

```text
2 * (8 + 3 * 3 + (4 + 5)) + 7 * 2
```

**Part 1.** Addition and multiplication have the *same* precedence and are
evaluated strictly left to right; parentheses group as usual. Sum the
value of every line. The statement's `1 + 2 * 3 + 4 * 5 + 6` is 71 —
`((((1 + 2) * 3) + 4) * 5) + 6` — where school arithmetic says 33.

**Part 2.** Addition now binds *tighter* than multiplication, the reverse
of school. The same expression is 231: `(1 + 2) * (3 + 4) * (5 + 6)`.
Sum every line again.

The real input is 370 lines, 3 to 73 tokens each, 10,528 tokens in all:
4,491 numbers (every one a single digit 2–9), 2,016 `+`, 2,105 `*` and 958
pairs of parentheses, nested at most two deep. Nothing in the code relies
on any of that — the tokenizer accepts multi-digit numbers and the stacks
grow as needed — but it says what the machine actually has to cope with.

## 2. Representation

**Tokens.** `parse_input` returns one `list[int | str]` per line: the
integers as `int`, the four symbols `+ * ( )` as one-character strings.
`1 + (2 * 3)` becomes `[1, "+", "(", 2, "*", 3, ")"]`. Turning text into
tokens once, up front, means the evaluator never looks at a character, and
both parts consume the same list.

**The precedence table** is a `dict[str, int]` — higher binds tighter:

| table             | `+` | `*` | reading                                   |
| ----------------- | --: | --: | ----------------------------------------- |
| `SAME_PRECEDENCE` |   1 |   1 | equal rank, so left to right (part 1)     |
| `ADDITION_FIRST`  |   2 |   1 | `+` outranks `*` (part 2)                 |

This is the entire difference between the parts. School arithmetic would
be `{"+": 1, "*": 2}`; the evaluator does not know or care which table it
is given.

**The machine** is two stacks: `values`, integers not yet consumed by an
operator, and `ops`, operators (and open parentheses) seen but not yet
applied. In embedded terms it is a tiny stack CPU with a data stack and a
return-address stack, and section 4 works out how deep each needs to be —
on the real input, never more than 7 values and 8 operators.

## 3. Function walkthrough

### `tokenize(line) -> list[Token]`

```python
TOKEN = re.compile(r"\d+|[+*()]|\S")
```

The regex finds, in order, a run of digits, one of the four symbols, or
*any other non-space character*. That last alternative is deliberate: a
`findall` over just the first two would silently skip a `-` or a letter,
and the day 6 lesson was that silently skipping is how a bad byte becomes
a wrong answer. Instead every match is checked — digits become `int`,
symbols are kept, anything else raises `ValueError` naming the character
and the line. Whitespace is never matched, so spacing is irrelevant:
`1+2` and `  1   +  2 ` tokenize identically (a test).

### `parse_input(raw) -> list[list[Token]]`

`splitlines()`, skip blank lines, `strip()` each and tokenize. The strip
is where CRLF is handled: a surviving `\r` would reach the tokenizer as a
non-space character and be rejected, so on a Windows download the strict
tokenizer would refuse every line. `test_crlf_input` pins it.

### `evaluate(tokens, precedence) -> int`

```python
for token in tokens:
    if isinstance(token, int):
        values.append(token)
    elif token == "(":
        ops.append(token)
    elif token == ")":
        while ops[-1] != "(":
            reduce()
        ops.pop()
    else:
        while ops and ops[-1] != "(" and precedence[ops[-1]] >= precedence[token]:
            reduce()
        ops.append(token)
while ops:
    reduce()
```

where `reduce()` pops one operator and two values and pushes the result.
Five cases, one per kind of token:

- **A number** is pushed onto `values`. It cannot be used yet because the
  operator to its right, if any, has not been seen.
- **`(`** is pushed onto `ops` as a fence. Nothing below it may be applied
  until the matching `)` arrives.
- **`)`** applies everything above the fence, then removes the fence. What
  is left on `values` is the parenthesised group's value, sitting exactly
  where a number would.
- **An operator** first applies every waiting operator that binds *at
  least as tightly* as itself — those are to its left and, by the rule
  being implemented, must go first — and then waits in turn. The fence
  stops the walk. The `>=` rather than `>` is what makes equal-precedence
  operators associate to the left; with `>`, `2 * 3 + 4` under the part 1
  table would come out as `2 * (3 + 4)`. That one character is a test
  (`test_equal_precedence_associates_left_not_right`).
- **End of input** applies whatever is still waiting. One value remains;
  anything else means the expression was malformed and the code raises
  rather than returning a guess.

Here is the statement's first example under the part 1 table. The
`values` stack never holds more than two numbers, because every operator
reduces the one before it the moment it arrives: this is a running total.

| token | values   | ops   | what happened      |
| ----- | -------- | ----- | ------------------ |
| `1`   | `[1]`    | `[]`  |                    |
| `+`   | `[1]`    | `[+]` |                    |
| `2`   | `[1, 2]` | `[+]` |                    |
| `*`   | `[3]`    | `[*]` | `+` ≥ `*`: 1 + 2   |
| `3`   | `[3, 3]` | `[*]` |                    |
| `+`   | `[9]`    | `[+]` | 3 × 3              |
| `4`   | `[9, 4]` | `[+]` |                    |
| `*`   | `[13]`   | `[*]` | 9 + 4              |
| `5`   | `[13, 5]`| `[*]` |                    |
| `+`   | `[65]`   | `[+]` | 13 × 5             |
| `6`   | `[65, 6]`| `[+]` |                    |
| end   | `[71]`   | `[]`  | 65 + 6 → **71**    |

Same tokens under the part 2 table. Now a `+` arriving over a waiting `*`
does *not* reduce it (1 < 2), so the `*` stays parked while the addition
is done on the spot, and the parked multiplications are cleared out when
the next `*` or the end arrives:

| token | values       | ops      | what happened                          |
| ----- | ------------ | -------- | -------------------------------------- |
| `1`   | `[1]`        | `[]`     |                                        |
| `+`   | `[1]`        | `[+]`    |                                        |
| `2`   | `[1, 2]`     | `[+]`    |                                        |
| `*`   | `[3]`        | `[*]`    | 1 + 2                                  |
| `3`   | `[3, 3]`     | `[*]`    |                                        |
| `+`   | `[3, 3]`     | `[*, +]` | `*` < `+`: do not reduce, park         |
| `4`   | `[3, 3, 4]`  | `[*, +]` |                                        |
| `*`   | `[21]`       | `[*]`    | 3 + 4 = 7 (2 ≥ 1), then 3 × 7 (1 ≥ 1)  |
| `5`   | `[21, 5]`    | `[*]`    |                                        |
| `+`   | `[21, 5]`    | `[*, +]` |                                        |
| `6`   | `[21, 5, 6]` | `[*, +]` |                                        |
| end   | `[231]`      | `[]`     | 5 + 6 = 11, then 21 × 11 → **231**     |

Read the `values` column: 3, then 3 and 7 collapsing to 21, then 21 and
11 collapsing to 231. The machine has computed `(1 + 2) * (3 + 4) * (5 + 6)`
without anyone writing the parentheses.

And the statement's parenthesised example, `1 + (2 * 3) + (4 * (5 + 6))`,
under the part 2 table, to show the fences at work — the answer is 51
under either table because the parentheses leave nothing to precedence:

| token | values         | ops                  | what happened            |
| ----- | -------------- | -------------------- | ------------------------ |
| `1`   | `[1]`          | `[]`                 |                          |
| `+`   | `[1]`          | `[+]`                |                          |
| `(`   | `[1]`          | `[+, (]`             | fence                    |
| `2`   | `[1, 2]`       | `[+, (]`             |                          |
| `*`   | `[1, 2]`       | `[+, (, *]`          | fence stops the walk     |
| `3`   | `[1, 2, 3]`    | `[+, (, *]`          |                          |
| `)`   | `[1, 6]`       | `[+]`                | 2 × 3; fence removed     |
| `+`   | `[7]`          | `[+]`                | 1 + 6                    |
| `(`   | `[7]`          | `[+, (]`             |                          |
| `4`   | `[7, 4]`       | `[+, (]`             |                          |
| `*`   | `[7, 4]`       | `[+, (, *]`          |                          |
| `(`   | `[7, 4]`       | `[+, (, *, (]`       | second fence             |
| `5`   | `[7, 4, 5]`    | `[+, (, *, (]`       |                          |
| `+`   | `[7, 4, 5]`    | `[+, (, *, (, +]`    |                          |
| `6`   | `[7, 4, 5, 6]` | `[+, (, *, (, +]`    |                          |
| `)`   | `[7, 4, 11]`   | `[+, (, *]`          | 5 + 6                    |
| `)`   | `[7, 44]`      | `[+]`                | 4 × 11                   |
| end   | `[51]`         | `[]`                 | 7 + 44 → **51**          |

All three traces were produced by an instrumented copy of the loop, not
typed from expectation.

### `part1` / `part2`

`sum(evaluate(tokens, TABLE) for tokens in homework)` with the respective
table. Across the six statement examples:

| expression                                          | part 1 | part 2  |
| --------------------------------------------------- | -----: | ------: |
| `1 + 2 * 3 + 4 * 5 + 6`                             |     71 |     231 |
| `1 + (2 * 3) + (4 * (5 + 6))`                       |     51 |      51 |
| `2 * 3 + (4 * 5)`                                   |     26 |      46 |
| `5 + (8 * 3 + 9 + 3 * 4 * 3)`                       |    437 |   1,445 |
| `5 * 9 * (7 * 3 * 3 + 9 * 3 + (8 + 6 * 4))`         | 12,240 | 669,060 |
| `((2 + 4 * 9) * (6 + 9 * 8 + 6) + 6) + 2 + 4 * 2`   | 13,632 |  23,340 |

All twelve match the statement and are parametrized tests. On the real
input the answers are **650,217,205,854** and **20,394,514,442,037**,
both submitted and accepted, and `LOCKED` asserts them. The largest single line is 221 billion in
part 1 and 5.88 trillion in part 2 — 38 and 43 bits — and the part 2 sum
is 45 bits. Python does not care; section 6 does.

## 4. Why it is correct

**What the operator stack looks like.** Consider only the operators above
the topmost fence (or above the bottom, if there is none). An operator is
pushed only after every waiting operator with precedence ≥ its own has
been reduced, so at the moment of the push everything below it in that
segment has *strictly lower* precedence. Nothing ever changes an entry's
precedence, and reductions only remove from the top. So the invariant is:

> Within each fence segment, `ops` is strictly increasing in precedence
> from bottom to top.

Under the part 1 table there is only one precedence level, so a segment
holds **at most one operator**: every operator is applied the instant its
right operand is complete, which is what "left to right" means. That is
why the part 1 trace is a running total, and
`test_part1_is_a_strict_left_fold` pins the consequence — a paren-free
line equals the fold `((((1 + 2) * 3) + 4) * 5) + 6` computed directly.

Under the part 2 table there are two levels, so a segment holds at most a
`*` with a `+` above it. A `+` is applied as soon as its right operand
arrives (nothing outranks it), so runs of additions collapse to a single
number before the next `*` sees them; the `*`s see only those sums. That
is exactly "sum the groups between the stars, then multiply", and
`test_part2_is_the_product_of_the_sums_between_stars` pins it on the
statement's example: groups `[3, 7, 11]`, product 231.

**Why an operator is reduced when it is.** Take two adjacent operators
`a` at the top of `ops` and `b` arriving. If `a` outranks `b`, `a` binds
its two operands more tightly than `b` would, so `a` must be applied
before `b` can take the result as its left operand. If they rank equally,
left-to-right says `a` (to the left) goes first. If `b` outranks `a`, `a`
must wait for `b`'s result — the number just pushed is `b`'s left operand,
not `a`'s right one. The `>=` test is those three cases with the first two
merged, which is the standard shunting-yard condition for left-associative
operators.

**Parentheses.** A fence hides everything below it from the precedence
walk, so a group is evaluated as though it were the whole expression;
when `)` reduces down to the fence, one value remains for the group, and
it sits on `values` exactly where a number would have. The surrounding
operators cannot tell the difference, which is the definition of
grouping. `test_parentheses_override_either_table` checks `(1 + 2) * 3`,
`1 + (2 * 3)` and `2 * (3 + 4)` under both tables;
`test_degenerate_expressions` checks `42`, `((((7))))` and `(1 + 2)`.

**How deep the stacks get.** From the invariant, a fence segment holds at
most as many operators as there are precedence levels — one in part 1,
two in part 2 — plus the fence itself, and `values` holds one more than
the number of operators waiting. With nesting depth *d* that bounds `ops`
at *d* + (*d* + 1)·*levels* and `values` at (*d* + 1)·*levels* + 1. The
real input has *d* = 2, predicting at most 5 / 4 for part 1 and 8 / 7 for
part 2. Measured (instrumented copy, every line): **5 and 4, 8 and 7**,
both bounds hit exactly. A fixed eight-slot register file would run this
homework; see section 6.

**Rejecting bad input.** A stray character raises in the tokenizer
(`test_tokenize_rejects_stray_characters`: `-`, `x`, `/`, `[`); two
adjacent numbers or a dangling operator raise in `evaluate`
(`test_malformed_expression_is_rejected_not_guessed`). Neither path can
return a number.

**An independent oracle.** The test module also evaluates every line of
the real input a second way: Python's own parser. Python already has a
left-associative equal-precedence pair, `+` and `-`, and a tighter/looser
pair, `*` over `+`. Relabel the homework's symbols onto those — part 1
writes `*` as `-`, part 2 swaps `+` and `*` — on an `int` subclass whose
`__sub__` (or `__add__`/`__mul__`) performs the *homework's* operation
rather than the symbol's, and `eval` becomes a second evaluator written by
somebody else. `test_real_input_matches_the_oracles_line_by_line` asserts
agreement on all 370 lines for both tables. The shipping code does not
`eval` anything; this is test-only.

**A third table the puzzle never asks for.** School precedence,
`{"+": 1, "*": 2}`, is Python's own, so plain `eval` of the untouched line
is the oracle with no relabelling at all.
`test_school_precedence_is_ordinary_arithmetic` and its real-input sibling
check that the evaluator handed that table agrees with Python on the six
examples (the first is 33, against 71 and 231 under the puzzle's tables)
and on all 370 lines, where the sum comes to 19,831,527,590. It is the
cleanest evidence that `evaluate` is a general precedence machine and not
something tuned to the two tables it ships with.

## 5. Complexity

Every token is pushed onto a stack exactly once and popped exactly once,
and each `reduce` is constant work, so `evaluate` is **O(n)** in the
token count — there is no rescanning and no backtracking, which is the
property that made shunting-yard the standard in the first place. Space
is the two stacks, bounded as in section 4 by nesting depth times
precedence levels, not by line length. Parsing is one regex pass per
line, also O(n).

Measured on the real input (`python\bench.py 18 -n 20`, best / median of
20):

| phase  |     best |   median |
| ------ | -------: | -------: |
| parse  | 1.619 ms | 1.649 ms |
| part 1 | 1.397 ms | 1.409 ms |
| part 2 | 1.454 ms | 1.467 ms |

Parsing is the slowest phase: 10,528 regex matches plus a type check and
an `int()` each. The two evaluations are within 4% of each other, which
is what O(n) predicts — the table changes *which* reductions happen when,
not how many (one per operator, 4,121 per part). About 140 ns per token
for the evaluate loop; nothing here is worth optimising, and section 7 is
about clarity trade-offs, not speed.

## 6. If I were writing this in Rust

The two-stack machine is the same program; what Rust adds is a type for
the token and a width for the number.

```rust
enum Token { Num(u64), Op(u8), Open, Close }

fn evaluate(tokens: &[Token], precedence: impl Fn(u8) -> u8) -> u64 {
    let mut values: Vec<u64> = Vec::with_capacity(8);
    let mut ops: Vec<Token> = Vec::with_capacity(8);
    for &token in tokens {
        match token {
            Token::Num(n) => values.push(n),
            Token::Open => ops.push(token),
            Token::Close => {
                while *ops.last().unwrap() != Token::Open { reduce(&mut values, &mut ops); }
                ops.pop();
            }
            Token::Op(op) => {
                while let Some(&Token::Op(top)) = ops.last() {
                    if precedence(top) >= precedence(op) { reduce(&mut values, &mut ops); } else { break; }
                }
                ops.push(token);
            }
        }
    }
    while !ops.is_empty() { reduce(&mut values, &mut ops); }
    values[0]
}
```

The full port (byte-level tokenizer, `reduce` as a nested fn, two
precedence functions in place of the dicts) was compiled with `rustc -O`
(1.93.1) and run three times on the real input while writing this guide.
Same two answers; parse **219–267 µs**, part 1 **85–105 µs**, part 2
**84–105 µs** — roughly 7× the Python on parse and 15× on evaluate. Notes:

- **The enum replaces `isinstance` and string compares.** The Python loop
  asks `isinstance(token, int)`, then `== "("`, then `== ")"`, then falls
  through. The `match` is one jump on the discriminant, and the compiler
  refuses to compile it if a variant is unhandled.
- **`while let Some(&Token::Op(top)) = ops.last()`** is the fence check
  and the empty check in one pattern: it fails to match on an empty stack
  *and* on an `Open`, which is exactly the Python condition
  `ops and ops[-1] != "("`. The precedence comparison is the only thing
  left inside the loop body.
- **`u64` is a decision.** The largest line is 43 bits and the part 2 sum
  is 45; `u32` would overflow silently in release and panic in debug. In
  Python the width question does not exist. This is the day 17 point
  again — the count fitting a `u8` there, the value fitting a `u64` here —
  and it is the kind of thing an embedded reader checks before the
  algorithm.
- **Fixed-size stacks are an option.** Section 4 shows the real input
  needs 8 operator slots and 7 value slots. `[u64; 8]` plus a depth index
  would remove the heap entirely, at the cost of a panic on a deeper
  input; `Vec::with_capacity(8)` is the compromise — one allocation per
  line, no reallocation in practice.
- **`precedence` as a function**, not a `HashMap`: `fn(u8) -> u8` on a
  byte is a comparison and a constant, and monomorphisation makes each
  part's evaluator a separate function with the table inlined.

## 7. Possible optimization

There is nothing to optimise for speed — 4.5 ms total — so this sidebar
is about the *other ways to write it*, which is where this puzzle's real
interest lies. All four below were run on the real input (scratchpad
`variants.py`, not the repo) and all agree with the shipping answers:

| variant                                     | part 1 | part 2  |
| ------------------------------------------- | -----: | ------: |
| shipping two-stack machine                  | 1.44 ms | 1.50 ms |
| recursive descent, one function per level   | 1.00 ms | 1.12 ms |
| regex collapse of innermost parens          | 3.01 ms | 7.06 ms |
| `eval` with an `int` subclass               | 9.83 ms | 10.14 ms |

**Recursive descent** is the grammar written as functions: for part 2,

```python
def product():  return total() then, while the next token is "*", multiply by total()
def total():    return atom()  then, while the next token is "+", add atom()
def atom():     a number, or "(" product ")"
```

Precedence is the *nesting order of the functions* — the loosest operator
is the outermost function — and the two parts are two different function
ladders rather than two tables. It is a little faster here (no operator
stack; the call stack is the stack) and it is what a hand-written
compiler front end looks like. It stays in the sidebar because the
precedence is implicit in the code structure, whereas the table version
puts the one thing that changes between the parts in one visible place.

**Regex collapse** is the no-parser approach: repeatedly find an innermost
`( ... )`, evaluate its flat contents by repeated `\d+ [+*] \d+`
substitution, splice the result back into the string. It works, it reads
like the statement's own worked examples, and it is 2–5× slower because
every step rescans and rebuilds the string. Also a reminder that
`str.replace` is O(n) each, so the loop is quadratic in line length.

**The `eval` trick** is the well-known one-liner for this puzzle and the
oracle in the tests (section 4): swap the operator *symbols* so that
Python's own precedence gives the homework's grouping, and give an `int`
subclass dunder methods that perform the homework's *operations*. It is
delightful and it is not shipped: it evaluates the input as Python
source, and it is the slowest of the four by a wide margin — each
operation is a Python-level method call and an object allocation. It
earns its place as a second, independent implementation to check the
first against, which is the one job where "written by somebody else"
matters more than speed.

**Tokenizer.** A single-character loop (`for c in line: if c.isdigit(): ...`)
tokenizes the real input in 0.94 ms against the regex's 1.6 ms, but only
because every number is one digit; the regex handles `234` and the loop
would have to grow a digit accumulator to match. The regex is kept for
the strictness argument in section 3, not for speed.
