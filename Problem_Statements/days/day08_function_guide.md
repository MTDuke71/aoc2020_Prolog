# Day 08 Function Guide — Handheld Halting

> This is the day the puzzle input *is a program* and your job is to
> **write the machine that runs it**. Three opcodes — `acc` (add to an
> accumulator), `jmp` (relative branch), `nop` (fall through) — over a
> single integer register and a program counter. That's a tiny virtual
> machine, and the whole day is one **fetch/decode/execute loop**. The
> only twist beyond a straight interpreter is a *visited set* of program
> counters, which turns "does this program halt?" into a decidable
> question: a machine with finite state that never revisits a PC must
> either step off the end or repeat — and repeating is the halting
> problem's easy case. Part 1 catches the first repeat; Part 2 searches
> one-instruction edits for the version that runs off the end instead.

## The puzzle in one paragraph

The boot code is 623 instructions, one per line, each an opcode and a
signed argument (`jmp +140`, `acc -6`, `nop +23`). **Part 1:** the boot
code loops forever; report the accumulator value *the instant before* an
instruction would execute a second time (example: `5`). **Part 2:**
exactly one instruction is corrupted — a single `jmp` should be a `nop`
or vice versa (`acc` lines are innocent). Flip the right one and the
program *terminates* by stepping to the position just past the last
instruction; report the accumulator when it does (example: `8`).

---

## Representation: the program as an assoc PC → Op-Arg

The parsed value is `prog(N, Assoc)`: `N` is the instruction count and
`Assoc` (SWI's AVL-tree map, `library(assoc)`, the same structure Day 7
used for the bag graph — see [Day 7](day07_function_guide.md)) maps each
**program counter** `0..N-1` to its instruction `Op-Arg`:

```
0 -> acc-13
1 -> acc-(-6)
2 -> acc-(-8)
3 -> jmp-140
...
```

`Op` is an atom (`acc`/`jmp`/`nop`); `Arg` is a (possibly negative)
integer. Why an assoc keyed by integer PC, rather than a plain list of
instructions?

- **The machine does random access.** `jmp -20` needs the instruction 20
  positions back; a list forces `nth0/3`'s `O(n)` walk on every branch,
  turning one run into `O(n²)`. `get_assoc/3` is `O(log n)`.
- **Part 2 needs a cheap, pure single-cell edit.** Flipping the
  instruction at one PC is `put_assoc(PC, Assoc, NewInstr, Assoc2)` —
  `O(log n)`, and `Assoc2` *shares structure* with the original, so the
  623 candidate programs never get copied wholesale. A list would force
  an `O(n)` rebuild per candidate.

Carrying `N` alongside the map means the halt test is the literal reading
of the puzzle — "attempting to execute an instruction immediately after
the last instruction in the file" is exactly `PC =:= N`.

> The other idiomatic encoding is a **compound term as a flat array** —
> `program(I0, I1, …, I622)` with `arg(PC+1, Program, Instr)` for genuine
> `O(1)` fetch and `functor/3` handing you `N` for free. It's the
> register-machine-flavored choice and slightly faster to read, but the
> single-cell *update* Part 2 wants is awkward (`setarg/3` on a
> `duplicate_term/2` copy, or an `=..`/rebuild). The assoc wins the day
> because Part 2's update pressure outweighs Part 1's read pressure. The
> array trick is in the optimization sidebar.

---

## Reading Prolog: an interpreter loop, opcode dispatch, a visited set

**1. `exec/6` — one instruction's effect, dispatched by opcode.** The
decode/execute core is three facts, one per opcode, mapping
`(Op, Arg, PC, Acc)` to the next `(PC1, Acc1)`:

```prolog
exec(acc, Arg, PC, Acc0, PC1, Acc1) :- PC1 is PC + 1,   Acc1 is Acc0 + Arg.
exec(jmp, Arg, PC, Acc,  PC1, Acc)  :- PC1 is PC + Arg.
exec(nop, _,   PC, Acc,  PC1, Acc)  :- PC1 is PC + 1.
```

Because the first argument is a bound atom, SWI's **first-argument
indexing** jumps straight to the matching clause — the dispatch is
`O(1)` and leaves *no choice point*, so the interpreter is deterministic
without a cut. `acc` advances PC by one and moves the accumulator; `jmp`
adds its argument to PC and leaves the accumulator alone (note `Acc` used
in both the input and output slot — "unchanged"); `nop` advances PC by
one and ignores its argument. This little table *is* the instruction set
architecture.

