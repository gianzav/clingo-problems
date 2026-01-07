%%% From https://algorithmminds.com/integer-linear-programming-concepts-and-code-examples/

dom(-100..100).
var(a;b;obj).
maximize(obj).

%% equality constraint on obj
%% obj = 5a + 4b
subject_to(1, geq(obj, add(prod(5,a), prod(4,b)))).
subject_to(2, leq(obj, add(prod(5,a), prod(4,b)))).

subject_to(3, leq(add(prod(2,a), prod(3,b)), 20)).  % 2a + 3b <= 20
subject_to(4, leq(add(prod(4,a), prod(2,b)), 24)).  % 4a + 2b <= 24
