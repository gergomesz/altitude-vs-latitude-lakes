import numpy as np, pandas as pd, statsmodels.formula.api as smf, json
df = pd.read_parquet("laketemp_clean.parquet")
d = df[(df.center_lat > 0) & (df.center_lat <= 70) & (df.Tmonth_mean_7 > 0) & (df.Tmonth_mean_7 < 40)].reset_index(drop=True)
d["coast_km"] = pd.read_parquet("coast_km.parquet").coast_km.values
d["T"] = d.Tmonth_mean_7; d["lat"] = d.center_lat; d["km"] = d.Elevation / 1000
d["ldc"] = np.log10(d.Depth_avg.clip(lower=0.3)); d["ldc"] -= d.ldc.median()
d["zone"] = (np.floor((d.lat - 1e-9) / 5) * 5).astype(int)
d["cell"] = pd.factorize(np.floor(d.lat).astype(int) * 1000 + np.floor(d.center_long).astype(int))[0]
d["co"] = (d.coast_km < 100).astype(float)
d["north"] = np.maximum(d.lat - 33, 0)
fit = lambda f, g: smf.ols(f, g).fit(cov_type="cluster", cov_kwds={"groups": g.cell})
ci = lambda m, v: (m.params[v], *m.conf_int().loc[v])
out = {}
S1, S3, S4 = [], [], []
for z, g in d.groupby("zone"):
    g = g.assign(dl=g.lat - (z + 2.5)); nhi = int((g.Elevation > 1000).sum())
    m1 = fit("T ~ km + dl + ldc", g)
    S1.append([f"{z}–{z+5}°N", len(g), nhi, *ci(m1, "km")])
    m3 = fit("T ~ co + km + dl + ldc", g)
    S3.append([f"{z}–{z+5}°N", int(g.co.sum()), int((1 - g.co).sum()), *ci(m3, "co")])
    S4.append([f"{z}–{z+5}°N", m3.params.Intercept, m3.params.km, m3.params.dl, m3.params.co, m3.params.ldc, m3.rsquared])
S2 = []
for lo, hi in [(0, 500), (500, 1000), (1000, 2000), (2000, 6000)]:
    g = d[(d.Elevation >= lo) & (d.Elevation < hi)]
    m = fit("T ~ lat + north + km + ldc", g)
    s = m.params.lat; n_ = m.params.lat + m.params.north
    w = pd.Series(0.0, index=m.params.index); w[["lat", "north"]] = 1; se = float(np.sqrt(w @ m.cov_params() @ w))
    S2.append([f"{lo}–{hi} m" if hi < 6000 else f"above {lo} m", len(g), int((g.lat <= 33).sum()), *ci(m, "lat"), n_, n_ - 1.96 * se, n_ + 1.96 * se])
for name, rows in [("S1", S1), ("S2", S2), ("S3", S3), ("S4", S4)]:
    print(name)
    for r in rows: print("  ", [round(x, 2) if isinstance(x, float) else x for x in r])
pd.DataFrame(S1,columns=["zone","lakes","lakes_above_1000m","per_km","ci_lo","ci_hi"]).to_csv("step1.csv",index=False)
pd.DataFrame(S2,columns=["height_band","lakes","lakes_south_of_33N","per_deg_south","s_lo","s_hi","per_deg_north","n_lo","n_hi"]).to_csv("step2.csv",index=False)
pd.DataFrame(S3,columns=["zone","coastal_lakes","inland_lakes","coastal_minus_inland","ci_lo","ci_hi"]).to_csv("step3.csv",index=False)
pd.DataFrame(S4,columns=["zone","a","per_km","per_deg","coastal_shift","depth_x10","r2"]).to_csv("step4.csv",index=False)
raise SystemExit
# accuracy, 5-fold by cell
rng = np.random.default_rng(0); fold = rng.integers(0, 5, d.cell.max() + 1)[d.cell]
def cv(f):
    err = np.full(len(d), np.nan)
    for k in range(5):
        for z, g in d.groupby("zone"):
            g = g.assign(dl=g.lat - (z + 2.5)); tr = g[fold[g.index] != k]; te = g[fold[g.index] == k]
            if len(te) == 0: continue
            m = smf.ols(f, tr).fit(); err[te.index] = te["T"] - m.predict(te)
    ok = ~np.isnan(err); return np.median(abs(err[ok])), 1 - np.nansum(err**2) / np.sum((d["T"] - d["T"].mean())**2)
for f in ["T ~ km", "T ~ km + dl", "T ~ km + dl + co", "T ~ km + dl + co + ldc"]:
    print(f, [round(x, 3) for x in cv(f)])
