:- module(day04, [parse_input/2, part1/2, part2/2, solve/3,
                  has_required_fields/1, valid_passport/1, valid_field/1]).

:- use_module(library(dcg/basics)).

% Day 4: Passport Processing.
% The batch file holds passports separated by blank lines; each passport
% is key:value fields separated by spaces or newlines. Part 1: count
% passports carrying all seven required fields (cid is optional).
% Part 2: additionally require every field's value to pass its
% validation rule.

% parse_input(+Raw, -Passports)
% Passports is a list of passports, each a list of Key-Value pairs
% (Key an atom like byr, Value a string). Blank lines separate passports.
parse_input(Raw, Passports) :-
    split_string(Raw, "\n", " \t\r", Lines),
    blocks(Lines, Blocks),
    maplist(block_passport, Blocks, Passports).

% blocks(+Lines, -Blocks)
% Group consecutive non-blank Lines into Blocks; blank lines separate
% blocks and never appear in one.
blocks([], []).
blocks([""|Rest], Blocks) :- !,
    blocks(Rest, Blocks).
blocks([Line|Rest], [[Line|More]|Blocks]) :-
    block_rest(Rest, More, Tail),
    blocks(Tail, Blocks).

% block_rest(+Lines, -More, -Tail)
% More is the non-blank prefix of Lines; Tail is everything after the
% blank line (or []) that ended it.
block_rest([], [], []).
block_rest([""|Rest], [], Rest) :- !.
block_rest([Line|Rest], [Line|More], Tail) :-
    block_rest(Rest, More, Tail).

% block_passport(+Lines, -Passport)
% One passport's lines become a list of Key-Value fields: join the
% lines with spaces, split into tokens, split each token at the colon.
block_passport(Lines, Passport) :-
    atomic_list_concat(Lines, ' ', Joined),
    split_string(Joined, " ", "", Tokens0),
    exclude(=(""), Tokens0, Tokens),
    maplist(token_field, Tokens, Passport).

token_field(Token, Key-Value) :-
    split_string(Token, ":", "", [KeyS, Value]),
    atom_string(Key, KeyS).

% has_required_fields(+Passport)
% Part-1 validity: all seven required keys present. cid is deliberately
% absent from the list — it is optional.
has_required_fields(Passport) :-
    forall(member(Key, [byr, iyr, eyr, hgt, hcl, ecl, pid]),
           memberchk(Key-_, Passport)).

% valid_passport(+Passport)
% Part-2 validity: all required fields present and every field's value
% passes its rule.
valid_passport(Passport) :-
    has_required_fields(Passport),
    forall(member(Field, Passport), valid_field(Field)).

% valid_field(+Key-Value)
% The statement's validation table, one clause per field kind.
valid_field(byr-V) :- year_range(V, 1920, 2002).
valid_field(iyr-V) :- year_range(V, 2010, 2020).
valid_field(eyr-V) :- year_range(V, 2020, 2030).
valid_field(hgt-V) :-
    string_codes(V, Codes),
    once(phrase(height(H, Unit), Codes)),
    (   Unit == cm
    ->  between(150, 193, H)
    ;   between(59, 76, H)
    ).
valid_field(hcl-V) :-
    string_codes(V, [0'#|Hex]),
    length(Hex, 6),
    maplist(hex_lower, Hex).
valid_field(ecl-V) :-
    memberchk(V, ["amb", "blu", "brn", "gry", "grn", "hzl", "oth"]).
valid_field(pid-V) :-
    string_codes(V, Codes),
    length(Codes, 9),
    maplist(digit_code, Codes).
valid_field(cid-_).

% year_range(+Value, +Lo, +Hi)
% Value is exactly four digits whose number lies in Lo..Hi.
year_range(Value, Lo, Hi) :-
    string_codes(Value, Codes),
    length(Codes, 4),
    maplist(digit_code, Codes),
    number_codes(Year, Codes),
    between(Lo, Hi, Year).

% height(-H, -Unit)//
% A height value is an integer directly followed by its unit.
height(H, cm) --> integer(H), "cm".
height(H, in) --> integer(H), "in".

digit_code(C) :- code_type(C, digit).

% hex_lower(+Code)
% A lowercase hex digit: 0-9 or a-f.
hex_lower(C) :- code_type(C, digit), !.
hex_lower(C) :- between(0'a, 0'f, C).

% part1(+Passports, -Answer)
part1(Passports, Answer) :-
    include(has_required_fields, Passports, Valid),
    length(Valid, Answer).

% part2(+Passports, -Answer)
part2(Passports, Answer) :-
    include(valid_passport, Passports, Valid),
    length(Valid, Answer).

% solve(+Raw, -Part1, -Part2)
solve(Raw, Part1, Part2) :-
    parse_input(Raw, Passports),
    part1(Passports, Part1),
    part2(Passports, Part2).
