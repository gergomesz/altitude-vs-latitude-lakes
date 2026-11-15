%% run_all.m  -  makes every figure in order (numbers match the report)
% (each figure script starts with "clear", so they are listed one per line instead of in a loop)
if ~isfile('lakes.mat'), step0_load_data; end
fig01_world_map
fig02_zone_widths
fig03_lat_alt_grid
fig04_variance_shares
fig05_zone_coefficients
fig06_sliding_band
fig07_robustness
fig08_alps_scatter
fig09_alps_region_slopes
fig10_alps_residual_map
fig11_alps_vs_canada
fig12_coast_distance
if ~isfile('heldout.mat'), step1_heldout_models; end
fig13_predicted_vs_actual
fig15_error_by_latitude
fig16_big_lakes
if isfile('south.mat'), fig17_hemispheres, else, disp('skipping fig17: run step0_load_south first'), end
if ~isfile('yearfit.mat') && isfile('year.mat'), step2_yearly_fit; end
if isfile('yearfit.mat')
    fig18_yearly_cycle
    fig19_timing_ice_prediction
else
    disp('skipping fig18 and fig19: run step0_load_year first')
end
disp('all figures are in the figures folder');
