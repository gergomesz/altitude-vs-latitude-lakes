function q = pct(v, p)
% percentile with linear interpolation (same rule as numpy), no toolbox needed
v = sort(v(:));
n = numel(v);
pos = (n - 1) * p / 100 + 1;
lo = floor(pos); hi = min(lo + 1, n);
q = v(lo) + (pos - lo) * (v(hi) - v(lo));
end
