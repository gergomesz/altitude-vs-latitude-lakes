%% fig15_error_by_latitude.m  -  Figure 15
% typical error (median size of the miss) in each 5 degree band of latitude, for each model,
% on lakes the model was NOT fitted to.
% needs heldout.mat (made by step1_heldout_models; it is run here if missing)

clear; close all
if ~isfile('heldout.mat'), step1_heldout_models; end
H = load('heldout.mat');  C = lake_style();
cols = {C.grey, C.canada, C.alps, C.ink};
names = {'Model 1 - 3 variables + continent', 'Model 2 - Model 1 + nearby lakes', ...
         'Model 3 - 7 variables', 'Model 4 - all variables + nearby lakes'};
bands = 0:5:65;
figure('Position', [100 100 850 420]); hold on; grid on
h = zeros(1, 4);
for m = 1:4
    e = abs(H.y - H.P(:, m));  v = nan(size(bands));
    for j = 1:numel(bands)
        k = H.lat > bands(j) & H.lat <= bands(j) + 5;
        if any(k), v(j) = median(e(k)); end
    end
    h(m) = plot(bands + 2.5, v, '-o', 'Color', cols{m}, 'MarkerFaceColor', cols{m}, 'MarkerSize', 4, 'LineWidth', 1.8);
end
plot([33 33], [0 3.6], ':', 'Color', C.grey);
text(33.5, 0.2, '33°N split', 'FontSize', 8, 'Color', C.grey);
ylim([0 3.6]); xlim([0 70]);
xlabel('Latitude (°N, 5° bands)'); ylabel('Typical error (°C)');
title('Typical error by latitude (lakes not used to fit the model)', 'FontWeight', 'normal');
try, legend(h, names, 'Location', 'southoutside', 'NumColumns', 2); catch, legend(h, names, 'Location', 'southoutside'); end
save_fig('fig15_error_by_latitude');
