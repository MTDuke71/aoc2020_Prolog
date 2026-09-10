# Day 22 Function Guide — Crab Combat

> Two decks of 25 cards, the numbers 1 to 50 dealt out once each, and a
> game of War. Part 1 is War exactly: higher card takes both, winner's
> card goes under the deck first, play until someone holds all fifty,
> score the deck bottom-up. Part 2 is *Recursive* Combat, the same game
> with two rules bolted on: a round whose starting position has been
> seen before in this game ends the game for player 1, and a round where
> both players hold at least as many cards as the value they just drew
> is settled by a sub-game on copies of that many cards. The shipping
> solution is one engine with a `recursive` switch, decks as tuples, and
> a set of positions per game. It plays 12,487 games and 986,517 rounds
> on the real input in 0.42 s. The interesting content is why the loop
> rule is load-bearing (without it the real input never finishes), and
> a one-line identity — the player holding the highest card in a
> sub-game cannot lose it — that decides three quarters of those games
> without playing them and is pinned as a test rather than shipped.

Source: [`python/day22.py`](../../python/day22.py) ·
Tests: [`python/tests/test_day22.py`](../../python/tests/test_day22.py)

---

## 1. The problem

The input is two blocks:

```text
Player 1:
9
2
6
3
1

Player 2:
5
8
4
7
10
```

Top card first. A round of **Combat**: both players draw their top
card; the higher wins; the winner puts both on the bottom of their own
deck, *their* card first. The game ends when a player holds every
card. The **score** of a deck weights the bottom card by 1, the next by
2, up to the top card by the deck size. The sample takes 29 rounds and
player 2 ends with `3, 2, 10, 6, 8, 5, 9, 4, 7, 1`:

```text
3*10 + 2*9 + 10*8 + 6*7 + 8*6 + 5*5 + 9*4 + 4*3 + 7*2 + 1*1 = 306
```

**Recursive Combat** (part 2) keeps the decks, the collection rule and
the scoring, and changes how a round is decided:

1. *Loop rule.* Before dealing, if this game has already had a round
   that started from exactly these two decks in this order, the game
   ends now and player 1 wins. Only rounds of *this* game count.
2. *Recursion rule.* After dealing, if both players still hold at
   least as many cards as the value they just drew, the round's winner
   is the winner of a sub-game whose decks are *copies* of exactly that
   many cards from the top of each deck. The parent game waits.
3. Otherwise the higher card wins as before.

The winner collects both cards, own card first, *even when their card
was the lower one*. On the sample, the first eight rounds are decided
on value; round 9 has player 1 draw 4 holding `9, 8, 5, 2` and player 2
draw 3 holding `10, 1, 7, 6`, both have enough, and game 2 is played on
`9, 8, 5, 2` versus `10, 1, 7`. Five games in all, three deep; player 2
wins with `7, 5, 6, 2, 4, 1, 10, 8, 9, 3`, score 291.

The statement also gives a two-card-versus-three-card game that would
loop forever without rule 1: `43, 19` against `2, 29, 14` returns to its
starting position after six rounds.

The real input: 25 cards each, the numbers 1 to 50 exactly once, the
50 in player 1's deck.

## 2. Representation

**A deck is a `tuple[int, ...]`, top card first**, and the parsed input
is a pair of them. The obvious alternative is `collections.deque`,
which makes draw and collect O(1). Tuples were chosen instead for three
reasons that all come from part 2:

- The loop rule needs a *hashable* snapshot of both decks every round.
  A tuple is its own snapshot; a deque has to be copied into one.
- A sub-game's decks are "copies of the next N cards", which is a slice.
- A sub-game must not disturb its parent. Tuples cannot be disturbed.

Drawing is `d[0], d[1:]` and collecting is `d + (a, b)`, each of which
copies the deck. At fifty cards that is a few hundred bytes per round,
and section 7 measures the deque version at slower, not faster, because
the snapshot it must build for the seen-set costs what the tuple
version's copies cost.