**2. `step/7` — the fetch loop with a halt/loop verdict.** The machine's
state is `(PC, Acc)` plus the `Seen` set of already-executed PCs. Three
mutually exclusive cases, each committed with a cut, with the outputs
unified *after* the cut (the repo's steadfast-cut style, in force since
[Day 3](day03_function_guide.md)):

```prolog
step(N, _Assoc, PC, Acc0, _Seen, Outcome, Acc) :-
    PC =:= N, !,
    Outcome = halt, Acc = Acc0.
step(_N, _Assoc, PC, Acc0, Seen, Outcome, Acc) :-
    get_assoc(PC, Seen, true), !,
    Outcome = loop, Acc = Acc0.
step(N, Assoc, PC, Acc0, Seen0, Outcome, Acc) :-
    get_assoc(PC, Assoc, Op-Arg),
    put_assoc(PC, Seen0, true, Seen1),
    exec(Op, Arg, PC, Acc0, PC1, Acc1),
    step(N, Assoc, PC1, Acc1, Seen1, Outcome, Acc).
```

Read the three clauses as a priority list checked before running each
instruction: **(1)** if the PC is off the end, the machine *halts* with
whatever the accumulator holds; **(2)** if we're about to re-enter a PC
we've already run, the machine *loops* — stop and report the accumulator
at that instant (this is the "immediately before an instruction runs a
second time" moment); **(3)** otherwise fetch the instruction, record the
PC as seen, execute it, and recurse on the new state. The `Seen` set is
what makes the loop detectable and guarantees termination: there are only
`N` possible PCs, so within `N` steps the machine must either halt or hit
a repeat.

**3. Part 1 — run and read the accumulator at the loop.**

```prolog
part1(Prog, Acc) :- run(Prog, loop, Acc).
```

`run/3` seeds an empty `Seen` and calls `step/7`. Constraining the middle
argument to `loop` isn't just pattern sugar — it *documents and checks*
that the boot code really does loop (if it ever halted, Part 1 would fail
loudly rather than return a wrong number).

**4. Part 2 — brute-force the one-instruction repair.**

```prolog
part2(prog(N, Assoc), Acc) :-
    N1 is N - 1,
    between(0, N1, PC),
    get_assoc(PC, Assoc, Op-Arg),
    flipped(Op, Op2),
    put_assoc(PC, Assoc, Op2-Arg, Assoc2),
    run(prog(N, Assoc2), halt, Acc),
    !.

flipped(jmp, nop).
flipped(nop, jmp).
```

`between/3` generates candidate PCs in order. For each, we fetch the
instruction and try to `flipped/2` its opcode — which **fails on `acc`**
(no clause), so `between` backtracks straight past the innocent
instructions ("no `acc` instructions were harmed"). For a `jmp`/`nop` we
build the patched program with a single `put_assoc/4` and `run` it,
*constraining the outcome to `halt`*: if the flip still loops, `run`'s
`Outcome = loop` won't unify with `halt`, the clause fails, and `between`
moves on. The first flip that halts satisfies the goal; the trailing `!`
commits to it. This is a linear scan over `≤ N` candidates, each a fresh
`O(N)` run — `O(N²)` worst case, and the honest, readable shape. (The
`O(N)` one-pass version is in the sidebar.)

---

## The Day 8 code, predicate by predicate

### `parse_input/2`, `parse_instr/2`

```prolog
parse_input(Raw, prog(N, Assoc)) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(parse_instr, Lines, Instrs),
    length(Instrs, N),
    N1 is N - 1,
    numlist(0, N1, Idxs),
    pairs_keys_values(Pairs, Idxs, Instrs),
    list_to_assoc(Pairs, Assoc).
```

The repo's standard split-and-clean opener (splitting on newlines, padding
away `\r`/spaces, dropping the trailing empty line), then one `Op-Arg` per
line via `maplist`. To key the instructions by position, `numlist(0, N-1,
Idxs)` makes the index list and `pairs_keys_values/3` zips
`Idxs`+`Instrs` into `0-(acc-13), 1-(acc-(-6)), …` for `list_to_assoc/2`.
`parse_instr/2` splits a line on its single space and reads the two
tokens:

```prolog
parse_instr(Line, Op-Arg) :-
    split_string(Line, " ", "", [OpS, ArgS]),
    atom_string(Op, OpS),
    number_string(Arg, ArgS).
```

