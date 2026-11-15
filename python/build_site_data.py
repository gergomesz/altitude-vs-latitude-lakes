# builds assets/data.js for the GitHub site: lakes (named + largest unnamed per country), all models, yearly/freeze models,
# a 0.5 degree distance-to-sea grid and a simplified coastline/border outline for the map
import json, base64, numpy as np, pandas as pd, scipy.io as sio
OUT = "/home/claude/site/assets/data.js"
df = pd.read_parquet("laketemp_clean.parquet")
d = df[(df.center_lat > 0) & (df.center_lat <= 70) & (df.Tmonth_mean_7 > 0) & (df.Tmonth_mean_7 < 40)].reset_index(drop=True)
d["coast_km"] = pd.read_parquet("coast_km.parquet").coast_km.values
d["Country"] = d.Country.fillna("Unknown")
named = d[d.Lake_name.notna()]
TOPN = 25
un = d[d.Lake_name.isna()].sort_values("Lake_area", ascending=False).groupby("Country").head(TOPN)
L = pd.concat([named, un]).sort_values(["Country", "Lake_area"], ascending=[True, False])
M = [f"Tmonth_mean_{i}" for i in range(1, 13)]
rows = []
for r in L.itertuples():
    nm = r.Lake_name if isinstance(r.Lake_name, str) else f"Unnamed lake #{r.Hylak_id}"
    months = [round(float(getattr(r, m)), 1) for m in M]
    rows.append([nm, r.Country, round(r.center_lat, 3), round(r.center_long, 3), int(round(r.Elevation)), round(float(r.coast_km), 1),
                 round(float(r.Depth_avg), 1), round(float(r.Lake_area), 2), round(float(r.Tmonth_mean_7), 2), months, int(r.ice_days), int(isinstance(r.Lake_name, str))])
C = json.load(open("/home/claude/lakecalc_data.json"))
SJ = json.load(open("seasonal.json")); MM = json.load(open("monthly_model.json"))
season = dict(mean=SJ["mean"]["coef"], mean_brk=SJ["mean"]["brk"], amp=SJ["amp"]["coef"], amp_brk=SJ["amp"]["brk"], peak=SJ["peak"]["coef"],
              open=SJ["open_days"]["coef"], open_brk=SJ["open_days"]["brk"], k=SJ["july_anchor"]["k"], monthly=MM["coef"], knots=MM["knots"],
              freeze_thr=1.5, stats=dict(year_r2=SJ["year_curve"]["r2"], year_mae=SJ["year_curve"]["mae"], blend_mae=SJ["july_anchor"]["blend"][1],
              open_typical=SJ["open_days"]["typical"], monthly_mae_freezing=MM["cv_mae_open_freezing"]))
# distance-to-sea grid, 0.5 degree, 0-70N
G = sio.loadmat("/home/claude/lake-matlab/coast_distance_grid.mat")
g = G["dist_km"][::5, ::5].astype(np.uint16)          # 141 x 721
grid = dict(lat0=0, lon0=-180, step=0.5, nlat=g.shape[0], nlon=g.shape[1], b64=base64.b64encode(g.tobytes()).decode())
# map outline: decimated coastline and borders, integers in 0.1 degree
def poly_lines(path, key):
    t = pd.read_csv(path); out = []
    for _, gr in t.groupby(key, sort=False):
        a = gr[["lon", "lat"]].values
        keep = [0]
        for i in range(1, len(a)):
            if abs(a[i, 0] - a[keep[-1], 0]) + abs(a[i, 1] - a[keep[-1], 1]) > 0.35: keep.append(i)
        if len(keep) > 2: out.append((np.round(a[keep] * 10)).astype(int).ravel().tolist())
    return out
land = poly_lines("/home/claude/lake-matlab/coast.csv", "poly")
bt = pd.read_csv("/home/claude/lake-matlab/borders.csv"); bt["k"] = bt["kind"].astype(str) + "_" + bt["line"].astype(str)
bt.to_csv("/tmp/borders_k.csv", index=False)
borders = poly_lines("/tmp/borders_k.csv", "k")
DATA = dict(lakes=rows, corr=C["corr"], zt=C["zt"], M1=C["M1"], M3=C["M3"], big=C["big"], cont=C["cont"], heldout=C["heldout"], n=C["n"],
            season=season, grid=grid, land=land, borders=borders, n_named=int(len(named)))
s = json.dumps(DATA, separators=(",", ":"))
open(OUT, "w").write("window.LAKE_DATA=" + s + ";\n")
print(len(rows), "lakes;", len(named), "named;", L.Country.nunique(), "countries;", round(len(s) / 1e6, 2), "MB;", len(land), "land lines;", len(borders), "border lines")