**The seen-set is `set[tuple[Deck, Deck]]`**, one per game, keyed on
both decks. The statement says "the same cards in the same order in the
same players' decks", and that is what a pair of tuples compares. A
common shortcut keys on player 1's deck alone; it is faster (section 7)
and not what the rule says, since player 2's *order* is not determined
by player 1's deck.

**The winner is `1` or `2`**, and `combat` returns `(winner, decks)`
so the caller can index the final pair with `winner - 1`.

## 3. Function walkthrough

### `parse_input(raw) -> Decks`

`splitlines()`, per-line `strip()`, and a two-state accumulator: a
`Player N:` header is skipped, a number is appended to the current
deck, and a blank line closes the current deck if it has anything in
it. A sentinel empty line is appended so the last deck closes without
a trailing newline in the file. Anything other than exactly two decks
is a `ValueError`.

The CRLF case here has a wrinkle the other days do not: the blank line
*between* the decks is `\r` on its own under Windows endings. Without
the strip it would not be blank, `int("\r")` would raise, and there is
no partial answer to mask that with. With it, the sample under `\r\n`
parses to the same pair, which is the CRLF test.

### `combat(decks, recursive=False) -> (winner, decks)`

The whole game, both parts:

```python
p1, p2 = decks
seen = set()
while p1 and p2:
    if (p1, p2) in seen:
        if not recursive:
            raise ValueError(...)
        return 1, (p1, p2)
    seen.add((p1, p2))

    c1, p1 = p1[0], p1[1:]
    c2, p2 = p2[0], p2[1:]
    if recursive and len(p1) >= c1 and len(p2) >= c2:
        winner, _ = combat((p1[:c1], p2[:c2]), recursive=True)
    else:
        winner = 1 if c1 > c2 else 2

    if winner == 1:
        p1 += (c1, c2)
    else:
        p2 += (c2, c1)
return (1 if p1 else 2), (p1, p2)
```

Three things to read off it.

*The recursion rule is checked after the draw*, on the cards remaining,
which is what "at least as many cards remaining in their deck as the
value of the card they just drew" says. `len(p1) >= c1` is inclusive:
a player who drew 1 with exactly 1 card behind it qualifies. The test
`test_sub_game_needs_both_players_to_have_enough_cards` sits exactly on
that edge (player 1 draws 1 with 1 behind, player 2 draws 2 with 2
behind).

*The sub-game gets slices and its result is only a winner.* The `_` is
the sub-game's final decks, which the parent never looks at; "the game
that triggered it is on hold and completely unaffected". `p1[:c1]` is a
new tuple, so nothing the sub-game does can reach the parent.

*Regular Combat uses the same seen-set but raises on a repeat.* The
statement gives part 1 no loop rule, and on the real input none is
needed (265 rounds, done). But the loop example loops under regular
Combat too, six rounds back to the start, and an engine that spins
forever on such an input is worse than one that says so. So the seen-set
is kept in both modes and its meaning is switched: player 1 wins in
recursive mode, `ValueError` otherwise.

### `score(deck) -> int`

`zip(deck, range(len(deck), 0, -1))` pairs the top card with the deck
size and the bottom card with 1, then a sum of products. The statement's
two worked decks (306 and 291) are the parametrised cases, with a
single-card deck and an empty deck for the ends.

### `part1(decks)` and `part2(decks)`

`combat(decks)` and `combat(decks, recursive=True)`, then
`score(final[winner - 1])`. Nothing else.

## 4. Why it is correct

**The engine is the rules, one line each,** and the sample pins the
whole: 29 rounds of Combat produce the statement's exact final deck, and
Recursive Combat produces the statement's exact final deck, which is the
strongest evidence available that the collection order, the recursion
threshold and the loop rule are all read as the statement means them,
since a mistake in any of them changes the order the cards end up in.
The recorder fixture in the tests, which wraps `combat` so that every
sub-game it plays is logged, adds that the sample is five games three
deep, with game 2 starting from `9, 8, 5, 2` versus `10, 1, 7` as the
statement's trace shows.

