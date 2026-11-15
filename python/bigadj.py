# big-lake adjustment for Models 1 and 2 (lakes of 500 km2 or more), fitted on held-out errors, tested leave-one-out
import json, numpy as np, pandas as pd
exec(open("models.py").read().split("SHRINK = 20")[0])
H = pd.read_parquet("heldout_predictions.parquet")
assert len(H) == len(y) and np.allclose(H.lat.values, lat)
area = d.Lake_area.values; depth = d.Depth_avg.values
big = area >= 500; idx = np.where(big)[0]
Z = np.c_[np.ones(len(idx)), np.log10(area[idx]) - np.log10(500), np.log10(np.clip(depth[idx], 0.3, None)) - np.log10(3.3), lat[idx] - 50]
J = json.load(open("models.json")); J["big_adj"] = {}
for k, nm in [("M3", "Model 1"), ("M4", "Model 2")]:
    r = y[idx] - H[k].values[idx]; loo = np.zeros(len(idx))
    for i in range(len(idx)):
        m = np.arange(len(idx)) != i
        loo[i] = Z[i] @ np.linalg.lstsq(Z[m], r[m], rcond=None)[0]
    b = np.linalg.lstsq(Z, r, rcond=None)[0]
    print(nm, "big lakes:", len(idx), "mean abs err %.2f -> %.2f (leave-one-out)" % (np.mean(abs(r)), np.mean(abs(r - loo))), "coef", np.round(b, 3))
    J["big_adj"][k] = dict(zip(["const", "logarea", "logdepth", "lat50"], map(float, b)))
    J["big_adj"][k + "_err"] = [float(np.mean(abs(r))), float(np.mean(abs(r - loo)))]
    H.loc[idx, k] = H[k].values[idx] + loo            # held-out predictions now include the adjustment
for k in ["M7", "MA"]:
    r = y[idx] - H[k].values[idx]; J["big_adj"][k + "_err"] = [float(np.mean(abs(r))), float(np.mean(abs(r)))]
SST = np.sum((y - y.mean()) ** 2)
def metrics(p):
    e = y - p
    return dict(r2=1 - np.sum(e ** 2) / SST, typical=float(np.median(abs(e))), rmse=float(np.sqrt(np.mean(e ** 2))),
                within1=float(np.mean(abs(e) <= 1)), within2=float(np.mean(abs(e) <= 2)), bias=float(np.mean(e)))
J["heldout"] = {k: metrics(H[k].values) for k in ["M3", "M4", "M7", "MA"]}
J["n"] = int(len(y)); J["n_big"] = int(len(idx))
for k, v in J["heldout"].items(): print(k, {a: round(b, 3) for a, b in v.items()})
H.to_parquet("heldout_predictions.parquet"); json.dump(J, open("models.json", "w"), indent=1)
