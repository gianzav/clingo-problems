facility(1..5).
location(1..5).

%% distance(Location 1, Location 2, Distance)
distance(1,1,0).
distance(1,2,1).
distance(1,3,2).
distance(1,4,3).
distance(1,5,4).

distance(2,2,0).
distance(2,3,1).
distance(2,4,2).
distance(2,5,3).

distance(3,3,0).
distance(3,4,1).
distance(3,5,2).

distance(4,4,0).
distance(4,5,1).

distance(5,5,0).

%% flow(Facility 1, Facility 2, Flow)
flow(1,1,0).
flow(1,2,1).
flow(1,3,2).
flow(1,4,3).
flow(1,5,4).

flow(2,2,0).
flow(2,3,1).
flow(2,4,2).
flow(2,5,3).

flow(3,3,0).
flow(3,4,1).
flow(3,5,2).

flow(4,4,0).
flow(4,5,1).

flow(5,5,0).
