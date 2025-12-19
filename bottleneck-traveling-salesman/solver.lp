%%% Solution based on the TSP encoding in the Potassco guide

% edges are undirected
edge(X,Y,W) :- edge(Y,X,W).

vertex(X) :- edge(X,_,_).
vertex(X) :- edge(_,X,_).

{cycle(X,Y) : edge(X,Y,_)} = 1 :- vertex(X).
{cycle(X,Y) : edge(X,Y,_)} = 1 :- vertex(Y).

reached(Y) :- cycle(1,Y).
reached(Y) :- cycle(X,Y), reached(X).

:- vertex(Y), not reached(Y).

max_weight(C) :- C = #max{W,X,Y : cycle(X,Y), edge(X,Y,W)}.

#minimize{X : max_weight(X)}.
#show cycle/2.
