"""Day 22: Crab Combat.

Two decks of distinct cards, one per player.  A round: both players draw
their top card, the higher card wins, and the winner puts both cards on the
bottom of their deck, their own card first.  The game ends when one player
holds everything, and the answer is that deck's score: the bottom card times
1, the next up times 2, and so on to the top card times the deck size.  On
the statement's decks the game takes 29 rounds and player 2 wins with

    3, 2, 10, 6, 8, 5, 9, 4, 7, 1   ->   3*10 + 2*9 + ... + 1*1 = 306

Part 2 is *Recursive* Combat, the same game with two rules added.  If a
round's starting position (both decks, in order) has occurred before in the
same game, the game ends at once and player 1 wins; that is the loop
breaker.  And when both players hold at least as many cards as the value of
the card they just drew, the round's winner is decided by a sub-game played
on copies of exactly that many cards from the top of each deck -- the parent
game waits, untouched.  A round won through a sub-game can hand the winner
the *lower* card, so the cards still go to the bottom winner's-card-first.
Same decks, same scoring; player 2 wins again, with 291.

One engine, `combat(decks, recursive)`, plays both parts; part 1 is the
engine with the two rules switched off.
"""

from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day22.txt"

Deck = tuple[int, ...]  # top card first
Decks = tuple[Deck, Deck]  # (player 1, player 2)


def parse_input(raw: str) -> Decks:
    """Two blank-line-separated blocks, each a `Player N:` header then one card per line.

    `splitlines()` plus a per-line `.strip()` means a Windows `\r` never
    reaches `int()`, and a `\r` on the blank line between the blocks still
    reads as blank.
    """
    decks: list[Deck] = []
    cards: list[int] = []
    for line in raw.splitlines() + [""]:
        line = line.strip()
        if line.startswith("Player"):
            continue
        if line:
            cards.append(int(line))
        elif cards:
            decks.append(tuple(cards))
            cards = []
    if len(decks) != 2:
        raise ValueError(f"expected two decks, found {len(decks)}")
    return decks[0], decks[1]


def combat(decks: Decks, recursive: bool = False) -> tuple[int, Decks]:
    """Play one game to the end.  Returns (winner, final decks), winner 1 or 2.

    Decks are tuples: drawing is `d[0], d[1:]`, collecting is `d + (a, b)`,
    and the sub-game's copies are slices.  Fifty cards make every one of
    those cheap, and a tuple is hashable, which the seen-set needs.

    `recursive=False` is regular Combat.  The statement gives that game no
    loop rule, so a repeated position there is reported as an error rather
    than looped on forever; it never happens on a real input.
    """
    p1, p2 = decks
    seen: set[Decks] = set()
    while p1 and p2:
        if (p1, p2) in seen:
            if not recursive:
                raise ValueError("regular Combat does not terminate on these decks")
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


def score(deck: Deck) -> int:
    """Bottom card times 1, up to the top card times the deck size."""
    return sum(card * weight for card, weight in zip(deck, range(len(deck), 0, -1)))


def part1(decks: Decks) -> int:
    """The winning deck's score under regular Combat."""
    winner, final = combat(decks)
    return score(final[winner - 1])


def part2(decks: Decks) -> int:
    """The winning deck's score under Recursive Combat."""
    winner, final = combat(decks, recursive=True)
    return score(final[winner - 1])


def solve(raw: str) -> tuple[int, int]:
    decks = parse_input(raw)
    return part1(decks), part2(decks)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
