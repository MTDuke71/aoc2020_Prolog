# Day 12 Function Guide — Rain Risk

> A tiny **turtle machine**: 769 instructions, each a letter and a number,
> driving a ship around a plane. Report its **Manhattan distance** from
> the origin. Part 2 arrives and announces that you misread every action —
> the letters actually steer a *waypoint* that the ship chases. It reads
> like a rewrite. It is not. The day's whole content is noticing that
> **both parts are the same machine with one argument changed**: carry a
> ship position and one vector; `F` always moves the ship along the
> vector, `L`/`R` always rotate the vector, and the only thing in dispute
> is whether `N/S/E/W` push the *ship* or the *vector*. Part 1's "facing"
> is a unit vector that starts at east. Everything else falls out.
> Secondary lesson, and the one most likely to bite: **rotation by right
> angles is exact integer arithmetic, not trigonometry** — one clockwise
> quarter turn sends `(x, y)` to `(y, −x)`, which is multiplication by
> `−i`. The instruction-stream shape is [Day 8](day08_function_guide.md)'s
> `Op-Arg` program seen again; the "one engine, two parameterisations"
> move is [Day 11](day11_function_guide.md)'s neighbour table in a much
> cheaper key.

## The puzzle in one paragraph

The input is 769 lines, each an action letter followed by an integer:
`N/S/E/W` (move by a value), `L/R` (turn by degrees), `F` (move forward by
a value). **Part 1:** the ship starts facing east; `N/S/E/W` move the
ship, `L/R` turn the ship's facing, `F` moves along the facing. Example →
`25`. **Part 2:** a waypoint starts 10 east and 1 north *relative to the
ship*; `N/S/E/W` move the waypoint, `L/R` rotate the waypoint about the
ship, `F` moves the ship to the waypoint `value` times. Example → `286`.
Both parts answer with `|x| + |y|`.

Real input: 190 `F`, 396 cardinal moves, 183 turns — all multiples of 90
(66 `L90`, 23 `L180`, 5 `L270`, 64 `R90`, 18 `R180`, 7 `R270`). Part 1
ends at **east 700, south 1256** → **1956**. Part 2 ends at **east 91964,
south 34833** → **126797**, with the waypoint never straying further than
52 units from the ship.

---

## Representation: the two parts are one machine

Read the two statements side by side and strike out everything they share:

| Action | Part 1 | Part 2 |
|---|---|---|
| `F v` | ship += facing × v | ship += waypoint × v |
| `L`/`R` | rotate facing | rotate waypoint |
| `N/S/E/W v` | **ship** += unit × v | **waypoint** += unit × v |

The first two rows are identical once you stop calling one of them
"facing" and the other "waypoint" and call both **the vector**. Part 1's
facing *is* a vector — a unit one, starting at `(1, 0)`, east. The
statement's "the ship starts by facing east" and its `E` action are
literally the same pair of numbers, which is the tell.

So the state is one term:

```prolog
nav(X, Y, VX, VY)     % ship position, then the vector
```

and the parts differ in exactly two places: the initial vector
(`(1,0)` vs `(10,1)`) and where a cardinal move lands. That second one is
a single predicate, `translate/5`, with one clause per mode. Everything
else — parsing, `F`, both turn directions, the distance — is written
once.

**Coordinates.** `+X` east, `+Y` north, origin at the start. Signs never
need special handling because the answer is an L¹ norm, which discards
them at the end; carrying signed coordinates is what makes north/south a
single axis instead of two cases.

**Why the vector and not an angle.** The tempting part-1 representation is
a heading in degrees, or an index into a four-element compass table. Both
work for part 1 and neither survives part 2, where the vector is
`(10, 1)` and has no entry in any compass table. Storing the *vector* is
the representation that generalises, and it costs nothing in part 1: a
compass direction is a vector that happens to have length 1.

---

## Rotation is integer arithmetic

This deserves its own section, because the natural instinct — degrees,
`sin`, `cos` — is wrong here in a way that is easy to ship.

In `(east, north)` coordinates, rotating a vector **clockwise** by one
right angle sends

```text
(x, y)  ->  (y, -x)
```

Check it on east: `(1, 0) -> (0, -1)`, which is south. Turn right from
east and you face south. Four applications return to start.

**Why that formula is the one you already know.** Identify `(x, y)` with
the complex number `x + yi`. Multiplication by `i` is a counter-clockwise
quarter turn:

