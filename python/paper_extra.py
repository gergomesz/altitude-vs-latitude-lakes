# extra sections for the expanded report
import json, numpy as np, pandas as pd
SJ = json.load(open("seasonal.json"))
IMP = json.load(open("improve.json")); IMP2 = json.load(open("improve2.json"))
S1c = pd.read_csv("step1.csv"); S2c = pd.read_csv("step2.csv"); S3c = pd.read_csv("step3.csv"); S4c = pd.read_csv("step4.csv")
FG = "/home/claude/lakes/figures/"
def g(x, p=2, sign=False):
    s = f"{x:+.{p}f}" if sign else f"{x:.{p}f}"
    return s.replace("-", "−")
def tm(c, sym):
    return (" − " if c < 0 else " + ") + g(abs(c), 3 if abs(c) < 1 else 2) + (" " + sym if sym else "")

# ---------- step tables
t1 = "".join(f"<tr><td>{r.zone}</td><td>{r.lakes:,}</td><td>{r.lakes_above_1000m:,}</td><td>{g(r.per_km)}</td><td>{g(r.ci_lo)} to {g(r.ci_hi)}</td></tr>" for r in S1c.itertuples())
t2 = "".join(f"<tr><td>{r.height_band}</td><td>{r.lakes:,}</td><td>{g(r.per_deg_south, 3)}</td><td>{g(r.s_lo, 3)} to {g(r.s_hi, 3)}</td><td>{g(r.per_deg_north, 3)}</td><td>{g(r.n_lo, 3)} to {g(r.n_hi, 3)}</td></tr>" for r in S2c.itertuples())
t3 = "".join(f"<tr><td>{r.zone}</td><td>{r.coastal_lakes:,}</td><td>{r.inland_lakes:,}</td><td>{g(r.coastal_minus_inland, 2, True)}</td><td>{g(r.ci_lo)} to {g(r.ci_hi)}</td></tr>" for r in S3c.itertuples())
t4 = "".join(f"<tr><td>{r.zone}</td><td>{g(r.a)}</td><td>{g(r.per_deg, 3)}</td><td>{g(r.per_km)}</td><td>{g(r.coastal_shift, 2, True)}</td><td>{g(r.depth_x10, 2, True)}</td><td>{r.r2*100:.0f}%</td></tr>" for r in S4c.itertuples())
step_html = f"""
<h2 class="pb">4. The effects one at a time</h2>
<p>Before building prediction equations, each control was measured on its own while the others were held fixed. All four steps use 5° zones of latitude
(north of the equator, July), ordinary least squares, and 95% confidence intervals with errors clustered by 1° square. Depth is included in every step
so that it does not distort the others. A lake is <i>coastal</i> here if it is within 100 km of the ocean.</p>

<h3>Step 1 · Altitude, at a fixed latitude</h3>
<p>Within each 5° zone: July temperature against height, holding position within the zone and depth fixed.</p>
<p><b>What it shows.</b> Wherever there are enough high lakes to measure it (0–55°N), a kilometre of height cools a lake by about 2.5–4 °C, less than the
air's 6.5 °C/km. North of 55°N high lakes are rare among hundreds of thousands of low ones, and the estimate becomes uncertain.</p>
<table class="compact" style="width:85%"><tr><th>Zone</th><th>Lakes</th><th>Above 1,000 m</th><th>°C per km of height</th><th>95% range</th></tr>{t1}</table>

<h3>Step 2 · Latitude, at a fixed height</h3>
<p>Within each height band: July temperature against latitude, with separate slopes south and north of 33°N.</p>
<p><b>What it shows.</b> South of 33°N, moving north does nothing to lakes below 1,000 m (lakes above 1,000 m even get slightly warmer, possibly because the
high plateaus around 25–33°N are dry and sunny). North of 33°N, every height band cools by 0.4–0.7 °C per degree, and high lakes cool fastest.</p>
<table class="compact"><tr><th>Height band</th><th>Lakes</th><th>South of 33°N, °C/degree</th><th>95% range</th><th>North of 33°N, °C/degree</th><th>95% range</th></tr>{t2}</table>

<h3>Step 3 · The coast, at a fixed latitude</h3>
<p>Within each zone: the temperature difference between coastal and inland lakes, holding height, position and depth fixed.</p>
<p><b>What it shows.</b> Near the equator, being near the sea makes little difference (within ±0.7 °C either way). From 20°N northward, coastal lakes are always colder than inland
ones, and the gap widens steadily, from about 1 °C at 25–35°N to almost 5 °C at 60–70°N. In summer, the ocean stays colder than the land and cools
everything near it.</p>
<table class="compact" style="width:85%"><tr><th>Zone</th><th>Coastal lakes</th><th>Inland lakes</th><th>Coastal minus inland (°C)</th><th>95% range</th></tr>{t3}</table>

<h3>Step 4 · All combined, zone by zone</h3>
<div class="eq">T = a + b<sub>φ</sub>(φ − φ<sub>mid</sub>) + b<sub>h</sub>h + b<sub>coast</sub>·[1 if within 100 km of the sea] + b<sub>D</sub>·log<sub>10</sub>(depth / 3.3 m)</div>
<p><b>What it shows.</b> a is the temperature of a typical (3.3 m deep) inland lake at sea level in the middle of the zone. It stays near 28.5–32 °C up to
40°N and then falls. Deeper lakes are colder in every zone north of 30°N, by 2–3.7 °C for each tenfold increase in depth. R² is lower in the north because
the variation there comes from regional climate, which these four variables do not capture.</p>
<table class="compact"><tr><th>Zone</th><th>a (°C)</th><th>b<sub>φ</sub> per degree</th><th>b<sub>h</sub> per km</th><th>b<sub>coast</sub></th><th>b<sub>D</sub> per 10× depth</th><th>R² in zone</th></tr>{t4}</table>
"""

