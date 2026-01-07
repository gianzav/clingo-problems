%% choose at least one element
1{choose(Id,X) : dom(Id, X)}.

%% the sum of the chosen elements must sum to the target
:- #sum{X,Id : choose(Id,X)} != T, target(T).

#show choose/2.
