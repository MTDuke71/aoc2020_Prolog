:- begin_tests(day04).

:- use_module('../src/day04.pl').

% --- Puzzle example (part 1 statement) ---

example_input("\
ecl:gry pid:860033327 eyr:2020 hcl:#fffffd
byr:1937 iyr:2017 cid:147 hgt:183cm

iyr:2013 ecl:amb cid:350 eyr:2023 pid:028048884
hcl:#cfa07d byr:1929

hcl:#ae17e1 iyr:2013
eyr:2024
ecl:brn pid:760753108 byr:1931
hgt:179cm

hcl:#cfa07d eyr:2025 pid:166559648
iyr:2011 ecl:brn hgt:59in
").

test(parse_input) :-
    parse_input("a:1 b:2\nc:3\n\nd:4\n", Passports),
    assertion(Passports == [[a-"1", b-"2", c-"3"], [d-"4"]]).

test(part1_example) :-
    example_input(Raw),
    parse_input(Raw, Passports),
    part1(Passports, P1),
    assertion(P1 == 2).

% --- Field validation table (part 2 statement's worked values) ---

test(field_valid, [forall(member(Field, [byr-"2002",
                                         hgt-"60in", hgt-"190cm",
                                         hcl-"#123abc",
                                         ecl-"brn",
                                         pid-"000000001"]))]) :-
    valid_field(Field).

test(field_invalid, [forall(member(Field, [byr-"2003",
                                           hgt-"190in", hgt-"190",
                                           hcl-"#123abz", hcl-"123abc",
                                           ecl-"wat",
                                           pid-"0123456789"]))]) :-
    \+ valid_field(Field).

% --- Whole-passport validation (part 2 statement's batches) ---

invalid_passports("\
eyr:1972 cid:100
hcl:#18171d ecl:amb hgt:170 pid:186cm iyr:2018 byr:1926

iyr:2019
hcl:#602927 eyr:1967 hgt:170cm
ecl:grn pid:012533040 byr:1946

hcl:dab227 iyr:2012
ecl:brn hgt:182cm pid:021572410 eyr:2020 byr:1992 cid:277

hgt:59cm ecl:zzz
eyr:2038 hcl:74454a iyr:2023
pid:3556412378 byr:2007
").

valid_passports("\
pid:087499704 hgt:74in ecl:grn iyr:2012 eyr:2030 byr:1980
hcl:#623a2f

eyr:2029 ecl:blu cid:129 byr:1989
iyr:2014 pid:896056539 hcl:#a97842 hgt:165cm

hcl:#888785
hgt:164cm byr:2001 iyr:2015 cid:88
pid:545766238 ecl:hzl
eyr:2022

iyr:2010 hgt:158cm hcl:#b6652a ecl:blu byr:1944 eyr:2021 pid:093154719
").

test(invalid_passports_rejected) :-
    invalid_passports(Raw),
    parse_input(Raw, Passports),
    length(Passports, 4),
    part2(Passports, P2),
    assertion(P2 == 0).

test(valid_passports_accepted) :-
    valid_passports(Raw),
    parse_input(Raw, Passports),
    length(Passports, 4),
    part2(Passports, P2),
    assertion(P2 == 4).

% --- Real-input answer locks ---

real_input(Raw) :-
    read_file_to_string('inputs/day04.txt', Raw, []).

test(part1_real) :-
    real_input(Raw),
    solve(Raw, P1, _),
    assertion(P1 == 250).

test(part2_real) :-
    real_input(Raw),
    solve(Raw, _, P2),
    assertion(P2 == 158).

:- end_tests(day04).