# ---------- building up the equation
lad = [(k, v) for k, v in IMP.items()]
lad_rows = "".join(f"<tr><td>{k.replace('now: ', 'Start: ').replace('ceiling: ', 'Ceiling: ')}</td><td>{v[1]*100:.1f}%</td><td>{v[0]:.2f}</td><td>{v[2]:.2f}</td></tr>" for k, v in lad)
pw = [("One equation: φ, φ², h<sup>0.5</sup>, C, continent", 0.775, 1.38), ("One equation: φ, φ², h, C, continent", 0.769, 1.39),
      ("One equation: φ, φ², h<sup>1.5</sup>, C, continent", 0.737, 1.46), ("One equation: φ, φ², h², C, continent", 0.713, 1.51),
      ("One equation: φ, φ², h, C, φ·C, continent", 0.773, 1.37), ("One equation: φ, φ², h, φ·h, C, φ·C, continent", 0.783, 1.35),
      ("<b>Split at 33°N: φ, h, C, continent (Model 1)</b>", 0.787, 1.33),
      ("Split: φ, h, h², C, continent", 0.790, 1.32), ("Split: φ, h, C, C², continent", 0.787, 1.33),
      ("Split: φ, h, C, φ·C, continent", 0.788, 1.31), ("Split: φ, h, C, φ·C, h·C, continent", 0.796, 1.29)]
