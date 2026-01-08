%% elem(Set identifier, Element identifier, Value)
%% Set identifier may be one of {x,y,z}
%% Element identifier is an integer. It is needed because we work with multisets
%% Value is an integer
elem(x, 1, 3).
elem(x, 2, 4).
elem(x, 3, 4).

elem(y, 1, 1).
elem(y, 2, 4).
elem(y, 3, 6).

elem(z, 1, 1).
elem(z, 2, 2).
elem(z, 3, 5).

elems(3).   % elements in each set
bound(10).

%% solution: {(3,6,1), (4,4,2), (4,1,5)}
