# one equation per month, fitted to ALL lakes within 70 degrees of the equator (frozen months count as 0 C).
# Used by the website for lakes predicted to freeze; tested on lakes not used in fitting (5 groups of 1x1 degree squares).
import json, numpy as np, pandas as pd
d = pd.read_parquet("seasonal.parquet")        # made by seas_prep.py
d["h"] = d.Elevation / 1000; d["C"] = np.log10(d.coast_km + 10)
d["D"] = np.log10(d.Depth_avg.clip(lower=0.3)) - np.log10(3.3); d["A"] = np.log10(d.Lake_area.clip(lower=0.01)) - np.log10(0.23)
d["S"] = (d.center_lat < 0).astype(float)
phi = d.alat.values; h = d.h.values; KN = [15, 25, 35, 45, 55]
X = np.c_[phi, *[np.maximum(phi - k, 0) for k in KN], h, np.maximum(h - 1.5, 0), d.C, d.D, d.A, d.S, d.S * phi]
T = d[[f"s{i}" for i in range(1, 13)]].values
cell = pd.factorize(np.floor(d.center_lat).astype(int) * 1000 + np.floor(d.center_long).astype(int))[0]
fold = np.random.default_rng(0).integers(0, 5, cell.max() + 1)[cell]
X1 = np.c_[np.ones(len(X)), X]; P = np.zeros_like(T)
for f in range(5):
    tr = fold != f; B = np.linalg.lstsq(X1[tr], T[tr], rcond=None)[0]; P[~tr] = X1[~tr] @ B
P = np.maximum(P, 0); fr = (d.ice_days > 0).values; e = np.abs(T - P)
B = np.linalg.lstsq(X1, T, rcond=None)[0]
json.dump(dict(knots=KN, coef=B.T.round(5).tolist(), cv_mae_open_freezing=float(e[(T > 0) & fr[:, None]].mean()), cv_mae_all=float(e.mean())), open("monthly_model.json", "w"))
print("ice-free months of freezing lakes: typical error %.2f C" % e[(T > 0) & fr[:, None]].mean())
