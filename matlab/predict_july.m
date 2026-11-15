function T = predict_july(lat, elev_m, coast_km, depth_m)
% predicted July lake surface temperature (C) from the zone equations
%   T = predict_july(lat, elev_m, coast_km, depth_m)
%   lat       latitude, degrees N (0-70)
%   elev_m    lake elevation, metres
%   coast_km  distance to the ocean, km  (coastal = under 100 km)
%   depth_m   mean lake depth, metres (optional, default = median lake, 3.3 m)
% each 5 degree zone has one equation for coastal lakes and one for inland lakes:
%   T = a + per_deg*(lat - zone middle) + per_km*elev_km + per_depth_x10*(log10(depth) - log10(3.3))
% example:  predict_july(46.5, 1000, 300, 20)
if nargin < 4, depth_m = 3.3; end
E = csvread('zone_equations.csv', 1, 0);   % zone_start, coastal, a, per_deg, per_km, per_depth_x10
T = zeros(size(lat));
for i = 1:numel(lat)
    z0 = 5 * floor((lat(i) - 1e-9) / 5);
    c  = double(coast_km(i) < 100);
    r  = E(E(:, 1) == z0 & E(:, 2) == c, :);
    T(i) = r(3) + r(4) * (lat(i) - (z0 + 2.5)) + r(5) * elev_m(i) / 1000 + ...
           r(6) * (log10(max(depth_m(min(i, end)), 0.3)) - log10(3.3));
end
end
