%%% ASP encoding from Köppl, Dominik. “Encoding Hard String Problems with Answer Set Programming.” LIPIcs, Volume 259, CPM 2023 259 (2023): 17:1-17:21. Application/pdf, 21 pages, 1090080 bytes. https://doi.org/10.4230/LIPICS.CPM.2023.17. Section 3.1

#script (python)
import clingo
import itertools

F = clingo.Function
S = clingo.String
N = clingo.Number

string_id = itertools.count()

def gen_input(x):
    sx = x.string
    id = next(string_id) 
    return [F("", [N(id),N(i),S(c)]) for i,c in enumerate(sx, start=1)]

#end.

%% to convert the input to the format used by the original encoding
input(@gen_input(X)) :- string(X).
%% s(String Id, Index, Character)
s(X,I,C) :- input((X,I,C)).

%%% ORIGINAL ENCODING
mat(X,I) :- s(X,I,_).
1 {t(I,C) : s(_,I,C)} 1 :- mat(_,I). %(CSP1)
c(X,I) :- t(I,C), s(X,I,A), C != A. %(CSP2)
cost(X,C) :- C = #sum {1,I : c(X,I)}, mat(X,_). %(CSP3)
mcost(M) :- M = #max {C : cost(_,C)}.
#minimize {M : mcost(M)}.
#show t/2. #show mcost/1. #show cost/2.
%%% END ORIGINAL ENCODING