pw_rows = "".join(f"<tr><td>{a}</td><td>{b*100:.1f}%</td><td>{c:.2f}</td></tr>" for a, b, c in pw)
i2_rows = "".join(f"<tr><td>{k[3:]}</td><td>{v[1]*100:.1f}%</td><td>{v[0]:.2f}</td></tr>" for k, v in IMP2.items())
build_html = f"""
<h2 class="pb">5. How the prediction equations were built</h2>
<p>Every number in this section is measured on lakes that were held out of the fit (5-fold cross-validation by 1° square). Typical error = median absolute error.</p>
<h3>5.1 Adding one ingredient at a time (5° zone equations)</h3>
<table><tr><th>Equation (each line adds to the one above)</th><th>R²</th><th>Typical error (°C)</th><th>RMSE (°C)</th></tr>{lad_rows}</table>
<p><b>What it shows.</b> The two biggest single gains come from the continent shift (+15 points) and from measuring distance to the coast as a number
rather than yes/no. Letting altitude bend at 1,500 m, letting the coast change the altitude effect, and adding lake size each add between 0 and 2 points.
The last line is a flexible machine-learning model (gradient-boosted trees) given the same inputs. It reaches 93%, which shows how much a perfect
choice of curves could gain from these variables. The gap to it (8 points) is what the nearby-lakes correction later recovers in a simpler way.</p>
<h3>5.2 How many equations?</h3>
<table><tr><th>Structure</th><th>R²</th><th>Typical error (°C)</th></tr>{i2_rows}</table>
<h3>5.3 Do curved terms help? (powers and interactions)</h3>
<table><tr><th>Equation</th><th>R²</th><th>Typical error (°C)</th></tr>{pw_rows}</table>
<p><b>What it shows.</b> Raising height to a power, squaring latitude or the coast term, or multiplying variables together changes R² by at most about
one point. The 33°N split already captures the main bend. Straight-line terms on each side of the split are therefore kept: they are nearly as accurate
and much easier to read.</p>
"""

# ---------- big lake figure
big_fig = f"""<figure><img src="file://{FG}fig_big_lakes.png" style="max-height:95mm"><figcaption><b>Figure 16.</b> The 158 lakes of 500 km² or more. (a) Model 1 predicts
them about 5 °C too warm on average; the big-lake adjustment halves this. The eight largest are named. (b) The error grows with area and is largest for deep lakes. The
line is the adjustment for a 30 m deep lake at 50°N.</figcaption></figure>"""

# ---------- seasonal section
M, A, P, O = SJ["mean"]["coef"], SJ["amp"]["coef"], SJ["peak"]["coef"], SJ["open_days"]["coef"]
bm, ba, bo = SJ["mean"]["brk"], SJ["amp"]["brk"], SJ["open_days"]["brk"]
eqM = g(M["const"]) + tm(M["alat"], "φ") + tm(M[f"alat_past_{bm}"], f"(φ − {bm:g})<sup>+</sup>") + tm(M["h"], "h") + tm(M["C"], "C") + tm(M["D"], "D") + tm(M["A"], "A") + tm(M["south"], "S")
eqA = g(A["const"]) + tm(A["alat"], "φ") + tm(A[f"alat_past_{ba}"], f"(φ − {ba:g})<sup>+</sup>") + tm(A["h"], "h") + tm(A["C"], "C") + tm(A["D"], "D") + tm(A["A"], "A") + tm(A["south"], "S")
eqP = g(P["const"]) + tm(P["alat"], "φ") + tm(P["h"], "h") + tm(P["C"], "C") + tm(P["D"], "D") + tm(P["A"], "A") + tm(P["south"], "S")
eqO = g(O["const"], 1) + tm(O["alat"], "φ") + tm(O[f"alat_past_{bo}"], f"(φ − {bo:g})<sup>+</sup>") + tm(O["h"], "h") + tm(O["C"], "C") + tm(O["D"], "D") + tm(O["A"], "A") + tm(O["south"], "S")
YC = SJ["year_curve"]; JA = SJ["july_anchor"]
mon = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
krow = "".join(f"<td>{k:.2f}</td>" for k in JA["k"])
erow_g = "".join(f"<td>{k:.1f}</td>" for k in YC["mae_by_month"])
erow_b = "".join(f"<td>{k:.1f}</td>" for k in JA["mae_blend"])
brow = "".join(f"<td>{g(k, 1, True)}</td>" for k in YC["bias_by_month"])
nrows = ""
for r in SJ["named"]:
    c = r["country"].replace("Democratic Republic of the Congo", "DR Congo")
    nrows += (f"<tr><td>{r['lake']}</td><td class='l'>{c}</td><td>{abs(r['lat']):.1f}°{'S' if r['lat'] < 0 else 'N'}</td><td>{r['elev']:,.0f}</td><td>{r['depth']:.0f}</td>"
              + "".join(f"<td><b>{r['act'][j]:.1f}</b> / {r['pred'][j]:.1f}</td>" for j in [0, 3, 6, 9])
              + f"<td><b>{r['swing']:.1f}</b> / {r['p_swing']:.1f}</td></tr>")
