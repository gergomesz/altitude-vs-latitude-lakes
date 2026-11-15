# seasonal cycle: per-lake harmonic fit for year-round open lakes; ice season for the rest
import json, numpy as np, pandas as pd
from scipy.spatial import cKDTree
df = pd.read_parquet("laketemp_clean.parquet")
df = df[(df.center_lat.abs() <= 70)].reset_index(drop=True)
M = [f"Tmonth_mean_{i}" for i in range(1, 13)]
# coast distance for every lake
pts = []
for f in json.load(open("/tmp/ne/coast.geojson"))["features"]:
    g = f["geometry"]; lines = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
    for ln in lines:
        a = np.array(ln)
        for (x0, y0), (x1, y1) in zip(a[:-1], a[1:]):
            n = max(1, int(np.hypot(x1 - x0, y1 - y0) / 0.02)); t = np.linspace(0, 1, n, endpoint=False)
            pts.append(np.c_[x0 + t * (x1 - x0), y0 + t * (y1 - y0)])
P = np.vstack(pts)
def xyz(lon, lat):
    lo, la = np.radians(lon), np.radians(lat); return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]
ch, _ = cKDTree(xyz(P[:, 0], P[:, 1])).query(xyz(df.center_long.values, df.center_lat.values), workers=-1)
df["coast_km"] = 2 * 6371 * np.arcsin(np.clip(ch / 2, 0, 1))
T = df[M].values.copy()
south = df.center_lat.values < 0
T[south] = np.roll(T[south], 6, axis=1)          # season-aligned: column 0 = midwinter month in both hemispheres
df[[f"s{i}" for i in range(1, 13)]] = T
th = 2 * np.pi * (np.arange(12) + 0.5) / 12
a = T @ np.cos(th) * 2 / 12; b = T @ np.sin(th) * 2 / 12; m0 = T.mean(1)
fit = m0[:, None] + a[:, None] * np.cos(th) + b[:, None] * np.sin(th)
sst = ((T - m0[:, None]) ** 2).sum(1); r2 = 1 - ((T - fit) ** 2).sum(1) / np.where(sst > 0, sst, np.nan)
df["mean"] = m0; df["amp"] = np.hypot(a, b)
df["peak"] = (np.degrees(np.arctan2(b, a)) % 360) / 30 + 0.5     # season-aligned month (Jan-equivalent = 1)
df["h1_r2"] = r2; df["rng"] = T.max(1) - T.min(1)
df["open_days"] = 365 - df.ice_days
df["yr_open"] = (df.ice_days == 0) & (df[M] > 0).all(axis=1)
df["alat"] = df.center_lat.abs()
df.drop(columns=M).to_parquet("seasonal.parquet")
y = df[df.yr_open]
print(len(df), "lakes;", len(y), "open all year")
print("one-wave fit R2 median", np.nanmedian(y.h1_r2).round(3), "10th pct", np.nanpercentile(y.h1_r2, 10).round(3))
print(y[["mean", "amp", "peak", "rng"]].describe().round(2))
