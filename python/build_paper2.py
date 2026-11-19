# research-paper style PDF: html -> chrome --print-to-pdf
import json
import subprocess
import pandas as pd
from paper_extra import *

J = json.load(open("models.json"))
HM = json.load(open("hemi.json"))
HZ = pd.read_csv("hemi_zones.csv")
H = J["heldout"]
NL = pd.read_csv("named_lakes.csv")
RL = pd.read_csv("random_lakes.csv")
ZT = pd.read_csv("zone_continent_equations.csv")
S1 = pd.read_csv("step1.csv"); S3 = pd.read_csv("step3.csv")
FIG = "/home/claude/paper/figm/"
IMG = "/home/claude/paper/img/"
M1, M3 = J["M3"], J["M7"]
CONT = J["continents"]


def f(x, p=2, sign=False):
    s = f"{x:+.{p}f}" if sign else f"{x:.{p}f}"
    return s.replace("-", "−")


def term(c, sym, first=False):
    if first:
        return f(c, 2)
    return (" − " if c < 0 else " + ") + f(abs(c), 3 if abs(c) < 1 else 2) + (" " + sym if sym else "")


def eq(b, keys, syms):
    out = term(b[keys[0]], "", True)
    for k, s in zip(keys[1:], syms[1:]):
        out += term(b[k], s)
    return out


caps = [
    ("fig01_world_map", "Mean July surface temperature of all 1,067,869 lakes, 2013–2021. Dashed: the Alps latitude band (45.8–47.8°N); dotted: southern Canada (50–53°N)."),
    ("fig02_zone_widths", "The zone equation fitted with uniform 2.5°, 5° and 10° zones. 5° is the narrowest width at which every zone has enough lakes above 1,000 m; it is used throughout."),
    ("fig03_lat_alt_grid", "Median July temperature in each 1° × 100 m box. Isotherms are flat south of ~33°N (only height matters) and lean north of it, where about 130 m of height equals 1° of latitude. Faded boxes are interpolated from neighbouring boxes."),
    ("fig04_variance_shares", "Share of lake-to-lake variation explained. Altitude alone explains almost nothing because high lakes are concentrated at low latitudes; once latitude is known, it adds 3.4%."),
    ("fig05_zone_coefficients", "Coefficients of the zone equation in each 5° zone (95% confidence intervals, standard errors clustered by 1° square). Latitude starts to cool lakes only north of about 35–40°N."),
    ("fig06_sliding_band", "A 2° band slid north one degree at a time. Sea-level July temperature is flat to 33.0°N, then falls about 0.45 °C per degree; the altitude effect has no single breakpoint."),
    ("fig07_robustness", "Altitude effect using July temperature vs the yearly ice-free mean. The two agree in the tropics; further north, high lakes are only open in summer, so their yearly mean is a summer mean."),
    ("fig08_alps_scatter", "The Alps latitude band (45.8–47.8°N) around the world: July temperature against elevation for the four regions with high lakes."),
    ("fig09_alps_region_slopes", "Lapse rate by region at the Alps latitude. Europe and Switzerland cool close to the air lapse rate (−6.5 °C/km); East Asia's plateau lakes cool far less."),
    ("fig10_alps_residual_map", "Lakes in the Alps band warmer (red) or colder (blue) than the zone equation predicts. Cold: Newfoundland and the glacier-fed Alps; warm: the Ukrainian steppe and the US interior west."),
    ("fig11_alps_vs_canada", "Low (<500 m) and high (>1,500 m) lakes at two latitudes. Moving 4.7° north costs ~2 °C; climbing ~1.8 km costs ~7.7 °C. The two lines are nearly parallel: the altitude cost is the same in both bands."),
    ("fig12_coast_distance", "Distance to the ocean. (a) North of 33°N inland lakes are up to 2.5 °C warmer than predicted and coastal lakes 2.6 °C colder. (b) Adding coast distance pulls the Alps-band region slopes closer. (c) Coastal mountain lakes cool faster with height."),
]

figs_html = ""
for i, (name, cap) in enumerate(caps, start=1):
    figs_html += f'<figure><img src="file://{FIG}{name}.png"><figcaption><b>Figure {i}.</b> {cap}</figcaption></figure>\n'

