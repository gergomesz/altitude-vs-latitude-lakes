%% fig13_predicted_vs_actual.m  -  Figure 13
% predicted vs actual July temperature for every lake, one panel per model,
% using predictions for lakes the model was NOT fitted to.
% needs heldout.mat (made by step1_heldout_models; it is run here if missing)

clear; close all
if ~isfile('heldout.mat'), step1_heldout_models; end
H = load('heldout.mat');  C = lake_style();
titles = {{'Model 1 - 3 variables', '+ continent'}, {'Model 2 - Model 1', '+ nearby lakes'}, ...
          {'Model 3 - 7 variables', '(no correction)'}, {'Model 4 - all variables', '+ nearby lakes'}};
edges = 0:0.5:36;  nb = numel(edges) - 1;
% count lakes in each 0.5 x 0.5 C box, for every model, so all panels share one colour scale
cnt = cell(1, 4);  top = 0;
for m = 1:4
    ix = min(max(floor(H.y / 0.5) + 1, 1), nb);
    iy = min(max(floor(H.P(:, m) / 0.5) + 1, 1), nb);
    cnt{m} = accumarray([iy ix], 1, [nb nb]);
    top = max(top, max(cnt{m}(:)));
end
figure('Position', [100 100 1300 420]);
pos = @(m) [0.055 + (m - 1) * 0.205, 0.17, 0.17, 0.62];    % same size for all four panels
ax = zeros(1, 4);
for m = 1:4
    ax(m) = axes('Position', pos(m));
    v = log10(cnt{m}) / log10(top);                 % 0 (one lake) .. 1 (fullest box), log scale
    idx = max(1, round(v * 255) + 1);
    rgb = ones(nb, nb, 3);                            % white where there are no lakes
    for ch = 1:3
        layer = C.seq(idx, ch);  layer = reshape(layer, nb, nb);
        layer(cnt{m} == 0) = 1;  rgb(:, :, ch) = layer;
    end
    image([0.25 35.75], [0.25 35.75], rgb); set(gca, 'YDir', 'normal'); hold on
    plot([0 36], [0 36], '--', 'Color', C.alps, 'LineWidth', 1.1);
    axis([0 36 0 36]); axis square
    e = H.y - H.P(:, m);  r2 = 1 - sum(e.^2) / sum((H.y - mean(H.y)).^2);
    title([titles{m}, {sprintf('R^2 %.2f, typical error %.1f °C', r2, median(abs(e)))}], 'FontWeight', 'normal', 'FontSize', 9);
    xlabel('Actual (°C)');
    if m == 1, ylabel('Predicted July temperature (°C)'); end
end
colormap(C.seq);
caxis([0 log10(top)]);  t = 0:floor(log10(top));  tl = arrayfun(@(k) sprintf('%d', 10^k), t, 'UniformOutput', false);
cb = colorbar;
try, set(cb, 'Ticks', t, 'TickLabels', tl); catch, set(cb, 'YTick', t, 'YTickLabel', tl); end
ylabel(cb, 'lakes per box (log scale)');
for m = 1:4, set(ax(m), 'Position', pos(m)); end    % the colour bar must not shrink the last panel
set(cb, 'Position', [0.885 0.2 0.012 0.56]);
save_fig('fig13_predicted_vs_actual');
