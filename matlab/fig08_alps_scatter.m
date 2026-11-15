%% fig08_alps_scatter.m  -  Figure VIII
% the Alps latitude (45.8-47.8 N) around the world: July temperature against height, by region

clear; close all
L = load('lakes.mat');  C = lake_style();
A = L.lat >= 45.8 & L.lat <= 47.8;

% only regions with enough high lakes to fit a slope (>= 100 lakes, >= 15 above 1000 m)
use = [];
for r = 1:6
    k = A & L.region == r;
    if sum(k) >= 100 && sum(k & L.elev > 1000) >= 15, use(end + 1) = r; end %#ok<AGROW>
end

figure('Position', [100 100 1300 380]);
for p = 1:numel(use)
    r = use(p);  k = A & L.region == r;
    b = [ones(sum(k), 1), L.elev(k) / 1000, L.logdepth(k)] \ L.july(k);
    subplot(1, numel(use), p); hold on; grid on
    scatter(L.elev(k), L.july(k), 6, C.grey, 'filled', 'MarkerFaceAlpha', 0.45);
    xx = linspace(0, max(L.elev(k)), 20);
    plot(xx, b(1) + b(3) * L.med_logdepth + b(2) * xx / 1000, '-', 'Color', C.alps, 'LineWidth', 1.8);
    title(sprintf('%s\n%.1f °C per km · %d lakes', L.regnames{r}, b(2), sum(k)), 'FontWeight', 'normal');
    xlim([-50 3300]); ylim([3 38]); set(gca, 'XTick', 0:1000:3000);
    xlabel('Lake elevation (m)');
    if p == 1
        ylabel({'July surface temperature (°C)', 'lakes at 45.8–47.8°N'});
        legend({'lakes', 'fitted line (median depth)'}, 'Location', 'southwest', 'FontSize', 8);
    end
end
save_fig('fig08_alps_scatter');
