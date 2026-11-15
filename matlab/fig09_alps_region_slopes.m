%% fig09_alps_region_slopes.m  -  Figure IX
% lapse rate (C per km) in each region of the Alps band, with 95% confidence intervals

clear; close all
L = load('lakes.mat');  C = lake_style();
A = L.lat >= 45.8 & L.lat <= 47.8;
names = {};  v = [];  lo = [];  hi = [];

for r = 1:6
    k = A & L.region == r;
    if sum(k) < 100 || sum(k & L.elev > 1000) < 15, continue, end
    [b, se] = ols_cl([ones(sum(k), 1), L.elev(k) / 1000, L.logdepth(k)], L.july(k), L.cell(k));
    names{end + 1} = L.regnames{r}; v(end + 1) = b(2); %#ok<AGROW>
    lo(end + 1) = b(2) - 1.96 * se(2); hi(end + 1) = b(2) + 1.96 * se(2); %#ok<AGROW>
end
% Switzerland only
k = A & L.isCH;
[b, se] = ols_cl([ones(sum(k), 1), L.elev(k) / 1000, L.logdepth(k)], L.july(k), L.cell(k));
names{end + 1} = 'Switzerland only'; v(end + 1) = b(2); lo(end + 1) = b(2) - 1.96 * se(2); hi(end + 1) = b(2) + 1.96 * se(2);
% whole band, with region effects
[b, se] = ols_cl([ones(sum(A), 1), L.elev(A) / 1000, L.logdepth(A), dummies(L.region(A))], L.july(A), L.cell(A));
names{end + 1} = 'Whole Alps band'; v(end + 1) = b(2); lo(end + 1) = b(2) - 1.96 * se(2); hi(end + 1) = b(2) + 1.96 * se(2);

figure('Position', [100 100 820 380]); hold on; grid on
n = numel(v);
for i = 1:n
    plot([lo(i) hi(i)], [i i], '-', 'Color', C.grey, 'LineWidth', 1.6);
end
plot(v(1:n-1), 1:n-1, 'o', 'Color', C.ink, 'MarkerFaceColor', 'w', 'MarkerSize', 8);
plot(v(n), n, 'd', 'Color', C.alps, 'MarkerFaceColor', C.alps, 'MarkerSize', 9);
plot([-6.5 -6.5], [0.5 n + 0.5], '--', 'Color', C.grey);
text(-6.45, n + 0.3, '−6.5 °C/km (standard air lapse rate)', 'FontSize', 8, 'Color', C.grey);
set(gca, 'YTick', 1:n, 'YTickLabel', names, 'YDir', 'reverse'); ylim([0.5 n + 0.5]);
xlabel('July temperature change per km of altitude (°C, bars = 95% CI)');
title('Alps latitude (45.8–47.8°N): altitude effect by region', 'FontWeight', 'normal');
save_fig('fig09_alps_region_slopes');
for i = 1:n, fprintf('%-18s %6.2f  (%.2f to %.2f)\n', names{i}, v(i), lo(i), hi(i)); end
