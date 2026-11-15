%% step1_heldout_models.m
% fits the four July models and tests each one on lakes it was NOT fitted to:
% the 1x1 degree squares are split into 5 groups, and each group is predicted by
% models fitted to the other four. Saves heldout.mat for fig13 and fig15.
% needs lakes.mat (step0_load_data) and coast_distance_grid.mat. Takes a few minutes.
%   Model 1: latitude, height, coast, continent (split at 33 N) + big-lake adjustment
%   Model 2: Model 1 + nearby-lakes correction (+ big-lake adjustment)
%   Model 3: 7 variables (split at 33 N)
%   Model 4: one equation per 5-degree zone x continent + nearby-lakes correction

clear; clc
L = load('lakes.mat');
if ~isfield(L, 'area'), error('lakes.mat has no lake areas yet: run the new step0_load_data.m once'); end
G = load('coast_distance_grid.mat');
coast = interp2(G.glon, G.glat, double(G.dist_km), L.lon, L.lat, 'linear');
y = L.july;  lat = L.lat;  lon = L.lon;  n = numel(y);

% the variables
km  = L.elev / 1000;                          % height, km
hp  = max(km - 1.5, 0);                       % extra height above 1.5 km
Cc  = log10(coast + 10);                      % distance to the sea
D   = L.logdepth - log10(3.3);                % depth (0 = typical 3.3 m lake)
A   = log10(max(L.area, 0.01)) - log10(0.23); % area  (0 = typical 0.23 km2 lake)
K   = double(L.region(:) == 2:6);             % continent shift (W. North America = 0)
side = double(lat > 33);
zone = floor((lat - 1e-9) / 5);  mid = zone * 5 + 2.5;
X3 = [lat km Cc K];
X7 = [lat km hp Cc D A K];
XZ = [lat - mid, km, hp, Cc, D, A];
SHRINK = 20;

% the 5 test groups, by 1x1 degree square
[~, ~, ci] = unique(L.cell);
rng(0);  fc = randi(5, max(ci), 1);  fold = fc(ci);

P = zeros(n, 4);          % columns: Model 1, Model 2, Model 3, Model 4
for f = 1:5
    tr = fold ~= f;  te = ~tr;
    p3 = model_split(X3, y, side, tr);
    p7 = model_split(X7, y, side, tr);
    pZ = model_zones(XZ, p7, y, zone, L.region, km, tr);
    c3 = model_nearby(lat, lon, y - p3, tr, SHRINK);      % corrections use training lakes only
    cZ = model_nearby(lat, lon, y - pZ, tr, SHRINK);
    P(te, 1) = p3(te);
    P(te, 2) = p3(te) + c3(te);
    P(te, 3) = p7(te);
    P(te, 4) = pZ(te) + cZ(te);
    fprintf('test group %d of 5 done\n', f);
end

% big-lake adjustment for Models 1 and 2 (lakes of 500 km2 or more), leave-one-out
big = find(L.area >= 500);
Z = [ones(numel(big), 1), log10(L.area(big)) - log10(500), D(big), lat(big) - 50];
for m = 1:2
    r = y(big) - P(big, m);  adj = zeros(numel(big), 1);
    for i = 1:numel(big)
        k = true(numel(big), 1);  k(i) = false;
        adj(i) = Z(i, :) * (Z(k, :) \ r(k));
    end
    P(big, m) = P(big, m) + adj;
end

% how close each model gets
names = {'Model 1 - 3 variables + continent', 'Model 2 - Model 1 + nearby lakes', ...
         'Model 3 - 7 variables', 'Model 4 - all variables + nearby lakes'};
fprintf('\n%-42s %6s %14s %10s %10s\n', 'lakes not used to fit the model', 'R2', 'typical error', 'within 1', 'within 2');
for m = 1:4
    e = y - P(:, m);
    fprintf('%-42s %6.3f %12.2f C %9.0f%% %9.0f%%\n', names{m}, 1 - sum(e.^2) / sum((y - mean(y)).^2), ...
        median(abs(e)), 100 * mean(abs(e) <= 1), 100 * mean(abs(e) <= 2));
end
save('heldout.mat', 'P', 'y', 'lat', 'names', '-v7');
disp('saved heldout.mat');
