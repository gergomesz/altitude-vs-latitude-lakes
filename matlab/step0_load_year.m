%% step0_load_year.m
% reads all 12 monthly temperatures and the ice-free days for every lake within 70 degrees
% of the equator (both hemispheres) and saves year.mat. Run this ONCE before step2_yearly_fit.
% needs laketemp_clean.csv.gz, coast_distance_grid.mat and coast_distance_grid_south.mat

clear; clc
fn = 'laketemp_clean.csv.gz';
if ~isfile(fn), fn = 'laketemp_clean_csv.gz'; end
if ~isfile(fn), error('put laketemp_clean.csv.gz in this folder first'); end
f = gunzip(fn);  f = f{1};
opts = detectImportOptions(f, 'FileType', 'text');
mon = arrayfun(@(m) sprintf('Tmonth_mean_%d', m), 1:12, 'UniformOutput', false);
opts.SelectedVariableNames = [{'center_lat', 'center_long', 'Lake_name', 'Lake_area', 'Depth_avg', 'Elevation', 'ice_days'}, mon];
opts = setvartype(opts, {'Lake_name'}, 'string');
Tb = readtable(f, opts);
delete(f);

Tb = Tb(abs(Tb.center_lat) <= 70, :);
lat   = Tb.center_lat;   lon = Tb.center_long;
elev  = Tb.Elevation;    depth = Tb.Depth_avg;   area = Tb.Lake_area;
ice   = Tb.ice_days;                             % days per year under ice
name  = Tb.Lake_name;    name(ismissing(name)) = "";
T     = Tb{:, mon};                              % n x 12, monthly mean surface temperature (0 = frozen)

% distance to the sea from the two 0.1 degree grids
Gn = load('coast_distance_grid.mat');  Gs = load('coast_distance_grid_south.mat');
coast = nan(size(lat));
n_ = lat >= 0;
coast(n_)  = interp2(Gn.glon, Gn.glat, double(Gn.dist_km), lon(n_),  lat(n_),  'linear');
coast(~n_) = interp2(Gs.glon, Gs.glat, double(Gs.dist_km), lon(~n_), lat(~n_), 'linear');
cell = floor(lat) * 1000 + floor(lon) + 500;

save('year.mat', 'lat', 'lon', 'elev', 'depth', 'area', 'ice', 'name', 'T', 'coast', 'cell', '-v7');
fprintf('%d lakes saved to year.mat (%d never freeze)\n', numel(lat), sum(ice == 0 & all(T > 0, 2)));
