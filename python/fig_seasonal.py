import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "axes.spines.top": False, "axes.spines.right": False})
J = json.load(open("seasonal.json")); Y = pd.read_parquet("seasonal_open.parquet"); F = pd.read_parquet("seasonal_frozen.parquet")
cN, cS = "#121316", "#d06a1a"
S = [f"s{i}" for i in range(1, 13)]
mlab = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
def binned(g, x, y, edges):
    b = pd.cut(g[x], edges); r = g.groupby(b, observed=True)[y].quantile([0.25, 0.5, 0.75]).unstack(); n = g.groupby(b, observed=True).size()
    r = r[n >= 100]; return np.array([i.mid for i in r.index]), r
# ---------- figure 17: the yearly cycle of lakes that never freeze
fig, ax = plt.subplots(2, 2, figsize=(12, 9.6))
a = ax[0, 0]; bands = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, 60)]
cols = plt.cm.viridis(np.linspace(0.05, 0.9, len(bands)))
for (lo, hi), c in zip(bands, cols):
    g = Y[(Y.alat >= lo) & (Y.alat < hi) & (Y.Elevation < 500)]
    a.plot(range(1, 13), g[S].median().values, "-o", color=c, ms=3.5, label=f"{lo}–{hi}° ({len(g):,})")
a.set_xticks(range(1, 13)); a.set_xticklabels(mlab)
a.set(xlabel="Month (southern lakes shifted 6 months, so July = midsummer in both)", ylabel="Median lake surface temperature (°C)", title="a · The yearly cycle by distance from the equator (lakes below 500 m)", ylim=(0, 40))
a.legend(frameon=False, loc="upper center", fontsize=8.3, title="Distance from the equator (number of lakes)", title_fontsize=8.5, ncol=3)
for k, (pan, tgt, lab, ttl) in enumerate([(ax[0, 1], "mean", "Yearly average temperature (°C)", "b · Yearly average"), (ax[1, 0], "amp", "Summer–winter swing (°C)", "c · How big the seasonal swing is")]):
    a = pan
    for hem, col, mk, nm in [(0, cN, "o", "Northern Hemisphere"), (1, cS, "s", "Southern Hemisphere")]:
        g = Y[(Y.S == hem) & (Y.Elevation < 500)].copy()
        if tgt == "amp": g["v"] = 2 * g.amp
        else: g["v"] = g[tgt]
        x, r = binned(g, "alat", "v", np.arange(0, 62, 2.5))
        a.fill_between(x, r[0.25], r[0.75], color=col, alpha=0.12, lw=0); a.plot(x, r[0.5], "-" + mk, color=col, mfc="white", ms=4, label=nm)
    a.set(xlabel="Distance from the equator (°)", ylabel=lab, title=ttl); a.grid(alpha=0.3)
bm = J["mean"]["brk"]; ax[0, 1].axvline(bm, color="#555", ls="--", lw=1); ax[0, 1].axvline(33, color="#555", ls=":", lw=1)
ax[0, 1].text(bm - 0.8, 6.0, f"yearly average\nstarts falling\nat {bm:.1f}°", ha="right", fontsize=8.3)
ax[0, 1].text(34, 31.0, "July temperature\nstarts falling at 33°", ha="left", va="top", fontsize=8.3)
ax[0, 1].set_ylim(4, 32); ax[0, 1].legend(frameon=False, loc="upper right", bbox_to_anchor=(1.0, 0.82), fontsize=8.5)
ba = J["amp"]["brk"]; ax[1, 0].axvspan(ba, 62, color="#999", alpha=0.1, lw=0)
ax[1, 0].text(ba + 1, 1.2, "past ~40°, only lakes in mild,\nsea-side climates stay unfrozen,\nso the swing looks smaller", fontsize=8.2, va="bottom")
ax[1, 0].set(ylim=(0, 32), xlim=(0, 61)); ax[1, 0].legend(frameon=False, loc="upper left", fontsize=8.5)
# d: coast effect on the swing, holding latitude to 25-40 deg and below 500 m
a = ax[1, 1]
for (lo, hi), c in zip([(20, 30), (30, 40)], ["#7a9cc6", "#1f3f73"]):
    g = Y[(Y.alat >= lo) & (Y.alat < hi) & (Y.Elevation < 500)].copy(); g["v"] = 2 * g.amp
    x, r = binned(g, "coast_km", "v", [0, 10, 25, 50, 100, 200, 400, 800, 1600, 3000])
    a.fill_between(x, r[0.25], r[0.75], color=c, alpha=0.15, lw=0); a.plot(x, r[0.5], "-o", color=c, mfc="white", ms=4, label=f"lakes {lo}–{hi}° from the equator")