The one thing to know: SWI's `number_string/2` parses the signed forms
`"+140"` and `"-6"` directly, so there's no manual sign stripping — the
leading `+` is not a gotcha here the way it can be with `number_codes`.

### `run/3`, `step/7`, `exec/6`

The interpreter (above). `run/3` is the public entry that seeds the empty
`Seen` set; `step/7` is the loop; `exec/6` is the ISA. `run/3` is exported
so tests can pin the `loop`-vs-`halt` verdict directly, not just the
accumulator.

### `part1/2`, `part2/2`, `flipped/2`, `solve/3`

Parts as above. `flipped/2` is a two-fact table that doubles as the "is
this a flippable instruction?" test (it simply has no `acc` clause).
`solve/3` is the standard parse-once-answer-both.

---

## Correctness notes

- **Parse:** each line yields `PC-(Op-Arg)`; positions are dense `0..N-1`,
  so `list_to_assoc/2` keys are unique and the map is total over valid
  PCs. Signed arguments parse via `number_string/2`.
- **Termination is guaranteed** by the `Seen` set: the machine has only
  `N` distinct PCs, so `step/7`'s third clause fires at most `N` times
  before either clause 1 (`PC =:= N`) or clause 2 (`PC ∈ Seen`) stops it.
  No input can make the interpreter itself diverge.
- **Halt is exact.** `PC =:= N` is the only halt. A flipped program whose
  branch lands *past* the end (`PC > N`) or *before* the start (`PC < 0`)
  finds no instruction — `get_assoc/3` in clause 3 simply *fails*, the run
  fails, and Part 2 backtracks to the next candidate. So an out-of-range
  jump is correctly treated as "not a valid repair," never as a spurious
  halt.
- **Part 1** returns the accumulator at the first repeat; the `loop`
  constraint asserts the boot code loops. Example → `5`, real → **1331**.
- **Part 2** returns the accumulator of the first (and, by the puzzle's
  guarantee, only) single-flip program that halts; `flipped/2` skips
  `acc`. Example → `8`, real → **1121**.
- **Determinism:** `exec/6` is first-argument indexed (no choice point);
  `step/7`'s three clauses are committed with cuts; `run/3` is therefore
  deterministic; `part1/2` is deterministic; `part2/2` commits with a
  trailing `!`. The suite runs with **no "succeeded with choicepoint"
  warnings** — the repo's determinism bar since [Day 5](day05_function_guide.md).
- Locked real-input answers: **Part 1 = 1331**, **Part 2 = 1121**,
  cross-validated by [python/day08.py](../../python/day08.py).

## Tests — what's pinned and why

[test/day08_tests.pl](../../test/day08_tests.pl) pins four layers, **7
tests green** (run `swipl test/run_tests.pl` from the repo root):

1. **Parser** — `acc +13 / jmp -6 / nop +0` parses to `N = 3` with the
   right opcode *and* signed argument at each PC (a bug in indexing or
   sign handling is caught).
2. **Interpreter verdict** — the example program `run`s to `loop` with
   accumulator `5`; a hand-built two-line program (`nop +0`, `acc +6`)
   `run`s to `halt` with `6`, pinning the "steps off the end" case
   directly.
3. **Parts on the example** — `part1 = 5` and `part2 = 8`.
4. **Real answers** — `1331` / `1121` locked against `inputs/day08.txt`.

## Complexity & benchmarks

Let `N` = instruction count (623).

- **Parse:** `O(N log N)` — one pass over the lines, `N` `list_to_assoc`
  insertions.
- **Part 1:** `O(N log N)` — one run, `≤ N` steps, each an `O(log N)`
  assoc fetch plus insert.
- **Part 2:** `O(N² log N)` worst case — up to `N` candidate flips, each a
  full `O(N log N)` run. This is the day's dominant cost and the reason
  the sidebar's `O(N)` version exists.

Inferences are exact and reproducible (`swipl bench/main.pl day08` reports
the same counts every run); times are representative single runs:

| Phase | Inferences | Time (ms) |
|-------|-----------:|----------:|
| parse | 11,877 | 2.09 |
| part1 | 9,758 | 0.53 |
| part2 | 2,130,893 | 86.8 |

