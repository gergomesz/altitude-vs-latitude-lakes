function p = model_zones(XZ, p7, y, zone, region, km, tr)
% Model 4: one equation per 5-degree zone x continent, fitted on the lakes in tr.
% A group gets its own equation if it has at least 300 training lakes and 20 above 1,000 m;
% otherwise it keeps the 7-variable prediction p7. Groups with fewer than 20 lakes above
% 1,500 m leave out the extra slope above 1,500 m (column 3 of XZ).
p = p7;
for z = 0:13
    for c = 1:6
        g = zone == z & region == c;
        gt = g & tr;
        if sum(gt) >= 300 && sum(gt & km > 1.0) >= 20
            X = XZ;
            if sum(gt & km > 1.5) < 20, X(:, 3) = 0; end
            b = [ones(sum(gt), 1), X(gt, :)] \ y(gt);
            p(g) = [ones(sum(g), 1), X(g, :)] * b;
        end
    end
end
end
