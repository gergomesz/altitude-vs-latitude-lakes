# the four prediction models: fit, test on held-out lakes, export coefficients and correction maps
import json
import numpy as np
import pandas as pd

df = pd.read_parquet("laketemp_clean.parquet")
d = df[(df.center_lat > 0) & (df.center_lat <= 70) & (df.Tmonth_mean_7 > 0) & (df.Tmonth_mean_7 < 40)].reset_index(drop=True)
d["coast_km"] = pd.read_parquet("coast_km.parquet").coast_km.values
y = d.Tmonth_mean_7.values
lat = d.center_lat.values; lon = d.center_long.values
km = d.Elevation.values / 1000; hinge = np.maximum(km - 1.5, 0)
C = np.log10(d.coast_km.values + 10)
MED_D, MED_A = 3.3, 0.23
D = np.log10(d.Depth_avg.clip(lower=0.3).values) - np.log10(MED_D)
A = np.log10(d.Lake_area.clip(lower=0.01).values) - np.log10(MED_A)
cont = np.digitize(lon, [-100, -60, -15, 40, 100])           # 0..5
CONT = ["Western N. America", "Eastern N. America", "N. Atlantic", "Europe", "Central Asia", "East Asia"]
K = np.eye(6)[cont][:, 1:]
side = (lat > 33).astype(int)
zone = np.floor((lat - 1e-9) / 5).astype(int); mid = zone * 5 + 2.5
ci = np.floor(lat).astype(int); cj = np.floor(lon).astype(int)
cell = pd.factorize(ci * 1000 + cj)[0]
fold = np.random.default_rng(0).integers(0, 5, cell.max() + 1)[cell]
SST = np.sum((y - y.mean()) ** 2)
SHRINK = 20

def ols(X, yy):
    return np.linalg.lstsq(np.c_[np.ones(len(yy)), X], yy, rcond=None)[0]
def predict(X, b):
    return np.c_[np.ones(len(X)), X] @ b

X3 = np.c_[lat, km, C, K]          # Model 1: latitude, height, coast + continent
X7 = np.c_[lat, km, hinge, C, D, A, K]
XZ = lambda idx: np.c_[lat[idx] - mid[idx], km[idx], hinge[idx], C[idx], D[idx], A[idx]]

def split_fit(X, mask):
    return {s: ols(X[mask & (side == s)], y[mask & (side == s)]) for s in (0, 1)}
def split_pred(X, B, idx):
    p = np.zeros(idx.sum())
    for s in (0, 1):
        m = side[idx] == s
        p[m] = predict(X[idx][m], B[s])
    return p

def zone_fit(mask, B7):
    """one equation per 5-degree zone x continent; groups that are too small use the 7-variable split equation"""
    coefs = {}
    for z in range(14):
        for c in range(6):
            g = mask & (zone == z) & (cont == c)
            ok = g.sum() >= 300 and (g & (km > 1.0)).sum() >= 20
            if ok:
                X = XZ(g)
                if (g & (km > 1.5)).sum() < 20:      # too few lakes above 1,500 m to estimate the extra slope: leave it out
                    X[:, 2] = 0
                b = ols(X, y[g])
                if (g & (km > 1.5)).sum() < 20: b[3] = 0.0
                coefs[(z, c)] = ("own", b)
            else:
                coefs[(z, c)] = ("fallback", None)
    return coefs
def zone_pred(coefs, B7, idx):
    p = split_pred(X7, B7, idx)
    ii = np.where(idx)[0]
    for (z, c), (kind, b) in coefs.items():
        if kind != "own": continue
        m = (zone[ii] == z) & (cont[ii] == c)
        if m.any():
            sel = np.zeros(len(y), bool); sel[ii[m]] = True
            p[m] = predict(XZ(sel), b)
    return p

def correction(res_train_mask, resid, target_idx):
    """average leftover of known lakes in the 3x3 block of 1-degree squares, shrunk when few neighbours"""
    s = pd.DataFrame(dict(i=ci[res_train_mask], j=cj[res_train_mask], r=resid[res_train_mask])).groupby(["i", "j"]).r.agg(["sum", "count"])
    keys = pd.MultiIndex.from_arrays([ci[target_idx], cj[target_idx]])
    uk = keys.unique(); tot = pd.Series(0.0, index=uk); cnt = tot.copy()
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            sh = s.copy()
            sh.index = pd.MultiIndex.from_arrays([sh.index.get_level_values(0) - di, sh.index.get_level_values(1) - dj])
            sh = sh.reindex(uk).fillna(0); tot += sh["sum"]; cnt += sh["count"]
    corr = (tot / cnt.clip(lower=1)) * (cnt / (cnt + SHRINK))
    return corr.reindex(keys).fillna(0).values, corr, cnt

