:- module(day6, [edge/2, path/3]).

edge(a, b).
edge(b, c).
edge(c, d).
edge(a, e).
edge(e, d).
edge(c, a). % cycle

path(Start, Goal, Path) :-
    path_(Start, Goal, [Start], Rev),
    reverse(Rev, Path).

path_(Goal, Goal, Visited, Visited).
path_(Node, Goal, Visited, Path) :-
    edge(Node, Next),
    \+ member(Next, Visited),
    path_(Next, Goal, [Next|Visited], Path).
