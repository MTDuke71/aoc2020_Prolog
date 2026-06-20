:- module(day8, [freq_assoc/2, freq_dict/2]).
:- use_module(library(assoc)).

freq_assoc(List, AssocOut) :-
    empty_assoc(A0),
    freq_assoc_(List, A0, AssocOut).

freq_assoc_([], A, A).
freq_assoc_([X|Xs], A0, AOut) :-
    ( get_assoc(X, A0, N0) -> N1 is N0 + 1 ; N1 = 1 ),
    put_assoc(X, A0, N1, A1),
    freq_assoc_(Xs, A1, AOut).

freq_dict(List, Dict) :-
    freq_dict_(List, _{}, Dict).

freq_dict_([], D, D).
freq_dict_([X|Xs], D0, DOut) :-
    ( get_dict(X, D0, N0) -> N1 is N0 + 1 ; N1 = 1 ),
    D1 = D0.put(X, N1),
    freq_dict_(Xs, D1, DOut).
