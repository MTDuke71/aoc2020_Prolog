"""Day 13: Shuttle Search."""

import pytest

import day13

LOCKED = (102, 327300950120029)

EXAMPLE = "939\n7,13,x,x,59,x,31,19\n"


def schedule(bus_list):
    """Parse a bare bus list by pinning a dummy earliest-departure line.

    Part 2's extra examples give only the second line, so this supplies the
    first one the parser expects.
    """
    return day13.parse_input(f"0\n{bus_list}\n")


def test_parse_input_keeps_list_positions_as_offsets():
    """59 sits at index 4, not index 2: the x entries are dropped but counted."""
    assert day13.parse_input(EXAMPLE) == (939, [(0, 7), (1, 13), (4, 59), (6, 31), (7, 19)])


def test_parse_input_tolerates_an_all_x_tail():
    assert day13.parse_input("100\n3,x,x\n") == (100, [(0, 3)])


@pytest.mark.parametrize(
    ("bus", "wait"),
    [(7, 6), (13, 10), (59, 5), (31, 22), (19, 11)],
)
def test_wait_table_at_939(bus, wait):
    """The statement's worked waits: 938 and 945 bracket 939 for bus 7."""
    assert (-939) % bus == wait


def test_standing_on_a_departure_means_no_wait():
    """The mod must return 0 here, not a whole period."""
    assert (-945) % 7 == 0


@pytest.mark.parametrize("earliest", [0, 1, 939, 1000053])
@pytest.mark.parametrize("bus", [7, 13, 19, 523])
def test_floored_modulo_is_what_makes_this_work(earliest, bus):
    """The identity part 1 rests on, pinned rather than asserted in the docstring.

    The wait is computed as (-earliest) % bus with no correction step, which
    is sound only because Python's % is floored -- the result takes the sign
    of the divisor and lands in 0..bus-1.  C and Rust truncate instead and
    would return a negative here.  This checks both the range and that the
    resulting departure minute is genuinely a multiple of the bus ID.
    """
    wait = (-earliest) % bus
    assert 0 <= wait < bus
    assert (earliest + wait) % bus == 0


def test_part1_example():
    assert day13.part1(day13.parse_input(EXAMPLE)) == 295


def test_part1_picks_the_soonest_bus_not_the_smallest_product():
    """Bus 59 waits 5 and scores 295; bus 7 waits 6 and scores only 42.

    The selection has to be on the wait, so the smaller product is the wrong
    answer -- which is what makes min() over (wait, bus) pairs the point.
    """
    _earliest, buses = day13.parse_input(EXAMPLE)
    products = [bus * ((-939) % bus) for _offset, bus in buses]
    assert min(products) == 42
    assert day13.part1(day13.parse_input(EXAMPLE)) == 295


def test_part2_example():
    assert day13.part2(day13.parse_input(EXAMPLE)) == 1068781


@pytest.mark.parametrize(
    ("bus_list", "expected"),
    [
        ("17,x,13,19", 3417),
        ("67,7,59,61", 754018),
        ("67,x,7,59,61", 779210),
        ("67,7,x,59,61", 1261476),
        ("1789,37,47,1889", 1202161486),
    ],
)
def test_part2_extra_examples(bus_list, expected):
    """The four extra schedules the statement lists, plus the large one."""
    assert day13.part2(schedule(bus_list)) == expected


def test_offsets_matter():
    """These two differ only in where the x sits, which is the whole reason
    the parser carries offsets rather than a bare list of bus IDs."""
    assert day13.part2(schedule("67,x,7,59,61")) != day13.part2(schedule("67,7,x,59,61"))


def test_the_answer_satisfies_every_congruence():
    """What the number means: each bus departs at exactly t + its own offset."""
    _earliest, buses = day13.parse_input(EXAMPLE)
    t = day13.part2((0, buses))
    assert all((t + offset) % bus == 0 for offset, bus in buses)


def test_the_answer_is_the_earliest_such_minute():
    """Brute force finds nothing below it.  Only viable on the example --
    the real answer is around 3.3e14, which is why part 2 is a CRT sieve
    and not a search."""
    _earliest, buses = day13.parse_input(EXAMPLE)
    t = day13.part2((0, buses))
    assert not any(all((candidate + offset) % bus == 0 for offset, bus in buses) for candidate in range(t))


def test_a_single_bus_at_offset_zero_is_solved_by_zero():
    """The degenerate case the fold starts from."""
    assert day13.part2(schedule("13")) == 0


def test_crt_is_order_independent():
    """CRT solutions are unique modulo the product of the IDs, so folding the
    same congruences backwards must land on the same timestamp."""
    _earliest, buses = day13.parse_input(EXAMPLE)
    assert day13.part2((0, buses)) == day13.part2((0, list(reversed(buses))))


def test_crlf_input():
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day13.parse_input(crlf) == day13.parse_input(EXAMPLE)
    assert day13.solve(crlf) == (295, 1068781)


def test_real_input_locked(check_locked):
    check_locked(day13, LOCKED)
