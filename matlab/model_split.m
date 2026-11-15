function p = model_split(X, y, side, tr)
% one least-squares equation each side of the 33 N split, fitted on the lakes in tr,
% then used to predict every lake (side = 0 south of 33 N, 1 north of it)
p = zeros(size(y));
for s = 0:1
    k = side == s;
    b = [ones(sum(k & tr), 1), X(k & tr, :)] \ y(k & tr);
    p(k) = [ones(sum(k), 1), X(k, :)] * b;
end
end
