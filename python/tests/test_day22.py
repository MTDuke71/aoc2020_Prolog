"""Day 22: Crab Combat."""

import pytest

import day22

LOCKED = (32413, 31596)

# The statement's decks.
SAMPLE = """\
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
"""
SAMPLE_DECKS = ((9, 2, 6, 3, 1), (5, 8, 4, 7, 10))

# "Here is an example of a small game that would loop forever without the
# infinite game prevention rule."
LOOP = """\
Player 1:
43
19

Player 2:
2
29
14
"""


@pytest.fixture
def recorded(monkeypatch):
    """Replace `day22.combat` with a recorder of every game it plays.

    The engine recurses through the module-global name, so wrapping that
    name sees every sub-game.  Each record is (starting decks, depth,
    winner, final decks); the top-level game is depth 1.
    """
    records = []
    depth = 0
    original = day22.combat

    def recording(decks, recursive=False):
        nonlocal depth
        depth += 1
        try:
            winner, final = original(decks, recursive)
        finally:
            depth -= 1
        records.append((decks, depth + 1, winner, final))
        return winner, final

    monkeypatch.setattr(day22, "combat", recording)
    return records


def test_parse_input():
    assert day22.parse_input(SAMPLE) == SAMPLE_DECKS


def test_crlf_input():
    """A Windows download ends every line in \r\n, including the blank line
    between the decks; neither the `\r` nor a `\r`-only line may reach int()."""
    assert day22.parse_input(SAMPLE.replace("\n", "\r\n")) == SAMPLE_DECKS


def test_parse_tolerates_missing_trailing_newline():
    assert day22.parse_input(SAMPLE.rstrip("\n")) == SAMPLE_DECKS


def test_parse_rejects_one_deck():
    with pytest.raises(ValueError):
        day22.parse_input("Player 1:\n1\n2\n")


@pytest.mark.parametrize(
    "deck, expected",
    [
        ((3, 2, 10, 6, 8, 5, 9, 4, 7, 1), 306),  # part 1's post-game deck, the statement's worked sum
        ((7, 5, 6, 2, 4, 1, 10, 8, 9, 3), 291),  # part 2's
        ((5,), 5),
        ((), 0),
    ],
)
def test_score(deck, expected):
    assert day22.score(deck) == expected


def test_score_weights_bottom_card_once_and_top_card_by_size():
    """The statement's rule read literally: bottom × 1, ..., top × n."""
    assert day22.score((1, 1, 1, 1)) == 4 + 3 + 2 + 1
    assert day22.score((10, 0, 0)) == 30


def test_regular_combat_example():
    """29 rounds, player 2 ends holding every card in the statement's order."""
    assert day22.combat(SAMPLE_DECKS) == (2, ((), (3, 2, 10, 6, 8, 5, 9, 4, 7, 1)))


def test_part1_example():
    assert day22.part1(SAMPLE_DECKS) == 306


def test_regular_combat_is_higher_card_wins_winner_card_first():
    """One round from the sample: 9 beats 5 and lands above it at the bottom
    of player 1's deck.  Seen from outside via a game that ends there."""
    assert day22.combat(((9,), (5,))) == (1, ((9, 5), ()))
    assert day22.combat(((5,), (9,))) == (2, ((), (9, 5)))


def test_regular_combat_refuses_to_loop():
    """The statement gives regular Combat no loop rule; the loop example
    cycles back to its start after six rounds under it, so the engine
    reports that rather than spin."""
    with pytest.raises(ValueError):
        day22.combat(day22.parse_input(LOOP))


def test_recursive_combat_example():
    assert day22.combat(SAMPLE_DECKS, recursive=True) == (2, ((), (7, 5, 6, 2, 4, 1, 10, 8, 9, 3)))


def test_part2_example():
    assert day22.part2(SAMPLE_DECKS) == 291


def test_loop_rule_ends_the_game_for_player_1():
    """Six rounds return the decks to 43,19 / 2,29,14; that repeat is a
    player 1 win on the spot, with both decks still in hand."""
    assert day22.combat(day22.parse_input(LOOP), recursive=True) == (1, ((43, 19), (2, 29, 14)))


def test_sub_game_needs_both_players_to_have_enough_cards(recorded):
    """Player 1 draws 1 with exactly 1 card left, player 2 draws 2 with
    exactly 2 left: "at least as many" is met with nothing to spare, and the
    round is settled by the sub-game 3 vs 4,5, which player 2 wins."""
    winner, final = day22.combat(((1, 3), (2, 4, 5)), recursive=True)
    assert (winner, final) == (2, ((), (5, 2, 1, 4, 3)))
    assert [(decks, winner) for decks, depth, winner, _ in recorded if depth > 1] == [(((3,), (4, 5)), 2)]


