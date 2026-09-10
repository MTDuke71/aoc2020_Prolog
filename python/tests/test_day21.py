"""Day 21: Allergen Assessment."""

import shutil
import subprocess
from pathlib import Path

import pytest

import day21

LOCKED = (2072, "fdsfpg,jmvxx,lkv,cbzcgvc,kfgln,pqqks,pqrvc,lclnj")

# The statement's four foods.
SAMPLE = """\
mxmxvkd kfcds sqjhc nhms (contains dairy, fish)
trh fvjkl sbzzf mxmxvkd (contains dairy)
sqjhc fvjkl (contains soy)
sqjhc mxmxvkd sbzzf (contains fish)
"""

SAMPLE_CANDIDATES = {
    "dairy": {"mxmxvkd"},
    "fish": {"mxmxvkd", "sqjhc"},
    "soy": {"sqjhc", "fvjkl"},
}


def test_parse_input():
    assert day21.parse_input(SAMPLE) == [
        day21.Food(("mxmxvkd", "kfcds", "sqjhc", "nhms"), ("dairy", "fish")),
        day21.Food(("trh", "fvjkl", "sbzzf", "mxmxvkd"), ("dairy",)),
        day21.Food(("sqjhc", "fvjkl"), ("soy",)),
        day21.Food(("sqjhc", "mxmxvkd", "sbzzf"), ("fish",)),
    ]


def test_parse_food_with_no_allergens_listed():
    """The statement says a food lists "some or all" of its allergens, so a
    line with no "(contains ...)" at all is legal and carries none."""
    assert day21.parse_input("kfcds nhms\n") == [day21.Food(("kfcds", "nhms"), ())]


def test_crlf_input():
    """A Windows download ends every line in \r\n; the \r must not survive
    as part of the last allergen's name (`fish)\r`)."""
    assert day21.parse_input(SAMPLE.replace("\n", "\r\n")) == day21.parse_input(SAMPLE)


def test_candidates_example():
    """The intersection rule on the statement's foods: dairy is listed by
    foods 1 and 2, whose only common ingredient is mxmxvkd; fish by foods 1
    and 4; soy by food 3 alone, so both its ingredients stay possible."""
    assert day21.candidates(day21.parse_input(SAMPLE)) == SAMPLE_CANDIDATES


def test_unlabelled_food_is_not_evidence():
    """ "Allergens aren't always marked": a food that lists no allergen but
    does contain sqjhc must not strike sqjhc from fish or soy."""
    foods = day21.parse_input(SAMPLE + "sqjhc kfcds\n")
    assert day21.candidates(foods) == SAMPLE_CANDIDATES


def test_safe_ingredients_example():
    """The statement names them: kfcds, nhms, sbzzf and trh can hold nothing."""
    foods = day21.parse_input(SAMPLE)
    everything = {ingredient for food in foods for ingredient in food.ingredients}
    suspect = set().union(*day21.candidates(foods).values())
    assert everything - suspect == {"kfcds", "nhms", "sbzzf", "trh"}


def test_part1_example():
    """Once each, except sbzzf which appears twice."""
    assert day21.part1(day21.parse_input(SAMPLE)) == 5


def test_part1_counts_appearances_not_distinct_ingredients():
    """Another food repeating two safe ingredients adds two to the count."""
    assert day21.part1(day21.parse_input(SAMPLE + "trh kfcds\n")) == 7


def test_part1_does_not_need_the_allergens_resolved():
    """x and y both narrow to {a, b} and can never be told apart, but
    "cannot possibly hold an allergen" is still decidable: d is in no
    candidate set.  Part 2 on the same foods must refuse."""
    foods = day21.parse_input("a b d (contains x)\na b (contains x)\na b (contains y)\n")
    assert day21.part1(foods) == 1
    with pytest.raises(ValueError):
        day21.part2(foods)


def test_assign_example():
    assert day21.assign(SAMPLE_CANDIDATES) == {"dairy": "mxmxvkd", "fish": "sqjhc", "soy": "fvjkl"}


