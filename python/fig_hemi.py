import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "axes.spines.top": False, "axes.spines.right": False})
Z = pd.read_csv("hemi_zones.csv"); H = json.load(open("hemi.json"))
sn, ss = pd.read_csv("slide_north.csv"), pd.read_csv("slide_south.csv")
S = pd.read_parquet("south_lakes.parquet")
cN, cS = "#121316", "#d06a1a"
fig, ax = plt.subplots(2, 2, figsize=(12, 9.6))
for hemi, col, mk, lab in [("north (July)", cN, "o", "Northern Hemisphere, July"), ("south (January)", cS, "s", "Southern Hemisphere, January")]:
    g = Z[Z.hemi == hemi]; x = g.zone + 2.5
    a = ax[0, 0]; a.fill_between(x, g.km_lo, g.km_hi, color=col, alpha=0.12, lw=0); a.plot(x, g.per_km, "-" + mk, color=col, mfc="white", label=lab)
    a = ax[0, 1]; a.fill_between(x, g.deg_lo, g.deg_hi, color=col, alpha=0.12, lw=0); a.plot(x, g.per_deg, "-" + mk, color=col, mfc="white", label=lab)
ax[0, 0].set(xlabel="Distance from the equator (°, 5° zones)", ylabel="Temperature change per km of altitude (°C)", title="a · Altitude effect"); 
ax[0, 1].axhline(0, color="#999", ls=":"); ax[0, 1].set(xlabel="Distance from the equator (°, 5° zones)", ylabel="Temperature change per degree poleward (°C)", title="b · Latitude effect")
a = ax[1, 0]
for s, col, mk, key, lab in [(sn, cN, "o", "break_north", "North, July"), (ss, cS, "s", "break_south", "South, January")]:
    b = H[key]; a.plot(s.alat, s.sea, mk, color=col, mfc="white", ms=4, label=f"{lab}: break at {b['bp']:.1f}° (95% range {b['lo']:.1f}–{b['hi']:.1f})")
    a.axvspan(b["lo"], b["hi"], color=col, alpha=0.1, lw=0); a.axvline(b["bp"], color=col, ls="--", lw=1)
a.set(xlabel="Distance from the equator (°, sliding 2° band)", ylabel="Predicted summer temperature at sea level (°C)", title="c · Where latitude starts to matter")
a.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=1, fontsize=8.5)
a = ax[1, 1]
hb = a.hexbin(S["T"], S.pred_from_north, gridsize=45, bins="log", cmap="cividis", mincnt=1, extent=(0, 36, 0, 36))
a.plot([0, 36], [0, 36], "--", color=cS); t = H["transfer"]; o = H["own_south"]
a.text(1, 41.5, f"Northern equation on southern lakes:\nR² = {t['r2']:.2f}, typical error {t['typical']:.1f} °C,\npredicts {abs(t['bias']):.1f} °C too warm on average\n(southern lakes' own equation: R² = {o['r2']:.2f})",
       va="top", fontsize=8.5, bbox=dict(fc="white", ec="#ccc"))
a.set(xlim=(0, 36), ylim=(0, 42), xlabel="Actual January temperature, southern lakes (°C)", ylabel="Predicted by the northern July equation (°C)",
      title="d · Does the northern equation work in the south?")
for a in ax.ravel()[:3]: a.grid(alpha=0.3)
fig.tight_layout(rect=(0, 0, 1, 0.96)); h_, l_ = ax[0, 0].get_legend_handles_labels(); fig.legend(h_, l_, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.0)); fig.savefig("/home/claude/paper/img/fig16_hemispheres.png", dpi=200, bbox_inches="tight")
print("ok")
