import numpy as np, pandas as pd, json
exec(open("improve.py").read().split("feats = {")[0])
SST = np.sum((y - y.mean()) ** 2)
hinge = np.maximum(km - 1.5, 0)
base = lambda dlat: np.c_[km, hinge, dlat, co, lc, lc * km, ld, la]
def cv(groups, X, extra=None):
    err = np.zeros(len(y)); pred = np.zeros(len(y))
    for k in range(5):
        for gval in np.unique(groups):
            tr = (groups == gval) & (fold != k); te = (groups == gval) & (fold == k)
            if te.sum() == 0: continue
            if tr.sum() < 30:            # too few: fall back on nothing better than the mean
                pred[te] = y[tr].mean() if tr.sum() else y.mean(); continue
            b = np.linalg.lstsq(np.c_[np.ones(tr.sum()), X[tr]], y[tr], rcond=None)[0]
            pred[te] = np.c_[np.ones(te.sum()), X[te]] @ b
    err = y - pred
    return err, (np.median(abs(err)), 1 - np.sum(err ** 2) / SST)
side = (lat > 33).astype(int)
out = {}
e, out["A  two halves (south/north of 33N), straight-line latitude, + continent"] = cv(side, np.c_[base(lat), R])
e, out["B  two halves x 6 continents = 12 equations"] = cv(side * 10 + reg, base(lat))
e, out["C  5-degree zones x 6 continents = up to 84 equations"] = cv(zone * 10 + reg, base(dl))
e, out["D  5-degree zones + continent term (best so far)"] = cv(zone, np.c_[base(dl), R])
for k, v in out.items(): print(f"{k:60s} typical err {v[0]:.2f}  R2 {v[1]:.3f}")
# E: add a local correction = average leftover of training lakes in the 8 neighbouring 1x1 cells
ci = np.floor(lat).astype(int); cj = np.floor(lon).astype(int)
err = e.copy(); pred = y - err; loc = np.zeros(len(y))
for k in range(5):
    tr = fold != k; te = fold == k
    s = pd.DataFrame(dict(i=ci[tr], j=cj[tr], r=err[tr])).groupby(["i", "j"]).r.agg(["sum", "count"])
    tot = pd.Series(0.0, index=pd.MultiIndex.from_arrays([ci[te], cj[te]]).unique()); cnt = tot.copy()
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            sh = s.copy(); sh.index = pd.MultiIndex.from_arrays([sh.index.get_level_values(0) - di, sh.index.get_level_values(1) - dj])
            sh = sh.reindex(tot.index).fillna(0); tot += sh["sum"]; cnt += sh["count"]
    corr = (tot / cnt.clip(lower=1)) * (cnt / (cnt + 20))       # shrink when few neighbours
    loc[te] = corr.reindex(pd.MultiIndex.from_arrays([ci[te], cj[te]])).fillna(0).values
e2 = y - (pred + loc)
out["E  D + local correction from neighbouring 1x1 cells"] = (np.median(abs(e2)), 1 - np.sum(e2 ** 2) / SST)
print("E", out["E  D + local correction from neighbouring 1x1 cells"])
json.dump(out, open("improve2.json", "w"), indent=1)
