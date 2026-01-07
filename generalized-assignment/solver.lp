%% assign(Task, Agent)
{assign(T, A)} :- task(T), agent(A).

%% the total cost must not exceed the agent's budget
:- agent(A), budget(A,B), #sum{Cost,T : assign(T,A), cost(A,T,Cost)} > B.

%% a task can be assigned only to one agent
:- assign(T, A1), assign(T, A2), A1 < A2.

%% maximize the profit
total_profit(P) :- P = #sum{Profit,A,T : assign(T,A), profit(A,T,Profit)}.
#maximize{P : total_profit(P)}.

#show assign/2.
