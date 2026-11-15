function [bp, b, F] = broken_stick(x, y, w, grid)
% two straight lines joined at a break point bp
%   y = b1 + b2*x + b3*max(x - bp, 0)
% tries every bp in grid and keeps the one with the smallest squared error
% slope before the break = b2, after the break = b2 + b3
x = x(:); y = y(:); sw = sqrt(w(:));
best = Inf;
for g = grid
    X = [ones(size(x)), x, max(x - g, 0)];
    bb = (X .* sw) \ (y .* sw);
    s = sum(((y - X * bb) .* sw).^2);
    if s < best, best = s; bp = g; b = bb; end
end
X0 = [ones(size(x)), x];
b0 = (X0 .* sw) \ (y .* sw);
s0 = sum(((y - X0 * b0) .* sw).^2);
F = ((s0 - best) / 2) / (best / (numel(x) - 4));
end
