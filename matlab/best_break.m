function [bk, b] = best_break(phi, Xrest, y, grid)
% finds the latitude where the straight line bends: fits y = a + b1*phi + b2*max(phi - bk, 0) + ...
% for every bk in grid and keeps the one with the smallest squared error
best = inf;  bk = grid(1);  b = [];
for g = grid
    X = [ones(numel(y), 1), phi, max(phi - g, 0), Xrest];
    bb = X \ y;  sse = sum((y - X * bb).^2);
    if sse < best, best = sse; bk = g; b = bb; end
end
end
