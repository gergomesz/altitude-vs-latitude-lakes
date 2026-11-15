# does the July (Northern Hemisphere) picture hold for the Southern Hemisphere in January (its summer)?
import json, numpy as np, pandas as pd, statsmodels.formula.api as smf
from scipy.spatial import cKDTree
df = pd.read_parquet("laketemp_clean.parquet")
N = df[(df.center_lat > 0) & (df.center_lat <= 70) & (df.Tmonth_mean_7 > 0) & (df.Tmonth_mean_7 < 40)].reset_index(drop=True)
N["coast_km"] = pd.read_parquet("coast_km.parquet").coast_km.values
S = df[(df.center_lat < 0) & (df.Tmonth_mean_1 > 0) & (df.Tmonth_mean_1 < 40)].reset_index(drop=True)
# distance to coast for the southern lakes
pts = []
for f_ in json.load(open("/tmp/ne/coast.geojson"))["features"]:
    g = f_["geometry"]; lines = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
    for ln in lines:
        a = np.array(ln)
        for (x0, y0), (x1, y1) in zip(a[:-1], a[1:]):
            n = max(1, int(np.hypot(x1 - x0, y1 - y0) / 0.02)); t = np.linspace(0, 1, n, endpoint=False)
            pts.append(np.c_[x0 + t * (x1 - x0), y0 + t * (y1 - y0)])
P = np.vstack(pts)
xyz = lambda lo, la: np.c_[np.cos(np.radians(la)) * np.cos(np.radians(lo)), np.cos(np.radians(la)) * np.sin(np.radians(lo)), np.sin(np.radians(la))]
ch, _ = cKDTree(xyz(P[:, 0], P[:, 1])).query(xyz(S.center_long.values, S.center_lat.values), workers=-1)
S["coast_km"] = 2 * 6371 * np.arcsin(np.clip(ch / 2, 0, 1))
for D_, tcol in [(N, "Tmonth_mean_7"), (S, "Tmonth_mean_1")]:
    D_["T"] = D_[tcol]; D_["alat"] = D_.center_lat.abs(); D_["km"] = D_.Elevation / 1000
    D_["ld"] = np.log10(D_.Depth_avg.clip(lower=0.3)) - np.log10(3.3); D_["C"] = np.log10(D_.coast_km + 10)
    D_["cell"] = pd.factorize(np.floor(D_.center_lat).astype(int) * 1000 + np.floor(D_.center_long).astype(int))[0]
    D_["zone"] = (np.floor((D_.alat - 1e-9) / 5) * 5).astype(int)
fit = lambda f, g: smf.ols(f, g).fit(cov_type="cluster", cov_kwds={"groups": g.cell})
out = {"n_south": len(S), "n_south_above_1000": int((S.Elevation > 1000).sum())}
# 1. zones by distance from the equator
rows = []
for hemi, D_ in [("north (July)", N), ("south (January)", S)]:
    for z, g in D_.groupby("zone"):
        if z >= 60 or len(g) < 200 or (g.Elevation > 1000).sum() < 20: continue
        g = g.assign(dl=g.alat - (z + 2.5)); m = fit("T ~ dl + km + ld", g); ci = m.conf_int()
        rows.append(dict(hemi=hemi, zone=z, n=len(g), nhi=int((g.Elevation > 1000).sum()), per_km=m.params.km, km_lo=ci.loc["km", 0], km_hi=ci.loc["km", 1],
                         per_deg=m.params.dl, deg_lo=ci.loc["dl", 0], deg_hi=ci.loc["dl", 1], sea=m.params.Intercept))
Zt = pd.DataFrame(rows); Zt.to_csv("hemi_zones.csv", index=False)
print(Zt.round(2).to_string())
# 2. sliding 2-degree band: sea-level summer temperature and the break
def slide(D_):
    r = []
    for c in range(1, 69):
        g = D_[(D_.alat >= c - 1) & (D_.alat < c + 1)]
        if len(g) < 150 or (g.Elevation > 1000).sum() < 15: continue
        m = smf.ols("T ~ km + ld", g).fit(); r.append((c, m.params.Intercept, m.params.km, len(g)))
    return pd.DataFrame(r, columns=["alat", "sea", "per_km", "n"])
def brk(s):
    best = (1e9, None)
    for bp in np.arange(15, 50.5, 0.5):
        X = np.c_[np.ones(len(s)), s.alat, np.maximum(s.alat - bp, 0)]
        b, res, *_ = np.linalg.lstsq(X, s.sea, rcond=None); sse = np.sum((s.sea - X @ b) ** 2)
        if sse < best[0]: best = (sse, bp, b)
    return best[1], best[2]
