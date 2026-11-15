import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
P = pd.read_parquet("heldout_predictions.parquet"); J = json.load(open("models.json"))
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
names = {"M3": "Model 1 · 3 variables + continent", "M4": "Model 2 · Model 1 + nearby lakes", "M7": "Model 3 · 7 variables", "MA": "Model 4 · all variables + nearby lakes"}
cols = {"M3": "#8d9096", "M4": "#2f6b9a", "M7": "#d06a1a", "MA": "#121316"}
# 1. predicted vs actual, four panels
fig, axs = plt.subplots(2, 2, figsize=(10, 9.4), sharex=True, sharey=True)
for ax, k in zip(axs.ravel(), names):
    hb = ax.hexbin(P.actual, P[k], gridsize=70, bins="log", cmap="cividis", mincnt=1, extent=(0, 36, 0, 36))
    ax.plot([0, 36], [0, 36], "--", color="#d06a1a" if k != "M7" else "#b4532f", lw=1.2)
    m = J["heldout"][k]
    ax.text(1, 34.5, f"R² = {m['r2']:.2f}\ntypical error = {m['typical']:.1f} °C\nwithin ±2 °C: {m['within2']*100:.0f}%", va="top", fontsize=9,
            bbox=dict(fc="white", ec="#cccccc", pad=3))
    ax.set_title(names[k], fontsize=10); ax.set_xlim(0, 36); ax.set_ylim(0, 36); ax.set_aspect("equal")
for ax in axs[1]: ax.set_xlabel("Actual July temperature (°C)")
for ax in axs[:, 0]: ax.set_ylabel("Predicted July temperature (°C)")
cb = fig.colorbar(hb, ax=axs, shrink=0.8, pad=0.01); cb.set_label("number of lakes (log scale)")
fig.savefig("/home/claude/paper/img/fig13_predicted_vs_actual.png", dpi=200, bbox_inches="tight"); plt.close(fig)
# 2. how often within 1, 2, 3 degrees
fig, ax = plt.subplots(figsize=(8.5, 3.6))
e = {k: np.abs(P.actual - P[k]) for k in names}
xs = np.linspace(0, 5, 101)
for k in names:
    ax.plot(xs, [np.mean(e[k] <= x) * 100 for x in xs], color=cols[k], lw=2, label=names[k])
ax.set_xlabel("Error allowed (± °C)"); ax.set_ylabel("Lakes predicted within it (%)"); ax.set_yticks(range(0, 101, 20)); ax.grid(alpha=0.3)
ax.set_ylim(0, 100); ax.set_xlim(0, 5); ax.legend(loc="lower right", fontsize=8.5, frameon=False)
ax.set_title("How close each model gets, on lakes it was not fitted to", fontsize=10)
fig.savefig("/home/claude/paper/img/fig14_error_curve.png", dpi=200, bbox_inches="tight"); plt.close(fig)
# 3. error by latitude band
fig, ax = plt.subplots(figsize=(8.5, 3.6))
bands = np.arange(0, 70, 5)
for k in names:
    v = [np.median(e[k][(P.lat > b) & (P.lat <= b + 5)]) for b in bands]
    ax.plot(bands + 2.5, v, "-o", color=cols[k], ms=4, lw=1.8, label=names[k])
ax.axvline(33, color="#999", ls=":", lw=1); ax.text(33.5, 0.15, "33°N split", fontsize=8, color="#666")
ax.set_xlabel("Latitude (°N, 5° bands)"); ax.set_ylabel("Typical error (°C)"); ax.grid(alpha=0.3); ax.set_ylim(0, 3.6)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), fontsize=8.5, frameon=False, ncol=2)
ax.set_title("Typical error by latitude (lakes not used to fit the model)", fontsize=10)
fig.savefig("/home/claude/paper/img/fig15_error_by_latitude.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("ok")
