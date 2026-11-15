function [b, se, r2, e] = ols_cl(X, y, g)
% least squares with standard errors clustered by group g
% (lakes in the same 1x1 degree cell share weather, so they are not independent)
%   X  : n-by-k design matrix, first column all ones
%   y  : n-by-1 response
%   g  : n-by-1 cluster id (any numbers)
b = X \ y;
e = y - X * b;
[n, k] = size(X);
r2 = 1 - sum(e.^2) / sum((y - mean(y)).^2);
if nargin < 3 || nargout < 2
    se = [];
    return
end
[~, ~, gi] = unique(g);
G = max(gi);
S = zeros(G, k);
for j = 1:k
    S(:, j) = accumarray(gi, X(:, j) .* e, [G 1]);
end
B = inv(X' * X);
V = B * (S' * S) * B * G / (G - 1) * (n - 1) / (n - k);
se = sqrt(diag(V));
end