```text
(x + yi) · i   =  xi + yi²  =  -y + xi    ->  (-y, x)   [left]
(x + yi) · -i  =  -xi - yi² =  y - xi     ->  (y, -x)   [right]
```

Since `i` and `−i` are **Gaussian integers**, the arithmetic never leaves
`ℤ`. Equivalently, in matrix form the clockwise quarter turn is

```text
[  0  1 ]
[ -1  0 ]
```

— every entry in `{-1, 0, 1}`. The four rotations form the **cyclic group
C₄** acting on `ℤ²`, which is why `mod 4` is the right normalisation and
why four facts cover every case.

**What the trigonometric version costs.** `cos(π/2)` in IEEE-754 double is
`6.123233995736766e-17`, not `0`. Rotate `(10, 1)` by 90° with `sin`/`cos`
and you get `(1.0000000000000002, -9.999999999999998)`, then you round,
then you rotate again — 183 turns of accumulating drift plus a rounding
policy you now have to defend. There is no reason to enter that world:
the puzzle only ever asks for right angles, and right angles are exact.
The multiple-of-90 guard in `quarter_turns/3` keeps that assumption
checkable rather than tacit.

**The `mod` trap, which is a real one.** Left turns are normalised to
clockwise by negating: `L d ≡ R (360 − d)`, i.e. `−(d // 90)` quarter
turns. That produces negative numbers, and languages disagree about what
`%` does to them:

| Language | `-1 mod 4` | Rule |
|---|---:|---|
| SWI-Prolog `mod` | `3` | sign of the **divisor** (floored) |
| SWI-Prolog `rem` | `-1` | sign of the **dividend** (truncated) |
| Python `%` | `3` | floored |
| C, C++, Rust, Java `%` | `-1` | truncated toward zero |
| Rust `rem_euclid` | `3` | Euclidean |

Prolog's `mod` is the one a rotation wants, so `-(Degrees // 90) mod 4`
lands in `0..3` with no fixup. Transliterate that line into C or Rust
unchanged and you index a table with `-1`. It is the same species of
distinction as arithmetic vs. logical right shift on a signed value: two
defensible answers to "what happens at the edge", and you have to know
which one your language picked.

---

## Reading Prolog: the four forms this day turns on

**1. `foldl/4` — the fold over a list, with an accumulator.**

```prolog
foldl(:Goal, ?List, +V0, -V)
```

calls `Goal(Elem, AccIn, AccOut)` for each element, threading the
accumulator. It is `Iterator::fold` with the closure's arguments in
Prolog's usual "inputs then output" order. Here:

```prolog
foldl(step(Mode), Instructions, State0, State)
```

`step(Mode)` is a **partial application**: `foldl/4` supplies three more
arguments, making the call `step(Mode, Instruction, State0, State)` —
exactly `step/4`'s signature. Prolog's answer to a closure capturing
`mode` is simply leaving an argument off the front. Same mechanism
[Day 3](day03_function_guide.md) used in `maplist(slope_trees(Grid), ...)`.

**2. First-argument indexing — dispatch without cuts.** SWI builds an
index on the first argument of a predicate's clauses. Given

```prolog
translate(ship,     EX, EY, nav(...), State) :- ...
translate(waypoint, EX, EY, nav(...), State) :- ...
```

a call with `Mode` bound to `ship` selects clause 1 directly. `rotate/5`
is written as four facts keyed on `0`/`1`/`2`/`3` for the same reason:
integers index as well as atoms, so the four-way rotation dispatch is a
lookup rather than a scan. This is the cheapest determinism available in
Prolog, and it is free whenever the discriminating value can be arranged
to sit first — which is worth designing for, not just noticing.

**3. Cuts with outputs unified after the `!`.** The repo's house style
since [Day 3](day03_function_guide.md):

```prolog
step(_Mode, 'F'-Value, State0, State) :-
    !,
    State0 = nav(X, Y, VX, VY),
    ...
    State = nav(X1, Y1, VX, VY).
```

`State` is *not* built in the head. If it were, and a caller passed a
partly-bound `State`, head unification could fail **after** the cut had
already discarded the remaining clauses — turning a wrong answer into a
silent failure. Binding outputs after the cut makes the predicate
**steadfast**: same behaviour whether the output argument arrives fresh or
pre-bound. The input side (`'F'-Value`) stays in the head, where it
belongs, because that is what selects the clause.