**"Previous rounds from other games are not considered"** is pinned by
a feature of the sample that the statement's trace shows and the
recorder catches: the sub-game `8` versus `10, 9, 7, 5` is played
*twice*. A seen-set shared across games would find the second one's
first round already present and hand it to player 1 on the spot; the
per-game set plays it out and 10 beats 8 both times.

**The winner of a sub-game takes the round with their own card first,
whichever card is lower.** A targeted test has player 1 draw 2 against
3 and win the sub-game `10, 9` versus `1, 4, 5`; the next position is
`10, 9, 2, 3` against `1, 4, 5`, 2 above 3.

**The loop rule is load-bearing, not a formality.** On the real input,
3,523 of the 12,487 games end by it, always for player 1, and with the
rule removed the top-level game does not finish within five million
rounds (measured while writing this; the shipping engine ran the
unguarded variant with a round budget). The rule is also what makes
`combat` a total function: every game either loses a card from one deck
per round or revisits a position, and the position space is finite.

**An identity, pinned rather than used.** In a game whose cards are
distinct positive integers, the highest card *cannot trigger a
sub-game*: with n cards in the game, the highest is at least n, and the
player who draws it has at most n − 2 cards behind it (one card is in
their hand, the opponent holds at least one). So that round is decided
on value, the high card wins it, and it goes back to its owner's deck.
It is therefore never lost, its owner never runs out of cards, and:

- if **player 1** holds it, player 1 wins the game, either by taking
  every card or by the loop rule;
- if **player 2** holds it, player 2 cannot lose on cards, but the loop
  rule can still end the game for player 1.

Sub-game decks are copies of distinct cards, so the identity applies to
every sub-game. On the real input, player 1 holds the high card in
9,440 of the 12,486 sub-games and wins all 9,440; player 2 holds it in
the other 3,046 and wins 2,434 of them, the remaining 612 going to
player 1 by the loop rule. Both halves are asserted in
`test_real_high_card_decides_a_sub_game_for_player_1`. The shipping
engine does not use the identity (section 7 measures what it buys);
the point of pinning it is that a claim in a sidebar is still a claim.

## 5. Complexity

Let n be the cards in a game (50 at the top). A round costs O(n) for
the tuple copies and O(n) to hash the position, and a game runs at most
as many rounds as there are distinct positions, so nothing tighter than
"finite" is available for the recursion in general. What the real input
actually does:

| | part 1 | part 2 |
| --- | ---: | ---: |
| games | 1 | 12,487 |
| rounds | 265 | 986,517 (503 in the top game) |
| deepest recursion | – | 10 |
| games ended by the loop rule | 0 | 3,523 |
| largest seen-set | 265 | 3,667 positions |

Measured on the real input (`python\bench.py 22 -n 5`, best / median):

| phase  |       best |     median |
| ------ | ---------: | ---------: |
| parse  |   0.008 ms |   0.008 ms |
| part 1 |   0.140 ms |   0.151 ms |
| part 2 | 419.9 ms   | 421.3 ms   |

About 0.43 µs per round; the day is the year's third slowest after
day 15's 30-million-turn walk and day 17's alternate scan. Part 2 is
the game count times the round count, and neither is under the
solver's control.

## 6. If I were writing this in Rust

A direct port, `Vec<u8>` decks with `remove(0)` and `push`, a
`HashSet<(Vec<u8>, Vec<u8>)>` for the seen-set and `to_vec()` slices
for sub-games, is short and reads like the Python:

