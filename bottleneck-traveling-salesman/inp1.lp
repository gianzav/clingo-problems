%% edge(node1, node2, weight).
edge(1,2,1).
edge(1,5,1).
edge(1,4,2).

edge(2,3,1).
edge(2,4,1).
edge(2,6,2).

edge(3,6,1).

edge(4,5,1).
edge(4,6,22).

edge(5,6,12).

%% expected chosen edges
% (1,5), (5,6), (6,3), (3,2), (2,4), (4,1)
