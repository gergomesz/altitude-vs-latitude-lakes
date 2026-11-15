%% fig10_alps_residual_map.m  -  Figure X
% which Alps-band lakes are warmer or colder than the zone equation predicts?

clear; close all
L = load('lakes.mat');  C = lake_style();

% 1. one model for the whole hemisphere where every 5 degree zone gets its own
%    intercept, its own altitude slope and its own latitude slope (depth is shared):
%    July = a_zone + b_zone*elev_km + c_zone*lat + d*log10(depth)
zone = floor((L.lat - 1e-9) / 5) + 1;          % zone 1 = 0-5 N, ..., zone 14 = 65-70 N
nz = max(zone);
design = @(idx) [double(zone(idx) == 1:nz), ...
                 double(zone(idx) == 1:nz) .* (L.elev(idx) / 1000), ...
                 double(zone(idx) == 1:nz) .* L.lat(idx), ...
                 L.logdepth(idx)];

% 2. solve it in chunks of 100,000 lakes so the laptop's memory never fills up
%    (adds up X'X and X'y piece by piece, then solves once)
n = numel(L.lat);  XtX = 0;  Xty = 0;
for s = 1:100000:n
    idx = (s:min(s + 99999, n))';
    X = design(idx);
    XtX = XtX + X' * X;
    Xty = Xty + X' * L.july(idx);
end
b = XtX \ Xty;

% 3. residual = observed minus predicted, for lakes in the Alps band only
A = find(L.lat >= 45.8 & L.lat <= 47.8);
res = L.july(A) - design(A) * b;
res = max(min(res, 6), -6);                    % colour scale stops at +-6 C
for r = 1:6
    fprintf('%-16s median residual %+.2f C (%d lakes)\n', L.regnames{r}, median(res(L.region(A) == r)), sum(L.region(A) == r));
end

% 4. three maps: North America, Europe, Asia (Europe gets its own panel so it isn't squashed)
figure('Position', [100 100 1200 760]);
ext = {[-128 -52 45.3 48.3], [-5 50 45.3 48.3], [50 145 45.3 48.3]};
ttl = {'North America', 'Europe', 'Asia'};
names = {{'USA', -112, 48.05; 'CANADA', -80, 48.05; 'USA', -100, 45.55; 'USA', -88, 45.55; 'CANADA', -76, 45.55}, ...
         {'FRANCE', 2, 48.05; 'GERMANY', 9, 48.05; 'AUSTRIA', 15, 48.05; 'SLOVAKIA', 19.5, 48.05; 'UKRAINE', 32, 48.05; ...
          'RUSSIA', 45, 48.05; 'ITALY', 10, 45.55; 'CROATIA', 16, 45.55; 'ROMANIA', 25, 45.55}, ...
         {'KAZAKHSTAN', 70, 48.05; 'MONGOLIA', 100, 48.05; 'CHINA', 124, 48.05; 'CHINA', 88, 45.55; 'RUSSIA', 136, 48.05}};
bottoms = [0.68 0.38 0.08];                    % each map gets its own fixed place, with room for titles
for p = 1:3
    axes('Position', [0.08 bottoms(p) 0.80 0.19]);
    draw_land(ext{p}, C.wash);
    draw_borders(ext{p});                      % country lines solid, state/province lines dotted
    scatter(L.lon(A), L.lat(A), 8, res, 'filled');
    colormap(C.div); caxis([-6 6]);
    if p == 1
        title({'Alps latitude (45.8–47.8°N): lakes warmer (red) or colder (blue) than the zone equation predicts', ttl{p}}, 'FontWeight', 'normal');
    else
        title(ttl{p}, 'FontWeight', 'normal');
    end
    for q = 1:size(names{p}, 1)                % country names, in grey, above and below the band
        text(names{p}{q, 2}, names{p}{q, 3}, names{p}{q, 1}, 'FontSize', 7.5, 'Color', [0.35 0.35 0.38], ...
             'HorizontalAlignment', 'center', 'BackgroundColor', C.wash, 'Margin', 1, 'Clipping', 'off');
    end
    ylabel('Latitude (°N)');
    if p == 3, xlabel('Longitude (°E)'); end
end
pos = get(gca, 'Position');
cb = colorbar; set(gca, 'Position', pos); set(cb, 'Position', [0.91 0.08 0.012 0.79]);
ylabel(cb, 'Observed minus predicted July temperature (°C)');
save_fig('fig10_alps_residual_map');
