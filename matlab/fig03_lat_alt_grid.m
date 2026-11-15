%% fig03_lat_alt_grid.m  -  Figure III
% median July temperature in every 1 degree x 100 m box (the squares, real data)
% the empty boxes in between are filled in by interpolating from the real boxes
% around them, so the isotherms can be drawn as continuous lines

clear; close all
L = load('lakes.mat');  C = lake_style();

%% 1. real data: put every lake into a box, take the median of each box
lb = 0:1:70;  eb = 0:100:4600;
k  = L.elev >= 0 & L.elev < 4600 & L.lat < 70;
i  = floor(L.lat(k)) + 1;            % column: 1 = 0-1 N, 2 = 1-2 N, ...
j  = floor(L.elev(k) / 100) + 1;     % row:    1 = 0-100 m, 2 = 100-200 m, ...
t  = L.july(k);
M = accumarray([j i], t, [numel(eb)-1, numel(lb)-1], @median, NaN);
N = accumarray([j i], 1, [numel(eb)-1, numel(lb)-1]);
M(N < 8) = NaN;                       % a box needs at least 8 lakes
xc = lb(1:end-1) + 0.5;  yc = eb(1:end-1) + 50;
[X, Y] = meshgrid(xc, yc);

%% 2. predict the empty boxes
% (a) join the real boxes into triangles and read each empty box off the triangle
%     it falls in (linear interpolation). Outside the outermost real boxes there is
%     nothing to interpolate from, so those stay empty.
%     Heights are in 100 m steps so 1 box across = 1 box up.
have = ~isnan(M);
F = griddata(X(have), Y(have) / 100, M(have), X, Y / 100, 'linear');
% (b) blur a little so the lines show the overall pattern, not box-to-box noise
[gx, gy] = meshgrid(-4:4);
K = exp(-(gx.^2 + gy.^2) / (2 * 1.5^2));
W = double(~isnan(F));  F0 = F;  F0(isnan(F)) = 0;
S = conv2(F0, K, 'same') ./ conv2(W, K, 'same');   % average of the boxes nearby that have a value
S(isnan(F)) = NaN;
% (c) only keep filled-in boxes that are close to real data (within 3 boxes);
%     further away the gap is too big to fill honestly
near = conv2(double(have), ones(7), 'same') > 0;
F(~near) = NaN;  S(~near) = NaN;

%% 3. draw
figure('Position', [100 100 1000 560]); hold on
tocol = @(T) C.seq(round(1 + 255 * (min(max(T, 8), 32) - 8) / 24), :);
RGB = ones([size(M) 3]);
for r = 1:size(M, 1)
    for c = 1:size(M, 2)
        if have(r, c)
            RGB(r, c, :) = tocol(M(r, c));                        % real data: full colour
        elseif ~isnan(F(r, c))
            RGB(r, c, :) = 0.35 * tocol(F(r, c)) + 0.65 * [1 1 1];  % filled in: faded
        end
    end
end
image(xc, yc, RGB);  set(gca, 'YDir', 'normal');
colormap(C.seq); caxis([8 32]);
cb = colorbar; ylabel(cb, 'Median July surface temperature (°C)');

[cc, hc] = contour(xc, yc, S, [12 16 20 24 28], 'LineColor', C.ink, 'LineWidth', 1.1);
clabel(cc, hc, 'FontSize', 8, 'LabelSpacing', 500);

% Alps and Canada bands
plot([45.8 45.8 47.8 47.8 45.8], [0 4600 4600 0 0], '--', 'Color', C.alps, 'LineWidth', 1.4);
plot([50 50 53 53 50], [0 4600 4600 0 0], ':', 'Color', C.canada, 'LineWidth', 1.6);
text(46.8, 4720, 'Alps', 'HorizontalAlignment', 'center', 'Color', C.alps, 'Clipping', 'off');
text(51.5, 4720, 'Canada', 'HorizontalAlignment', 'center', 'Color', C.canada, 'Clipping', 'off');
xlim([0 70]); ylim([0 4600]);
xlabel('Latitude (°N)'); ylabel('Lake elevation (m)');
title('Median July lake temperature by latitude and elevation (1° × 100 m boxes)', 'FontWeight', 'normal', 'Units', 'normalized', 'Position', [0.5 1.06 0]);
text(1, 3600, {'Bright squares: real lakes (median of each box)', 'Faded squares: filled in from the boxes around them', 'Lines: isotherms (July °C)'}, ...
     'FontSize', 8, 'VerticalAlignment', 'top');
% fixed positions: leave room above the plot for the Alps/Canada labels and the title
set(gca, 'Position', [0.08 0.11 0.78 0.74]);
set(cb, 'Position', [0.89 0.11 0.02 0.74]);
save_fig('fig03_lat_alt_grid');
