function v = r2_shares(lat, km, logdepth, T)
% four least-squares fits; depth is in all of them so it is not counted for either variable
one = ones(numel(T), 1);
[~, ~, r_full]  = ols_cl([one lat km logdepth], T);
[~, ~, r_nolat] = ols_cl([one km logdepth], T);
[~, ~, r_noel]  = ols_cl([one lat logdepth], T);
[~, ~, r_dep]   = ols_cl([one logdepth], T);
v = 100 * [r_noel - r_dep;     % latitude alone
           r_nolat - r_dep;    % altitude alone
           r_full - r_nolat;   % latitude, once altitude is already in
           r_full - r_noel];   % altitude, once latitude is already in
end
