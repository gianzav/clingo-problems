#script (python)
import clingo
S = clingo.String

def conc(x,y):
    sx = x.string
    sy = y.string
    return S(sx+sy)
#end.


%% how to force the ordered choice of the matches?
1{match(1,X) : tile(a,X,_), tile(b,X,_)}1.
{match(I+1,X)} :- match(I,_), tile(a,X,_), tile(b,X,_), I<bound.

string(a, 0, "").
string(b, 0, "").
string(S, I+1, @conc(P,Q)) :- string(S,I,P), match(I+1,X), tile(S,X,Q).

%% the strings given by the matches should be equal
:- string(a, TilesUsed, X), string(b, TilesUsed, Y), X != Y, TilesUsed = #max{I : string(_,I,_)}.

#show match/2.
