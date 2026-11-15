%% fig19_timing_ice_prediction.m  -  Figure 19
%   a: deep lakes reach their warmest later          b: lakes that freeze: how long they stay open
%   c: four lakes not used in fitting, measured vs predicted year
%   d: typical error of the whole-year prediction, by month
% needs yearfit.mat (step2_yearly_fit)

clear; close all
R = load('yearfit.mat');  O = R.O;  F = R.F;  C = lake_style();
mons = {'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'};
figure('Position', [100 100 1200 960]);

% a. days between mid-July and the warmest point, by depth
subplot(2, 2, 1); hold on; grid on
k = O.amp > 1.5;
[x, q] = binned(O.depth(k), (O.peak(k) - 7) * 30.4, [0.3 1 2 4 8 16 32 64 128 256 600]);
fill([x; flipud(x)], [q(:, 1); flipud(q(:, 3))], C.alps, 'FaceAlpha', 0.15, 'EdgeColor', 'none');
plot(x, q(:, 2), '-o', 'Color', C.alps, 'MarkerFaceColor', 'w', 'MarkerSize', 4);
plot([0.3 600], [0 0], ':', 'Color', C.grey);
set(gca, 'XScale', 'log');  xlim([0.4 100]);
xlabel('Mean lake depth (m, log scale)'); ylabel('Warmest point, days after mid-July');
title('a - Deep lakes reach their warmest later', 'FontWeight', 'normal');

% b. ice-free days by latitude, one line per height band (Northern Hemisphere)
subplot(2, 2, 2); hold on; grid on
eb = [-500 500; 500 1500; 1500 3000; 3000 7000];  bc = {[0.61 0.72 0.83], [0.31 0.49 0.67], [0.12 0.25 0.45], C.ink};
mk = {'o', 's', '^', 'd'};  hh = zeros(1, 4);  lb = cell(1, 4);
for j = 1:4
    kk = F.S == 0 & F.elev >= eb(j, 1) & F.elev < eb(j, 2);
    [x, q] = binned(F.phi(kk), F.odays(kk), 20:2:72);
    hh(j) = plot(x, q(:, 2), ['-' mk{j}], 'Color', bc{j}, 'MarkerFaceColor', 'w', 'MarkerSize', 4);
    lb{j} = sprintf('%d-%d m', max(eb(j, 1), 0), eb(j, 2));
end
plot(R.bkO * [1 1], [0 365], '--', 'Color', C.grey);
text(R.bkO + 0.6, 345, sprintf('slows down\npast %.1f°', R.bkO), 'VerticalAlignment', 'top', 'FontSize', 8);
axis([20 71 0 365]);
xlabel('Latitude (°N)'); ylabel('Ice-free days per year (median)');
title('b - Lakes that freeze: how long they stay open', 'FontWeight', 'normal');
legend(hh, lb, 'Location', 'southwest');

% c. four example lakes: measured months (dots) and the year predicted from geography (lines)
subplot(2, 2, 3); hold on; grid on
ex = {'Tonle Sap', 'Titicaca', 'Geneva', 'Taupo'};
ec = {[0.16 0.62 0.56], [0.48 0.37 0.65], C.ink, C.alps};
hh = [];  lb = {};
mm = linspace(0.5, 12.5, 200);
for j = 1:numel(ex)
    i = find(strcmp(O.name, ex{j}), 1);
    if isempty(i), continue; end
    act = O.Ts(i, :);  pr = O.pred(i, :);
    % back to the real calendar for southern lakes, and a smooth line through the 12 predicted months
    if O.S(i) == 1, act = circshift(act, -6, 2); pr = circshift(pr, -6, 2); end
    c1 = pr * cos(2 * pi * ((1:12)' - 0.5) / 12) * 2 / 12;  s1 = pr * sin(2 * pi * ((1:12)' - 0.5) / 12) * 2 / 12;
    smooth = mean(pr) + c1 * cos(2 * pi * (mm - 0.5) / 12) + s1 * sin(2 * pi * (mm - 0.5) / 12);
    plot(1:12, act, 'o', 'Color', ec{j}, 'MarkerFaceColor', ec{j}, 'MarkerSize', 5);
    hh(end + 1) = plot(mm, smooth, '-', 'Color', ec{j}, 'LineWidth', 1.4);
    lb{end + 1} = sprintf('%s (%.0f°%s, %s m)', ex{j}, abs(O.lat(i)), char('N' + 5 * O.S(i)), commas(round(O.elev(i))));
end
set(gca, 'XTick', 1:12, 'XTickLabel', mons); axis([0.6 12.4 0 36]);
xlabel('Month (real calendar)'); ylabel('Surface temperature (°C)');
title('c - Measured (dots) vs predicted year (lines), unseen lakes', 'FontWeight', 'normal');
if ~isempty(hh), try, legend(hh, lb, 'Location', 'north', 'NumColumns', 2); catch, legend(hh, lb, 'Location', 'north'); end, end

% d. typical error by month
subplot(2, 2, 4); hold on
bar(1:12, R.maeMonth, 0.7, 'FaceColor', [0.31 0.49 0.67], 'EdgeColor', 'none');
for j = 1:12, text(j, R.maeMonth(j) + 0.05, sprintf('%.1f', R.maeMonth(j)), 'HorizontalAlignment', 'center', 'FontSize', 8); end
set(gca, 'XTick', 1:12, 'XTickLabel', mons); ylim([0 2.6]); xlim([0.4 12.6]);
xlabel('Month (southern lakes shifted 6 months)'); ylabel('Typical error on unseen lakes (°C)');
title(sprintf('d - Whole-year prediction: R^2 = %.2f, typical error %.1f °C', R.r2year, mean(R.maeMonth)), 'FontWeight', 'normal');
save_fig('fig19_timing_ice_prediction');
