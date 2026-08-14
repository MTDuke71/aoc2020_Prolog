"""Day 8: Handheld Halting.

The puzzle input is a program for a tiny accumulator machine (opcodes acc /
jmp / nop), so the solution is an interpreter.  Parse into an indexed list
of (op, arg), then run a fetch/decode/execute loop carrying a "seen" set of
program counters.

  - part1: run the boot code, which loops forever, and report the
    accumulator at the instant control is about to repeat an instruction,
  - part2: flip one jmp<->nop at a time until the program halts (the PC
    steps to exactly len(program)), and report the halting accumulator.

Re-confirms part1=1331 / part2=1121.
"""

from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day08.txt"


def parse_input(raw: str) -> list[tuple[str, int]]:
    program = []
    for line in raw.strip().splitlines():
        op, arg = line.split()
        program.append((op, int(arg)))
    return program


def run(program: list[tuple[str, int]]) -> tuple[bool, int]:
    """Return (halted, acc): halted is True if PC ran off the end, False if
    control revisited an instruction (an infinite loop)."""
    seen: set[int] = set()
    pc = 0
    acc = 0
    n = len(program)
    while pc != n:
        if pc in seen:
            return (False, acc)  # about to repeat an instruction
        seen.add(pc)
        op, arg = program[pc]
        if op == "acc":
            acc += arg
            pc += 1
        elif op == "jmp":
            pc += arg
        else:  # nop
            pc += 1
    return (True, acc)  # PC == n: stepped off the end


def part1(program: list[tuple[str, int]]) -> int:
    _halted, acc = run(program)
    return acc


def part2(program: list[tuple[str, int]]) -> int:
    flip = {"jmp": "nop", "nop": "jmp"}
    for i, (op, arg) in enumerate(program):
        if op not in flip:
            continue  # no acc instructions were harmed
        patched = program[:i] + [(flip[op], arg)] + program[i + 1 :]
        halted, acc = run(patched)
        if halted:
            return acc
    raise ValueError("no single jmp/nop flip terminates the program")


def solve(raw: str) -> tuple[int, int]:
    program = parse_input(raw)
    return part1(program), part2(program)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
