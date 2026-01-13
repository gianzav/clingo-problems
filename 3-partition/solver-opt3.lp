num_elements(X) :- X = #max{I : elem(I,_)}.

%% if the number of elements can't be divided by 3, then the instance is unsat
:- num_elements(X), X\3 != 0.

%% compute the exact numbers of partitions to be created
num_partitions(X/3) :- num_elements(X).
partition_id(1..N) :- num_partitions(N).

%% target is the value that each sum should have
target(S/N) :- num_partitions(N), S = #sum{X,I : elem(I,X)}.
%% target should be integer
:- num_partitions(N), S = #sum{X,I : elem(I,X)}, S\N != 0.

%%% partition(Partition Id, Element number {1,2,3}, Element Id))
%% Assign the first element to the first partition
partition(1,1,1).
%% Guess the first element of a partition only if the previous partition is full
{partition(Id,1,Eid) : elem(Eid,_)} = 1 :- partition_id(Id), partition(Id-1,3,_).
%% assign elements in a partition in order
{partition(Id,2,Eid) : elem(Eid,_)} = 1 :- partition(Id,1,_).
{partition(Id,3,Eid) : elem(Eid,_)} = 1 :- partition(Id,2,_).

%% elements in a partition are ordered
:- partition(Id,I,X), partition(Id,J,Y), I<J, X>Y.

%% an elemet can't be put in two different partitions
:- partition(I1,_,Eid), partition(I2,_,Eid), I1 < I2.

%% no two elements in the same partition have the same id
:- partition(Id,X,A), partition(Id,X,B), A<B.

%% the same element can't be put two times in the same partition
:- partition(Id,X,A), partition(Id,Y,A), X<Y.

%% there is no element which is not put in a partition
chosen(1).
chosen(Eid) :- partition(_,_,Eid), chosen(Eid-1).
:- elem(Eid,_), not chosen(Eid).

% The sum of the elements of each partition must be the same
partition_sum(Id, S) :- S = #sum{X,Eid : partition(Id,_,Eid), elem(Eid,X)}, partition_id(Id).

:- partition_sum(I, S), partition_id(I), S != T, target(T).

#show partition/3.
