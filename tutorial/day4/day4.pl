:- module(day4, [parse_lines/2, parse_int_lines/2, parse_csv_ints/2]).

parse_lines(Raw, Lines) :-
    split_string(Raw, "\n", " \t\r", Split),
    exclude(=(""), Split, Lines).

parse_int_lines(Raw, Ints) :-
    parse_lines(Raw, Lines),
    maplist(number_string, Ints, Lines).

parse_csv_ints(Line, Ints) :-
    split_string(Line, ",", " \t\r", Pieces),
    exclude(=(""), Pieces, Clean),
    maplist(number_string, Ints, Clean).
