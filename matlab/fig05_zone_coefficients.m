%% fig05_zone_coefficients.m  -  Figure V
% the zone equation in uniform 5 degree zones: one row per zone, three coefficients

clear; close all
L = load('lakes.mat');  C = lake_style();
Z = zone_fit(L, 5);

% whole Alps band lapse rate, for the reference line
k = L.lat >= 45.8 & L.lat <= 47.8;
b = [ones(sum(k), 1), L.elev(k) / 1000, L.logdepth(k), dummies(L.region(k))] \ L.july(k);
alps_km = b(2);

y = 1:numel(Z);
names = arrayfun(@(z) sprintf('%g–%g°N', z.z0, z.z0 + 5), Z, 'UniformOutput', false);

figure('Position', [100 100 1250 460]);
subplot(1, 3, 1); hold on; grid on
plot([Z.km_lo; Z.km_hi], [y; y], '-', 'Color', C.grey, 'LineWidth', 1.4);
plot([Z.per_km], y, 'o', 'Color', C.ink, 'MarkerFaceColor', 'w', 'MarkerSize', 7);
plot([alps_km alps_km], [0 numel(Z) + 1], '--', 'Color', C.alps);
text(alps_km + 0.05, numel(Z) + 0.55, 'whole Alps band', 'HorizontalAlignment', 'left', 'Color', C.alps, 'FontSize', 8);
set(gca, 'YTick', y, 'YTickLabel', names, 'YDir', 'reverse'); ylim([0 numel(Z) + 1]);
xlabel('Temperature change per km of altitude (°C)');
title('a · Altitude effect (bars = 95% CI)', 'FontWeight', 'normal');

subplot(1, 3, 2); hold on; grid on
plot([Z.deg_lo; Z.deg_hi], [y; y], '-', 'Color', C.grey, 'LineWidth', 1.4);
plot([Z.per_deg], y, 'o', 'Color', C.ink, 'MarkerFaceColor', 'w', 'MarkerSize', 7);
plot([0 0], [0 numel(Z) + 1], '--', 'Color', C.grey);
set(gca, 'YTick', y, 'YTickLabel', {}, 'YDir', 'reverse'); ylim([0 numel(Z) + 1]);
xlabel('Temperature change per degree north (°C)');
text(0.02, numel(Z) + 0.55, 'no effect', 'FontSize', 8, 'Color', C.grey);
title('b · Latitude effect (bars = 95% CI)', 'FontWeight', 'normal');

subplot(1, 3, 3); hold on; grid on
plot([Z.sea], y, 'o', 'Color', C.ink, 'MarkerFaceColor', 'w', 'MarkerSize', 7);
set(gca, 'YTick', y, 'YTickLabel', {}, 'YDir', 'reverse'); ylim([0 numel(Z) + 1]);
xlabel({'Predicted July temperature (°C)', 'at sea level, zone''s middle latitude, median depth'});
title('c · Starting value', 'FontWeight', 'normal');
save_fig('fig05_zone_coefficients');

% the numbers behind the figure (Table I on the site)
fprintf('\n%-9s %8s %8s %8s %16s %8s %9s\n', 'zone', 'lakes', '>1000m', 'C/km', '95% CI', 'C/deg', 'sea-lvl');
for z = Z
    fprintf('%-9s %8d %8d %8.2f %7.2f to %5.2f %8.2f %9.1f\n', sprintf('%g-%g', z.z0, z.z0 + 5), ...
            z.n, z.nhi, z.per_km, z.km_lo, z.km_hi, z.per_deg, z.sea);
end
