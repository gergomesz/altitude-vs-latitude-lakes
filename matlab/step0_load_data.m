%% step0_load_data.m
% reads laketemp_clean.csv.gz (made by laketemp_filter.py) and saves lakes.mat
% run this ONCE. every figure script then loads lakes.mat, which is much faster.

clear; clc
fn = 'laketemp_clean.csv.gz';
if ~isfile(fn), fn = 'laketemp_clean_csv.gz'; end
if ~isfile(fn), error('put laketemp_clean.csv.gz in this folder first'); end

% 1. unzip (makes a plain text copy next to the .gz)
f = gunzip(fn);
f = f{1};

% 2. read only the columns we need
opts = detectImportOptions(f, 'FileType', 'text');
opts.SelectedVariableNames = {'center_lat', 'center_long', 'Country', 'Lake_name', 'Lake_area', 'Depth_avg', ...
    'Elevation', 'Tyear_mean_open', 'ice_days', 'Tmonth_mean_7'};
opts = setvartype(opts, {'Country', 'Lake_name'}, 'string');
T = readtable(f, opts);

% 3. keep Northern Hemisphere lakes up to 70 N with a sensible July temperature
k = T.center_lat > 0 & T.center_lat <= 70 & T.Tmonth_mean_7 > 0 & T.Tmonth_mean_7 < 40;
T = T(k, :);

% 4. the variables every script uses
lat   = T.center_lat;
lon   = T.center_long;
elev  = T.Elevation;                         % metres
july  = T.Tmonth_mean_7;                     % July mean surface temperature, C
openw = T.Tyear_mean_open;                   % yearly mean over ice-free days, C
ice   = T.ice_days;
logdepth = log10(max(T.Depth_avg, 0.3));     % depth on a log scale
area  = T.Lake_area;                         % km2
name  = T.Lake_name;  name(ismissing(name)) = "";
isCH  = T.Country == "Switzerland";
isCH(ismissing(T.Country)) = false;

% 1x1 degree cell number, used to cluster the standard errors
cell = floor(lat) * 1000 + floor(lon) + 500;

% six longitude sectors: 1 N.America west, 2 N.America east, 3 N.Atlantic,
%                        4 Europe, 5 Central Asia, 6 East Asia
edges  = [-180 -100 -60 -15 40 100 180];
region = discretize(lon, edges);
regnames = {'N. America west', 'N. America east', 'N. Atlantic', 'Europe', 'Central Asia', 'East Asia'};

med_logdepth = median(logdepth);

save('lakes.mat', 'lat', 'lon', 'elev', 'july', 'openw', 'ice', 'logdepth', 'isCH', 'area', 'name', ...
     'cell', 'region', 'regnames', 'med_logdepth', '-v7');
fprintf('%d lakes saved to lakes.mat\n', numel(lat));
delete(f);   % remove the unzipped copy, the .gz stays
