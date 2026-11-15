%% fig04_variance_shares.m  -  Figure 4
% how much of the lake-to-lake difference in summer temperature each variable explains (R squared),
% for the Northern Hemisphere (July) and, if south.mat exists, the Southern Hemisphere (January)
% needs lakes.mat (step0_load_data); for the south also south.mat (step0_load_south)

clear; close all
L = load('lakes.mat');  C = lake_style();

% Northern Hemisphere: latitude, height, depth; July temperature
vals = r2_shares(L.lat, L.elev / 1000, L.logdepth, L.july);
hemis = {sprintf('Northern Hemisphere, July (%s lakes)', commas(numel(L.lat)))};
cols = {C.ink};
if isfile('south.mat')
    S = load('south.mat');
    % Southern Hemisphere: distance from the equator, height, depth; January temperature
    vals(:, 2) = r2_shares(S.alat, S.elev / 1000, S.logdepth, S.jan);
    hemis{2} = sprintf('Southern Hemisphere, January (%s lakes)', commas(numel(S.lat)));
    cols{2} = C.alps;
else
    disp('south.mat not found (run step0_load_south): showing the Northern Hemisphere only');
end

labels = {'Latitude alone', 'Altitude alone', 'Latitude, controlling for altitude', 'Altitude, controlling for latitude'};
nh = size(vals, 2);  w = 0.34;                 % bar thickness
off = ((1:nh) - (nh + 1) / 2) * (w + 0.04);    % bars of the two hemispheres side by side
figure('Position', [100 100 860 440]); hold on
h = zeros(1, nh);
for s = 1:nh
    for i = 1:4
        y0 = i + off(s) - w / 2;  v = vals(i, s);
        hp = patch([0 v v 0], [y0 y0 y0 + w y0 + w], cols{s}, 'EdgeColor', 'none');
        text(v + 0.6, i + off(s), sprintf('%.1f%%', v), 'FontSize', 9, 'VerticalAlignment', 'middle');
        if i == 1, h(s) = hp; end
    end
end
set(gca, 'YTick', 1:4, 'YTickLabel', labels, 'YDir', 'reverse', 'Box', 'off');
ylim([0.4 4.6]); xlim([0 50]); grid on
xlabel('% of lake-to-lake variation in summer temperature explained (R^2)');
title({'Which explains more: latitude or altitude?', 'lake depth held constant'}, 'FontWeight', 'normal');
legend(h, hemis, 'Location', 'southoutside');
save_fig('fig04_variance_shares');

