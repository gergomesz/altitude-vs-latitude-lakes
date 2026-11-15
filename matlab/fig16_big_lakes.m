%% fig16_big_lakes.m  -  Figure 16
% lakes of 500 km2 or more: why they need their own adjustment
%   a: Model 1 (3 variables + continent) predicts big lakes too warm; the big-lake adjustment fixes most of it
%   b: the error grows with lake size
% needs lakes.mat (step0_load_data) and coast_distance_grid.mat

clear; close all
L = load('lakes.mat');  C = lake_style();
G = load('coast_distance_grid.mat');
coast = interp2(G.glon, G.glat, double(G.dist_km), L.lon, L.lat, 'linear');
Cc = log10(coast + 10);  km = L.elev / 1000;
if ~isfield(L, 'area'), error('lakes.mat has no lake areas yet: run the new step0_load_data.m once'); end

%% 1. Model 1: latitude, height, coast, continent; one equation each side of 33 N
pred = zeros(size(L.lat));
for side = 0:1
    k = (L.lat > 33) == side;
    X = [ones(sum(k), 1), L.lat(k), km(k), Cc(k), dummies(L.region(k))];
    b = X \ L.july(k);
    pred(k) = X * b;
end

%% 2. the big lakes and their errors
big = L.area >= 500;
err = L.july(big) - pred(big);                 % negative = colder than Model 1 says
la = log10(L.area(big)) - log10(500);
D  = L.logdepth(big) - log10(3.3);
la50 = L.lat(big) - 50;
% big-lake adjustment: error explained by size, depth and latitude (leave-one-out, so each lake is predicted fairly)
Z = [ones(sum(big), 1), la, D, la50];
adj = zeros(sum(big), 1);
for i = 1:sum(big)
    m = true(sum(big), 1); m(i) = false;
    adj(i) = Z(i, :) * (Z(m, :) \ err(m));
end
b = Z \ err;
fprintf('%d lakes of 500 km2 or more\n', sum(big));
fprintf('Model 1 average error: %.1f C before, %.1f C after the big-lake adjustment\n', mean(abs(err)), mean(abs(err - adj)));
fprintf('adjustment = %.2f %+.2f*[log10(area)-log10(500)] %+.2f*D %+.3f*(lat-50)\n', b);

%% draw
figure('Position', [100 100 1150 470]);
act = L.july(big);  p0 = pred(big);  p1 = p0 + adj;
subplot(1, 2, 1); hold on; grid on
plot([0 32], [0 32], '--', 'Color', C.grey);
h1 = plot(act, p0, 'o', 'Color', C.grey, 'MarkerSize', 5);
h2 = plot(act, p1, 'o', 'Color', C.alps, 'MarkerFaceColor', C.alps, 'MarkerSize', 5);
% label the 8 biggest by name
idx = find(big);
[~, o] = sort(L.area(big), 'descend');
for j = o(1:min(8, numel(o)))'
    nm = L.name(idx(j)); if iscell(nm), nm = nm{1}; end
    text(act(j) + 0.4, p1(j), char(nm), 'FontSize', 8, 'Color', C.ink);
end
axis([0 32 0 32]); axis square
xlabel('Actual July temperature (°C)'); ylabel('Predicted July temperature (°C)');
legend([h1 h2], {'Model 1 equation', '+ big-lake adjustment'}, 'Location', 'southeast');
title(sprintf('a - %d lakes of 500 km^2 or more', sum(big)), 'FontWeight', 'normal');

subplot(1, 2, 2); hold on; grid on
dep = 10 .^ L.logdepth(big);  ar = L.area(big);
cls = {dep < 10, dep >= 10 & dep < 50, dep >= 50};
cc  = {C.wash * 0.75, C.grey, C.ink};
lab = {'shallow (under 10 m)', '10-50 m deep', 'deep (over 50 m)'};
hh = zeros(1, 3);
for q = 1:3
    hh(q) = plot(ar(cls{q}), err(cls{q}), 'o', 'Color', cc{q}, 'MarkerFaceColor', cc{q}, 'MarkerSize', 5);
end
plot([450 1e5], [0 0], ':', 'Color', C.grey);
xx = logspace(log10(500), 5, 50);
hf = plot(xx, b(1) + b(2) * (log10(xx) - log10(500)) + b(3) * median(D), '-', 'Color', C.alps, 'LineWidth', 1.8);
set(gca, 'XScale', 'log'); xlim([450 1e5]); ylim([-20 8]);
legend([hh hf], [lab, {'adjustment (typical depth)'}], 'Location', 'southwest');
xlabel('Lake area (km^2, log scale)'); ylabel('Actual minus Model 1 (°C)');
title('b - The bigger and deeper the lake, the colder than predicted', 'FontWeight', 'normal');
save_fig('fig16_big_lakes');
