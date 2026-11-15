function draw_borders(ext)
% country borders (solid) and state/province borders (dotted) from borders.csv
% ext = [lon1 lon2 lat1 lat2]; only lines inside it are drawn
persistent B
if isempty(B), B = csvread('borders.csv', 1, 0); end   % columns: kind, line id, lon, lat
hold on
ids = unique(B(:, 2));
for i = ids'
    k = B(:, 2) == i;
    x = B(k, 3); y = B(k, 4);
    if max(x) < ext(1) || min(x) > ext(2) || max(y) < ext(3) || min(y) > ext(4), continue, end
    if B(find(k, 1), 1) == 1
        plot(x, y, '-', 'Color', [0.30 0.30 0.32], 'LineWidth', 0.9);   % country
    else
        plot(x, y, ':', 'Color', [0.55 0.55 0.58], 'LineWidth', 0.7);   % state / province
    end
end
xlim(ext(1:2)); ylim(ext(3:4));
end
