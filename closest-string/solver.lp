#script (python)
import clingo
import itertools

F = clingo.Function
S = clingo.String
N = clingo.Number

def hamming(a, b):
    aa = a.string
    bb = b.string
    dist = sum(1 for x,y in zip(aa,bb) if x!=y)
    return N(dist)

def generate(alphabet, length):
    """Generates all the strings of the given length using the alphabet."""
    nlen = length.number
    salph = alphabet.string
    return [S("".join(c for c in x)) for x in itertools.combinations_with_replacement(salph, nlen)]
#end.

% dom(0..length).

hamming(X,X,0) :- string(X).
hamming(X,Y,@hamming(X,Y)) :- center(X), string(Y).
% :- hamming(_,_,D), not dom(D).

%% generate strings of the given length using the characters from the alphabet
1{center(@generate(alphabet,length))}1.

max_distance(Di) :- Di = #max{D : hamming(C,Y,D), string(Y)}, center(C).
:- max_distance(D), D < 0.
:- max_distance(D), D > length.
#minimize{D : max_distance(D)}.

% #show center/1.
% #show hamming/3.
