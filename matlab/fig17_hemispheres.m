%% fig17_hemispheres.m  -  Figure 17
% Northern Hemisphere in July vs Southern Hemisphere in January (each hemisphere's summer)
% needs lakes.mat (step0_load_data), south.mat (step0_load_south) and both coast grids
%   a: altitude effect in 5 degree zones      b: latitude effect in 5 degree zones
%   c: where latitude starts to matter        d: does the northern equation work in the south?
% both hemispheres use the same simple model: distance from the equator, height, depth

clear; close all
L = load('lakes.mat');  S = load('south.mat');  C = lake_style();
G = load('coast_distance_grid.mat');
L.coast = interp2(G.glon, G.glat, double(G.dist_km), L.lon, L.lat, 'linear');

% the two hemispheres in the same form: distance from equator, km, depth term, summer temperature
H(1) = struct('alat', L.lat, 'km', L.elev / 1000, 'ld', L.logdepth - log10(3.3), 'T', L.july, ...
              'C', log10(L.coast + 10), 'cell', L.cell, 'elev', L.elev);
H(2) = struct('alat', S.alat, 'km', S.elev / 1000, 'ld', S.logdepth - log10(3.3), 'T', S.jan, ...
              'C', log10(S.coast + 10), 'cell', S.cell, 'elev', S.elev);
name = {'Northern Hemisphere, July', 'Southern Hemisphere, January'};
col  = {C.ink, C.alps};  mk = {'o', 's'};

%% 1. 5 degree zones: T = a + b_lat*(distance - zone middle) + b_km*km + c*depth
for s = 1:2
    Z{s} = [];
    for z0 = 0:5:55
        k = H(s).alat > z0 & H(s).alat <= z0 + 5;
        if sum(k) < 200 || sum(k & H(s).elev > 1000) < 20, continue, end
        X = [ones(sum(k), 1), H(s).alat(k) - (z0 + 2.5), H(s).km(k), H(s).ld(k)];
        [b, se] = ols_cl(X, H(s).T(k), H(s).cell(k));
        Z{s}(end + 1, :) = [z0 + 2.5, b(3), b(3) - 1.96 * se(3), b(3) + 1.96 * se(3), b(2), b(2) - 1.96 * se(2), b(2) + 1.96 * se(2)]; %#ok<SAGROW>
    end
end

%% 2. sliding 2 degree band and its breakpoint
for s = 1:2
    SL{s} = [];
    for c = 1:68
        k = H(s).alat >= c - 1 & H(s).alat < c + 1;
        if sum(k) < 150 || sum(k & H(s).elev > 1000) < 15, continue, end
        b = [ones(sum(k), 1), H(s).km(k), H(s).ld(k)] \ H(s).T(k);
        SL{s}(end + 1, :) = [c, b(1)]; %#ok<SAGROW>
    end
    bpgrid = 15:0.5:50;
    [bp(s), bb] = broken_stick(SL{s}(:, 1), SL{s}(:, 2), ones(size(SL{s}, 1), 1), bpgrid); %#ok<SAGROW>
    rng(0);  n = size(SL{s}, 1);  boots = zeros(300, 1);
    for r = 1:300
        i = randi(n, n, 1);
        boots(r) = broken_stick(SL{s}(i, 1), SL{s}(i, 2), ones(n, 1), bpgrid);
    end
    bci(s, :) = [pct(boots, 2.5), pct(boots, 97.5)]; %#ok<SAGROW>
    fprintf('%s: break at %.1f deg (95%% range %.1f-%.1f), %.2f C per degree after it\n', name{s}, bp(s), bci(s, 1), bci(s, 2), bb(2) + bb(3));
end

%% 3. fit the 3-variable split equation (distance, km, coast) on the north, use it on the south
pred = zeros(numel(H(2).T), 1);
for side = 0:1
    kn = (H(1).alat > 33) == side;  ks = (H(2).alat > 33) == side;
    b = [ones(sum(kn), 1), H(1).alat(kn), H(1).km(kn), H(1).C(kn)] \ H(1).T(kn);
    pred(ks) = [ones(sum(ks), 1), H(2).alat(ks), H(2).km(ks), H(2).C(ks)] * b;
end
e = H(2).T - pred;
r2 = 1 - sum(e.^2) / sum((H(2).T - mean(H(2).T)).^2);
fprintf('northern equation on southern lakes: R2 = %.2f, typical error %.1f C, %.1f C too warm on average\n', r2, median(abs(e)), -mean(e));

%% draw
figure('Position', [100 100 1200 900]);
h = zeros(1, 2);
for s = 1:2
    subplot(2, 2, 1); hold on; grid on
    x = Z{s}(:, 1);
    fill([x; flipud(x)], [Z{s}(:, 3); flipud(Z{s}(:, 4))], col{s}, 'FaceAlpha', 0.12, 'EdgeColor', 'none');
    h(s) = plot(x, Z{s}(:, 2), ['-' mk{s}], 'Color', col{s}, 'MarkerFaceColor', 'w');
    subplot(2, 2, 2); hold on; grid on
    fill([x; flipud(x)], [Z{s}(:, 6); flipud(Z{s}(:, 7))], col{s}, 'FaceAlpha', 0.12, 'EdgeColor', 'none');
    plot(x, Z{s}(:, 5), ['-' mk{s}], 'Color', col{s}, 'MarkerFaceColor', 'w');
end
subplot(2, 2, 1)
xlabel('Distance from the equator (°, 5° zones)'); ylabel('Temperature change per km of altitude (°C)');
title('a - Altitude effect', 'FontWeight', 'normal');
ylim([-6.5 1.5]); legend(h, name, 'Location', 'southwest');
subplot(2, 2, 2)
plot([0 60], [0 0], ':', 'Color', C.grey);
xlabel('Distance from the equator (°, 5° zones)'); ylabel('Temperature change per degree poleward (°C)');
title('b - Latitude effect', 'FontWeight', 'normal');

subplot(2, 2, 3); hold on; grid on
hb = zeros(1, 2);
for s = 1:2
    fill([bci(s, 1) bci(s, 2) bci(s, 2) bci(s, 1)], [10 10 32 32], col{s}, 'FaceAlpha', 0.1, 'EdgeColor', 'none');
    plot([bp(s) bp(s)], [10 32], '--', 'Color', col{s});
    hb(s) = plot(SL{s}(:, 1), SL{s}(:, 2), mk{s}, 'Color', col{s}, 'MarkerSize', 4, 'MarkerFaceColor', 'w');
end
ylim([10 33]); xlim([0 70]);
xlabel('Distance from the equator (°, sliding 2° band)'); ylabel('Predicted summer temperature at sea level (°C)');
title('c - Where latitude starts to matter', 'FontWeight', 'normal');
legend(hb, {sprintf('North: break at %.1f° (%.1f-%.1f)', bp(1), bci(1, 1), bci(1, 2)), ...
            sprintf('South: break at %.1f° (%.1f-%.1f)', bp(2), bci(2, 1), bci(2, 2))}, 'Location', 'southoutside');

subplot(2, 2, 4); hold on
% 2-D histogram of actual vs predicted, coloured by number of lakes (log scale)
w = 0.75;  nb = 48;                             % 48 boxes of 0.75 C from 0 to 36 C
ix = min(max(floor(H(2).T / w) + 1, 1), nb);  iy = min(max(floor(pred / w) + 1, 1), nb);
N = accumarray([iy ix], 1, [nb nb]);             % rows = predicted, columns = actual
cen = (1:nb) * w - w / 2;
% colour each box by log10(number of lakes); empty boxes stay white
ci = round(1 + 255 * log10(max(N, 1)) / max(log10(max(N(:), 2))));
RGB = reshape(C.seq(ci, :), [nb nb 3]);
RGB(repmat(N == 0, [1 1 3])) = 1;
image(cen, cen, RGB);
set(gca, 'YDir', 'normal'); colormap(gca, C.seq);
plot([0 36], [0 36], '--', 'Color', C.alps);
axis([0 36 0 42]);
text(1, 41, sprintf('Northern equation on southern lakes:\nR^2 = %.2f, typical error %.1f °C,\n%.1f °C too warm on average', r2, median(abs(e)), -mean(e)), ...
     'VerticalAlignment', 'top', 'FontSize', 9);
xlabel('Actual January temperature, southern lakes (°C)'); ylabel('Predicted by the northern July equation (°C)');
title('d - Does the northern equation work in the south?', 'FontWeight', 'normal');
save_fig('fig17_hemispheres');