seas_html = f"""
<h2 class="pb">9. Through the whole year</h2>
<p>The July models describe one month. LakeTEMP also gives a mean for every month, so the same approach was extended to the full year. Frozen months
are recorded as 0 °C, so two groups were treated separately:</p>
<ul><li><b>Lakes that never freeze</b> ({SJ['n_open']:,} lakes, from 55°S to 60°N): their 12 monthly values form a full yearly curve.</li>
<li><b>Lakes that freeze</b> ({SJ['n_frozen']:,} lakes, 20–70° from the equator): for these the useful number is how many days a year they are free of ice.</li></ul>
<p>Southern Hemisphere months were shifted by six months, so that month 7 means midsummer in both hemispheres. φ here is distance from the equator
(latitude without its sign), and S = 1 for a southern lake. The other symbols are as in Section 6.</p>

<h3>9.1 One wave describes a lake's year</h3>
<p>For each never-frozen lake, a single smooth wave was fitted to its 12 monthly temperatures:</p>
<div class="eq">T(m) = T̄ + a · cos(2π(m − p) / 12)</div>
<p>Here T̄ is the yearly average, a is how far the warmest month sits above the average (so the full summer–winter swing is 2a), and p is the month of the
peak. m is the month number (January = 1). This one wave fits the median lake with R² = {SJ['one_wave_r2_median']:.3f}; 90% of lakes are fitted with
R² above {SJ['one_wave_r2_p10']:.2f}. Each lake's year can therefore be reduced to three numbers, and each number gets its own equation.</p>

<h3>9.2 The yearly average</h3>
<div class="eq">T̄ = {eqM}</div>
<p>Held-out R² = {SJ['mean']['r2']:.2f} ({SJ['mean']['r2_nobreak']:.2f} without the break). <b>Why the break is at {bm:g}° and not 33°:</b> yearly sunlight starts
falling soon after the tropics. July sunlight does not: at mid-latitudes the sun is lower, but the days are longer, which makes up for it until about 35°.
So July temperature stays tropical until 33°N, while the yearly average already falls about 0.5 °C per degree from {bm:g}°.
Southern lakes are {abs(M['south']):.1f} °C colder on average, and height costs {abs(M['h']):.1f} °C per km of yearly average.</p>

<h3>9.3 The size of the swing</h3>
<div class="eq">a = {eqA} &nbsp;&nbsp;(set to 0 if negative; full swing = 2a)</div>
<p>Held-out R² = {SJ['amp']['r2']:.2f} ({SJ['amp']['r2_nobreak']:.2f} without the break). The swing grows by {2*A['alat']:.2f} °C per degree away from the equator,
because the gap between summer and winter sunlight widens. The sea flattens it: the swing grows by {2*A['C']:.1f} °C per unit of C (about 5 °C between a lake on the
coast and one 1,000 km inland), and southern lakes swing {abs(2*A['south']):.1f} °C less than northern lakes at the same latitude, because the Southern Hemisphere is
mostly ocean. Water stores so much heat that it evens out the seasons for land nearby. Notably, distance to the sea changes the <i>swing</i> a lot but the
<i>average</i> very little ({g(M['C'], 2, True)} °C per unit of C). The flattening past {ba:g}° is mostly the selection effect described under Figure 18c.</p>

<figure><img src="file://{FG}fig17_yearly_cycle.png" style="max-height:175mm"><figcaption><b>Figure 18.</b> The yearly cycle of lakes that never freeze. (a) Median monthly
temperature of low (&lt;500 m) lakes by distance from the equator. (b) The yearly average stays flat to {bm:g}° and then falls, much earlier than July's 33°.
(c) The summer–winter swing grows from almost nothing at the equator to about 25 °C at 35–40°N. Past about 40°, only lakes in mild sea-side climates stay
unfrozen, which makes the swing appear to shrink (grey). (d) At the same latitude, lakes far inland usually have a bigger swing. Shading: middle 50% of lakes.</figcaption></figure>
<h3>9.4 When the warmest point comes</h3>
<div class="eq">p = {eqP} &nbsp;&nbsp;(month number; 7.0 = mid-July, 7.5 ≈ 1 August)</div>
<p>Fitted on the {SJ['peak']['n']:,} never-frozen lakes whose swing is big enough to have a clear peak (a &gt; 3 °C); held-out R² = {SJ['peak']['r2']:.2f}, the weakest of the
four equations. Deep and large lakes peak later. A deep lake is like a heavy pot: it takes longer to heat up, and longer to cool down. Lakes shallower than about
4 m peak in mid-July; a 50 m deep lake peaks about two weeks later (Figure 19a). High lakes peak slightly earlier.</p>

<h3>9.5 Predicting every month</h3>
<p>Putting the three equations into the wave predicts all 12 months from geography alone. On held-out lakes: <b>R² = {YC['r2']:.2f}</b>, average error {YC['mae']:.1f} °C,
{YC['within1']*100:.0f}% of lake-months within ±1 °C and {YC['within2']*100:.0f}% within ±2 °C.</p>
<table><tr><th></th>{''.join(f'<th>{x}</th>' for x in mon)}</tr>
<tr><td>Average error, geography only (°C)</td>{erow_g}</tr>
<tr><td>Average bias (actual − predicted)</td>{brow}</tr></table>
<p class="small">The wave is slightly too pointed: real lakes are a little warmer than the wave in spring and autumn and a little cooler at the peak.</p>

<p><b>Worked example: Lake Geneva</b> (46.46°N, 370 m, 281 km from the sea, 156 m deep, 572 km²). The inputs are φ = 46.46, h = 0.37,
C = log<sub>10</sub>(291) = 2.463, D = 1.674, A = 3.395 and S = 0. The three equations give a yearly average T̄ = 10.6 °C, a half-swing a = 10.1 °C and a peak at
p = 7.66 (about 5 August). Then, for example, July (m = 7): T = 10.6 + 10.1 × cos(2π(7 − 7.66)/12) = 10.6 + 10.1 × 0.94 = <b>20.1 °C</b> (measured 22.1 °C);
January (m = 1): T = 10.6 + 10.1 × cos(2π(1 − 7.66)/12) = 10.6 − 9.5 = <b>1.2 °C</b> (measured 5.9 °C). Summer is close, but winter is about 5 °C too cold,
the big-lake problem described in 9.7.</p>
<h3>9.6 Using a known July temperature</h3>
<p>If a lake's July temperature is already known (measured, or from Models 1–4), it can sharpen the other months. Shifting the whole wave so it passes
through the measured July value makes things <b>worse</b> (R² {JA['shift'][0]:.2f}, error {JA['shift'][1]:.1f} °C, against {JA['geo'][0]:.2f} and {JA['geo'][1]:.1f} °C), because a lake's July
miss does not carry over to winter. Summer temperature depends on how much sun a lake gets and how quickly it heats up; winter temperature depends on stored
heat and how mild the local winter is. The best rule carries over only part of the July miss:</p>
<div class="eq">T(m) = T<sub>geo</sub>(m) + k<sub>m</sub> × (July measured − T<sub>geo</sub>(7))</div>
<table><tr><th></th>{''.join(f'<th>{x}</th>' for x in mon)}</tr><tr><td>k<sub>m</sub></td>{krow}</tr><tr><td>Average error (°C)</td>{erow_b}</tr></table>
<p>This gives R² = {JA['blend'][0]:.2f} and an average error of {JA['blend'][1]:.1f} °C for the other 11 months. Knowing July pins down June and August to about 0.6 °C, but winter
stays as uncertain as before.</p>

<figure><img src="file://{FG}fig18_timing_ice_prediction.png" style="max-height:175mm"><figcaption><b>Figure 19.</b> (a) Days between mid-July and a lake's warmest point,
by depth. (b) Ice-free days per year for Northern Hemisphere lakes that freeze, by latitude and height. (c) Four lakes not used in fitting: measured monthly temperatures
(dots) and the yearly curve predicted from geography alone (lines). (d) Typical error of the whole-year prediction by month (southern lakes shifted by six months).</figcaption></figure>
<h3>9.7 Named lakes through the year</h3>
<p>Measured (<b>bold</b>) / predicted from geography alone, in the lake's own calendar months, for never-frozen lakes. None of these lakes was used in the fit
that predicts it.</p>
<p><b>What it shows.</b> Shallow tropical lakes such as Tonle Sap and Nicaragua are predicted within about 1–3 °C in every month. The large deep lakes of the Alps,
East Africa, Turkey and New Zealand are predicted about 2–3.5 °C too cold on average, and the deep Alpine lakes and Taupo get a swing that is too large. This is the same big-lake problem seen in July (Section 7): a deep lake carries summer heat
into winter, so its real swing is smaller. A volume term in the swing equation would be the natural next step.</p>
<table><tr><th>Lake</th><th>Country</th><th>Lat.</th><th>Elev. (m)</th><th>Depth (m)</th><th>January</th><th>April</th><th>July</th><th>October</th><th>Swing</th></tr>{nrows}</table>

<h3>9.8 Lakes that freeze: the ice-free season</h3>
<div class="eq">N = {eqO} &nbsp;&nbsp;(days per year; keep between 0 and 365)</div>
<p>Fitted on {SJ['open_days']['n']:,} lakes that freeze for part of the year, 20–70° from the equator. Held-out R² = {SJ['open_days']['r2']:.2f}, typical error
{SJ['open_days']['typical']:.0f} days. Moving one degree poleward costs about {abs(O['alat']):.0f} ice-free days up to {bo:g}°, and about {abs(O['alat'] + O[f'alat_past_{bo}']):.1f} days beyond it, where most
lakes are already open only in the short summer. Each kilometre of height costs {abs(O['h']):.0f} days. Deeper lakes stay open longer, by {O['D']:.0f} days for each tenfold increase
in depth, because they hold their summer heat further into the autumn.</p>
"""

