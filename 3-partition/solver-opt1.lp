num_elements(X) :- X = #max{I : elem(I,_)}.

%% if the number of elements can't be divided by 3, then the instance is unsat
:- num_elements(X), X\3 != 0.

%% compute the exact numbers of partitions to be created
num_partitions(X/3) :- num_elements(X).
partition_id(1..N) :- num_partitions(N).

%%% partition(Partition Id, Element number {1,2,3}, Element Id))
%% Assign the first element to the first partition
partition(1,1,1).
%% Guess the first element of a partition only if the previous partition is full
{partition(Id,1,Eid) : elem(Eid,_)} = 1 :- partition_id(Id), partition(Id-1,3,_).
%% assign elements in a partition in order
{partition(Id,2,Eid) : elem(Eid,_)} = 1 :- partition(Id,1,_).
{partition(Id,3,Eid) : elem(Eid,_)} = 1 :- partition(Id,2,_).

%% an elemet can't be put in two different partitions
:- partition(I1,_,Eid), partition(I2,_,Eid), I1 < I2.

%% no two elements in the same partition have the same id
:- partition(Id,X,A), partition(Id,X,B), A<B.

%% there is no element which is not put in a partition
chosen(1).
chosen(Eid) :- partition(_,_,Eid), chosen(Eid-1).
:- elem(Eid,_), not chosen(Eid).

% The sum of the elements of each partition must be the same
partition_sum(Id, S) :- S = #sum{X,Eid : partition(Id,_,Eid), elem(Eid,X)}, partition_id(Id).
:- partition_sum(I,S1), partition_sum(J,S2), I<J, S1 != S2.

#show partition/3.
