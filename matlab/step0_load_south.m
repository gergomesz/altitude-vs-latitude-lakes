%% step0_load_south.m
% reads the Southern Hemisphere lakes from laketemp_clean.csv.gz and saves south.mat
% run this ONCE before fig17_hemispheres.m (it needs coast_distance_grid_south.mat in this folder)
% January is the summer month in the south, so January is used instead of July

clear; clc
fn = 'laketemp_clean.csv.gz';
if ~isfile(fn), fn = 'laketemp_clean_csv.gz'; end
if ~isfile(fn), error('put laketemp_clean.csv.gz in this folder first'); end

f = gunzip(fn);  f = f{1};
opts = detectImportOptions(f, 'FileType', 'text');
opts.SelectedVariableNames = {'center_lat', 'center_long', 'Depth_avg', 'Elevation', 'Tmonth_mean_1'};
T = readtable(f, opts);
delete(f);

k = T.center_lat < 0 & T.Tmonth_mean_1 > 0 & T.Tmonth_mean_1 < 40;
T = T(k, :);

lat   = T.center_lat;           % negative = south
lon   = T.center_long;
alat  = abs(lat);               % distance from the equator, degrees
elev  = T.Elevation;
jan   = T.Tmonth_mean_1;        % January mean surface temperature, C
logdepth = log10(max(T.Depth_avg, 0.3));
cell  = floor(lat) * 1000 + floor(lon) + 500;

% distance to the sea, read off the 0.1 degree grid
G = load('coast_distance_grid_south.mat');
coast = interp2(G.glon, G.glat, double(G.dist_km), lon, lat, 'linear');

save('south.mat', 'lat', 'lon', 'alat', 'elev', 'jan', 'logdepth', 'cell', 'coast', '-v7');
fprintf('%d southern lakes saved to south.mat (%d above 1000 m)\n', numel(lat), sum(elev > 1000));
