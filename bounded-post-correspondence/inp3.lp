%% hard instance, from https://ai.dmi.unibas.ch/_files/teaching/fs24/theo/slides/theory-c05-handout4.pdf
%% shortest match has length 252

#const low_bound = 1.
#const top_bound = 252.

tile(a, 1, "1101").
tile(a, 2, "0110").
tile(a, 3, "1").

tile(b, 1, "1").
tile(b, 2, "11").
tile(b, 3, "110").
