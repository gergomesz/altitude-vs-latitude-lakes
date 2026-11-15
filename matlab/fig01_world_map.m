%% fig01_world_map.m  -  Figure I
% every lake coloured by its July temperature, with the two comparison bands

clear; close all
L = load('lakes.mat');  C = lake_style();

figure('Position', [100 100 1100 470]);
draw_land([-170 180 0 72], C.wash);

% every lake, drawn in random order so no group of lakes is always drawn on top
rng(0);
s = randperm(numel(L.lat));
scatter(L.lon(s), L.lat(s), 1, L.july(s), 'filled');
colormap(C.seq); caxis([8 32]);
cb = colorbar; ylabel(cb, 'Mean July surface temperature, 2013–2021 (°C)');

% Alps band (orange dashed) and southern Canada band (blue dotted)
ha = plot([-170 180], [45.8 45.8], '--', 'Color', C.alps, 'LineWidth', 1.2);
plot([-170 180], [47.8 47.8], '--', 'Color', C.alps, 'LineWidth', 1.2);
hc = plot([-170 180], [50 50], ':', 'Color', C.canada, 'LineWidth', 1.5);
plot([-170 180], [53 53], ':', 'Color', C.canada, 'LineWidth', 1.5);
legend([ha hc], {'Alps latitude band (45.8–47.8°N)', 'Southern Canada band (50–53°N)'}, 'Location', 'southwest');

daspect([1.25 1 1]);
xlabel('Longitude (°E)'); ylabel('Latitude (°N)');
title({'July lake surface temperature, Northern Hemisphere', ...
       'Landsat 8 (LakeTEMP), 2013–2021 · all 1,067,869 lakes'}, 'FontWeight', 'normal');
save_fig('fig01_world_map');
