bin(1..X) :- num_bins(X).

%% each item is assigned to a bin
{assign(I,B)} :- item(I), bin(B).

%% an item is assigned to only one bin (the bins are disjoint)
:- assign(I,B1), assign(I,B2), B1<B2.

%% an item must be assigned to at least one bin
:- item(I), not assign(I,_).

bin_content_size(B,S) :- bin(B), S = #sum{Size,I : assign(I,B), size(I,Size)}.

%% the sum of the sizes of the elements in the bins must be <= the bin capacity
:- bin(B), bin_content_size(B, S), bin_capacity(C), S > C.

%% minimize the number of bins
bins_unused(X) :- X = #count{B : bin(B), bin_content_size(B, 0)}.
#maximize{X : bins_unused(X)}.

#show assign/2.
#show bin_content_size/2.
