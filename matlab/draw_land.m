function draw_land(ext, colour)
% grey land from coast.csv, only the polygons inside ext = [lon1 lon2 lat1 lat2]
persistent P
if isempty(P), P = csvread('coast.csv', 1, 0); end
hold on
ids = unique(P(:, 1));
for i = ids'
    k = P(:, 1) == i;
    x = P(k, 2); y = P(k, 3);
    if max(x) < ext(1) || min(x) > ext(2) || max(y) < ext(3) || min(y) > ext(4), continue, end
    fill(x, y, colour, 'EdgeColor', [0.6 0.6 0.6], 'LineWidth', 0.3);
end
xlim(ext(1:2)); ylim(ext(3:4)); box on
end
