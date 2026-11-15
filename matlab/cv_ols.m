function p = cv_ols(X, y, fold)
% least squares tested on lakes it was not fitted to: each of the 5 groups is predicted
% by an equation fitted to the other four
p = zeros(size(y));
for f = 1:5
    tr = fold ~= f;
    b = [ones(sum(tr), 1), X(tr, :)] \ y(tr);
    p(~tr) = [ones(sum(~tr), 1), X(~tr, :)] * b;
end
end
