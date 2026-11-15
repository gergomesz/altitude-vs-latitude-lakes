function S = slide_fit(L)
% a 2 degree window slides north 1 degree at a time
% in each window: July = a + b_alt*elev_km + c*log10(depth) + region
S = struct('lat', [], 'n', [], 'per_km', [], 'lo', [], 'hi', [], 'sea', []);
for c = 5:69
    k = L.lat >= c - 1 & L.lat < c + 1;
    if sum(k) < 300 || sum(k & L.elev > 1000) < 30, continue, end
    R = dummies(L.region(k));
    X = [ones(sum(k), 1), L.elev(k) / 1000, L.logdepth(k), R];
    [b, se] = ols_cl(X, L.july(k), L.cell(k));
    regpart = 0;
    if ~isempty(R), regpart = mean(R * b(4:end)); end
    S.lat(end + 1, 1) = c;
    S.n(end + 1, 1) = sum(k);
    S.per_km(end + 1, 1) = b(2);
    S.lo(end + 1, 1) = b(2) - 1.96 * se(2);
    S.hi(end + 1, 1) = b(2) + 1.96 * se(2);
    S.sea(end + 1, 1) = b(1) + b(3) * L.med_logdepth + regpart;
end
end
