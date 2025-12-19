#const n=10.
%% there could be up to 'n' partitions
partition_id(1..n).

%% each element can be put in each partition
{partition(I,P,E)} :- partition_id(I), elem(P,E).

%% an elemet can't be put in two different partitions
:- partition(I1,P,E), partition(I2,P,E), I1 < I2.

%% there is no element which is not put in a partition
chosen(P,E) :- partition(_,P,E).
:- elem(P,E), not chosen(P,E).

% each partition must contain exactly three elements
:- X = #count{P,E : partition(I, P, E)}, X > 0, X != 3, partition_id(I).

% The sum of the elements of each partition must be the same
:- S1 = #sum{E1,P1 : partition(I, P1, E1)}, 
   S2 = #sum{E2,P2 : partition(J, P2, E2)}, 
   partition_id(I), partition_id(J), I < J, S1 != S2, S1 > 0, S2 > 0.

#show partition/3.