```rust
fn combat(mut p1: Vec<u8>, mut p2: Vec<u8>, recursive: bool) -> (u8, Vec<u8>, Vec<u8>) {
    let mut seen: HashSet<(Vec<u8>, Vec<u8>)> = HashSet::new();
    while !p1.is_empty() && !p2.is_empty() {
        if !seen.insert((p1.clone(), p2.clone())) {
            return (1, p1, p2); // loop rule
        }
        let (c1, c2) = (p1.remove(0), p2.remove(0));
        let winner = if recursive && p1.len() >= c1 as usize && p2.len() >= c2 as usize {
            combat(p1[..c1 as usize].to_vec(), p2[..c2 as usize].to_vec(), true).0
        } else if c1 > c2 { 1 } else { 2 };
        if winner == 1 { p1.push(c1); p1.push(c2) } else { p2.push(c2); p2.push(c1) }
    }
    (if p1.is_empty() { 2 } else { 1 }, p1, p2)
}
```

`HashSet::insert` returning `false` folds the "seen? add." pair into
one lookup. The ownership story is the tuple story from section 2 made
explicit: the sub-game *takes* its two `Vec`s by value, so the borrow
checker guarantees the parent's decks are untouched, where the Python
relies on tuples being immutable.

Compiled with `rustc -O` (1.93.1) and run three times on the real input
while writing this guide, best of 200 inside each run for the fast
phases and best of 20 for part 2. Same two answers. Parse 0.0006 ms,
part 1 0.040 ms, part 2 **138 ms**. Only 3× faster than Python on the
part that matters, which is the number worth explaining. Each round
allocates two fresh `Vec`s for the seen-set key and runs SipHash over
them, and `remove(0)` shifts the deck; none of that is interpreter
overhead, it is the algorithm's memory traffic, and Rust pays it too.
Swapping in a single flat byte key `[len1, p1…, p2…]` under an FNV-1a
hasher (no crates, twenty lines) takes it to **101 ms**, 27% off, which
bounds how much of the cost is hashing; the rest is the per-round copy
and shift. The high-card shortcut from section 4 in the same port: 0.9
ms, and 0.65 ms with the flat key. This is the day 19 shape: when the
work is inherent, the language buys 3–4×, not 50×.

## 7. Possible optimization

All measured on the real input from a scratch script (best of N; every
variant produces 31,596):

| variant | part 2 |
| --- | ---: |
| shipping (tuples, seen-set of both decks) | 422 ms |
| `deque` decks, tuple snapshot per round for the seen-set | 500 ms |
| seen-set keyed on player 1's deck only | 106 ms |
| sub-game results memoised by starting decks | 428 ms |
| high-card shortcut: a sub-game where player 1 holds the max is a player 1 win | 2.7 ms |

**Deques** are the textbook queue and lose here, as section 2 predicted:
`popleft` and `extend` are O(1), but the seen-set still needs
`(tuple(p1), tuple(p2))` every round, which is the same copy the tuple
version does for its draw, plus the `list(...)[:n]` conversions for the
sub-games.

**Keying on player 1's deck** is 4× faster and is the commonest version
on the internet. It is wrong in principle: the multiset of player 2's
cards is fixed by player 1's, but their *order* is not, so two distinct
positions can collide and end a game early. Right answer on this input,
and no way to know that in advance.

**Memoising sub-games** by their starting decks is the natural idea
once the recorder shows the sample playing one sub-game twice. On the
real input only 1,032 of the 12,487 starts repeat, and the dictionary
costs what it saves.

**The high-card shortcut** is section 4's identity applied: before
playing a *sub-game*, if `max(p1) > max(p2)`, return player 1 without
playing. (It cannot be applied to the top-level game, whose final deck
is needed for the score, and it says nothing when player 2 holds the
max.) 9,440 of the 12,486 sub-games return at once and most of the rest
are shallow, so part 2 drops from 422 ms to 2.7 ms, 150× faster. It is
one `if` and a docstring, and it is correct for any decks of distinct
positive integers. It stays out of the shipping engine on the repo's
policy: the plain engine is the statement's rules and nothing else,
0.42 s is an acceptable price for that, and the identity is guarded by
a test on this input rather than by the solver depending on it. If the
day were ever ported to a hot path, this is the change to make, and the
test is already there.
