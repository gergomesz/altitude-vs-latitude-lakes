%% fig12_coast_distance.m  -  Figure XII
% does distance to the ocean explain why the lapse rate changes between continents?
%   a: are inland lakes warmer than the zone equation predicts?
%   b: Alps latitude: region slopes before and after adding distance to the ocean
%   c: lapse rate for coastal vs inland lakes, north of the 33 N break

clear; close all
L = load('lakes.mat');  C = lake_style();

% 0. distance from each lake to the nearest ocean coast (km)
%    coast_distance_grid.mat holds the distance on a 0.1 degree grid; read it at each lake
G = load('coast_distance_grid.mat');
coast = interp2(G.glon, G.glat, double(G.dist_km), L.lon, L.lat, 'linear');
logcoast = log10(coast + 10);          % log scale: going from 10 to 100 km matters as much as 100 to 1000 km
km = L.elev / 1000;
fprintf('distance to the ocean: median %.0f km, 90%% of lakes within %.0f km\n', median(coast), pct(coast, 90));

% a. residuals from the zone equation (same model as fig10), by distance to the ocean
zone = floor((L.lat - 1e-9) / 5) + 1;  nz = max(zone);
design = @(idx) [double(zone(idx) == 1:nz), double(zone(idx) == 1:nz) .* km(idx), ...
                 double(zone(idx) == 1:nz) .* L.lat(idx), L.logdepth(idx)];
n = numel(L.lat);  XtX = 0;  Xty = 0;
for s = 1:100000:n
    idx = (s:min(s + 99999, n))';  X = design(idx);
    XtX = XtX + X' * X;  Xty = Xty + X' * L.july(idx);
end
b = XtX \ Xty;
res = zeros(n, 1);
for s = 1:100000:n
    idx = (s:min(s + 99999, n))';  res(idx) = L.july(idx) - design(idx) * b;
end
edges = [0 25 50 100 200 400 800 1600 4000];
mid = sqrt(max(edges(1:end-1), 5) .* edges(2:end));           % middle of each bin on a log scale
medN = NaN(1, numel(mid));  medS = medN;
for i = 1:numel(mid)
    in = coast >= edges(i) & coast < edges(i + 1);
    if sum(in & L.lat > 33) >= 200,  medN(i) = median(res(in & L.lat > 33));  end
    if sum(in & L.lat <= 33) >= 200, medS(i) = median(res(in & L.lat <= 33)); end
end

% b. Alps latitude: slope per region without and with distance to the ocean
A = L.lat >= 45.8 & L.lat <= 47.8;
names = {};  before = [];  after = [];
for r = 1:6
    k = A & L.region == r;
    if sum(k) < 100 || sum(k & L.elev > 1000) < 15, continue, end
    b0 = [ones(sum(k), 1), km(k), L.logdepth(k)] \ L.july(k);
    b1 = [ones(sum(k), 1), km(k), L.logdepth(k), logcoast(k)] \ L.july(k);
    names{end + 1} = L.regnames{r};  before(end + 1) = b0(2);  after(end + 1) = b1(2); %#ok<AGROW>
    fprintf('%-16s %.2f -> %.2f C/km\n', L.regnames{r}, b0(2), b1(2));
end

% c. lapse rate by distance class, north of 33 N (latitude, depth and region held fixed)
cls = [0 100; 100 500; 500 1000; 1000 5000];
clsname = {'coastal (<100 km)', '100–500 km', '500–1000 km', 'inland (>1000 km)'};
v = zeros(1, 4);  lo = v;  hi = v;
for i = 1:4
    k = L.lat > 33 & coast >= cls(i, 1) & coast < cls(i, 2);
    [bb, se] = ols_cl([ones(sum(k), 1), km(k), L.lat(k), L.logdepth(k), dummies(L.region(k))], L.july(k), L.cell(k));
    v(i) = bb(2);  lo(i) = bb(2) - 1.96 * se(2);  hi(i) = bb(2) + 1.96 * se(2);
    fprintf('%-18s %.2f C/km (%.2f to %.2f)\n', clsname{i}, v(i), lo(i), hi(i));
end

%% draw
figure('Position', [100 100 1500 460]);
subplot(1, 3, 1); hold on; grid on
plot(mid, medN, '-o', 'Color', C.ink, 'MarkerFaceColor', 'w', 'MarkerSize', 7);
plot(mid, medS, '-s', 'Color', C.grey, 'MarkerFaceColor', 'w', 'MarkerSize', 7);
plot([5 4000], [0 0], ':', 'Color', C.grey);
set(gca, 'XScale', 'log', 'XTick', [10 30 100 300 1000], 'XTickLabel', {'10', '30', '100', '300', '1000'}); xlim([8 3000]);
legend({'north of 33°N', 'south of 33°N'}, 'Location', 'northwest');
xlabel('Distance to the ocean (km, log scale)'); ylabel('Observed minus predicted July temperature (°C)');
title('a · Inland lakes are warmer in July', 'FontWeight', 'normal');

subplot(1, 3, 2); hold on; grid on
[~, o] = sort(before);  y = 1:numel(o);
for i = y
    plot([before(o(i)) after(o(i))], [i i], '-', 'Color', C.grey, 'LineWidth', 1.2);
end
h1 = plot(before(o), y, 'o', 'Color', C.grey, 'MarkerFaceColor', 'w', 'MarkerSize', 8);
h2 = plot(after(o), y, 'o', 'Color', C.alps, 'MarkerFaceColor', C.alps, 'MarkerSize', 8);
plot([-6.5 -6.5], [0.4 numel(o) + 0.6], '--', 'Color', C.grey);
set(gca, 'YTick', y, 'YTickLabel', names(o)); ylim([0.4 numel(o) + 0.6]);
legend([h1 h2], {'height + depth only', '+ distance to the ocean'}, 'Location', 'southeast');
text(-6.45, numel(o) + 0.45, '−6.5 air', 'FontSize', 8, 'Color', C.grey);
xlabel('July temperature change per km of altitude (°C)');
title('b · Alps latitude: region slopes move closer', 'FontWeight', 'normal');

subplot(1, 3, 3); hold on; grid on
for i = 1:4, plot([lo(i) hi(i)], [i i], '-', 'Color', C.grey, 'LineWidth', 1.8); end
plot(v, 1:4, 'o', 'Color', C.ink, 'MarkerFaceColor', 'w', 'MarkerSize', 8);
plot([-6.5 -6.5], [0.5 4.5], '--', 'Color', C.grey);
set(gca, 'YTick', 1:4, 'YTickLabel', clsname, 'YDir', 'reverse'); ylim([0.5 4.5]);
text(-6.45, 0.6, '−6.5 air', 'FontSize', 8, 'Color', C.grey, 'VerticalAlignment', 'top');
xlabel({'July temperature change per km of altitude (°C)', 'lakes north of 33°N, bars = 95% CI'});
title('c · Coastal mountains cool faster', 'FontWeight', 'normal');
save_fig('fig12_coast_distance');
