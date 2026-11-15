function [x, q] = binned(v, y, edges)
% middle of each bin and the 25th, 50th and 75th percentile of y in it (bins with 100+ lakes)
x = [];  q = [];
for j = 1:numel(edges) - 1
    k = v >= edges(j) & v < edges(j + 1);
    if sum(k) >= 100
        x(end + 1, 1) = (edges(j) + edges(j + 1)) / 2;
        q(end + 1, :) = [pct(y(k), 25), pct(y(k), 50), pct(y(k), 75)];
    end
end
end
