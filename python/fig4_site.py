import json, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
H = json.load(open("hemi.json"))
labels = ["Latitude alone", "Altitude alone", "Latitude, controlling\nfor altitude", "Altitude, controlling\nfor latitude"]
keys = ["lat_alone", "alt_alone", "lat_unique", "alt_unique"]
N = [100 * H["r2_north"][k] for k in keys]; S = [100 * H["r2_south"][k] for k in keys]
for theme, ink, rule, ink2 in [("light", "#121316", "#dcdcd8", "#8d9096"), ("dark", "#ecebe6", "#2c2d30", "#7c7d7a")]:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": ink, "axes.edgecolor": ink, "xtick.color": ink, "ytick.color": ink,
                         "axes.labelcolor": ink, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(8.4, 4.0))
    y = range(4)
    ax.barh([i - 0.19 for i in y], N, 0.36, color=ink, label="Northern Hemisphere, July (1,067,869 lakes)")
    ax.barh([i + 0.19 for i in y], S, 0.36, color="none", edgecolor=ink, hatch="////", lw=1, label="Southern Hemisphere, January (30,203 lakes)")
    for i in y:
        ax.text(N[i] + 0.6, i - 0.19, f"{N[i]:.1f}%", va="center", fontsize=9); ax.text(S[i] + 0.6, i + 0.19, f"{S[i]:.1f}%", va="center", fontsize=9)
    ax.set_yticks(list(y)); ax.set_yticklabels(labels); ax.invert_yaxis(); ax.set_xlim(0, 50)
    ax.grid(axis="x", color=rule, lw=0.8); ax.set_axisbelow(True)
    ax.set_xlabel("% of lake-to-lake variation in summer temperature explained (R²)")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1, fontsize=9)
    fig.savefig(f"/home/claude/site/figures/{theme}/f12_variance_both.png", dpi=200, bbox_inches="tight", transparent=True); plt.close(fig)
print("ok")
