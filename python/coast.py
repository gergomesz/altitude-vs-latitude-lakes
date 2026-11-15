# distance from every lake to the nearest ocean coastline, and what it does to the lapse rates
import json
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.spatial import cKDTree

R_EARTH = 6371.0
w = pd.read_parquet("with_resid.parquet")
df = pd.read_parquet("laketemp_clean.parquet")
d = df[(df.center_lat > 0) & (df.center_lat <= 70) & (df.Tmonth_mean_7 > 0) & (df.Tmonth_mean_7 < 40)].reset_index(drop=True)
assert len(d) == len(w) and np.allclose(d.center_lat.values, w.lat.values)
d["lat"] = d.center_lat; d["resid"] = w.resid.values; d["region"] = w.region.values
d["elev_km"] = d.Elevation / 1000
d["logdepth"] = np.log10(d.Depth_avg.clip(lower=0.3))
d["cell"] = (np.floor(d.lat).astype(int).astype(str) + "_" + np.floor(d.center_long).astype(int).astype(str))

# 1. coastline points every ~2 km
pts = []
for f in json.load(open("/tmp/ne/coast.geojson"))["features"]:
    g = f["geometry"]
    lines = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
    for ln in lines:
        a = np.array(ln)
        for (x0, y0), (x1, y1) in zip(a[:-1], a[1:]):
            n = max(1, int(np.hypot(x1 - x0, y1 - y0) / 0.02))
            t = np.linspace(0, 1, n, endpoint=False)
            pts.append(np.c_[x0 + t * (x1 - x0), y0 + t * (y1 - y0)])
P = np.vstack(pts)
def xyz(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]
tree = cKDTree(xyz(P[:, 0], P[:, 1]))
chord, _ = tree.query(xyz(d.center_long.values, d.lat.values), workers=-1)
d["coast_km"] = 2 * R_EARTH * np.arcsin(np.clip(chord / 2, 0, 1))
d["logcoast"] = np.log10(d.coast_km + 10)
print(d.coast_km.describe().round(0))
d[["coast_km"]].to_parquet("coast_km.parquet")

def fit(f, g):
    return smf.ols(f, g).fit(cov_type="cluster", cov_kwds={"groups": g.cell})

out = {}
# 2. hemisphere: residual vs distance, south and north of the 33N break
bins = [0, 25, 50, 100, 200, 400, 800, 1600, 4000]
d["cbin"] = pd.cut(d.coast_km, bins)
tab = d.groupby([d.lat > 33, "cbin"], observed=True).resid.agg(["median", "count"]).round(2)
print(tab)
out["resid_by_coast"] = [dict(north=bool(k[0]), lo=k[1].left, hi=k[1].right, median=float(v["median"]), n=int(v["count"])) for k, v in tab.iterrows()]

# 3. Alps band: region slopes without and with distance to coast
A = d[(d.lat >= 45.8) & (d.lat <= 47.8)].copy()
rows = []
for r, g in A.groupby("region", observed=True):
    if len(g) < 100 or (g.Elevation > 1000).sum() < 15:
        continue
    m0 = fit("Tmonth_mean_7 ~ elev_km + logdepth", g)
    m1 = fit("Tmonth_mean_7 ~ elev_km + logdepth + logcoast", g)
    rows.append(dict(region=r, n=len(g),
                     before=m0.params.elev_km, b_lo=m0.conf_int().loc["elev_km", 0], b_hi=m0.conf_int().loc["elev_km", 1],
                     after=m1.params.elev_km, a_lo=m1.conf_int().loc["elev_km", 0], a_hi=m1.conf_int().loc["elev_km", 1],
                     per_log10_coast=m1.params.logcoast,
                     corr_elev_coast=np.corrcoef(g.Elevation, g.logcoast)[0, 1],
                     med_coast_low=g.loc[g.Elevation < 500, "coast_km"].median(),
                     med_coast_high=g.loc[g.Elevation > 1000, "coast_km"].median()))
AR = pd.DataFrame(rows)
print(AR.round(2).to_string())
m_all0 = fit("Tmonth_mean_7 ~ C(region) * elev_km + logdepth", A)
m_all1 = fit("Tmonth_mean_7 ~ C(region) * elev_km + logdepth + logcoast * C(region)", A)
def wald(m):
    names = [p for p in m.params.index if p.startswith("C(region)") and p.endswith(":elev_km")]
    return float(np.squeeze(m.f_test([f"{p} = 0" for p in names]).fvalue))
out["slopes_differ_F_before"] = wald(m_all0); out["slopes_differ_F_after"] = wald(m_all1)
print("slopes differ F before", out["slopes_differ_F_before"], "after", out["slopes_differ_F_after"])
out["alps_regions"] = AR.to_dict("records")
spread = lambda c: AR[c].max() - AR[c].min()
out["spread_before"] = spread("before"); out["spread_after"] = spread("after")
print("spread before/after", out["spread_before"], out["spread_after"])

# 4. lapse rate by distance class, north of the break (all regions, region effects)
N = d[d.lat > 33].copy()
cls = [(0, 100, "coastal (<100 km)"), (100, 500, "100-500 km"), (500, 1000, "500-1000 km"), (1000, 5000, "inland (>1000 km)")]
lr = []
for lo, hi, name in cls:
    g = N[(N.coast_km >= lo) & (N.coast_km < hi)]
    m = fit("Tmonth_mean_7 ~ elev_km + lat + logdepth + C(region)", g)
    lr.append(dict(cls=name, n=len(g), nhi=int((g.Elevation > 1000).sum()), per_km=m.params.elev_km,
                   lo=m.conf_int().loc["elev_km", 0], hi=m.conf_int().loc["elev_km", 1],
                   sea=m.params.Intercept))
LR = pd.DataFrame(lr); print(LR.round(2).to_string())
out["lapse_by_coast"] = lr
# global coast coefficient, north of the break
m = fit("Tmonth_mean_7 ~ elev_km + lat + logdepth + logcoast + C(region)", N)
out["north_coast_coef"] = [m.params.logcoast, *m.conf_int().loc["logcoast"]]
print("north of 33N: per x10 distance", out["north_coast_coef"], "per km", m.params.elev_km)
json.dump(out, open("coast_results.json", "w"), indent=1, default=float)
