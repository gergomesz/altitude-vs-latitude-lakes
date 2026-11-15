import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "axes.spines.top": False, "axes.spines.right": False})
exec(open("models.py").read().split("SHRINK = 20")[0])
H = pd.read_parquet("heldout_predictions.parquet")
area = d.Lake_area.values; depth = d.Depth_avg.values; name = d.Lake_name.fillna("").values
idx = np.where(area >= 500)[0]
Z = np.c_[np.ones(len(idx)), np.log10(area[idx]) - np.log10(500), np.log10(np.clip(depth[idx], 0.3, None)) - np.log10(3.3), lat[idx] - 50]
after = H.M3.values[idx]; r_after = y[idx] - after
# recover 'before' by removing the leave-one-out adjustment
J = json.load(open("models.json")); b = np.array([J["big_adj"]["M3"][k] for k in ["const", "logarea", "logdepth", "lat50"]])
loo = np.zeros(len(idx))
# r_before = r_after + loo ; solve iteratively: loo depends on r_before of others -> recompute from scratch using r_before guess
rb = r_after + Z @ b
for _ in range(3):
    for i in range(len(idx)):
        mm = np.arange(len(idx)) != i; loo[i] = Z[i] @ np.linalg.lstsq(Z[mm], rb[mm], rcond=None)[0]
    rb = r_after + loo
before = y[idx] - rb
fig, ax = plt.subplots(1, 2, figsize=(13, 5.4))
a = ax[0]
a.plot(y[idx], before, "o", mfc="none", mec="#888", ms=5, label=f"Model 1 equation (average error {np.mean(abs(rb)):.1f} °C)")
a.plot(y[idx], after, "o", color="#d06a1a", ms=5, label=f"+ big-lake adjustment (average error {np.mean(abs(r_after)):.1f} °C)")
a.plot([0, 32], [0, 32], "--", color="#777")
big8 = idx[np.argsort(-area[idx])][:8]
for j in big8:
    k = np.where(idx == j)[0][0]
    a.annotate(name[j], (y[j], after[k]), xytext=(4, 2), textcoords="offset points", fontsize=8)
a.set(xlim=(0, 32), ylim=(0, 33), xlabel="Actual July temperature (°C)", ylabel="Predicted July temperature (°C)", title=f"a · {len(idx)} lakes of 500 km² or more")
a.legend(frameon=True, loc="lower right", fontsize=8.5); a.grid(alpha=0.3)
a = ax[1]
for lo, hi, c, lab in [(0, 10, "#b0b0b0", "shallow (under 10 m)"), (10, 50, "#777", "10–50 m deep"), (50, 1e4, "#121316", "deep (over 50 m)")]:
    s = (depth[idx] >= lo) & (depth[idx] < hi)
    a.plot(area[idx][s], rb[s], "o", color=c, ms=5, label=lab)
xs = np.logspace(np.log10(500), 5, 50)
a.plot(xs, b[0] + b[1] * (np.log10(xs) - np.log10(500)) + b[2] * (np.log10(30) - np.log10(3.3)), "-", color="#d06a1a", lw=2, label="adjustment (30 m deep, 50°N)")
a.axhline(0, color="#999", ls=":"); a.set_xscale("log"); a.set_ylim(-20, 8)
a.set(xlabel="Lake area (km², log scale)", ylabel="Actual minus Model 1 (°C)", title="b · The bigger and deeper the lake, the colder than predicted")
a.legend(frameon=True, loc="lower left", fontsize=8.5); a.grid(alpha=0.3)
fig.tight_layout(); fig.savefig("figures/fig_big_lakes.png", dpi=200, bbox_inches="tight")
print("before", np.mean(abs(rb)), "after", np.mean(abs(r_after)), J["big_adj"]["M3_err"])