Part 2 does ~200× the work of Part 1 — every one of the leading `jmp`/`nop`
candidates triggers a near-full re-run before the repairing flip is found.
At ~87 ms it's still comfortably fast, so the shipped code keeps the
brute-force clarity (the repo's correctness-and-clarity-first policy).

## If I were writing this in Rust

```rust
enum Op { Acc, Jmp, Nop }

fn run(program: &[(Op, i64)]) -> (bool, i64) {
    let mut seen = vec![false; program.len()];
    let (mut pc, mut acc) = (0i64, 0i64);
    loop {
        if pc as usize == program.len() { return (true, acc); }   // halt
        if seen[pc as usize]            { return (false, acc); }   // loop
        seen[pc as usize] = true;
        let (op, arg) = &program[pc as usize];
        match op {
            Op::Acc => { acc += arg; pc += 1; }
            Op::Jmp => { pc += arg; }
            Op::Nop => { pc += 1; }
        }
    }
}

fn part2(program: &mut Vec<(Op, i64)>) -> i64 {
    for i in 0..program.len() {
        let flip = match program[i].0 { Op::Jmp => Op::Nop, Op::Nop => Op::Jmp, _ => continue };
        let orig = std::mem::replace(&mut program[i].0, flip);
        if let (true, acc) = run(program) { program[i].0 = orig; return acc; }
        program[i].0 = orig;                                       // restore, keep scanning
    }
    unreachable!()
}
```

- **assoc PC→instr ↔ `&[(Op, i64)]`.** Rust reaches for a flat slice with
  `O(1)` indexing where Prolog reaches for the `O(log n)` assoc; the assoc
  earns its keep by giving Part 2 a *pure* single-cell update, which is
  why Rust here mutates-and-restores (`mem::replace`) instead.
- **`step/7`'s three clauses ↔ the `loop { … }` with two early returns.**
  The halt/loop/continue priority is identical; Prolog's `Seen` assoc is
  Rust's `vec![false; n]` visited bitmap, and returning `(bool, i64)` is
  exactly `run/3`'s `(Outcome, Acc)`.
- **`exec/6` ↔ the `match op`.** Same opcode dispatch; Prolog gets it from
  first-argument clause indexing, Rust from an enum `match`.
- **`flipped/2` failing on `acc` ↔ `_ => continue`.** Both encode "skip
  the innocent `acc` lines" as a non-match that advances the scan.

The Python reference ([python/day08.py](../../python/day08.py)) is the
same interpreter — a `while pc != n` loop returning `(halted, acc)`, and a
Part 2 that rebuilds the program with one instruction swapped per
candidate — and re-confirms `1331` / `1121`.

## Possible optimization

- **One-pass Part 2 in `O(N)`.** The unmodified program is a *functional
  graph* — every PC has exactly one successor — so memoize two facts per
  PC by following that single successor to the end: `terminates(PC)`
  (does control from here reach the end?) and `acc_to_end(PC)` (the
  accumulator delta from here to the end). Then walk the original
  execution trace once; at each `jmp`/`nop` with running accumulator `A`,
  compute the *flipped* successor `PCf` — for `jmp→nop` it's `PC+1`, for
  `nop→jmp` it's `PC+Arg`. The first PC where `terminates(PCf)` holds is
  the repair, and the answer is `A + delta_to(PCf) + acc_to_end(PCf)` with
  no re-run at all. This collapses Part 2 from `O(N²)` to `O(N)` (~87 ms →
  well under 1 ms), at the cost of two memo tables and more moving parts.
  Declined for `src/` under the clarity-first policy; the brute force is
  fast enough and reads like the puzzle statement.
- **Compound-term array representation.** Parse into
  `program(I0, …, I622)` for `O(1)` `arg/3` fetch and free `N` via
  `functor/3` (the register-machine encoding). Faster reads, but Part 2's
  single-cell edit becomes `setarg/3` on a `duplicate_term/2` copy — a
  destructive-then-fresh idiom that's less transparent than the assoc's
  `put_assoc/4`. A wash overall here; kept as a note.
- **Visited bitmap instead of an assoc `Seen`.** Since PCs are dense
  `0..N-1`, a mutable bit-vector (or `nb_`-array) would drop the `Seen`
  operations from `O(log N)` to `O(1)`. Real but small next to the
  `O(N²)` re-runs Part 2 does — fixing the algorithm (bullet 1) dwarfs
  fixing the constant.
- Sidebar material only; the shipped shape follows the repo's
  correctness-and-clarity-first policy.