# ---------- held-out test (5 folds of 1x1 squares) ----------
P = {k: np.zeros(len(y)) for k in ["M3", "M4", "M7", "MA"]}
base3 = np.zeros(len(y)); baseZ = np.zeros(len(y))
for k in range(5):
    tr = fold != k; te = fold == k
    B3 = split_fit(X3, tr); B7 = split_fit(X7, tr); CZ = zone_fit(tr, B7)
    base3[te] = split_pred(X3, B3, te); P["M7"][te] = split_pred(X7, B7, te); baseZ[te] = zone_pred(CZ, B7, te)
    # in-fold residuals for the corrections come from the training lakes only
    r3 = np.zeros(len(y)); r3[tr] = y[tr] - split_pred(X3, B3, tr)
    rZ = np.zeros(len(y)); rZ[tr] = y[tr] - zone_pred(CZ, B7, tr)
    P["M4"][te] = base3[te] + correction(tr, r3, te)[0]
    P["MA"][te] = baseZ[te] + correction(tr, rZ, te)[0]
P["M3"] = base3
def metrics(p):
    e = y - p
    return dict(r2=1 - np.sum(e ** 2) / SST, typical=float(np.median(abs(e))), rmse=float(np.sqrt(np.mean(e ** 2))),
                within1=float(np.mean(abs(e) <= 1)), within2=float(np.mean(abs(e) <= 2)), bias=float(np.mean(e)))
M = {k: metrics(v) for k, v in P.items()}
for k, v in M.items(): print(k, {a: round(b, 3) for a, b in v.items()})
pd.DataFrame(dict(lat=lat, lon=lon, actual=y, **{k: v for k, v in P.items()})).to_parquet("heldout_predictions.parquet")

# ---------- final fit on all lakes ----------
allm = np.ones(len(y), bool)
B3 = split_fit(X3, allm); B7 = split_fit(X7, allm); CZ = zone_fit(allm, B7)
r3 = y - split_pred(X3, B3, allm); rZ = y - zone_pred(CZ, B7, allm)
# correction maps for every 1x1 square that has lakes or touches one
lake_cells = pd.MultiIndex.from_arrays([ci, cj]).unique()
grid = set()
for i, j in lake_cells:
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            grid.add((i + di, j + dj))
grid = sorted(g for g in grid if 0 <= g[0] < 70)
gi = np.array([g[0] for g in grid]); gj = np.array([g[1] for g in grid])
def map_for(resid):
    s = pd.DataFrame(dict(i=ci, j=cj, r=resid)).groupby(["i", "j"]).r.agg(["sum", "count"])
    tot = np.zeros(len(grid)); cnt = np.zeros(len(grid))
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            sh = s.reindex(pd.MultiIndex.from_arrays([gi + di, gj + dj])).fillna(0)
            tot += sh["sum"].values; cnt += sh["count"].values
    return np.where(cnt > 0, tot / np.maximum(cnt, 1) * cnt / (cnt + SHRINK), 0), cnt
c3, n3 = map_for(r3); cZ, nZ = map_for(rZ)
CM = pd.DataFrame(dict(lat_floor=gi, lon_floor=gj, key=[f"{i}|{j}" for i, j in grid], neighbours=n3.astype(int),
                       corr_M4=np.round(c3, 3), corr_all=np.round(cZ, 3)))
CM = CM[CM.neighbours > 0]
CM.to_csv("correction_map.csv", index=False)
print("correction cells", len(CM))

# zone x continent coefficient table (fallback rows written as the 7-variable equation in the same form)
rows = []
for z in range(14):
    for c in range(6):
        kind, b = CZ[(z, c)]
        n = int(((zone == z) & (cont == c)).sum())
        if kind == "own":
            co = list(b)
        else:
            s = 1 if z * 5 + 2.5 > 33 else 0
            bb = B7[s]; m_ = z * 5 + 2.5
            kshift = bb[7 + c - 1] if c > 0 else 0.0
            co = [bb[0] + bb[1] * m_ + kshift, bb[1], bb[2], bb[3], bb[4], bb[5], bb[6]]
        rows.append(dict(key=f"{z*5}|{c}", zone=f"{z*5}-{z*5+5}N", zone_start=z * 5, continent=CONT[c], lakes=n, source="own fit" if kind == "own" else "7-variable equation",
                         a=co[0], per_deg=co[1], per_km=co[2], extra_per_km_above_1500=co[3], coast=co[4], depth=co[5], area=co[6], coast_x_km=0.0))
ZT = pd.DataFrame(rows); ZT.to_csv("zone_continent_equations.csv", index=False)
print("own fits", (ZT.source == "own fit").sum(), "of", len(ZT))

# full-data in-sample fit too (for reference)
inS = {"M3": split_pred(X3, B3, allm), "M7": split_pred(X7, B7, allm)}
def coefdict(B, names):
    return {s: dict(zip(["const"] + names, map(float, B[s]))) for s in (0, 1)}
OUT = dict(heldout=M,
           M3=coefdict(B3, ["lat", "h", "C"] + [f"K_{c}" for c in CONT[1:]]),
           M7=coefdict(B7, ["lat", "h", "h_plus", "C", "D", "A"] + [f"K_{c}" for c in CONT[1:]]),
           n=int(len(y)), shrink=SHRINK, median_depth=MED_D, median_area=MED_A, continents=CONT,
           insample={k: metrics(v) for k, v in inS.items()})
json.dump(OUT, open("models.json", "w"), indent=1)
print(json.dumps(OUT["M3"], indent=0)); print(json.dumps(OUT["M7"], indent=0))
