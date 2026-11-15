import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
P = pd.read_parquet("heldout_predictions.parquet"); J = json.load(open("models.json"))
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
names = {"M3": "Model 1 · 3 variables\n+ continent", "M4": "Model 2 · Model 1\n+ nearby lakes", "M7": "Model 3 · 7 variables\n(no correction)", "MA": "Model 4 · all variables\n+ nearby lakes"}
fig, axs = plt.subplots(1, 4, figsize=(13, 4.2), sharey=True)
for ax, k in zip(axs, names):
    hb = ax.hexbin(P.actual, P[k], gridsize=60, bins="log", cmap="cividis", mincnt=1, extent=(0, 36, 0, 36))
    ax.plot([0, 36], [0, 36], "--", color="#d06a1a", lw=1.1)
    m = J["heldout"][k]
    ax.set_title(names[k] + f"\nR² {m['r2']:.2f} · typical error {m['typical']:.1f} °C", fontsize=8.6); ax.set_xlim(0, 36); ax.set_ylim(0, 36); ax.set_aspect("equal"); ax.set_xlabel("Actual (°C)")
axs[0].set_ylabel("Predicted July temperature (°C)")
cb = fig.colorbar(hb, ax=axs, shrink=0.85, pad=0.01); cb.set_label("lakes (log scale)")
fig.savefig("/home/claude/paper/img/fig13_predicted_vs_actual.png", dpi=200, bbox_inches="tight")
