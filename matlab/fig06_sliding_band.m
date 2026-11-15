%% fig06_sliding_band.m  -  Figure VI
% a 2 degree band slides north; where does the latitude effect switch on?

clear; close all
L = load('lakes.mat');  C = lake_style();
S = slide_fit(L);

% 1. two-line fit to sea-level July temperature, break searched from 15 to 60 N
bpgrid = 15:0.5:60;
[bp, b, F] = broken_stick(S.lat, S.sea, ones(size(S.lat)), bpgrid);

% 2. bootstrap: refit 500 times on resampled bands to get a range for the break
rng(0);  boots = zeros(500, 1);  n = numel(S.lat);
for r = 1:500
    i = randi(n, n, 1);
    boots(r) = broken_stick(S.lat(i), S.sea(i), ones(n, 1), bpgrid);
end
ci = [pct(boots, 2.5), pct(boots, 97.5)];
fprintf('break at %.1f N (95%% range %.1f-%.1f), slope before %.3f, after %.3f C/deg, F = %.0f\n', ...
        bp, ci(1), ci(2), b(2), b(2) + b(3), F);

% 3. hemisphere-wide altitude coefficient, for the dotted line
km = L.elev / 1000;
bg = [ones(numel(km), 1), L.lat, km, L.logdepth] \ L.july;

figure('Position', [100 100 1000 720]);
subplot(2, 1, 1); hold on; grid on
fill([ci(1) ci(2) ci(2) ci(1)], [13 13 33 33], C.wash, 'EdgeColor', 'none');
xx = linspace(min(S.lat), max(S.lat), 200);
plot(xx, b(1) + b(2) * xx + b(3) * max(xx - bp, 0), '-', 'Color', C.ink, 'LineWidth', 1.6);
plot(S.lat, S.sea, 'o', 'Color', C.ink, 'MarkerFaceColor', 'w', 'MarkerSize', 5);
plot([bp bp], [13 33], '--', 'Color', C.alps);
text(bp + 0.6, min(S.sea) + 0.5, sprintf('break %.1f°N\n(95%% range %.1f–%.1f°N)', bp, ci(1), ci(2)));
ylim([min(S.sea) - 1, max(S.sea) + 1]); xlim([5 72]);
ylabel('Predicted July temperature at sea level (°C)');
title('a · Where latitude starts to matter (2° band sliding north, two-line fit)', 'FontWeight', 'normal');

subplot(2, 1, 2); hold on; grid on
fill([S.lat; flipud(S.lat)], [S.lo; flipud(S.hi)], C.wash, 'EdgeColor', 'none');
plot(S.lat, S.per_km, '-o', 'Color', C.ink, 'MarkerFaceColor', 'w', 'MarkerSize', 4);
plot([5 72], [bg(3) bg(3)], ':', 'Color', C.grey);
text(6, bg(3) + 0.25, 'whole hemisphere', 'FontSize', 8, 'Color', C.grey, 'VerticalAlignment', 'bottom');
xlim([5 72]);
xlabel('Centre of 2° band (°N)'); ylabel('July temperature change per km of altitude (°C)');
title('b · Altitude effect in the same bands (shading = 95% CI)', 'FontWeight', 'normal');
save_fig('fig06_sliding_band');
