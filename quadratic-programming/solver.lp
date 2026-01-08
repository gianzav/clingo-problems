%% parse all the expressions in the input
expr(Id, leq(X,Y)) :- subject_to(Id, leq(X,Y)).
expr(Id, geq(X,Y)) :- subject_to(Id, geq(X,Y)).
expr(Id, X) :- expr(Id, neg(X)).
expr(Id, X) :- expr(Id, add(X,_)).
expr(Id, X) :- expr(Id, add(_,X)).
expr(Id, X) :- expr(Id, prod(X,_)).
expr(Id, X) :- expr(Id, prod(_,X)).
expr(Id, X) :- expr(Id, minus(X,_)).
expr(Id, X) :- expr(Id, minus(_,X)).
expr(Id, X) :- expr(Id, geq(X,_)).
expr(Id, X) :- expr(Id, geq(_,X)).
expr(Id, X) :- expr(Id, leq(X,_)).
expr(Id, X) :- expr(Id, leq(_,X)).
expr(Id, X) :- expr(Id, square(X)).
expr(-1, X) :- maximize(X).

%% each variable must have one assigned domain value
1{assign(X,V) : dom(V)}1 :- var(X).

%% variables are evaluated as their assignment
eval(Id, X, V) :- expr(Id, X), var(X), assign(X,V).

%% domain values are evaluated as themselves 
eval(Id, X, X) :- expr(Id, X), dom(X).

%% neg
eval(Id, neg(X), -V) :- expr(Id, neg(X)), eval(Id, X, V).

%% add
eval(Id, add(X,Y), P+Q) :- expr(Id, add(X,Y)), eval(Id, X, P), eval(Id, Y, Q).
%% minus
eval(Id, minus(X,Y), P-Q) :- expr(Id, minus(X,Y)), eval(Id, X, P), eval(Id, Y, Q).

%% prod
eval(Id, prod(X,Y), P*Q) :- expr(Id, prod(X,Y)), eval(Id, X, P), eval(Id, Y, Q).

%% square
eval(Id, square(X), P**2) :- expr(Id, square(X)), eval(Id, X, P).

%% geq
:- expr(Id, geq(X,Y)), eval(Id, X, P), eval(Id, Y, Q), P < Q.

%% leq
:- expr(Id, leq(X,Y)), eval(Id, X, P), eval(Id, Y, Q), P > Q.

%% maximize
#maximize{V : maximize(X), eval(-1, X, V)}.

#show assign/2.
