:- module(day12, [parse_input/2, part1/2, part2/2, solve/3,
                  navigate/3, quarter_turns/3, rotate/5, manhattan/3]).

% Day 12: Rain Risk.
% A list of single-letter actions with integer values, run as a tiny
% turtle machine. The ship ends somewhere; report its Manhattan distance
% from the origin.
%
% The two parts look different in the statement and are the same machine.
% Carry a ship position (X, Y) and one vector (VX, VY), and read the
% actions like this:
%   F moves the ship along the vector, V times      -- both parts;
%   L/R rotate the vector about the origin          -- both parts;
%   N/S/E/W translate *the ship* (part 1) or *the vector* (part 2).
% Part 1's "facing" is just a unit vector starting at east, so the only
% real difference between the parts is which of the two points N/S/E/W
% pushes. That is one argument, Mode, threaded through step/4.
%
% Coordinates are (east, north): +X east, +Y north. Everything stays in
% integers -- see rotate/5 for why no trigonometry is needed.

% ---------------------------------------------------------------------------
% Parsing
% ---------------------------------------------------------------------------

% parse_input(+Raw, -Instructions)
% Instructions is a list of Action-Value pairs, Action one of the char
% atoms 'N','S','E','W','L','R','F'. Same Op-Arg shape day08 used for
% the handheld's program.
parse_input(Raw, Instructions) :-
    split_string(Raw, "\n", " \t\r", Lines0),
    exclude(=(""), Lines0, Lines),
    maplist(parse_instruction, Lines, Instructions).

% parse_instruction(+Line, -Instruction)
% Every line is one letter followed by a decimal number, so the split is
% positional: sub_string/5 twice, no DCG needed.
parse_instruction(Line, Action-Value) :-
    sub_string(Line, 0, 1, _, ActionS),
    atom_string(Action, ActionS),
    sub_string(Line, 1, _, 0, ValueS),
    number_string(Value, ValueS).

% ---------------------------------------------------------------------------
% The action table
% ---------------------------------------------------------------------------

% cardinal(?Action, ?DX, ?DY)
% The four absolute headings as unit steps. Note 'E' is 1-0, which is
% also part 1's starting facing -- the statement's "the ship starts by
% facing east" and its E action are the same vector.
cardinal('N',  0,  1).
cardinal('S',  0, -1).
cardinal('E',  1,  0).
cardinal('W', -1,  0).

% quarter_turns(+Action, +Degrees, -Quarters)
% Normalise both turn directions to clockwise quarter turns, so there is
% one rotation primitive instead of two. L D is R (360-D), and turning
% four quarters is turning none, hence the mod 4. SWI's mod/2 takes the
% sign of its divisor, so the negated left turns come back in 0..3.
% The multiple-of-90 check is a guard, not decoration: without it a
% stray L45 would silently truncate to no turn at all.
quarter_turns('R', Degrees, Quarters) :-
    Degrees mod 90 =:= 0,
    Quarters is (Degrees // 90) mod 4.
quarter_turns('L', Degrees, Quarters) :-
    Degrees mod 90 =:= 0,
    Quarters is -(Degrees // 90) mod 4.

% rotate(+Quarters, +VX, +VY, -VX1, -VY1)
% Rotate a vector clockwise by Quarters right angles about the origin.
%
% In (east, north) coordinates one right turn sends (x, y) to (y, -x).
% That is multiplication of the Gaussian integer x + yi by -i, so all
% four turns are sign swaps and coordinate swaps: exact integer work,
% no sin/cos, no rounding, and nothing to get wrong at 180 degrees.
% Four facts rather than repeated application keeps the clause set
% first-argument indexed and the call deterministic.
rotate(0, VX, VY, VX1, VY1) :-
    VX1 = VX,
    VY1 = VY.
rotate(1, VX, VY, VX1, VY1) :-
    VX1 = VY,
    VY1 is -VX.
rotate(2, VX, VY, VX1, VY1) :-
    VX1 is -VX,
    VY1 is -VY.
rotate(3, VX, VY, VX1, VY1) :-
    VX1 is -VY,
    VY1 = VX.

% ---------------------------------------------------------------------------
% The machine
% ---------------------------------------------------------------------------
%
% State is nav(X, Y, VX, VY): ship position, then the vector each part
% interprets its own way (part 1's heading, part 2's waypoint offset).

% start_state(+Mode, -State)
% Part 1 starts facing east; part 2's waypoint starts 10 east, 1 north.
start_state(ship,     nav(0, 0,  1, 0)).
start_state(waypoint, nav(0, 0, 10, 1)).

% navigate(+Mode, +Instructions, -Distance)
% Run the whole program and measure the ship. foldl/4 is the fold over
% instructions; the state term is the accumulator.
navigate(Mode, Instructions, Distance) :-
    start_state(Mode, State0),
    foldl(step(Mode), Instructions, State0, State),
    State = nav(X, Y, _VX, _VY),
    manhattan(X, Y, Distance).

% step(+Mode, +Instruction, +State0, -State)
% One instruction. Three clauses, one per action family; outputs are
% unified after the cut so a pre-bound State cannot skip a clause the
% guard already committed to.
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

% translate(+Mode, +EX, +EY, +State0, -State)
% Where a cardinal move lands. This predicate *is* the difference
% between the two parts: part 1 shoves the ship and leaves the heading
% alone, part 2 shoves the waypoint and leaves the ship alone. Indexed
% on Mode, so no cut is needed to keep it deterministic.
translate(ship, EX, EY, nav(X, Y, VX, VY), State) :-
    X1 is X + EX,
    Y1 is Y + EY,
    State = nav(X1, Y1, VX, VY).
translate(waypoint, EX, EY, nav(X, Y, VX, VY), State) :-
    VX1 is VX + EX,
    VY1 is VY + EY,
    State = nav(X, Y, VX1, VY1).

% manhattan(+X, +Y, -Distance)
manhattan(X, Y, Distance) :-
    Distance is abs(X) + abs(Y).

% ---------------------------------------------------------------------------
% Parts
% ---------------------------------------------------------------------------

% part1(+Instructions, -Distance)
part1(Instructions, Distance) :-
    navigate(ship, Instructions, Distance).

% part2(+Instructions, -Distance)
part2(Instructions, Distance) :-
    navigate(waypoint, Instructions, Distance).

% solve(+Raw, -Part1, -Part2)
solve(Raw, Part1, Part2) :-
    parse_input(Raw, Instructions),
    part1(Instructions, Part1),
    part2(Instructions, Part2).
