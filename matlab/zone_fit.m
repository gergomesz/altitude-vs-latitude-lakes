function Z = zone_fit(L, width)
% fit  July = a + b_lat*lat + b_alt*elev_km + c*log10(depth) + region  in every zone
% zones are uniform: (0, width], (width, 2*width], ... up to 70 N
% a zone is only fitted if it has >= 200 lakes and >= 20 above 1000 m
Z = struct([]);
for z0 = 0:width:(70 - width)
    k = L.lat > z0 & L.lat <= z0 + width;
    r.z0 = z0; r.n = sum(k); r.nhi = sum(k & L.elev > 1000);
    r.per_km = NaN; r.km_lo = NaN; r.km_hi = NaN;
    r.per_deg = NaN; r.deg_lo = NaN; r.deg_hi = NaN;
    r.sea = NaN; r.open_per_km = NaN;
    if r.n >= 200 && r.nhi >= 20
        R = dummies(L.region(k));
        X = [ones(r.n, 1), L.lat(k), L.elev(k) / 1000, L.logdepth(k), R];
        [b, se] = ols_cl(X, L.july(k), L.cell(k));
        r.per_deg = b(2); r.deg_lo = b(2) - 1.96 * se(2); r.deg_hi = b(2) + 1.96 * se(2);
        r.per_km  = b(3); r.km_lo  = b(3) - 1.96 * se(3); r.km_hi  = b(3) + 1.96 * se(3);
        % sea-level July temperature: 0 m, middle latitude, median depth, averaged over regions
        regpart = 0;
        if ~isempty(R), regpart = mean(R * b(5:end)); end
        r.sea = b(1) + b(2) * (z0 + width / 2) + b(4) * L.med_logdepth + regpart;
        bo = X \ L.openw(k);           % same model, yearly open-water mean
        r.open_per_km = bo(3);
    end
    Z = [Z, r]; %#ok<AGROW>
end
end
