%% a facility might be opened or not
%% open(Facility)
{open(F)} :- facility(F).
close(F) :- not open(F), facility(F).
open(F) :- not close(F), facility(F).

%% a customer might be served by a facility
%% served(Customer, Facility)
{served(C,F)} :- customer(C), open(F), facility(F).

%% a customer must be served by a facility
:- customer(C), not served(C,_).

%% in the **uncapacitated** facility location problem, a single facility can fulfill the entire customer's demand
%% then, we can constrain that each customer is served by a single facility
:- customer(C), facility(F1), facility(F2), served(C,F1), served(C,F2), F1<F2.

opened_total_cost(X) :- X = #sum{C,F : opening_cost(F,C)}.
ship_total_cost(X) :- X = #sum{Cost*Demand,Fac,Cust : demand(Cust, Demand), ship_cost(Fac,Cust,Cost), open(Fac), served(Cust,Fac)}.

#minimize{X + Y : opened_total_cost(X), ship_total_cost(Y)}.
#show served/2.
