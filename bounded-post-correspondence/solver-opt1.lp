#script (python)
import clingo
S = clingo.String
F = clingo.Function

def conc(x,y):
    sx = x.string
    sy = y.string
    return S(sx+sy)
#end.


%% first match
1{match(1,X) : tile(a,X,_), tile(b,X,_)}1.
%% generate ordered, unique matches 
{match(I+1,X)} :- match(I,_), tile(a,X,_), tile(b,X,_), I<top_bound,
    string(a,I,_), string(b,I,_). % generate a new match only if the strings have been generated
:- match(I,X), match(I,Y), X<Y.

string(a, 0, "").
string(b, 0, "").
string(S, I+1, @conc(P,Q)) :- string(S,I,P), match(I+1,X), tile(S,X,Q), 
    not stop(_,I). %% generate a new string only if stop has not been derived

%% Derive 'stop' as soon as two equal strings are constructed
stop(X,T) :- string(a,T,X), string(b,T,X), T >= low_bound.
:- stop(_,T), stop(_,T+1).
:- not stop(_,_).

#show string/3.
#show match/2.
#show stop/2.