cont_rows1 = "".join(
    f"<tr><td>{c}</td><td>{'0' if j == 0 else f(M1['0']['K_' + c])}</td><td>{'0' if j == 0 else f(M1['1']['K_' + c])}</td></tr>"
    for j, c in enumerate(CONT))
cont_rows = "".join(
    f"<tr><td>{c}</td><td>{'0' if j == 0 else f(M3['0']['K_' + c])}</td><td>{'0' if j == 0 else f(M3['1']['K_' + c])}</td></tr>"
    for j, c in enumerate(CONT))

acc_rows = ""
labels = {"M3": "Model 1 · 3 variables + continent", "M4": "Model 2 · Model 1 + nearby lakes", "M7": "Model 3 · 7 variables", "MA": "Model 4 · all variables + nearby lakes"}
for k, nm in labels.items():
    m = H[k]
    acc_rows += f"<tr><td>{nm}</td><td>{m['r2']*100:.1f}%</td><td>{m['typical']:.2f}</td><td>{m['rmse']:.2f}</td><td>{m['within1']*100:.0f}%</td><td>{m['within2']*100:.0f}%</td></tr>"

nl_rows = ""
for r in NL.itertuples():
    nl_rows += (f"<tr><td>{r.lake}</td><td>{r.country.replace('United States of America', 'USA')}</td><td>{r.elev_m:.0f}</td><td>{r.area_km2:,.0f}</td>"
                f"<td><b>{r.actual:.1f}</b></td><td>{r.M1:.1f}</td><td>{r.M2:.1f}</td><td>{r.M3:.1f}</td><td>{r.M4:.1f}</td></tr>")
mae = {k: (NL[k] - NL.actual).abs().mean() for k in ["M1", "M2", "M3", "M4"]}
nl_rows += "<tr class='sum'><td colspan=5>Average size of error (°C)</td>" + "".join(f"<td>{mae[k]:.1f}</td>" for k in ["M1", "M2", "M3", "M4"]) + "</tr>"
# random lakes: predictions need the same calculation; reuse named.py logic
import importlib.util
spec = importlib.util.spec_from_file_location("named", "named.py")
src = open("named.py").read().split("names = [")[0] + "\n" + open("named.py").read().split("def pred(r):")[1].join(["def pred(r):", ""]) if False else None
exec(open("named.py").read().split("N = pd.DataFrame(rows)")[0].split("names = [")[0])
exec("def pred(r):" + open("named.py").read().split("def pred(r):")[1].split("N = pd.concat")[0])
RLp = pd.concat([RL, RL.apply(pred, axis=1)], axis=1)
maer = {k: (RLp[k] - RLp.actual).abs().mean() for k in ["M1", "M2", "M3", "M4"]}
rl_rows = ""
for r in RLp.itertuples():
    rl_rows += (f"<tr><td>{r.lat:.1f}</td><td>{r.lon:.1f}</td><td>{r.country.replace('United States of America', 'USA') if isinstance(r.country, str) else ''}</td><td>{r.elev_m:.0f}</td>"
                f"<td><b>{r.actual:.1f}</b></td><td>{r.M1:.1f}</td><td>{r.M2:.1f}</td><td>{r.M3:.1f}</td><td>{r.M4:.1f}</td></tr>")
rl_rows += "<tr class='sum'><td colspan=5>Average size of error (°C)</td>" + "".join(f"<td>{maer[k]:.1f}</td>" for k in ["M1", "M2", "M3", "M4"]) + "</tr>"

own = ZT[ZT.source == "own fit"]
zt_rows = "".join(
    f"<tr><td>{r.zone.replace('N', '°N')}</td><td>{r.continent}</td><td>{r.lakes:,}</td><td>{f(r.a)}</td><td>{f(r.per_deg)}</td><td>{f(r.per_km)}</td>"
    f"<td>{f(r.extra_per_km_above_1500)}</td><td>{f(r.coast)}</td><td>{f(r.depth)}</td><td>{f(r.area)}</td></tr>"
    for r in own.itertuples())

