%% assign(Facility, Location)
1{assign(F, L) : location(L)}1 :- facility(F).

%% all facilities to different locations
:- assign(F1, L), assign(F2, L), F1 < F2.

%% minimize the sum of distances multiplied by the corresponding flows
obj(S) :- S = #sum{Flow*Dist,F1,F2 : assign(F1,L1), assign(F2,L2), distance(L1,L2, Dist), flow(F1,F2,Flow)}.

#minimize{S : obj(S)}.

#show assign/2.
