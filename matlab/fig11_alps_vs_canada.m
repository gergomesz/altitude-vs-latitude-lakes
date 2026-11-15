%% fig11_alps_vs_canada.m  -  Figure XI
% low and high lakes at the Alps latitude vs southern Canada: is it latitude or height?

clear; close all
L = load('lakes.mat');  C = lake_style();
bands = {[45.8 47.8], [50 53]};
names = {'Alps latitude (45.8–47.8°N)', 'Southern Canada latitude (50–53°N)'};
cols  = {C.alps, C.canada};
style = {'-o', '--s'};
heights = {[-500 500], [1500 6000]};            % low = below 500 m, high = above 1500 m

figure('Position', [100 100 760 450]); hold on; grid on
h = zeros(1, 2);
for i = 1:2
    xs = zeros(1, 2); ys = zeros(1, 2); ns = zeros(1, 2);
    for j = 1:2
        k = L.lat >= bands{i}(1) & L.lat <= bands{i}(2) & L.elev >= heights{j}(1) & L.elev < heights{j}(2);
        xs(j) = median(L.elev(k)); ys(j) = median(L.july(k)); ns(j) = sum(k);
        text(xs(j) + 60, ys(j) + 0.35, sprintf('%.1f °C\n%s lakes', ys(j), regexprep(num2str(ns(j)), '\d(?=(\d{3})+$)', '$0,')), 'FontSize', 9);
    end
    h(i) = plot(xs, ys, style{i}, 'Color', cols{i}, 'MarkerFaceColor', 'w', 'MarkerSize', 9, 'LineWidth', 1.5);
    fprintf('%s: low %.2f C, high %.2f C, difference %.2f C over %.0f m\n', names{i}, ys(1), ys(2), ys(2) - ys(1), xs(2) - xs(1));
end
legend(h, names, 'Location', 'southwest');
xlim([0 2600]); ylim([12 25]);
xlabel('Median elevation of group (m)'); ylabel('Median July surface temperature (°C)');
title({'Is it latitude or height?', 'Low lakes (below 500 m) vs high lakes (above 1,500 m) at two latitudes'}, 'FontWeight', 'normal');
save_fig('fig11_alps_vs_canada');