**4. `sub_string/5` — positional slicing.**

```prolog
sub_string(+String, ?Before, ?Length, ?After, ?SubString)
```

relates a string to a substring by three numbers: *characters before*,
*length*, *characters after*. Any of them may be unbound, which is what
makes it usable in both directions:

```prolog
sub_string(Line, 0, 1, _, ActionS)    % first character
sub_string(Line, 1, _, 0, ValueS)     % everything after the first
```

The second call says "start at offset 1, run to the end" without knowing
the length — `After = 0` pins the right edge and `Length` is solved for.
[Day 2](day02_function_guide.md) reached for a DCG because its lines had
real structure; `letter + integer` has none worth parsing, so two slices
and a `number_string/2` are the whole parser.

---

## The Day 12 code, predicate by predicate

### `parse_input/2` and `parse_instruction/2`

```prolog
parse_input(Raw, Instructions) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(parse_instruction, Lines, Instructions).

parse_instruction(Line, Action-Value) :-
    sub_string(Line, 0, 1, _, ActionS),
    atom_string(Action, ActionS),
    sub_string(Line, 1, _, 0, ValueS),
    number_string(Value, ValueS).
```

The `split_string/4` + `exclude(=(""))` opening is the repo's standard
line splitter, with `" \t\r"` as the pad set so Windows line endings never
reach the parser. Output is a list of `Action-Value` pairs where `Action`
is a **char atom** (`'N'`, `'F'`, …) — the same `Op-Arg` shape
[Day 8](day08_function_guide.md) used for the handheld's program, and for
the same reason: an instruction stream is naturally opcode plus operand.

`atom_string/2` rather than leaving it a string matters. Atoms are
interned, so they compare by pointer identity: `cardinal('N', ...)` is a
table lookup rather than a character-by-character string compare, and
first-argument indexing works on it.

### `cardinal/3`

```prolog
cardinal('N',  0,  1).
cardinal('S',  0, -1).
cardinal('E',  1,  0).
cardinal('W', -1,  0).
```

Four facts, the compass as unit vectors. Two things this buys beyond
readability. First, it is a **predicate, not a lookup table** — the first
clause of `step/4` calls it as a guard, and its *failure* is precisely how
`F`, `L` and `R` fall through to the later clauses. There is no separate
"is this a cardinal?" test that could drift out of sync with the table it
tests against. Second, `cardinal('E', 1, 0)` is the same vector
`start_state/2` uses for part 1's initial facing; sharing the value makes
the "facing is just a vector" claim structural rather than a comment.

### `quarter_turns/3`

```prolog
quarter_turns('R', Degrees, Quarters) :-
    Degrees mod 90 =:= 0,
    Quarters is (Degrees // 90) mod 4.
quarter_turns('L', Degrees, Quarters) :-
    Degrees mod 90 =:= 0,
    Quarters is -(Degrees // 90) mod 4.
```

