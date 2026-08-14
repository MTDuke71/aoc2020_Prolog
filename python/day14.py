"""Day 14: Docking Data.

An emulator for a 36-bit machine whose only instructions are "load a mask"
and "store a value".  Both parts run the same program with the same masks
and differ only in what a mask *means*:

  part 1 -- the mask rewrites the **value**.  0 and 1 overwrite that bit,
            X leaves it alone.
  part 2 -- the mask rewrites the **address**.  0 leaves it alone, 1
            overwrites with 1, and X is *floating*: the write lands at
            every address obtained by setting those bits both ways.

So part 1 is one masked write per instruction and part 2 is 2**k writes,
where k is the number of X bits in the current mask.

Neither part builds 2**36 words of memory.  Addresses are sparse -- the
real program touches a few hundred thousand at most -- so memory is a dict
and the answer is the sum of its values.  "The entire address space begins
at 0" costs nothing when absent keys are simply not in the dict.

Bit mechanics, part 1:

    ones  = mask with X -> 0     value | ones   forces every 1 bit on
    zeros = mask with X -> 1     value & zeros  forces every 0 bit off

    X positions are 0 in `ones` and 1 in `zeros`, so they survive both
    operations untouched.  That is the whole of part 1: two integers
    precomputed per mask, then one OR and one AND per write.

Bit mechanics, part 2:

    The floating bits are cleared from the address and then re-set from
    every subset of them.  Enumerating subsets by counting 0..2**k-1 and
    scattering those k counter bits out to the k floating positions is
    what `floating_addresses` does -- no string building, no recursion.

Python integers are arbitrary precision, so 36-bit values need no special
handling and the final sum is not truncated (the statement is explicit
about that).
"""

import re
from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day14.txt"

MASK_WIDTH = 36

MEM = re.compile(r"mem\[(\d+)\] = (\d+)")


def parse_input(raw: str) -> list[tuple[str, list[tuple[int, int]]]]:
    """Parse into [(mask, [(address, value), ...]), ...].

    A mask stays in force until the next mask line, so the program is really
    a sequence of blocks rather than a flat instruction list.  Grouping the
    writes under the mask that governs them is the parse; both parts then
    iterate blocks without tracking any current-mask state of their own.

    The mask is left as its 36-character string.  Decoding it into integers
    is part-specific -- part 1 wants two masks, part 2 wants a bit list --
    so doing it here would just mean doing the wrong one.
    """
    blocks: list[tuple[str, list[tuple[int, int]]]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("mask"):
            mask = line.split(" = ")[1]
            if len(mask) != MASK_WIDTH:
                raise ValueError(f"mask is not {MASK_WIDTH} bits: {mask!r}")
            blocks.append((mask, []))
            continue
        m = MEM.fullmatch(line)
        if m is None:
            raise ValueError(f"bad line: {line!r}")
        if not blocks:
            raise ValueError("a write appeared before any mask was set")
        blocks[-1][1].append((int(m.group(1)), int(m.group(2))))
    return blocks


def value_masks(mask: str) -> tuple[int, int]:
    """Part 1's (ones, zeros) pair: OR with the first, AND with the second."""
    return int(mask.replace("X", "0"), 2), int(mask.replace("X", "1"), 2)


def floating_bits(mask: str) -> list[int]:
    """Bit positions of the X entries, counting from the least significant."""
    return [i for i, c in enumerate(reversed(mask)) if c == "X"]


def floating_addresses(address: int, mask: str) -> list[int]:
    """Every address a part-2 write to `address` under `mask` lands on.

    1 bits are forced on, 0 bits are left alone, and the X bits are first
    cleared and then re-set from each of the 2**k subsets.  The subsets are
    enumerated by counting: bit j of the counter selects the j-th floating
    position, so counter 0..2**k-1 scatters out to every combination exactly
    once.
    """
    ones = int(mask.replace("X", "0"), 2)
    floats = floating_bits(mask)

    base = address | ones
    for bit in floats:
        base &= ~(1 << bit)

    addresses = []
    for counter in range(1 << len(floats)):
        candidate = base
        for j, bit in enumerate(floats):
            if counter >> j & 1:
                candidate |= 1 << bit
        addresses.append(candidate)
    return addresses


def part1(blocks: list[tuple[str, list[tuple[int, int]]]]) -> int:
    memory: dict[int, int] = {}
    for mask, writes in blocks:
        ones, zeros = value_masks(mask)
        for address, value in writes:
            memory[address] = value & zeros | ones
    return sum(memory.values())


def part2(blocks: list[tuple[str, list[tuple[int, int]]]]) -> int:
    memory: dict[int, int] = {}
    for mask, writes in blocks:
        for address, value in writes:
            for target in floating_addresses(address, mask):
                memory[target] = value
    return sum(memory.values())


def solve(raw: str) -> tuple[int, int]:
    blocks = parse_input(raw)
    return part1(blocks), part2(blocks)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
