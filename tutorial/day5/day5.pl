:- module(day5, [sum_acc/2, reverse_acc/2]).

sum_acc(List, Sum) :-
    sum_acc_(List, 0, Sum).

sum_acc_([], Acc, Acc).
sum_acc_([X|T], Acc, Sum) :-
    Acc1 is Acc + X,
    sum_acc_(T, Acc1, Sum).

reverse_acc(List, Rev) :-
    reverse_acc_(List, [], Rev).

reverse_acc_([], Acc, Acc).
reverse_acc_([X|T], Acc, Rev) :-
    reverse_acc_(T, [X|Acc], Rev).
