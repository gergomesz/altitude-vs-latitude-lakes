%% fig07_robustness.m  -  Figure VII
% does the altitude effect look the same if we use the yearly open-water mean instead of July?

clear; close all
L = load('lakes.mat');  C = lake_style();
Z = zone_fit(L, 5);
x = [Z.z0] + 2.5;

figure('Position', [100 100 820 380]); hold on; grid on
plot(x, [Z.per_km], '-o', 'Color', C.ink, 'MarkerFaceColor', 'w');
plot(x, [Z.open_per_km], '--s', 'Color', C.grey, 'MarkerFaceColor', 'w');
legend({'July mean', 'Yearly mean over ice-free days'}, 'Location', 'northwest');
xlabel('5° zone centre (°N)'); ylabel('Temperature change per km of altitude (°C)');
title('Robustness check: altitude effect with July vs yearly temperature', 'FontWeight', 'normal');
save_fig('fig07_robustness');
