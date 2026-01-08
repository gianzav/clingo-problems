{choose(I)} :- item(I).

:- #sum{W,I : choose(I), weight(I,W)} > L, limit(L).
total_value(S) :- S = #sum{V,I : choose(I), value(I,V)}.

#maximize{S : total_value(S)}.

#show choose/1.
#show total_value/1.