SL = {}
for hemi, D_ in [("north", N), ("south", S)]:
    s = slide(D_); bp, b = brk(s); SL[hemi] = s
    rng = np.random.default_rng(0); boots = []
    for _ in range(300):
        i = rng.integers(0, len(s), len(s)); boots.append(brk(s.iloc[i].reset_index(drop=True))[0])
    out[f"break_{hemi}"] = dict(bp=float(bp), lo=float(np.percentile(boots, 2.5)), hi=float(np.percentile(boots, 97.5)),
                                before=float(b[1]), after=float(b[1] + b[2]))
    print(hemi, "break", out[f"break_{hemi}"])
    s.to_csv(f"slide_{hemi}.csv", index=False)
# 3. coast effect: residual by distance band, poleward of 33 degrees, same simple model
for hemi, D_ in [("north", N), ("south", S)]:
    g = D_[D_.alat > 33]; m = fit("T ~ alat + km + ld + C", g)
    out[f"coast_{hemi}"] = [float(m.params.C), *map(float, m.conf_int().loc["C"])]
    g2 = D_[D_.alat <= 33]; m2 = fit("T ~ alat + km + ld + C", g2)
    out[f"coast_{hemi}_tropics"] = [float(m2.params.C), *map(float, m2.conf_int().loc["C"])]
    print(hemi, "coast per unit C poleward of 33:", np.round(out[f"coast_{hemi}"], 2), " equatorward:", np.round(out[f"coast_{hemi}_tropics"], 2))
# 4. latitude vs altitude importance in each hemisphere
for hemi, D_ in [("north", N), ("south", S)]:
    r = lambda f: smf.ols(f, D_).fit().rsquared
    full, nolat, noel, dep = r("T ~ alat + km + ld"), r("T ~ km + ld"), r("T ~ alat + ld"), r("T ~ ld")
    out[f"r2_{hemi}"] = dict(lat_alone=noel - dep, alt_alone=nolat - dep, lat_unique=full - nolat, alt_unique=full - noel)
    print(hemi, {k: round(v, 3) for k, v in out[f"r2_{hemi}"].items()})
# 5. transfer: fit the 3-variable split equation (latitude, height, coast; no continent) on the north, predict the south
def split3(D_):
    B = {}
    for s_ in (0, 1):
        g = D_[(D_.alat > 33) == bool(s_)]; B[s_] = np.linalg.lstsq(np.c_[np.ones(len(g)), g.alat, g.km, g.C], g["T"], rcond=None)[0]
    return B
def pred3(B, D_):
    p = np.zeros(len(D_))
    for s_ in (0, 1):
        m = ((D_.alat > 33) == bool(s_)).values; g = D_[m]; p[m] = np.c_[np.ones(len(g)), g.alat, g.km, g.C] @ B[s_]
    return p
SST = lambda D_: np.sum((D_["T"] - D_["T"].mean()) ** 2)
Bn = split3(N); pS = pred3(Bn, S); e = S["T"] - pS
out["transfer"] = dict(r2=float(1 - np.sum(e ** 2) / SST(S)), typical=float(np.median(abs(e))), bias=float(np.mean(e)))
# southern equation fitted on the south (5-fold by cell)
fold = np.random.default_rng(0).integers(0, 5, S.cell.max() + 1)[S.cell]; pO = np.zeros(len(S))
for k in range(5):
    Bs = split3(S[fold != k]); pO[fold == k] = pred3(Bs, S[fold == k])
e2 = S["T"] - pO
out["own_south"] = dict(r2=float(1 - np.sum(e2 ** 2) / SST(S)), typical=float(np.median(abs(e2))), bias=float(np.mean(e2)))
out["B_north"] = {k: list(map(float, v)) for k, v in Bn.items()}; out["B_south"] = {k: list(map(float, v)) for k, v in split3(S).items()}
print("north equation on southern lakes:", out["transfer"]); print("southern equation (held-out):", out["own_south"])
print("B north", {k: np.round(v, 3) for k, v in Bn.items()}); print("B south", {k: np.round(v, 3) for k, v in split3(S).items()})
S[["center_lat", "center_long", "T", "Elevation", "coast_km"]].assign(pred_from_north=pS).to_parquet("south_lakes.parquet")
json.dump(out, open("hemi.json", "w"), indent=1)
