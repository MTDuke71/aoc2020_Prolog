"""Day 12: Rain Risk.

A list of single-letter actions with integer values, run as a tiny turtle
machine.  The two parts read differently in the statement but are the same
machine: carry a ship position and one vector, where

  F   moves the ship along the vector, `value` times   -- both parts;
  L/R rotate the vector about the origin               -- both parts;
  NSEW translate *the ship* (part 1) or *the vector* (part 2).

Part 1's "facing" is a unit vector starting at east, so the only real
difference is which point the cardinal moves push.  That is the `mode`
argument.

Coordinates are (east, north).  Rotation is exact integer arithmetic: one
clockwise right angle sends (x, y) to (y, -x), i.e. multiplication of the
Gaussian integer x + yi by -i.  No trigonometry, no rounding.
"""

from pathlib import Path

CARDINALS = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}

START = {"ship": (0, 0, 1, 0), "waypoint": (0, 0, 10, 1)}

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day12.txt"


def parse_input(raw: str) -> list[tuple[str, int]]:
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    return [(line[0], int(line[1:])) for line in lines]


def quarter_turns(action: str, degrees: int) -> int:
    # Normalise both turn directions to clockwise quarter turns; L d == R (360-d).
    assert degrees % 90 == 0, f"turn is not a multiple of 90 degrees: {action}{degrees}"
    turns = degrees // 90
    return (turns if action == "R" else -turns) % 4


def rotate(turns: int, vx: int, vy: int) -> tuple[int, int]:
    for _ in range(turns):
        vx, vy = vy, -vx
    return vx, vy


def navigate(mode: str, instructions: list[tuple[str, int]]) -> int:
    x, y, vx, vy = START[mode]
    for action, value in instructions:
        if action in CARDINALS:
            dx, dy = CARDINALS[action]
            if mode == "ship":
                x, y = x + dx * value, y + dy * value
            else:
                vx, vy = vx + dx * value, vy + dy * value
        elif action == "F":
            x, y = x + vx * value, y + vy * value
        else:
            vx, vy = rotate(quarter_turns(action, value), vx, vy)
    return abs(x) + abs(y)


def part1(instructions: list[tuple[str, int]]) -> int:
    return navigate("ship", instructions)


def part2(instructions: list[tuple[str, int]]) -> int:
    return navigate("waypoint", instructions)


def solve(raw: str) -> tuple[int, int]:
    instructions = parse_input(raw)
    return part1(instructions), part2(instructions)


def main() -> None:
    p1, p2 = solve(INPUT.read_text())
    print(f"part1={p1} part2={p2}")


if __name__ == "__main__":
    raise SystemExit(main())
