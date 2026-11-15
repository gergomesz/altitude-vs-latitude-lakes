function save_fig(name)
% saves the current figure as figures/<name>.png inside the current folder,
% at a fixed size so nothing gets cut off
sizes = struct('fig01_world_map', [11 4.7], 'fig02_zone_widths', [11.5 4.2], ...
    'fig03_lat_alt_grid', [10 5.6], 'fig04_variance_shares', [8.6 4.6], ...
    'fig05_zone_coefficients', [12.5 4.6], 'fig06_sliding_band', [10 7.2], ...
    'fig07_robustness', [8.2 3.8], 'fig08_alps_scatter', [13 3.8], ...
    'fig09_alps_region_slopes', [8.2 3.8], 'fig10_alps_residual_map', [12 7.6], ...
    'fig11_alps_vs_canada', [7.6 4.5], 'fig12_coast_distance', [15 4.6], 'fig13_predicted_vs_actual', [13 4.4], 'fig15_error_by_latitude', [8.5 4.4], ...
    'fig16_big_lakes', [13 5.2], 'fig17_hemispheres', [12 10], ...
    'fig18_yearly_cycle', [12 9.6], 'fig19_timing_ice_prediction', [12 9.6]);
wh = [10 5];                                   % width, height in inches
if isfield(sizes, name), wh = sizes.(name); end

folder = fullfile(pwd, 'figures');
if ~isfolder(folder), mkdir(folder); end
f = fullfile(folder, [name '.png']);

fig = gcf;
set(fig, 'Units', 'inches', 'Position', [0.5 0.5 wh], 'Color', 'w');
drawnow;
if exist('exportgraphics', 'file')
    % exportgraphics crops tightly around what is drawn, which can shave the
    % bottom of the axis labels; 'Padding' leaves a small white margin instead
    try
        exportgraphics(fig, f, 'Resolution', 200, 'BackgroundColor', 'white', 'Padding', 15);
    catch
        % older MATLAB without 'Padding': an invisible white frame round the whole figure does the same job
        annotation(fig, 'rectangle', [0 0 1 1], 'Color', 'w');
        exportgraphics(fig, f, 'Resolution', 200, 'BackgroundColor', 'white');
    end
else
    set(fig, 'PaperUnits', 'inches', 'PaperPositionMode', 'manual', 'PaperPosition', [0 0 wh], 'PaperSize', wh);
    print(fig, f, '-dpng', '-r200');
end
fprintf('saved figures/%s.png\n', name);
end
