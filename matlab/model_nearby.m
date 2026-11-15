function c = model_nearby(lat, lon, r, tr, shrink)
% nearby-lakes correction: the average leftover error r of the lakes in tr that sit in the
% 3 x 3 block of 1-degree squares around each lake, multiplied by n / (n + shrink)
% so that a few neighbours only give a small correction
i = floor(lat) + 2;  j = floor(lon) + 182;          % +1 square of margin on every side
sz = [max(i) + 1, 363];
Ssum = accumarray([i(tr) j(tr)], r(tr), sz);
Ncnt = accumarray([i(tr) j(tr)], 1, sz);
S3 = conv2(Ssum, ones(3), 'same');
N3 = conv2(Ncnt, ones(3), 'same');
cg = S3 ./ max(N3, 1) .* N3 ./ (N3 + shrink);
c = cg(sub2ind(sz, i, j));
end