a.set_xscale("log"); a.set(xlabel="Distance to the sea (km, log scale)", ylabel="Summer–winter swing (°C)", title="d · Distance to the sea and the swing (same latitude)", ylim=(0, 32)); a.grid(alpha=0.3)
a.legend(frameon=False, loc="upper left", fontsize=8.5)
fig.tight_layout(); fig.savefig("figures/fig17_yearly_cycle.png", dpi=200, bbox_inches="tight"); plt.close(fig)
# ---------- figure 18: timing, ice and predicting the whole year
fig, ax = plt.subplots(2, 2, figsize=(12, 9.6))
a = ax[0, 0]; W = Y[Y.amp > 1.5].copy(); W["days"] = (W.peak - 7.0) * 30.4
x, r = binned(W, "Depth_avg", "days", [0.3, 1, 2, 4, 8, 16, 32, 64, 128, 256, 600])
a.fill_between(x, r[0.25], r[0.75], color=cS, alpha=0.15, lw=0); a.plot(x, r[0.5], "-o", color=cS, mfc="white", ms=4)
a.axhline(0, color="#999", ls=":"); a.set_xscale("log")
a.set(xlabel="Mean lake depth (m, log scale)", ylabel="Warmest point, days after mid-July", title="a · Deep lakes reach their warmest later"); a.grid(alpha=0.3)
a = ax[0, 1]; G = F[F.S == 0]
for lo, hi, c, mk in [(-500, 500, "#9bb7d4", "o"), (500, 1500, "#4f7cac", "s"), (1500, 3000, "#1f3f73", "^"), (3000, 7000, "#121316", "D")]:
    g = G[(G.Elevation >= lo) & (G.Elevation < hi)]
    x, r = binned(g, "alat", "open_days", np.arange(20, 72, 2))
    a.plot(x, r[0.5], "-" + mk, color=c, mfc="white", ms=4, label=f"{max(lo,0)}–{hi} m")
bo = J["open_days"]["brk"]; a.axvline(bo, color="#555", ls="--", lw=1)
a.text(bo + 0.6, 345, f"slows down\npast {bo:.1f}°", fontsize=8.3, va="top")
a.set(xlabel="Latitude (°N)", ylabel="Ice-free days per year (median)", title="b · Lakes that freeze: how long they stay open", ylim=(0, 365), xlim=(20, 71)); a.grid(alpha=0.3)
a.legend(frameon=False, loc="lower left", fontsize=8.5, title="Elevation", title_fontsize=8.5)
a = ax[1, 0]; th = np.linspace(0, 2 * np.pi, 200); mm = th / (2 * np.pi) * 12 + 0.5
ex = [("Tonle Sap", "#2a9d8f"), ("Titicaca", "#7b5ea7"), ("Geneva", "#121316"), ("Taupo", cS)]
for nm, c in ex:
    r = Y[Y.Lake_name == nm].iloc[0]; act = r[S].values.astype(float); pk = r.p_peak if pd.notna(r.p_peak) else 7.0
    pred = r.p_mean + max(r.p_amp, 0) * np.cos(2 * np.pi * (mm - pk) / 12)
    sh = 6 if r.S == 1 else 0; act = np.roll(act, -sh); mmc = (mm + sh - 1) % 12 + 1; o = np.argsort(mmc)
    a.plot(range(1, 13), act, "o", color=c, ms=5); a.plot(mmc[o], pred[o], "-", color=c, lw=1.4, label=f"{nm} ({abs(r.center_lat):.0f}°{'S' if r.S else 'N'}, {int(r.Elevation):,} m)")
a.set_xticks(range(1, 13)); a.set_xticklabels(mlab); a.set_ylim(0, 36); a.set_xlim(0.6, 12.4)
a.set(xlabel="Month (real calendar)", ylabel="Surface temperature (°C)", title="c · Measured (dots) vs predicted year (lines), unseen lakes")
a.legend(frameon=False, loc="upper center", ncol=2, fontsize=8.3); a.grid(alpha=0.3)
a = ax[1, 1]; e = J["year_curve"]["mae_by_month"]
a.bar(range(1, 13), e, color="#4f7cac", width=0.7)
a.set_xticks(range(1, 13)); a.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
a.set(xlabel="Month (southern lakes shifted 6 months)", ylabel="Typical error on unseen lakes (°C)", title=f"d · Whole-year prediction: R² = {J['year_curve']['r2']:.2f}, typical error {J['year_curve']['mae']:.1f} °C", ylim=(0, 2.6))
for i, v in enumerate(e): a.text(i + 1, v + 0.05, f"{v:.1f}", ha="center", fontsize=8)
fig.tight_layout(); fig.savefig("figures/fig18_timing_ice_prediction.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("ok")
