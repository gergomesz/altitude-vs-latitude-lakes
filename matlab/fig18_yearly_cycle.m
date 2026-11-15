%% fig18_yearly_cycle.m  -  Figure 18
% the yearly cycle of lakes that never freeze
%   a: median temperature in each month, by distance from the equator (lakes below 500 m)
%   b: yearly average vs distance from the equator      c: size of the summer-winter swing
%   d: distance to the sea and the swing, at the same latitude
% needs yearfit.mat (step2_yearly_fit)

clear; close all
R = load('yearfit.mat');  O = R.O;  C = lake_style();
mons = {'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'};
figure('Position', [100 100 1200 960]);

% a. median yearly curve per 10 degree band
subplot(2, 2, 1); hold on; grid on
bands = 0:10:50;  cm = interp1([0 1], [0.27 0.00 0.33; 0.74 0.87 0.18], linspace(0, 1, numel(bands)));
h = zeros(1, numel(bands));  lab = cell(1, numel(bands));
for j = 1:numel(bands)
    k = O.phi >= bands(j) & O.phi < bands(j) + 10 & O.elev < 500;
    h(j) = plot(1:12, median(O.Ts(k, :), 1), '-o', 'Color', cm(j, :), 'MarkerFaceColor', cm(j, :), 'MarkerSize', 3.5);
    lab{j} = sprintf('%d-%d° (%s)', bands(j), bands(j) + 10, commas(sum(k)));
end
set(gca, 'XTick', 1:12, 'XTickLabel', mons); ylim([0 40]); xlim([0.5 12.5]);
xlabel('Month (southern lakes shifted 6 months, so July = midsummer in both)');
ylabel('Median lake surface temperature (°C)');
title('a - The yearly cycle by distance from the equator (lakes below 500 m)', 'FontWeight', 'normal');
try, legend(h, lab, 'Location', 'north', 'NumColumns', 3); catch, legend(h, lab, 'Location', 'north'); end

% b and c: yearly average and swing against distance from the equator, north vs south
col = {C.ink, C.alps};  mk = {'o', 's'};  hn = {'Northern Hemisphere', 'Southern Hemisphere'};
vals = {O.Tbar, 2 * O.amp};
for pnl = 1:2
    subplot(2, 2, pnl + 1); hold on; grid on
    if pnl == 2   % grey band first, so the lines stay on top of it
        patch([R.bkA 62 62 R.bkA], [0 0 32 32], C.wash, 'EdgeColor', 'none');
    end
    hh = zeros(1, 2);
    for s = 0:1
        k = O.S == s & O.elev < 500;
        [x, q] = binned(O.phi(k), vals{pnl}(k), 0:2.5:62.5);
        fill([x; flipud(x)], [q(:, 1); flipud(q(:, 3))], col{s + 1}, 'FaceAlpha', 0.12, 'EdgeColor', 'none');
        hh(s + 1) = plot(x, q(:, 2), ['-' mk{s + 1}], 'Color', col{s + 1}, 'MarkerFaceColor', 'w', 'MarkerSize', 4);
    end
    xlabel('Distance from the equator (°)'); xlim([0 62]);
    if pnl == 1
        plot(R.bkM * [1 1], [4 32], '--', 'Color', C.grey);  plot([33 33], [4 32], ':', 'Color', C.grey);
        text(R.bkM + 0.8, 14, sprintf('yearly average\nstarts falling\nat %.1f°', R.bkM), 'HorizontalAlignment', 'left', 'FontSize', 8);
        text(34, 31, sprintf('July temperature\nstarts falling at 33°'), 'VerticalAlignment', 'top', 'FontSize', 8);
        ylim([4 32]); ylabel('Yearly average temperature (°C)');
        title('b - Yearly average', 'FontWeight', 'normal');
        legend(hh, hn, 'Location', 'southwest');
    else
        text(R.bkA + 1, 1.2, sprintf('past ~40°, only lakes in mild,\nsea-side climates stay unfrozen,\nso the swing looks smaller'), ...
             'VerticalAlignment', 'bottom', 'FontSize', 8);
        ylim([0 32]); ylabel('Summer-winter swing (°C)');
        title('c - How big the seasonal swing is', 'FontWeight', 'normal');
        legend(hh, hn, 'Location', 'northwest');
    end
end

% d. distance to the sea and the swing, at the same latitude
subplot(2, 2, 4); hold on; grid on
bc = {[0.48 0.61 0.78], [0.12 0.25 0.45]};  hh = zeros(1, 2);  lb = {};
for j = 1:2
    lo = 10 + 10 * j;
    k = O.phi >= lo & O.phi < lo + 10 & O.elev < 500;
    [x, q] = binned(O.coast(k), 2 * O.amp(k), [0 10 25 50 100 200 400 800 1600 3000]);
    fill([x; flipud(x)], [q(:, 1); flipud(q(:, 3))], bc{j}, 'FaceAlpha', 0.15, 'EdgeColor', 'none');
    hh(j) = plot(x, q(:, 2), '-o', 'Color', bc{j}, 'MarkerFaceColor', 'w', 'MarkerSize', 4);
    lb{j} = sprintf('lakes %d-%d° from the equator', lo, lo + 10);
end
set(gca, 'XScale', 'log'); ylim([0 32]); xlim([3 3000]);
xlabel('Distance to the sea (km, log scale)'); ylabel('Summer-winter swing (°C)');
title('d - Distance to the sea and the swing (same latitude)', 'FontWeight', 'normal');
legend(hh, lb, 'Location', 'northwest');
save_fig('fig18_yearly_cycle');
