% Optimized Bounded Post Correspondence Problem (BPCP) Solver
%
% Problem: Given a set of domino tiles with top and bottom strings,
% find a sequence such that concatenating tops equals concatenating bottoms.

% ============================================
% PYTHON INTEGRATION - String Concatenation
% ============================================
#script (python)
import clingo
S = clingo.String

def conc(x, y):
    """Efficiently concatenate two strings"""
    return S(x.string + y.string)
#end.

% ============================================
% INPUT: Define the tiles
% ============================================
% Format: tile(Side, ID, String)
% Side 'a' = top, Side 'b' = bottom

tile(a, 1, "a").
tile(b, 1, "baa").

tile(a, 2, "ab").
tile(b, 2, "aa").

tile(a, 3, "bba").
tile(b, 3, "bb").

% ============================================
% CONFIGURATION
% ============================================
#const bound = 8.

% ============================================
% GENERATE: Select tiles in sequence
% ============================================
% First position: must select exactly one tile
1 { match(1, X) : tile(a, X, _), tile(b, X, _) } 1.

% Subsequent positions: may select a tile (bounded by bound)
{ match(I+1, X) : tile(a, X, _), tile(b, X, _) } 1 :- 
    match(I, _), 
    I < bound.

% ============================================
% COMPUTE: Build concatenated strings
% ============================================
% Base case: empty strings at position 0
string(a, 0, "").
string(b, 0, "").

% Recursive case: concatenate previous string with new tile
string(Side, I+1, @conc(PrevString, TileString)) :- 
    string(Side, I, PrevString),
    match(I+1, TileID),
    tile(Side, TileID, TileString).

% ============================================
% DEFINE: Helper predicates
% ============================================
% Find the maximum position used
max_pos(M) :- M = #max { I : match(I, _) }.

% Get final strings at the last position
final_string(Side, S) :- 
    max_pos(Pos),
    string(Side, Pos, S).

% ============================================
% CONSTRAINT: Strings must match
% ============================================
% The final top and bottom strings must be equal
:- final_string(a, X), final_string(b, Y), X != Y.

% ============================================
% OPTIMIZATION: Minimize sequence length
% ============================================
% Prefer shorter solutions
#minimize { Pos : match(Pos, _) }.

% ============================================
% OUTPUT
% ============================================
#show match/2.
#show final_string/2.

% Optional: show intermediate steps for debugging
% #show string/3.
