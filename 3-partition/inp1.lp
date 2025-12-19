%% input multi-set elements
elem(1, 20).
elem(2, 23).
elem(3, 25).
elem(4, 30).
elem(5, 49).
elem(6, 45).
elem(7, 27).
elem(8, 30).
elem(9, 30).
elem(10, 40).
elem(11, 22).
elem(12, 19).

%% Expected output [i1, i2...] in place of actual numbers
%% partition(i1,4,30)
%% partition(i1,8,30)
%% partition(i1,9,30)
%% 
%% partition(i2,11,22)
%% partition(i2,12,19)
%% partition(i2,5,49)
%% 
%% partition(i3,10,40)
%% partition(i3,2,23)
%% partition(i3,7,27)
%% 
%% partition(i4,1,20)
%% partition(i4,3,25)
%% partition(i4,6,45)
