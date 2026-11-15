import numpy as np, pandas as pd, json, time
df = pd.read_parquet("laketemp_clean.parquet")
d = df[(df.center_lat > 0) & (df.center_lat <= 70) & (df.Tmonth_mean_7 > 0) & (df.Tmonth_mean_7 < 40)].reset_index(drop=True)
d["coast_km"] = pd.read_parquet("coast_km.parquet").coast_km.values
y = d.Tmonth_mean_7.values; lat = d.center_lat.values; lon = d.center_long.values
km = d.Elevation.values / 1000; ld = np.log10(d.Depth_avg.clip(lower=0.3).values); ld -= np.median(ld)
la = np.log10(d.Lake_area.clip(lower=0.01).values); la -= np.median(la)
lc = np.log10(d.coast_km.values + 10); co = (d.coast_km.values < 100).astype(float)
reg = np.digitize(lon, [-100, -60, -15, 40, 100])
zone = np.floor((lat - 1e-9) / 5).astype(int); dl = lat - (zone * 5 + 2.5)
cell = pd.factorize(np.floor(lat).astype(int) * 1000 + np.floor(lon).astype(int))[0]
fold = np.random.default_rng(0).integers(0, 5, cell.max() + 1)[cell]
R = np.eye(6)[reg][:, 1:]
feats = {
 "now: altitude + latitude + coast (yes/no) + depth": lambda: np.c_[km, dl, co, ld],
 "+ continent (6 longitude sectors)": lambda: np.c_[km, dl, co, ld, R],
 "+ distance to coast as a number": lambda: np.c_[km, dl, co, lc, ld, R],
 "+ altitude bends at 1,500 m": lambda: np.c_[km, np.maximum(km - 1.5, 0), dl, co, lc, ld, R],
 "+ coast changes the altitude effect": lambda: np.c_[km, np.maximum(km - 1.5, 0), dl, co, lc, lc * km, ld, R],
 "+ lake size": lambda: np.c_[km, np.maximum(km - 1.5, 0), dl, co, lc, lc * km, ld, la, R],
}
SST = np.sum((y - y.mean()) ** 2); res = {}
for name, F in feats.items():
    X = F(); err = np.zeros(len(y))
    for k in range(5):
        for z in np.unique(zone):
            tr = (zone == z) & (fold != k); te = (zone == z) & (fold == k)
            Xt = np.c_[np.ones(tr.sum()), X[tr]]; b = np.linalg.lstsq(Xt, y[tr], rcond=None)[0]
            err[te] = y[te] - np.c_[np.ones(te.sum()), X[te]] @ b
    res[name] = (np.median(abs(err)), 1 - np.sum(err ** 2) / SST, np.sqrt(np.mean(err ** 2)))
    print(f"{name:55s} typical err {res[name][0]:.2f}  R2 {res[name][1]:.3f}  RMSE {res[name][2]:.2f}", flush=True)
# ceiling: flexible machine-learning model with the same information
from sklearn.ensemble import HistGradientBoostingRegressor
X = np.c_[lat, lon, km, lc, ld, la]; err = np.zeros(len(y)); t = time.time()
for k in range(5):
    m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.1, max_leaf_nodes=63, random_state=0).fit(X[fold != k], y[fold != k])
    err[fold == k] = y[fold == k] - m.predict(X[fold == k])
res["ceiling: machine-learning model, same inputs"] = (np.median(abs(err)), 1 - np.sum(err ** 2) / SST, np.sqrt(np.mean(err ** 2)))
print("ML ceiling", res["ceiling: machine-learning model, same inputs"], round(time.time() - t))
json.dump(res, open("improve.json", "w"), indent=1)
