%% Must specify the domain for the variables
dom(-100..100).

%% Must specify the variable names
var(x). var(y).

%% Optimization statement
maximize(square(y)).

%% Constraints
%% The available functions/relations are: add, minus, neg, leq, geq, square

subject_to(1, leq(add(neg(x), y), 1)).                 % -x + y <= 1
subject_to(2, leq(add(prod(3,x), prod(2,y)), 12)).     % 3x + 2y <= 12
subject_to(3, leq(add(prod(2,x), prod(3,y)), 12)).     % 2x + 3y <= 12
subject_to(4, geq(x,0)).                               % x >= 0
subject_to(5, geq(y,0)).                               % y >= 0

%% solutions: (x=1, y=2), (x=2, y=2)
