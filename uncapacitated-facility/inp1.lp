facility(1..3).
customer(1..2).

%% the fixed cost of opening a facility
%% opening_cost(Facility, Cost)
opening_cost(1,1).
opening_cost(2,2).
opening_cost(3,3).

%% the cost of shipping a product from a facility to a customer
%% ship_cost(Facility, Customer, Cost)
ship_cost(1, 1, 1).
ship_cost(2, 1, 2).
ship_cost(3, 1, 3).

ship_cost(1, 2, 3).
ship_cost(2, 2, 2).
ship_cost(3, 2, 2).

%% the demand of product for each customer
%% demand(Customer, Demand)
demand(C, 1) :- customer(C).