def test_assign_strikes_across_rounds():
    """Neither fish nor soy is forced on its own (two candidates each); the
    chain runs dairy -> fish -> soy, one strike per round."""
    assert day21.assign({"fish": {"mxmxvkd", "sqjhc"}, "soy": {"sqjhc", "fvjkl"}, "dairy": {"mxmxvkd"}}) == {
        "dairy": "mxmxvkd",
        "fish": "sqjhc",
        "soy": "fvjkl",
    }


def test_assign_refuses_to_guess():
    with pytest.raises(ValueError):
        day21.assign({"x": {"a", "b"}, "y": {"a", "b"}})


def test_assign_refuses_two_allergens_in_one_ingredient():
    """Each ingredient holds at most one allergen; sets that force two onto
    the same one contradict the statement and are reported, not returned."""
    with pytest.raises(ValueError):
        day21.assign({"x": {"a"}, "y": {"a"}})


def test_assign_of_nothing_is_nothing():
    assert day21.assign({}) == {}


def test_part2_example():
    assert day21.part2(day21.parse_input(SAMPLE)) == "mxmxvkd,sqjhc,fvjkl"


def test_part2_is_sorted_by_allergen_not_by_ingredient():
    """dairy < fish < soy puts fvjkl last even though it sorts first."""
    answer = day21.part2(day21.parse_input(SAMPLE))
    assert answer.split(",") != sorted(answer.split(","))
    assert " " not in answer


@pytest.fixture(scope="module")
def real(real_input):
    return day21.parse_input(real_input(21))


def test_real_input_shape(real):
    assert len(real) == 38
    assert all(food.allergens for food in real)
    assert len({ingredient for food in real for ingredient in food.ingredients}) == 200
    assert len(day21.candidates(real)) == 8


def test_real_candidates_are_not_a_staircase_but_still_resolve(real):
    """Unlike day 16 the sets are not nested by size -- two allergens start
    at four candidates -- yet each round of striking forces at least one,
    and the whole thing settles in six rounds."""
    possible = day21.candidates(real)
    assert sorted(len(options) for options in possible.values()) == [1, 2, 2, 2, 3, 3, 4, 4]
    assert len(day21.assign(possible)) == 8


def test_real_every_suspect_ingredient_holds_an_allergen(real):
    """The identity the two parts share: the union of the candidate sets
    (what part 1 excludes) is exactly the set of holders part 2 finds, so
    part 1 is the total appearances minus the holders' appearances."""
    suspect = set().union(*day21.candidates(real).values())
    holders = set(day21.assign(day21.candidates(real)).values())
    assert suspect == holders
    appearances = sum(len(food.ingredients) for food in real)
    held = sum(ingredient in holders for food in real for ingredient in food.ingredients)
    assert day21.part1(real) == appearances - held


def test_real_input_locked(check_locked):
    check_locked(day21, LOCKED)


# ---- the Prolog companion, prolog/day21.pl -------------------------------
# Same puzzle with part 2 as a three-clause backtracking search instead of
# singleton peeling.  Run through swipl when one is on PATH; skipped otherwise
# so a machine without SWI-Prolog stays green.

PROLOG = Path(__file__).resolve().parents[2] / "prolog" / "day21.pl"


@pytest.fixture(scope="module")
def prolog():
    swipl = shutil.which("swipl")
    if swipl is None:
        pytest.skip("no swipl on PATH")

    def run(path: Path) -> tuple[int, str]:
        out = subprocess.run([swipl, str(PROLOG), str(path)], capture_output=True, text=True, check=True)
        p1, p2 = out.stdout.split()
        return int(p1.removeprefix("part1=")), p2.removeprefix("part2=")

    return run


def test_prolog_companion_example(prolog, tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text(SAMPLE)
    assert prolog(sample) == (5, "mxmxvkd,sqjhc,fvjkl")


def test_prolog_companion_crlf(prolog, tmp_path):
    sample = tmp_path / "sample_crlf.txt"
    sample.write_bytes(SAMPLE.replace("\n", "\r\n").encode())
    assert prolog(sample) == (5, "mxmxvkd,sqjhc,fvjkl")


def test_prolog_companion_agrees_on_the_real_input(prolog, real_input):
    real_input(21)  # skip alongside the other real-input tests when the file is absent
    assert prolog(day21.INPUT) == day21.solve(day21.INPUT.read_text())
