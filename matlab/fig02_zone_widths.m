%% fig02_zone_widths.m  -  Figure II
% the same zone equation with 2.5, 5 and 10 degree zones, to choose a zone width

clear; close all
L = load('lakes.mat');  C = lake_style();
widths = [2.5 5 10];
cols   = {C.grey, C.ink, C.alps};
marks  = {'o', 's', 'd'};

figure('Position', [100 100 1150 420]);
for p = 1:2
    subplot(1, 2, p); hold on; grid on
end
h = zeros(1, 3);
for i = 1:3
    Z = zone_fit(L, widths(i));
    ok = ~isnan([Z.per_km]);
    x = [Z(ok).z0] + widths(i) / 2;
    fprintf('%g degree zones: %d of %d fitted\n', widths(i), sum(ok), numel(Z));

    subplot(1, 2, 1)
    if widths(i) > 2.5   % 95% confidence band for the 5 and 10 degree zones
        fill([x fliplr(x)], [[Z(ok).km_lo] fliplr([Z(ok).km_hi])], cols{i}, 'FaceAlpha', 0.12, 'EdgeColor', 'none');
    end
    h(i) = plot(x, [Z(ok).per_km], ['-' marks{i}], 'Color', cols{i}, 'MarkerFaceColor', 'w');

    subplot(1, 2, 2)
    if widths(i) > 2.5
        fill([x fliplr(x)], [[Z(ok).deg_lo] fliplr([Z(ok).deg_hi])], cols{i}, 'FaceAlpha', 0.12, 'EdgeColor', 'none');
    end
    plot(x, [Z(ok).per_deg], ['-' marks{i}], 'Color', cols{i}, 'MarkerFaceColor', 'w');
end
subplot(1, 2, 1)
xlabel('Zone centre (°N)'); ylabel('July temperature change per km of altitude (°C)');
legend(h, {'2.5° zones', '5° zones', '10° zones'}, 'Location', 'southwest');
title('a · Altitude effect (shading = 95% CI)', 'FontWeight', 'normal');
subplot(1, 2, 2)
plot([0 70], [0 0], ':', 'Color', C.grey);
xlabel('Zone centre (°N)'); ylabel('July temperature change per degree north (°C)');
text(69, 0.04, 'no latitude effect', 'FontSize', 8, 'Color', C.grey, 'VerticalAlignment', 'bottom', 'HorizontalAlignment', 'right');
title('b · Latitude effect (shading = 95% CI)', 'FontWeight', 'normal');
save_fig('fig02_zone_widths');
