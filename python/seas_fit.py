import json, numpy as np, pandas as pd
d = pd.read_parquet("seasonal.parquet")
d["h"] = d.Elevation / 1000; d["C"] = np.log10(d.coast_km + 10)
d["D"] = np.log10(d.Depth_avg.clip(lower=0.3)) - np.log10(3.3); d["A"] = np.log10(d.Lake_area.clip(lower=0.01)) - np.log10(0.23)
d["S"] = (d.center_lat < 0).astype(float)
cell = pd.factorize(np.floor(d.center_lat).astype(int) * 1000 + np.floor(d.center_long).astype(int))[0]
d["fold"] = np.random.default_rng(0).integers(0, 5, cell.max() + 1)[cell]
def ols(X, y): return np.linalg.lstsq(np.c_[np.ones(len(y)), X], y, rcond=None)[0]
def cv(g, Xf, y):
    X = Xf(g); p = np.zeros(len(g))
    for k in range(5):
        tr = g.fold.values != k; b = ols(X[tr], y[tr]); p[~tr] = np.c_[np.ones((~tr).sum()), X[~tr]] @ b
    return 1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum(), ols(X, y), p
out = {}
Y = d[d.yr_open].reset_index(drop=True)
base = lambda g: [g.h, g.C, g.D, g.A, g.S]
for tgt in ["mean", "amp"]:
    best = None
    for b in np.arange(10, 40.5, 0.5):
        Xf = lambda g, b=b: np.c_[g.alat, np.maximum(g.alat - b, 0), *base(g)]
        X = Xf(Y); bb = ols(X, Y[tgt].values); sse = ((Y[tgt] - np.c_[np.ones(len(Y)), X] @ bb) ** 2).sum()
        if best is None or sse < best[0]: best = (sse, b)
    b = best[1]; Xf = lambda g, b=b: np.c_[g.alat, np.maximum(g.alat - b, 0), *base(g)]
    r2, coef, p = cv(Y, Xf, Y[tgt].values); Y[f"p_{tgt}"] = p
    r2lin, _, _ = cv(Y, lambda g: np.c_[g.alat, *base(g)], Y[tgt].values)
    out[tgt] = dict(brk=float(b), r2=float(r2), r2_nobreak=float(r2lin), coef=dict(zip(["const", "alat", f"alat_past_{b}", "h", "C", "D", "A", "south"], map(float, coef))))
W = Y[Y.amp > 3].reset_index(drop=True)
r2, coef, p = cv(W, lambda g: np.c_[g.alat, *base(g)], W.peak.values)
Y["p_peak"] = np.nan; Y.loc[Y.amp > 3, "p_peak"] = p
out["peak"] = dict(r2=float(r2), n=len(W), coef=dict(zip(["const", "alat", "h", "C", "D", "A", "south"], map(float, coef))))
F = d[~d.yr_open & (d.alat >= 20)].reset_index(drop=True)
best = None
for b in np.arange(25, 60.5, 0.5):
    X = np.c_[F.alat, np.maximum(F.alat - b, 0), *base(F)]; bb = ols(X, F.open_days.values)
    sse = ((F.open_days - np.c_[np.ones(len(F)), X] @ bb) ** 2).sum()
    if best is None or sse < best[0]: best = (sse, b)
b = best[1]; r2, coef, p = cv(F, lambda g, b=b: np.c_[g.alat, np.maximum(g.alat - b, 0), *base(g)], F.open_days.values); F["p_open"] = p
out["open_days"] = dict(brk=float(b), r2=float(r2), n=len(F), coef=dict(zip(["const", "alat", f"alat_past_{b}", "h", "C", "D", "A", "south"], map(float, coef))))
# whole-year reconstruction on held-out lakes
th = 2 * np.pi * (np.arange(12) + 0.5) / 12
T = Y[[f"s{i}" for i in range(1, 13)]].values
pk = np.where(Y.p_peak.notna(), Y.p_peak, 7.0)
Pc = Y.p_mean.values[:, None] + Y.p_amp.clip(lower=0).values[:, None] * np.cos(th - 2 * np.pi * (pk[:, None] - 0.5) / 12)
r2m = 1 - ((T - Pc) ** 2).sum() / ((T - T.mean()) ** 2).sum()
out["year_curve"] = dict(r2=float(r2m), mae=float(np.abs(T - Pc).mean()), mae_by_month=np.abs(T - Pc).mean(0).round(2).tolist())
json.dump(out, open("seasonal.json", "w"), indent=1)
Y.to_parquet("seasonal_open.parquet"); F[["center_lat", "center_long", "alat", "Elevation", "coast_km", "open_days", "p_open", "S"]].to_parquet("seasonal_frozen.parquet")
print(json.dumps(out, indent=1))
