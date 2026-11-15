%% step2_yearly_fit.m
% the whole year: fits one smooth yearly wave to every lake that never freezes,
%   T(m) = Tbar + a * cos(2*pi*(m - p)/12)       (m = month, January = 1)
% then finds equations for Tbar (yearly average), a (half the summer-winter swing) and
% p (month of the peak), and one for the ice-free days of lakes that freeze.
% Southern lakes are shifted by 6 months so that month 7 is midsummer in both hemispheres.
% Saves yearfit.mat for fig18 and fig19 and prints every equation.
% needs year.mat (step0_load_year)

clear; clc
Y = load('year.mat');
phi = abs(Y.lat);  S = double(Y.lat < 0);
h  = Y.elev / 1000;
Cc = log10(Y.coast + 10);
D  = log10(max(Y.depth, 0.3)) - log10(3.3);
A  = log10(max(Y.area, 0.01)) - log10(0.23);
Ts = Y.T;  Ts(S == 1, :) = circshift(Ts(S == 1, :), 6, 2);    % season-aligned months

% 1. one wave per lake (exact for 12 evenly spaced months)
th  = 2 * pi * ((1:12) - 0.5) / 12;
ca  = Ts * cos(th') * 2 / 12;   sa = Ts * sin(th') * 2 / 12;
Tbar = mean(Ts, 2);
amp  = hypot(ca, sa);                                   % half the swing
peak = mod(atan2(sa, ca) * 180 / pi, 360) / 30 + 0.5;    % month of the peak (7.0 = mid-July)
fitw = Tbar + ca .* cos(th) + sa .* sin(th);
sst  = sum((Ts - Tbar).^2, 2);  wr2 = 1 - sum((Ts - fitw).^2, 2) ./ sst;

open = Y.ice == 0 & all(Y.T > 0, 2);                    % lakes that never freeze
o = find(open);
fprintf('%d lakes never freeze; one wave fits the median lake with R2 = %.3f\n', numel(o), median(wr2(o(~isnan(wr2(o))))));

% test groups by 1x1 degree square
[~, ~, ci] = unique(Y.cell);  rng(0);  fc = randi(5, max(ci), 1);  fold = fc(ci);

% 2. yearly average and swing: straight lines that bend at a latitude found from the data
Xr = [h(o) Cc(o) D(o) A(o) S(o)];
[bkM, bM] = best_break(phi(o), Xr, Tbar(o), 10:0.5:40);
[bkA, bA] = best_break(phi(o), Xr, amp(o),  10:0.5:40);
pM = cv_ols([phi(o), max(phi(o) - bkM, 0), Xr], Tbar(o), fold(o));
pA = cv_ols([phi(o), max(phi(o) - bkA, 0), Xr], amp(o),  fold(o));
% 3. month of the peak, only where there is a clear swing (a > 3 C)
w = o(amp(o) > 3);
Xp = [phi(w) h(w) Cc(w) D(w) A(w) S(w)];
bP = [ones(numel(w), 1) Xp] \ peak(w);
pP = 7 * ones(numel(o), 1);  [~, iw] = ismember(w, o);  pP(iw) = cv_ols(Xp, peak(w), fold(w));
% 4. the whole year from geography alone, on lakes not used in fitting
pred = pM + max(pA, 0) .* cos(2 * pi * ((1:12) - pP) / 12);
e = Ts(o, :) - pred;
To = Ts(o, :);  r2year = 1 - sum(e(:).^2) / sum((To(:) - mean(To(:))).^2);
maeMonth = mean(abs(e), 1);
% 5. ice-free days for lakes that freeze, 20-70 degrees from the equator
fz = find(~open & phi >= 20);
Xf = [h(fz) Cc(fz) D(fz) A(fz) S(fz)];
odays = 365 - Y.ice(fz);
[bkO, bO] = best_break(phi(fz), Xf, odays, 25:0.5:60);
pO = cv_ols([phi(fz), max(phi(fz) - bkO, 0), Xf], odays, fold(fz));

r2 = @(yy, pp) 1 - sum((yy - pp).^2) / sum((yy - mean(yy)).^2);
eqs = @(b, vars) strjoin(arrayfun(@(k) sprintf('%+.3f %s', b(k), vars{k}), 1:numel(b), 'UniformOutput', false), ' ');
fprintf('\nphi = distance from the equator, h = height (km), C = log10(km to sea + 10), D = depth term, A = area term, S = 1 if southern\n');
fprintf('\nYearly average (R2 %.2f on unseen lakes):\n  Tbar = %s\n', r2(Tbar(o), pM), ...
    eqs(bM, {'', 'phi', sprintf('(phi-%g)+', bkM), 'h', 'C', 'D', 'A', 'S'}));
fprintf('Half-swing (R2 %.2f):\n  a = %s\n', r2(amp(o), pA), eqs(bA, {'', 'phi', sprintf('(phi-%g)+', bkA), 'h', 'C', 'D', 'A', 'S'}));
fprintf('Month of the peak (R2 %.2f):\n  p = %s\n', r2(peak(w), pP(iw)), eqs(bP, {'', 'phi', 'h', 'C', 'D', 'A', 'S'}));
fprintf('Whole year from geography: R2 %.2f, average error %.2f C\n', r2year, mean(abs(e(:))));
fprintf('Ice-free days (R2 %.2f):\n  N = %s\n', r2(odays, pO), eqs(bO, {'', 'phi', sprintf('(phi-%g)+', bkO), 'h', 'C', 'D', 'A', 'S'}));

% what the figures need
O.phi = phi(o); O.S = S(o); O.elev = Y.elev(o); O.coast = Y.coast(o); O.depth = Y.depth(o); O.lat = Y.lat(o);
O.Ts = Ts(o, :); O.Tbar = Tbar(o); O.amp = amp(o); O.peak = peak(o); O.pred = pred; O.name = Y.name(o);
F.phi = phi(fz); F.S = S(fz); F.elev = Y.elev(fz); F.odays = odays;
save('yearfit.mat', 'O', 'F', 'bkM', 'bkA', 'bkO', 'bM', 'bA', 'bP', 'bO', 'r2year', 'maeMonth', '-v7');
disp('saved yearfit.mat');