_rows = [r for r in zt_rows.split("</tr>") if r.strip()]
SPLIT_K = int(open("split_k.txt").read()) if __import__("os").path.exists("split_k.txt") else 16
_half = SPLIT_K
zt_a = "</tr>".join(_rows[:_half]) + "</tr>"; zt_b = "</tr>".join(_rows[_half:]) + "</tr>" if _half < len(_rows) else ""
ZT_B = ("""<p class="small">Continued below.</p>
<table class="compact"><tr><th>Zone</th><th>Continent</th><th>Lakes</th><th>a</th><th>b<sub>φ</sub></th><th>b<sub>h</sub></th><th>b<sub>h+</sub></th><th>b<sub>C</sub></th><th>b<sub>D</sub></th><th>b<sub>A</sub></th></tr>""" + zt_b + """</table>""") if zt_b else ""
def bigeq(k):
    a = J["big_adj"][k]
    return (f(a["const"]) + term(a["logarea"], "[log<sub>10</sub>(area) − log<sub>10</sub>(500)]") + term(a["logdepth"], "D")
            + term(a["lat50"], "(φ − 50)"))


m1s = eq(M1["0"], ["const", "lat", "h", "C"], ["", "φ", "h", "C"])
m1n = eq(M1["1"], ["const", "lat", "h", "C"], ["", "φ", "h", "C"])
k7 = ["const", "lat", "h", "h_plus", "C", "D", "A"]; s7 = ["", "φ", "h", "h<sup>+</sup>", "C", "D", "A"]
m3s = eq(M3["0"], k7, s7) + " + K<sub>S</sub>"
m3n = eq(M3["1"], k7, s7) + " + K<sub>N</sub>"

