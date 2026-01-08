%% select a subset of x * y * z
{triple(elem(x,Idx,X), elem(y,Idy,Y), elem(z,Idz,Z))} :- elem(x,Idx,X), elem(y,Idy,Y), elem(z,Idz,Z).

%% each element must be chosen to be part of a triple
chosen(Set, Id, Elem) :- triple(elem(Set,Id,Elem),_,_).
chosen(Set, Id, Elem) :- triple(_,elem(Set,Id,Elem),_).
chosen(Set, Id, Elem) :- triple(_,_,elem(Set,Id,Elem)).

:- not chosen(Set,Id,Elem), elem(Set,Id,Elem).

%% the elements of each triple must sum to the bound value
:- triple(elem(x,_,X), elem(y,_,Y), elem(z,_,Z)), X+Y+Z != B, bound(B).

#show.
#show triple(X,Y,Z) : triple(elem(_,_,X), elem(_,_,Y), elem(_,_,Z)).