Normalises both turn directions into a single count of **clockwise
quarter turns**, so downstream there is one rotation primitive instead of
two mirror-image ones. `L d` is `R (360 − d)`; expressed in quarters that
is just negation, and `mod 4` folds it back into `0..3` (see the trap
table above for why Prolog's `mod` is the right operator).

The `Degrees mod 90 =:= 0` guard is not decoration. Without it an `L45`
would silently floor to zero quarter turns and produce a plausible wrong
answer — exactly the failure mode this repo keeps trying to make
unrepresentable. With it, malformed input **fails**, and the failure
propagates out of `step/4` to the caller instead of being absorbed. The
real input contains only 90/180/270, so the guard never fires; it is there
to make the assumption checkable rather than remembered.

Note the precedence in the `'L'` clause: `-` binds tighter than `mod`, so
`-(Degrees // 90) mod 4` is `(-(Degrees // 90)) mod 4`. The parentheses
are written anyway.

### `rotate/5`

```prolog
rotate(0, VX, VY, VX1, VY1) :- VX1 = VX,    VY1 = VY.
rotate(1, VX, VY, VX1, VY1) :- VX1 = VY,    VY1 is -VX.
rotate(2, VX, VY, VX1, VY1) :- VX1 is -VX,  VY1 is -VY.
rotate(3, VX, VY, VX1, VY1) :- VX1 is -VY,  VY1 = VX.
```

The four elements of C₄, written out. Two design notes:

- **Four facts, not repeated application.** `rotate(3, ...)` could be
  `rotate(1, ...)` applied three times, and that is how the Python
  reference does it (`for _ in range(turns)`). Enumerating instead makes
  every turn a single indexed clause selection — no recursion, no
  accumulator, no choicepoint — and it puts the 180° case on the page,
  which is the one people get wrong when deriving it from a general
  formula.
- **`=` where nothing needs evaluating.** `VX1 = VY` is plain
  unification; `VY1 is -VX` calls arithmetic because there is a negation
  to perform. Using `is/2` for both would work, and would be marginally
  slower and less honest about which coordinates are merely *moved*.

### `start_state/2` and `navigate/3`

```prolog
start_state(ship,     nav(0, 0,  1, 0)).
start_state(waypoint, nav(0, 0, 10, 1)).

navigate(Mode, Instructions, Distance) :-
    start_state(Mode, State0),
    foldl(step(Mode), Instructions, State0, State),
    State = nav(X, Y, _VX, _VY),
    manhattan(X, Y, Distance).
```

The two initial vectors are the only numeric difference between the parts
that survives into `navigate/3`; `Mode` carries the rest. `foldl/4` runs
the program, and the final vector is discarded — where the waypoint ends
up is not part of any answer, though it is worth knowing it is still
there (part 2 finishes with it at `(-26, -43)`).

Because `nav/4` is a fresh term per instruction, the state is
**immutable** in the same sense [Day 11](day11_function_guide.md)'s
`occ/N` was. Here nothing depends on that: `step/4` reads its input state
once, so there is no simultaneous-update hazard to protect against. Noted
only so the contrast with the previous day is explicit — Day 11's
immutability was load-bearing, this day's is incidental.

### `step/4`

```prolog
step(Mode, Action-Value, State0, State) :-
    cardinal(Action, DX, DY),
    !,
    EX is DX * Value,
    EY is DY * Value,
    translate(Mode, EX, EY, State0, State).
step(_Mode, 'F'-Value, State0, State) :-
    !,
    State0 = nav(X, Y, VX, VY),
    X1 is X + VX * Value,
    Y1 is Y + VY * Value,
    State = nav(X1, Y1, VX, VY).
step(_Mode, Action-Degrees, State0, State) :-
    quarter_turns(Action, Degrees, Quarters),
    State0 = nav(X, Y, VX, VY),
    rotate(Quarters, VX, VY, VX1, VY1),
    State = nav(X, Y, VX1, VY1).
```

Three clauses, one per action **family** rather than one per letter —
seven letters, three behaviours. Dispatch is by guard rather than by
index, because the discriminating value sits inside the second argument's
pair where first-argument indexing cannot reach it; the cuts do the work
indexing would otherwise do for free.

- Clause 1 fires when `cardinal/3` recognises the letter. It scales the
  unit vector by `Value` *before* handing off, so `translate/5` deals only
  in "here is a displacement" and never needs to know about compasses.
- Clause 2 is `F`: the ship moves along the vector, `Value` times. This is
  the one line that is genuinely identical between the parts, and where
  the whole "part 2 is the same machine" claim cashes out.
- Clause 3 is the fallthrough, and it is deliberately **not** guarded on
  `member(Action, ['L','R'])`. `quarter_turns/3` has clauses only for
  those two letters, so an unrecognised action makes `step/4` fail rather
  than quietly no-op. No cut, because it is last.

The scaling in clause 1 multiplies by zero half the time, since every
compass unit vector has a zero component — about 400 wasted
multiplications across the input, which is nothing, and it buys a uniform
interface into `translate/5`.

### `translate/5`

```prolog
translate(ship, EX, EY, nav(X, Y, VX, VY), State) :-
    X1 is X + EX,
    Y1 is Y + EY,
    State = nav(X1, Y1, VX, VY).
translate(waypoint, EX, EY, nav(X, Y, VX, VY), State) :-
    VX1 is VX + EX,
    VY1 is VY + EY,
    State = nav(X, Y, VX1, VY1).
```

**This predicate is the difference between the two parts.** Ten lines into
which the entire Part Two "you misread everything" twist compresses: the
same displacement, applied to the other point. Part 1 moves the ship and
leaves the heading alone — the statement is explicit about this ("if the
ship is facing east and the next instruction is `N10`, the ship would move
north 10 units, but would still move east if the following action were
`F`"). Part 2 moves the waypoint and leaves the ship alone.

Indexed on `Mode`, so it is deterministic without a cut. The input state
is destructured in the head here, unlike in `step/4`, because there is no
cut in these clauses for the head pattern to interact with, and the
pattern documents the argument.

### `manhattan/3`, `part1/2`, `part2/2`, `solve/3`

```prolog
manhattan(X, Y, Distance) :- Distance is abs(X) + abs(Y).

part1(Instructions, Distance) :- navigate(ship,     Instructions, Distance).
part2(Instructions, Distance) :- navigate(waypoint, Instructions, Distance).
```

The **L¹ / taxicab norm**, and the reason nothing in the solution ever
needs to care which quadrant the ship is in. `part1/2` and `part2/2` are
one word apart, which is the point of the entire design; `solve/3` parses
once and runs both.

---

## Correctness notes

**The two parts really are one machine.** The claim worth verifying is
that part 1's ship-with-facing *is* the `Mode = ship` instantiation, not
merely something similar to it. Part 1's vector takes only the four unit
values: `start_state/2` begins at `(1, 0)`, `rotate/5` maps units to
units, and under `Mode = ship` nothing else ever writes the vector. So the
vector is a compass direction throughout, `F v` adds `facing × v`, and
that is exactly the statement's rule. The cardinal moves are absolute in
both readings, which is what lets `cardinal/3` be shared unchanged.

**Rotation is closed and exact.** `rotate/5` maps `ℤ² → ℤ²` with no
division, so no representation error can enter. Composition is correct
because `quarter_turns/3` reduces mod 4 and the four clauses enumerate
C₄'s elements: `rotate(a)` then `rotate(b)` equals `rotate((a+b) mod 4)`
because that is the group law. The suite pins the two instances that
matter — `rotate(1)` twice equals `rotate(2)`, and four quarters is the
identity.

**Termination is trivial**, unlike the previous day's. `foldl/4` over a
finite list of 769 elements, each `step/4` deterministic and
non-recursive. There is no loop to diverge and no fixpoint to fail to
reach. Worth stating only because Day 11 sits next door and *its*
termination is the puzzle's promise rather than a proof.

**Overflow does not arise, and would not matter if it did.** Part 2's ship
reaches ~94,000 units from the origin and the waypoint never exceeds 52;
both fit a 32-bit integer with enormous room. SWI's integers are
arbitrary-precision regardless, so unlike a C version there is nothing to
check — the same non-event as [Day 10](day10_function_guide.md)'s
97-trillion answer, and the reason the Rust sketch below has to pick a
width while this code does not.

**Where a wrong answer would come from**, ranked by how easy each is to
ship:

1. Rotating the wrong way. `(x, y) -> (-y, x)` is *left*; wire it into the
   `R` path and part 1's example still produces a number, just not 25.
2. Normalising `L` with a truncating remainder, giving a negative quarter
   count and no matching `rotate/5` clause. This one fails loudly in
   Prolog and indexes out of bounds silently in C.
3. Writing `translate/5`'s two clauses and wiring the modes backwards.
4. Reading `F v` in part 2 as "move to the waypoint, and now the waypoint
   is where the ship is". It is a *relative* offset that travels with the
   ship; the ship moves by `v` copies of it and the offset is unchanged.

---

## Tests — what's pinned and why

Seventeen tests plus five `forall` sub-tests in
[`test/day12_tests.pl`](../../test/day12_tests.pl). The answer locks are
the least interesting entries:

- `parse_action_value_pairs` / `parse_all_actions` — pin the
  `Action-Value` shape, the char-atom action, and multi-digit values. The
  second covers every letter, so a positional-slicing mistake cannot hide
  in the one action the example happens not to use.
- `left_is_mirrored_right` (`forall` over `90-270`, `180-180`, `270-90`)
  — pins `L d ≡ R (360−d)` as a *property* rather than three separately
  computed expected numbers. `full_turn_is_identity` pins the `mod 4`
  wrap.
- `non_right_angle_rejected` — declared `[fail]`, so the suite asserts
  that `quarter_turns('R', 45, _)` **has no solution**. This is the guard
  test; delete the `Degrees mod 90 =:= 0` line and it is the only thing
  that notices.
- `right_turns_walk_the_compass` — `findall/3` over `between(0, 3, Q)`
  from east gives `[1-0, 0-(-1), -1-0, 0-1]`: E, S, W, N. One test pinning
  both the rotation direction and all four table entries, and the first
  place to look when part 1 is off.
- `four_quarters_is_identity` (`forall` over four vectors, including `0-0`
  and one with a negative component) and `half_turn_composes` — the group
  laws, checked on vectors that are *not* unit compass directions, because
  part 2 rotates arbitrary offsets.
- `cardinal_move_leaves_facing_alone` — runs the statement's own
  `F10, N3, F7` prefix and expects **20**, i.e. east 17 north 3. That
  distance only comes out right if `N3` left the facing pointing east. The
  statement flags this in a parenthetical, which usually means it is where
  readers go wrong.
- `waypoint_scales_the_offset` — `F1` → 11, `F10` → 110. Pins that `F`
  scales the offset rather than stepping to it once: the misreading listed
  fourth above.
- `rotation_alone_does_not_move_the_ship` — `R90` alone → 0, then
  `R90, F1` → 11 (east 1, south 10). Separates the rotation from its
  effect.
- `empty_program_goes_nowhere` and `distance_ignores_sign`
  (`W17, S8` → 25) — the degenerate fold, and the `abs/1` in
  `manhattan/3`.
- Answer locks: **1956** and **126797**.

Cross-validated against [`python/day12.py`](../../python/day12.py), which
is the same machine over tuples and a dict — but with a *different*
rotation implementation (repeated quarter turns rather than four
enumerated cases), so the two languages disagree about how to rotate while
agreeing on every answer. It independently prints
`part1=1956 part2=126797`.

---

## Complexity & benchmarks

Let *n* be the instruction count (769). Every phase is **O(n)** with a
small constant: one pass to parse, one fold to run, constant work per
instruction. There is no data structure to build, nothing to search, and
no iteration to a fixpoint.

| Phase | Cost |
|---|---|
| Parse | O(n) — two slices and a `number_string/2` per line |
| One `step/4` | O(1) — at most four multiplications and two additions |
| `navigate/3` | O(n) |
| Both parts | O(n) |

Measured (`swipl bench/main.pl day12`):

```text
  parse          7,985 inf      0.998 ms
  part1          5,789 inf      0.355 ms
  part2          5,629 inf      0.216 ms
```

Two things worth reading off that. First, **parsing costs more than
either part on its own** — 7,985 inferences (≈10.4 per line) against
5,789 and 5,629 (≈7.5 per instruction), and with string allocation behind
it that the folds do not pay. When the algorithm is a linear scan with
almost nothing in the body, getting the bytes in *is* the program.
Second, the two parts differ by under 3% in inferences, which is what the
"identical clause counts, different arithmetic operands" model predicts;
the wall-clock gap between them is larger than the inference gap and is
measurement noise at this scale — anything under a millisecond in SWI
is.

For scale: [Day 11](day11_function_guide.md)'s part 1 spent 12.6
**million** inferences on the same machine. This entire day is roughly
0.1% of that.

---

## If I were writing this in Rust

The shape transfers directly. The interesting differences are all in the
type system and in `%`.

```rust
#[derive(Clone, Copy)]
struct Vec2 { x: i64, y: i64 }

impl Vec2 {
    fn rotate_cw(self, quarters: u32) -> Vec2 {
        match quarters {
            0 => self,
            1 => Vec2 { x:  self.y, y: -self.x },
            2 => Vec2 { x: -self.x, y: -self.y },
            _ => Vec2 { x: -self.y, y:  self.x },
        }
    }
    fn scale(self, k: i64) -> Vec2 { Vec2 { x: self.x * k, y: self.y * k } }
}

enum Action { Cardinal(Vec2), Turn(u32), Forward }

fn navigate(program: &[(Action, i64)], mode: Mode) -> i64 {
    let (mut ship, mut vec) = mode.start();
    for (action, value) in program {
        match action {
            Action::Cardinal(unit) => match mode {
                Mode::Ship     => ship = ship + unit.scale(*value),
                Mode::Waypoint => vec  = vec  + unit.scale(*value),
            },
            Action::Forward => ship = ship + vec.scale(*value),
            Action::Turn(q) => vec  = vec.rotate_cw(*q),
        }
    }
    ship.x.abs() + ship.y.abs()
}
```

| Prolog | Rust | Note |
|---|---|---|
| `nav(X, Y, VX, VY)` | two `Vec2`s | Rust names the pair; Prolog flattens both into one term |
| `step/4`'s three clauses | `match action` arms | A clause head plus guard *is* a match arm |
| `translate/5` on `Mode` | `match mode` inside the arm | Prolog's dispatch is a separate indexed predicate; Rust nests it |
| `cardinal/3` as a guard | resolved into `Action::Cardinal` | Rust decodes the letter **once**, at parse time |
| four `rotate/5` facts | `match quarters` | Identical structure, identical reason |
| bignums | `i64` chosen by hand | ~94k fits anything; the choice is still yours to make |

Three genuine differences:

1. **`%` on negatives.** `(-1i32) % 4` is `-1` in Rust, as in C. The `L`
   normalisation must be `(-(degrees / 90)).rem_euclid(4)`. Forget it, and
   with `quarters: u32` the code will not compile — the type catches it,
   which is the good outcome. Write the same thing with `i32` and it
   compiles and falls into the `_` arm, rotating `L90` as though it were
   `R270`. Prolog's `mod` sidesteps this by being floored and its `rem` is
   the trap; Rust's `%` is the trap and `rem_euclid` the sidestep. Same
   fork, opposite defaults — which is the whole argument for knowing the
   rule rather than the idiom.
2. **Parsing resolves the action.** `enum Action` decodes the letter once
   into a variant carrying its unit vector or quarter count, so the hot
   loop never touches a character. Prolog *could* do the same —
   `parse_instruction/2` could emit `cardinal(0, 1)-Value` — and this
   version deliberately does not, keeping the parsed form a faithful
   `Action-Value` echo of the input so tests can assert on something
   recognisable. At 769 instructions the difference is unmeasurable; at a
   million it is the first change to make.
3. **`Mode` as a parameter vs. as a type.** The sketch branches on `mode`
   inside the loop — a perfectly predicted branch, free in practice. The
   more Rust-idiomatic version makes `Mode` a trait with two impls and
   monomorphises the loop twice, eliminating the branch entirely. That is
   the same "one engine, two instantiations" idea the Prolog gets from a
   plain extra argument: Prolog pays a clause-index lookup, Rust pays with
   a trait and a second copy of the code.

The complex-number framing has a direct Rust expression too:
`num_complex::Complex<i64>`, with rotation as `* Complex::new(0, -1)`. It
is genuinely the clearest encoding of the mathematics, and it is one
dependency for four lines of arithmetic — the right call in a crate
already pulling in `num`, and overkill here.

---

## Possible optimization

Shipping code stays as written. At well under a millisecond there is
nothing to buy, so these are listed for the shape of the ideas rather than
the speed.

**1. Fuse the two parts into one fold.** Both parts read the same
instruction list and neither depends on the other, so a single pass could
carry both states and halve the traversal. It would save one walk of a
769-element list, cost a six-argument state term, and make `step/4` serve
two masters. The clearest example in this repo of an optimization that is
real, measurable in principle, and still not worth it.

**2. Decode actions at parse time.** As in the Rust note: emit the unit
vector or quarter count from `parse_instruction/2`, and let `step/4`
dispatch on an already-resolved term via first-argument indexing instead
of a `cardinal/3` guard plus cuts. This is the change that would matter if
the input were large, and it trades a faithful parse for a faster one.

**3. Collapse runs of rotations.** Consecutive `L`/`R` instructions
compose into a single quarter count before any rotation is applied
(`R90, R180` ≡ `R270`), because C₄ is a group and rotation is its law.
The real input has too few adjacent turn pairs for this to buy anything —
but it is the right instinct for a longer program, and it generalises:
any run of instructions containing only turns and cardinal moves is a
single affine map that could be folded into one step ahead of time.

**4. Parse on codes rather than strings.** Parsing is the largest line in
the benchmark, and `split_string/4` allocates a string per line before
`sub_string/5` allocates two more. Reading with `phrase_from_file/2` over
a code list would cut that allocation substantially. This is the only item
here that would actually move the numbers — and it is a parsing change,
not an algorithm change, which is itself the day's closing observation:
when the algorithm is O(n) with a two-instruction body, the only thing
left to optimize is the I/O.