exec(open("paper_cat.py").read())
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: A4; margin: 20mm 18mm 20mm 18mm; }}
body {{ font-family: 'DejaVu Serif', Georgia, serif; font-size: 10.2pt; line-height: 1.45; color: #111; }}
h1 {{ font-size: 19pt; line-height: 1.2; margin: 0 0 4pt; }}
h2, h3 {{ page-break-after: avoid; }}
h2 {{ font-size: 13pt; margin: 18pt 0 6pt; border-bottom: 1px solid #999; padding-bottom: 2pt; }}
h3 {{ font-size: 11pt; margin: 12pt 0 4pt; }}
.sub {{ color: #444; font-style: italic; margin-bottom: 10pt; }}
.abstract {{ background: #f3f3ef; padding: 8pt 11pt; border-left: 3px solid #333; margin: 10pt 0 6pt; }}
figure {{ margin: 8pt 0 4pt; text-align: center; }}
.figblock {{ break-inside: avoid; page-break-inside: avoid; margin: 6pt 0 10pt; }}
.expl {{ font-size: 9.3pt; line-height: 1.38; background: #fafaf7; border-left: 3px solid #c9c9c0; padding: 4pt 9pt; margin-top: 4pt; }}
.expl p {{ margin: 2pt 0; }}
.tblock {{ break-inside: avoid; page-break-inside: avoid; margin: 4pt 0 6pt; }}
.tblock table {{ margin: 2pt 0 4pt; }}
h2 {{ break-after: avoid; }} h3 {{ break-after: avoid; }}
p {{ orphans: 3; widows: 3; }}
figure img {{ max-width: 100%; max-height: 118mm; }}
figcaption {{ font-size: 8.8pt; text-align: left; color: #222; margin-top: 4pt; }}
.eq {{ font-family: 'DejaVu Serif', serif; font-size: 11pt; background: #f7f7f4; border: 1px solid #ddd; padding: 7pt 10pt; margin: 6pt 0; }}
.road td:first-child {{ white-space: nowrap; }}
.compact td {{ padding: 0.6pt 5pt; font-size: 7.8pt; white-space: nowrap; }}
.compact th {{ font-size: 7.9pt; }}
.road td {{ white-space: normal; }} .road td:first-child {{ white-space: nowrap; }}
table {{ border-collapse: collapse; font-size: 8.2pt; margin: 6pt 0 10pt; width: 100%; page-break-inside: auto; }}
th, td {{ border: 1px solid #ccc; padding: 1.6pt 5pt; text-align: right; }}
th {{ background: #1f2a36; color: #fff; font-weight: normal; text-align: center; }}
td:first-child, td.l {{ text-align: left; }}
tr.sum td {{ font-weight: bold; background: #eef3f7; }}
tr {{ page-break-inside: avoid; }}
.small {{ font-size: 8.6pt; color: #444; }}
.pb {{ page-break-before: always; }}
ol.key li, ol.cat > li {{ margin-bottom: 4pt; }}
.cat .eq {{ font-size: 10pt; padding: 4pt 8pt; margin: 3pt 0 2pt; }}
.keybox {{ border: 1px solid #bbb; padding: 4pt 12pt 2pt; margin: 8pt 0; font-size: 9.6pt; }}
.box {{ display: flex; gap: 14pt; }} .box > div {{ flex: 1; }}
</style></head><body>

<h1>Height or Latitude? What sets the surface temperature of the world's lakes, in summer and through the year</h1>
<div class="sub">November 2026</div>

<div class="abstract"><b>Summary.</b> Using Landsat 8 surface temperatures for 1,067,869 lakes (LakeTEMP, 2013–2021), we test whether latitude or altitude
controls July lake temperature, where that balance changes, and how well simple equations predict it. Latitude explains far more of the variation
(41% vs 3%), but per unit altitude is stronger: about 130 m of height cools a lake as much as one degree of latitude. Latitude only begins to matter
north of <b>33.0°N</b>. Distance to the ocean is the third major control: north of 33°N, inland lakes are up to 5 °C warmer than coastal lakes at the
same latitude and height. An equation with three variables (latitude, height, distance to the coast) and a continent shift, split at 33°N, explains
{H['M3']['r2']*100:.0f}% of the variation in lakes it was not fitted to; adding a correction from nearby lakes raises this to {H['M4']['r2']*100:.0f}%, and the full model reaches
{H['MA']['r2']*100:.0f}% with a typical error of {H['MA']['typical']:.1f} °C. The same controls hold in the Southern Hemisphere, but the break comes earlier
(27.5°S) and the coast matters less. Extending the analysis to the whole year, the {SJ['n_open']:,} lakes that never freeze follow a single yearly wave
whose average, size and timing are set by the same few variables; geography alone predicts every month with R² = {SJ['year_curve']['r2']:.2f}.</div>
{KEY}

<h2>1. Introduction</h2>
<p>Lakes are warming worldwide (O'Reilly et al., 2015), but how fast depends on what sets their temperature in the first place. Air cools by about
6.5 °C per km of altitude and summers shorten with latitude, yet a lake is heated by sunlight at its surface and stores heat, so neither rule
transfers directly. This report asks three questions: (1) does latitude or altitude matter more for lake surface temperature; (2) is the trade-off
between them the same everywhere, or does it change at particular latitudes; and (3) how accurately can a small number of variables predict the
July temperature of any lake; (4) whether the answers hold in the Southern Hemisphere; and (5) how lake temperature changes through
the rest of the year.</p>

<h2>2. Data and methods</h2>
<p><b>Data.</b> LakeTEMP aggregated file (Korver et al., 2024): monthly mean Landsat 8 skin temperature for 2013–2021 for each HydroLAKES lake.
Natural lakes with ≥46 cloud-free observations, standard statistics and no intermittency were kept; Northern Hemisphere, 0–70°N, July mean
0–40 °C (1,067,869 lakes). For the Southern Hemisphere, January (summer) means were used for 30,203 lakes. For the yearly analysis,
all 12 monthly means of 1,098,137 lakes within 70° of the equator were used. Distance to the ocean was computed from each lake centre to the Natural Earth 1:50m coastline.</p>
<p><b>Methods.</b> Ordinary least squares with standard errors clustered by 1° × 1° square. Latitude effects were estimated in uniform 5° zones and
in a sliding 2° band with a two-line breakpoint fit (bootstrap confidence interval). Prediction accuracy was measured by 5-fold cross-validation:
lakes were split into five groups by 1° square, and each group was predicted by a model fitted to the other four.</p>

<h3>How this report is organised</h3>
<p class="small" style="margin:0 0 3pt">Every figure is followed by a box explaining how to read it and what it shows.</p>
<table class="compact road"><tr><th>Section</th><th>What it covers</th></tr>
<tr><td>3. Results</td><td class="l">Twelve figures on July temperature: height vs latitude, the 33°N break, the Alps latitude, the ocean</td></tr>
<tr><td>4. Effects one at a time</td><td class="l">Altitude, latitude and coast measured separately, zone by zone</td></tr>
<tr><td>5. Building the equations</td><td class="l">What each ingredient adds; number of equations; curved terms</td></tr>
<tr><td>6. Prediction equations</td><td class="l">The four models with every coefficient</td></tr>
<tr><td>7. How close the models are</td><td class="l">Accuracy on unseen lakes; random lakes; famous and big lakes</td></tr>
<tr><td>8. Southern Hemisphere</td><td class="l">The same analysis for southern lakes in January</td></tr>
<tr><td>9. Through the whole year</td><td class="l">Yearly cycle, its equations, whole-year predictions, ice-free season</td></tr>
<tr><td>10. What could still improve</td><td class="l">Ingredients that could close the remaining gap</td></tr>
<tr><td>11. Everything found</td><td class="l">Every result in one numbered list, each with its equation</td></tr>
<tr><td>12. Limits</td><td class="l">What the data and methods cannot tell us</td></tr></table>
<h2 class="pb">3. Results</h2>
{figs_html}

{step_html}
{build_html}
<h2 class="pb">6. Prediction equations</h2>
<p>Symbols: <i>φ</i> = latitude (°N); <i>h</i> = elevation (km); <i>h</i><sup>+</sup> = max(<i>h</i> − 1.5, 0); <i>C</i> = log<sub>10</sub>(distance to ocean in km + 10);
<i>D</i> = log<sub>10</sub>(depth in m) − log<sub>10</sub>(3.3); <i>A</i> = log<sub>10</sub>(area in km²) − log<sub>10</sub>(0.23). 3.3 m and 0.23 km² are the median lake,
so <i>D</i> = <i>A</i> = 0 for a typical lake. <i>T</i> is the mean July surface temperature (°C).</p>

<h3>Model 1 · three variables + continent (latitude, height, distance to the coast, continent shift), split at 33°N</h3>
<div class="eq">South of 33°N:&nbsp; T = {m1s} + K<sub>S</sub><br>North of 33°N:&nbsp; T = {m1n} + K<sub>N</sub></div>
<table style="width:60%"><tr><th>Continent (by longitude)</th><th>K<sub>S</sub> (south)</th><th>K<sub>N</sub> (north)</th></tr>{cont_rows1}</table>

<p><b>Big-lake adjustment</b> (lakes of 500 km² or more only), added to Model 1:</p>
<div class="eq">B<sub>1</sub> = {bigeq('M3')}</div>

<h3>Model 2 · Model 1 + nearby-lakes correction</h3>
<div class="eq">T = Model 1 equation + c(square) + B<sub>2</sub> &nbsp;&nbsp;(B<sub>2</sub> only for lakes of 500 km² or more)<br>B<sub>2</sub> = {bigeq('M4')}</div>
<p>c is the average error of the Model 1 equation for all known lakes in the 3 × 3 block of one-degree squares around the lake (≈300 × 300 km),
multiplied by n / (n + {J['shrink']}), where n is the number of those lakes, so that sparse areas receive a small correction. Values for all 12,749 squares
are in the spreadsheet (sheet <i>Correction map</i>).</p>

<h3>Model 3 · seven variables, split at 33°N</h3>
<div class="eq">South of 33°N:&nbsp; T = {m3s}<br>North of 33°N:&nbsp; T = {m3n}</div>
<table style="width:60%"><tr><th>Continent (by longitude)</th><th>K<sub>S</sub> (south)</th><th>K<sub>N</sub> (north)</th></tr>{cont_rows}</table>
<p class="small">Western N. America: west of 100°W · Eastern N. America: 100–60°W · N. Atlantic: 60–15°W · Europe: 15°W–40°E · Central Asia: 40–100°E · East Asia: east of 100°E.</p>

<h3>Model 4 · all variables + nearby-lakes correction</h3>
<div class="eq">T = a + b<sub>φ</sub>(φ − φ<sub>mid</sub>) + b<sub>h</sub>h + b<sub>h+</sub>h<sup>+</sup> + b<sub>C</sub>C + b<sub>D</sub>D + b<sub>A</sub>A + c(square)</div>
<p>A separate equation for each 5° zone × continent (84 groups). The {len(own)} groups with at least 300 lakes and 20 above 1,000 m have their own
coefficients (Appendix; groups with fewer than 20 lakes above 1,500 m leave out the h<sup>+</sup> term); the rest use Model 3. φ<sub>mid</sub> is the middle of the zone. The correction c is computed as in Model 2, from Model 4's own errors.</p>

<h2 class="pb">7. How close the models are to the actual temperatures</h2>
<p>All numbers in Table 1 and Figures 13–16 come from lakes that were <b>not used</b> to fit the model being tested.</p>
<figure><img src="file://{IMG}fig13_predicted_vs_actual.png" style="max-height:150mm"><figcaption><b>Figure 13.</b> Predicted vs actual July temperature for every lake (colour = number of lakes, log scale). Dashed line: perfect prediction.</figcaption></figure>
<figure><img src="file://{IMG}fig14_error_curve.png"><figcaption><b>Figure 14.</b> Share of lakes predicted within a given error. Model 4 puts 60% of lakes within ±1 °C and 87% within ±2 °C.</figcaption></figure>
<figure><img src="file://{IMG}fig15_error_by_latitude.png"><figcaption><b>Figure 15.</b> Typical error by latitude. Errors grow toward the Arctic and just north of the 33°N split; the nearby-lakes correction (Models 2 and 4) removes most of this.</figcaption></figure>

<table><tr><th>Model</th><th>Variation explained (R²)</th><th>Typical error (°C)</th><th>RMSE (°C)</th><th>Within ±1 °C</th><th>Within ±2 °C</th></tr>{acc_rows}</table>
<p class="small"><b>Table 1.</b> Out-of-sample accuracy, 1,067,869 lakes. Typical error = median absolute error.</p>
<h3 class="pb">Random lakes</h3>
<p>34 lakes picked at random across all latitudes, the kind of lake the models were built on (predictions from the final equations).</p>
<table class="compact"><tr><th>Lat</th><th>Lon</th><th>Country</th><th>Elev. (m)</th><th>Actual</th><th>Model 1</th><th>Model 2</th><th>Model 3</th><th>Model 4</th></tr>{rl_rows}</table>

<h3 class="pb">Famous lakes</h3>
<p>Very large and deep lakes are far from the typical lake (median 0.23 km², 3.3 m deep) and stay colder in summer because of their volume.
Models 1 and 2 have no size or depth term, so they use the big-lake adjustment for lakes of 500 km² or more; Models 3 and 4 already include size and depth.
The two biggest, Lake Superior and Great Bear Lake, are still predicted 4–7 °C too warm by every model: their volume is so large that the adjustment cannot fully capture it.</p>
<table style="width:75%"><tr><th>{J['n_big']} lakes of 500 km² or more</th><th>Average error before</th><th>Average error after adjustment</th></tr>
<tr><td>Model 1</td><td>{J['big_adj']['M3_err'][0]:.1f} °C</td><td>{J['big_adj']['M3_err'][1]:.1f} °C</td></tr>
<tr><td>Model 2</td><td>{J['big_adj']['M4_err'][0]:.1f} °C</td><td>{J['big_adj']['M4_err'][1]:.1f} °C</td></tr>
<tr><td>Model 3 (no adjustment needed)</td><td>{J['big_adj']['M7_err'][0]:.1f} °C</td><td>—</td></tr>
<tr><td>Model 4 (no adjustment needed)</td><td>{J['big_adj']['MA_err'][0]:.1f} °C</td><td>—</td></tr></table>
<p class="small">Errors for these lakes are from lakes not used to fit the model (the adjustment itself tested by leave-one-out).</p>
<table class="compact"><tr><th>Lake</th><th>Country</th><th>Elev. (m)</th><th>Area (km²)</th><th>Actual</th><th>Model 1</th><th>Model 2</th><th>Model 3</th><th>Model 4</th></tr>{nl_rows}</table>
{big_fig}



<h2 class="pb">8. Does it hold in the Southern Hemisphere?</h2>
<p>July is the Northern Hemisphere summer, so the same analysis was repeated for the {HM['n_south']:,} Southern Hemisphere lakes using January,
their summer month ({HM['n_south_above_1000']:,} of them above 1,000 m, mostly in the Andes and East Africa). For a like-for-like comparison both
hemispheres use the same simple model (distance from the equator, height, depth; no continent effects), so the northern break here is
{HM['break_north']['bp']:.1f}°N rather than 33.0°N.</p>
<table><tr><th></th><th>North (July)</th><th>South (January)</th></tr>
<tr><td>Break latitude (95% range)</td><td>{HM['break_north']['bp']:.1f}° ({HM['break_north']['lo']:.1f}–{HM['break_north']['hi']:.1f})</td><td>{HM['break_south']['bp']:.1f}° ({HM['break_south']['lo']:.1f}–{HM['break_south']['hi']:.1f})</td></tr>
<tr><td>Cooling per degree beyond the break</td><td>{f(HM['break_north']['after'])} °C</td><td>{f(HM['break_south']['after'])} °C</td></tr>
<tr><td>Coast effect poleward of 33° (per unit of C)</td><td>{f(HM['coast_north'][0], 2, True)} °C</td><td>{f(HM['coast_south'][0], 2, True)} °C</td></tr>
<tr><td>Variation explained by latitude, once height is known</td><td>{HM['r2_north']['lat_unique']*100:.0f}%</td><td>{HM['r2_south']['lat_unique']*100:.0f}%</td></tr>
<tr><td>Variation explained by height, once latitude is known</td><td>{HM['r2_north']['alt_unique']*100:.0f}%</td><td>{HM['r2_south']['alt_unique']*100:.0f}%</td></tr>
<tr><td>Northern 3-variable equation on southern lakes</td><td>—</td><td>R² {HM['transfer']['r2']:.2f}, typical error {HM['transfer']['typical']:.1f} °C, {abs(HM['transfer']['bias']):.1f} °C too warm</td></tr>
<tr><td>Southern lakes' own 3-variable equation (held-out)</td><td>—</td><td>R² {HM['own_south']['r2']:.2f}, typical error {HM['own_south']['typical']:.1f} °C</td></tr></table>
<p><b>Height matters more in the south.</b> Once latitude is known, height explains {HM['r2_south']['alt_unique']*100:.0f}% of the variation among southern lakes but only
{HM['r2_north']['alt_unique']*100:.0f}% among northern lakes. The cooling per km is the same in both; the difference is that {HM['n_south_above_1000']/HM['n_south']*100:.0f}% of southern lakes lie above 1,000 m,
while the north is dominated by low-lying lakes in Canada and Scandinavia. Height can only explain variation where lakes differ in height.</p>
<p><b>What carries over:</b> the altitude effect (3–4 °C per km) and the flat tropical band are the same in both hemispheres, and the northern equation still
explains {HM['transfer']['r2']*100:.0f}% of southern lake temperatures. <b>What does not:</b> the break comes earlier in the south ({HM['break_south']['bp']:.1f}°S) and the cooling
beyond it is steeper, while the coast effect is much weaker. Poleward of 30°S there is little land, all of it close to cold ocean, so summers cannot heat up
the way they do over the large northern continents. The 33°N break is therefore not a fixed latitude: it depends on how much land there is.
The northern equation's largest misses are cold glacial lakes in Patagonia (around 48°S).</p>
<figure><img src="file://{IMG}fig16_hemispheres.png" style="max-height:170mm"><figcaption><b>Figure 17.</b> Northern Hemisphere in July vs Southern Hemisphere in January.
(a) The altitude effect is the same in both, about 3–4 °C per km. (b) Latitude does nothing near the equator in either hemisphere. (c) The break comes earlier in the south
and the cooling beyond it is steeper. (d) The 3-variable equation fitted on northern lakes, applied unchanged to southern lakes.</figcaption></figure>
<div style="break-inside:avoid"><p><b>The equations used for this comparison</b> (distance from the equator φ, height h, coast C; no continent), split at 33° from the equator:</p>
<div class="eq">North, within 33°: T = {SEQ['n0']}<br>North, beyond 33°: T = {SEQ['n1']}<br>South, within 33°: T = {SEQ['s0']}<br>South, beyond 33°: T = {SEQ['s1']}</div></div>

{seas_html}
{future_html}
{CAT}
<h2 class="pb">12. Limits</h2>
<p>Landsat measures the top fraction of a millimetre of water in the late morning on clear days. 2013–2021 is a snapshot, not a trend. Canada and
Scandinavia hold most of the lakes, so hemisphere-wide numbers lean toward them. Continents are coarse longitude sectors. The models predict typical
lakes well but extrapolate poorly to the largest and deepest lakes. In the yearly analysis, frozen months appear as 0 °C, so the yearly wave can
only be fitted to lakes that never freeze; poleward of about 40° those lakes are a biased sample (mild, sea-side climates). The ice-free-days equation
is a straight-line approximation and misses by about two weeks for a typical lake. Months are calendar months; shifting southern lakes by exactly six months
is an approximation.</p>

<h2>References</h2>
<p class="small">Korver, M. C. et al. (2024). LakeTEMP: a global lake surface water temperature dataset from Landsat. <i>Remote Sensing of Environment</i>.<br>
Messager, M. L. et al. (2016). Estimating the volume and age of water stored in global lakes. <i>Nature Communications</i>, 7 (HydroLAKES).<br>
O'Reilly, C. M. et al. (2015). Rapid and highly variable warming of lake surface waters around the globe. <i>Geophysical Research Letters</i>, 42.<br>
Woolway, R. I. &amp; Merchant, C. J. (2019). Worldwide alteration of lake mixing regimes in response to climate change. <i>Nature Geoscience</i>, 12.<br>
Kraemer, B. M. et al. (2015). Morphometry and average temperature affect lake stratification responses to climate change. <i>Geophysical Research Letters</i>, 42.<br>
Natural Earth. 1:50m coastline and administrative boundaries. naturalearthdata.com.<br>
RGI Consortium (2017). Randolph Glacier Inventory, version 6.0. GLIMS.<br>
Hersbach, H. et al. (2020). The ERA5 global reanalysis. <i>Quarterly Journal of the Royal Meteorological Society</i>, 146.</p>

<h2>Appendix · Model 4 coefficients for the {len(own)} groups with their own equation (all other groups use Model 3)</h2>
<table class="compact"><tr><th>Zone</th><th>Continent</th><th>Lakes</th><th>a</th><th>b<sub>φ</sub></th><th>b<sub>h</sub></th><th>b<sub>h+</sub></th><th>b<sub>C</sub></th><th>b<sub>D</sub></th><th>b<sub>A</sub></th></tr>{zt_a}</table>
{ZT_B}

</body></html>"""
import re
exec(open("paper_expl.py").read())
import os
FH = json.load(open("fig_heights.json")) if os.path.exists("fig_heights.json") else {}
def _blk(m):
    fig = m.group(0); n = int(re.search(r"<b>Figure (\d+)\.</b>", fig).group(1)); how, what = EXPL[n]
    fig = re.sub(r"<figcaption>.*?</figcaption>", f"<figcaption><b>Figure {n}.</b> {SHORT[n]}</figcaption>", fig, flags=re.S)
    fig = re.sub(r'<img src="([^"]+)"[^>]*>', (lambda mm: f'<img src="{mm.group(1)}" style="height:{FH[str(n)]}mm;max-width:100%;max-height:none;object-fit:contain">') if str(n) in FH else (lambda mm: f'<img src="{mm.group(1)}" style="max-width:100%">'), fig)
    return (f'<div class="figblock">{fig}<div class="expl"><p><b>How to read it.</b> {how}</p>'
            f'<p><b>What it shows.</b> {what}</p></div></div>')
html = re.sub(r"<figure>.*?</figure>", _blk, html, flags=re.S)
# tables: keep each table (with the caption line that follows) on one page
html = re.sub(r'(<table.*?</table>)(\s*<p class="small"><b>Table.*?</p>)?', lambda m: f'<div class="tblock">{m.group(0)}</div>', html, flags=re.S)
html = html.replace('class="pb"', 'class="flow"').replace('<h2 class="flow">Appendix', '<h2>Appendix').replace('<h2 class="flow">3. Results', '<h2 class="pb">3. Results')
open("/home/claude/paper/paper.html", "w").write(html)
out = "/mnt/user-data/outputs/Lake_Temperature_Report.pdf"
subprocess.run(["google-chrome", "--headless", "--no-sandbox", "--disable-gpu", "--allow-file-access-from-files",
                f"--print-to-pdf={out}", "--no-pdf-header-footer", "file:///home/claude/paper/paper.html"], check=True, capture_output=True)
print("pdf written")
