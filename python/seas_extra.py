import json, numpy as np, pandas as pd
J = json.load(open("seasonal.json")); Y = pd.read_parquet("seasonal_open.parquet")
S = [f"s{i}" for i in range(1, 13)]; T = Y[S].values; m = np.arange(1, 13)
pk = np.where(Y.p_peak.notna(), Y.p_peak, 7.0)[:, None]; a = Y.p_amp.clip(lower=0).values[:, None]
geo = Y.p_mean.values[:, None] + a * np.cos(2 * np.pi * (m - pk) / 12)
e = T - geo
J["year_curve"]["within1"] = float((np.abs(e) <= 1).mean()); J["year_curve"]["within2"] = float((np.abs(e) <= 2).mean())
J["year_curve"]["bias_by_month"] = e.mean(0).round(2).tolist()
J["n_open"] = len(Y); J["n_frozen"] = int(len(pd.read_parquet("seasonal_frozen.parquet")))
J["one_wave_r2_median"] = float(np.nanmedian(Y.h1_r2)); J["one_wave_r2_p10"] = float(np.nanpercentile(Y.h1_r2, 10))
# anchoring to July
w = np.cos(2 * np.pi * (m - pk) / 12); w7 = np.cos(2 * np.pi * (7 - pk) / 12); anch = T[:, [6]] + a * (w - w7)
r7 = T[:, 6] - geo[:, 6]; f = Y.fold.values; P = geo.copy()
for k in range(5):
    tr = f != k; kk = [(r7[tr] * (T[tr, j] - geo[tr, j])).sum() / (r7[tr] ** 2).sum() for j in range(12)]
    P[~tr] = geo[~tr] + np.outer(r7[~tr], kk)
kk = [(r7 * (T[:, j] - geo[:, j])).sum() / (r7 ** 2).sum() for j in range(12)]
o = np.arange(12) != 6
def sc(Pp):
    ee = T[:, o] - Pp[:, o]; return [float(1 - (ee ** 2).sum() / ((T[:, o] - T[:, o].mean()) ** 2).sum()), float(np.abs(ee).mean())]
J["july_anchor"] = dict(geo=sc(geo), shift=sc(anch), blend=sc(P), k=[round(x, 2) for x in kk], mae_blend=np.abs(T - P).mean(0).round(2).tolist())
# named lakes
rows = []
for nm in ["Tonle Sap", "Nicaragua", "Malawi", "Tanganyika", "Titicaca", "Chapala", "Van", "Garda", "Como", "Geneva", "Constance", "Taupo"]:
    g = Y[Y.Lake_name == nm]
    if not len(g): continue
    i = g.index[0]; r = Y.loc[i]; sh = 6 if r.S == 1 else 0
    act = np.roll(T[i], -sh); pr = np.roll(geo[i], -sh)
    rows.append(dict(lake=nm, country=r.Country, lat=float(r.center_lat), elev=float(r.Elevation), depth=float(r.Depth_avg), area=float(r.Lake_area),
                     act=act.round(1).tolist(), pred=pr.round(1).tolist(), mean=float(r["mean"]), p_mean=float(r.p_mean), swing=float(2 * r.amp), p_swing=float(2 * max(r.p_amp, 0))))
J["named"] = rows
# ice-free days by latitude & height, plus accuracy
F = pd.read_parquet("seasonal_frozen.parquet"); ee = F.open_days - F.p_open
J["open_days"]["typical"] = float(np.median(np.abs(ee))); J["open_days"]["mae"] = float(np.abs(ee).mean())
json.dump(J, open("seasonal.json", "w"), indent=1)
print(json.dumps({k: J[k] for k in ["year_curve", "july_anchor", "open_days"]}, indent=0)[:2500])
for r in rows: print(r["lake"], r["country"], round(r["mean"],1), round(r["p_mean"],1), round(r["swing"],1), round(r["p_swing"],1))