def test_no_sub_game_when_one_player_is_short(recorded):
    """Player 1 draws 3 with two cards behind it; player 2 has plenty.  No
    recursion: the higher card, 4, takes the round."""
    day22.combat(((3, 1, 2), (4, 5, 6, 7, 8)), recursive=True)
    first_round_sub_games = [decks for decks, depth, _, _ in recorded if depth == 2 and decks[0] == (1, 2)]
    assert first_round_sub_games == []


def test_sub_game_winner_takes_the_round_with_the_lower_card(recorded):
    """Player 1's 2 loses to 3 on value but the sub-game 10,9 vs 1,4,5 is
    player 1's, so player 1 collects both cards, own card first: 2 above 3."""
    day22.combat(((2, 10, 9), (3, 1, 4, 5)), recursive=True)
    assert recorded[0] == (((10, 9), (1, 4, 5)), 2, 1, ((1, 9, 4, 10, 5), ()))


def test_lower_card_round_leaves_the_expected_decks():
    """Same round, checked on the decks rather than the recorder: after it,
    player 1 holds 10, 9, 2, 3 and player 2 holds 1, 4, 5.  The game from
    *there* ends the same way as the game from one round earlier: the
    repeat that eventually ends it (a player 1 win) closes on a later
    position, so the extra entry in the seen set changes nothing."""
    before = day22.combat(((2, 10, 9), (3, 1, 4, 5)), recursive=True)
    after = day22.combat(((10, 9, 2, 3), (1, 4, 5)), recursive=True)
    assert before == after


def test_previous_rounds_from_other_games_are_not_considered(recorded):
    """The sample plays the sub-game 8 vs 10,9,7,5 twice.  A seen-set shared
    across games would flag the second one's first round as a repeat and
    hand it to player 1; per game, 10 beats 8 both times."""
    day22.combat(SAMPLE_DECKS, recursive=True)
    same_start = [winner for decks, _, winner, _ in recorded if decks == ((8,), (10, 9, 7, 5))]
    assert same_start == [2, 2]


def test_sample_plays_five_games_three_deep(recorded):
    """Game 1 spawns games 2 and 3 (from 9,8,5,2 vs 10,1,7 and 8,1 vs
    3,4,10,9,7,5); game 3 spawns games 4 and 5, which are the same game."""
    day22.combat(SAMPLE_DECKS, recursive=True)
    assert len(recorded) == 5
    assert max(depth for _, depth, _, _ in recorded) == 3


@pytest.fixture(scope="module")
def real(real_input):
    return day22.parse_input(real_input(22))


def test_real_input_shape(real):
    assert (len(real[0]), len(real[1])) == (25, 25)
    assert sorted(real[0] + real[1]) == list(range(1, 51))
    assert 50 in real[0]


def test_real_regular_combat_ends_with_player_1_holding_all_fifty(real):
    winner, final = day22.combat(real)
    assert winner == 1
    assert len(final[0]) == 50 and final[1] == ()


def test_real_recursive_combat_shape(real, recorded):
    """12,487 games, ten deep; 3,523 of them end by the loop rule, i.e.
    with both decks still non-empty.  Without that rule the top game does
    not finish in five million rounds (checked while writing this)."""
    winner, final = day22.combat(real, recursive=True)
    assert winner == 1 and len(final[0]) == 50
    assert len(recorded) == 12487
    assert max(depth for _, depth, _, _ in recorded) == 10
    loop_ended = [winner for _, _, winner, final in recorded if final[0] and final[1]]
    assert len(loop_ended) == 3523
    assert set(loop_ended) == {1}


def test_real_high_card_decides_a_sub_game_for_player_1(real, recorded):
    """The identity behind the guide's shortcut: in a game of n distinct
    positive cards the highest is at least n, so the player drawing it can
    never have n cards behind it and it never triggers a sub-game.  It wins
    every round it is played in, is never lost, and so its holder never
    runs out of cards.  For player 1 that is a win outright (all cards, or
    the loop rule).  For player 2 it only rules out losing on cards; the
    loop rule can still hand the game to player 1 -- and does, 612 times."""
    day22.combat(real, recursive=True)
    sub_games = [(decks, winner) for decks, depth, winner, _ in recorded if depth > 1]
    player_1_high = [winner for (p1, p2), winner in sub_games if max(p1) > max(p2)]
    player_2_high = [winner for (p1, p2), winner in sub_games if max(p2) > max(p1)]
    assert len(player_1_high) + len(player_2_high) == len(sub_games)
    assert (len(player_1_high), set(player_1_high)) == (9440, {1})
    assert (len(player_2_high), player_2_high.count(2), player_2_high.count(1)) == (3046, 2434, 612)


def test_real_input_locked(check_locked):
    check_locked(day22, LOCKED)