future_html = """
<h2 class="pb">10. What could still improve the models</h2>
<p>Model 4 explains about 91% of the variation in July temperature for lakes it has not seen. The nearby-lakes correction already acts as a stand-in for
regional climate, so most of what is left is differences between neighbouring lakes. Some of it is measurement noise: Landsat passes over in the late
morning on clear days only, small lakes include shoreline pixels, and some monthly means rest on only a few images. No variable can predict noise, so 100%
cannot be reached. The ingredients most likely to close part of the remaining gap, in order of expected value:</p>
<ol>
<li><b>Glacier and snowmelt inflow.</b> Meltwater-fed lakes in the Alps, Himalaya and Rockies stay cold in July regardless of height. Distance to the nearest glacier
(Randolph Glacier Inventory) would target exactly the mountain lakes where errors are largest.</li>
<li><b>Lake volume and residence time.</b> Both are already in HydroLAKES. Water that passes through in days stays close to river temperature; water that stays for
years stores heat. This would also address the big-lake winter problem in Section 9.</li>
<li><b>Which side the ocean is on.</b> Distance to the coast treats a lake next to a cold current the same as one next to a warm sea. Sea temperature at the
nearest coast, or whether the coast is upwind (mostly west at these latitudes), would help along California, Chile, Portugal and Morocco.</li>
<li><b>Cloud cover and sunlight.</b> The monsoon makes South and Southeast Asia cloudy in July, which is part of why latitude stops mattering south of 33°N. A
July sunlight value (e.g. ERA5) would explain this directly instead of through the split.</li>
<li><b>Wind exposure and lake shape.</b> Long lakes facing the wind are mixed, bringing up cold water. Shoreline length relative to area is a rough measure.</li>
<li><b>Water clarity.</b> Murky water traps heat near the surface. Probably a small gain, and harder to obtain.</li>
</ol>
<p>Adding air temperature would raise R² further, but only because lake temperature is close to air temperature. The models would then no longer show
<i>why</i> height, latitude and the coast set the pattern, which is the purpose of this study.</p>
"""
