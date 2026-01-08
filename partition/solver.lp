%% s1(Id,X) means that element with id=Id and value=X is included in subset 1.
%% The same applies to s2
1{s1(Id, X); s2(Id,X)}1 :- elem(Id,X).

%% the sum of the elements in the two partitions must be the same
:- #sum{X,Idx : s1(Idx,X)} != S, S = #sum{Y,Idy : s2(Idy,Y)}.

#show s1/2.
#show s2/2.
