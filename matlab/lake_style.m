function C = lake_style()
% one set of colours used by every figure, so the same thing is always the same colour
C.ink    = [0.07 0.07 0.09];   % data points and fitted lines
C.grey   = [0.55 0.56 0.59];   % secondary lines, error bars
C.wash   = [0.91 0.91 0.89];   % land, shaded ranges
C.alps   = [0.85 0.42 0.10];   % anything about the Alps band (orange)
C.canada = [0.18 0.42 0.65];   % anything about the southern Canada band (blue)
C.warm   = [0.71 0.33 0.18];   % warmer than predicted
C.cool   = [0.18 0.42 0.60];   % colder than predicted
% cividis colour map (dark blue -> yellow), built from 5 anchor colours
a = [0.000 0.135 0.304; 0.255 0.302 0.420; 0.487 0.484 0.471; 0.741 0.679 0.420; 0.995 0.909 0.217];
C.seq = interp1(linspace(0, 1, 5), a, linspace(0, 1, 256));
% blue - white - red for residuals
C.div = [interp1([0 1], [C.cool; 1 1 1], linspace(0, 1, 128)); interp1([0 1], [1 1 1; C.warm], linspace(0, 1, 128))];
% draw figures off-screen: MATLAB Online squeezes on-screen figures into its panel,
% which cut the saved pictures off. Off-screen they keep the size each script asks for.
% (to see a graph, open its .png in the figures folder)
set(groot, 'defaultFigureVisible', 'off');
set(groot, 'defaultAxesFontSize', 10, 'defaultAxesBox', 'off', 'defaultAxesTickDir', 'out', ...
    'defaultFigureColor', 'w', 'defaultAxesColor', 'none', 'defaultLineLineWidth', 1.2);
end
