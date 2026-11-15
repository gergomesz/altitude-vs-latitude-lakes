# writes the GitHub site's index.html (plate style), reusing the report's numbers and figure explanations
import json, re
exec(open("paper_expl.py").read())
J = json.load(open("models.json")); HM = json.load(open("hemi.json")); SJ = json.load(open("seasonal.json"))
H = J["heldout"]
paper = open("/home/claude/paper/paper.html").read()
cat = re.search(r'<h2[^>]*>11\. Everything found, with its equation</h2>(.*?)<h2[^>]*>12\. Limits', paper, re.S).group(1)
cat = re.sub(r'<div class="tblock">|</div>\s*(?=<)', lambda m: m.group(0) if 'eq' in m.group(0) else m.group(0), cat)
eqs = re.search(r'(<h3>Model 1 · three variables.*?)<h2[^>]*>7\. How close', paper, re.S).group(1)

FOOT = "Lake surface temperature / LakeTEMP 2013–2021"
plates = []
def eli(pid, title, text):
    return (f'<button class="eli-btn" type="button" aria-expanded="false" aria-controls="eli-{pid}" aria-label="{title}: explain in simple terms">?</button>',
            f'<div class="eli" id="eli-{pid}" hidden><p class="eli-k">{title} · in simple terms</p><p>{text}</p></div>')
def head(pid, title, sub, simple, h1=False):
    b, box = eli(pid, title, simple); tag = "h1" if h1 else "h2"
    return f'<div class="plate-head"><div><{tag}>{title} {b}</{tag}><p class="sub{" sub-hero" if h1 else ""}">{sub}</p></div></div>\n{box}'
def fig(n, light=None, dark=None, report=None):
    how, what = EXPL[n]
    if report:
        img = f'<a href="figures/report/{report}" target="_blank"><img class="card" src="figures/report/{report}" alt="Figure {n}: {SHORT[n]}" loading="lazy"></a>'
    else:
        img = (f'<a href="figures/light/{light}" target="_blank"><img class="lt" src="figures/light/{light}" alt="Figure {n}: {SHORT[n]}" loading="lazy">'
               f'<img class="dk" src="figures/dark/{dark or light}" alt="" loading="lazy"></a>')
    return (f'<div class="figure fig">{img}<p class="fig-cap"><b>Figure {n}</b>{SHORT[n]}</p>'
            f'<details class="howto"><summary>How to read it · what it shows</summary><p><span class="kicker">How to read it.</span> {how}</p>'
            f'<p><span class="kicker">What it shows.</span> {what}</p></details></div>')
def plate(pid, inner, k):
    return f'<section class="plate" id="{pid}">\n{inner}\n<div class="plate-foot"><span>{FOOT}</span><span>{k:02d} / NN</span></div>\n</section>'

# 01 hero
plates.append(("overview", head("overview", "Altitude or Latitude?", "What sets the surface temperature of the world's lakes, in summer and through the year",
  "Going north and going uphill both make a lake colder, but by how much each? This project takes about a million lakes measured from space, works out how much latitude, altitude and the nearby ocean each cool a lake, and turns that into equations that predict any lake's temperature. You can try them on any lake in the calculator below.", h1=True) + f"""
<div class="hero-intro">
  <p class="epigraph">There are two ways to walk into the cold: climb a mountain, or travel toward the pole. Both journeys end in winter, yet they are not the same journey. The air keeps a simple rule, losing 6.5 °C for every kilometre of altitude. A lake keeps no such rule. It gathers the sun, holds on to summer, and lives by seasons of its own. To ask which journey a lake feels more is to ask what really makes a place what it is: how far it stands from the equator, or how close it stands to the sky.</p>
  <p>LakeTEMP (Korver et al., 2024) averaged nine years of Landsat 8 surface temperatures, 2013–2021, for every lake it could see. After quality checks, 1,067,869 natural lakes between the equator and 70°N are used for July, 30,203 southern lakes for January, and 1.1 million lakes for the whole year. The question: <strong>which matters more, latitude or altitude, where does that change, and how well can a few numbers predict a lake's temperature?</strong></p>
</div>
<div class="hero-figs">
  <div><div class="v">33°N</div><div class="k">where latitude starts to cool July lakes</div></div>
  <div><div class="v">41% · 3%</div><div class="k">variation explained by latitude · altitude (north)</div></div>
  <div><div class="v">{H['MA']['r2']*100:.0f}%</div><div class="k">of July temperature predicted, unseen lakes</div></div>
  <div><div class="v">{SJ['year_curve']['r2']*100:.0f}%</div><div class="k">of every month predicted from geography</div></div>
</div>
{fig(1, "f2_world_map.png")}"""))

# 02 calculator
plates.append(("calculator", head("calculator", "Lake calculator", "Pick a lake, or enter your own, to see its predicted July temperature, every month of the year, and whether it freezes",
  "Choose a country to see its lakes on the map and in the list, then click one. The calculator runs the four July models from this project, shows each step of the arithmetic, and extends the equations to every month of the year and to ice. Lakes in the list also show what Landsat actually measured, so you can see how close the predictions get.") + """
<div class="tabs" role="tablist"><button class="tab" role="tab" aria-selected="true" data-pane="find" type="button">Find a lake</button><button class="tab" role="tab" aria-selected="false" data-pane="own" type="button">Enter your own lake</button></div>
<div id="pane-find" class="finder">
  <div class="finder-ctl">
    <label class="ctl-l">Country<select id="country"></select></label>
    <label class="ctl-l">Search<input id="q" type="search" placeholder="Lake or country name" autocomplete="off"></label>
    <label class="chk"><input id="named-only" type="checkbox"> Named lakes only</label>
    <p class="small"><span id="list-count"></span> · every named lake in HydroLAKES with a July measurement, plus the 25 largest unnamed lakes in each country. Click a lake in the list or on the map.</p>
    <div id="lake-list" class="lake-list" role="list"></div>
  </div>
  <div class="map-wrap"><svg id="lake-map" class="lake-map" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Map of the lakes in the list"></svg><p class="small">Larger dots are named lakes. Hover for the July temperature.</p></div>
</div>
<div id="pane-own" hidden>
  <form id="own-form" class="own">
    <label>Latitude (°N, 0–70)<input id="f-lat" type="number" step="any" value="46.5"></label>
    <label>Longitude (°E, negative = west)<input id="f-lon" type="number" step="any" value="8.0"></label>
    <label>Elevation (m)<input id="f-elev" type="number" step="any" value="500"></label>
    <label>Distance to the sea (km) <span class="small">filled in from the map</span><input id="f-coast" type="number" step="any" value="300"></label>
    <label>Mean depth (m)<input id="f-depth" type="number" step="any" value="10"></label>
    <label>Area (km²)<input id="f-area" type="number" step="any" value="1"></label>
    <button class="replay" type="submit">Predict</button><span id="own-msg" class="small"></span>
  </form>
</div>
<div id="result" class="result" aria-live="polite" hidden></div>"""))

# 03 which matters more
plates.append(("which", head("which", "Which matters more?", "Latitude and altitude, one lake at a time",
  "Picture every lake as a dot on a chart of how far north it is against how high it is, coloured by its July temperature. If only latitude mattered, colour would change left to right only; if only altitude mattered, bottom to top only. The lines of equal temperature lean, so both matter, and how much they lean tells you how many metres of altitude equal one degree of latitude.") + f"""
{fig(3, "f1_lat_alt_grid.png")}
<div class="plate-body">{fig(4, "f12_variance_both.png")}
<div class="notes"><p><span class="kicker">Latitude wins on reach.</span> On its own, altitude explains almost nothing in the north (0%), because the high lakes (Tibet, the Pamirs, the southern Rockies) sit far south, where lakes are warm anyway. Once latitude is known, altitude adds 3.4% and latitude 41.1%.</p>
<p><span class="kicker">Altitude wins per unit.</span> North of 33°N, about <strong>80–130 m of altitude</strong> cools a lake as much as one degree of latitude.</p>
<p><span class="kicker">The south is different.</span> Altitude explains <strong>16%</strong> of southern lake-to-lake variation against 3% in the north. The cooling per km is the same; the south simply has many more high lakes (Andes, East Africa).</p></div></div>"""))

# 04 where latitude starts to matter
plates.append(("break", head("break", "Where latitude starts to matter", "A flat tropical band, then a steady fall",
  "Cut the hemisphere into 5° strips and measure, in each strip, how much a degree north and a kilometre up cool a lake. Near the equator a degree north does nothing; from about 33°N it starts to cost about half a degree. Altitude costs about the same everywhere.") + f"""
{fig(6, "f4_sliding_band.png")}
<div class="fig-pair">{fig(5, "f3_zone_coefficients.png")}{fig(2, "f11_zone_widths.png")}</div>
<div class="plate-body">{fig(7, "f10_robustness.png")}<div class="notes"><p><span class="kicker">Why 33°N?</span> In July the sun is still high at mid-latitudes and the days are longer, which makes up for the lower sun. July sunlight therefore stays almost tropical up to about 35°, and lake temperature does too.</p><p><span class="kicker">Why July?</span> Comparing lakes in the same month keeps the comparison fair: further north, high lakes are only open in summer, so a yearly average is really a summer average.</p></div></div>"""))

# 05 alps
plates.append(("alps", head("alps", "Same latitude, different mountains", "The Alps latitude band around the world, and the Alps against southern Canada",
  "Take one narrow strip of latitude, the one the Alps sit in, and look at it all the way round the world. Lakes at the same latitude cool with altitude at very different rates in different regions, and the leftover pattern (red warmer, blue colder than predicted) points to the ocean.") + f"""
<div class="fig-pair">{fig(8, "f6_alps_scatter.png")}{fig(9, "f7_alps_regions.png")}</div>
{fig(10, "f5_alps_band_residuals.png")}
<div class="plate-body">{fig(11, "f8_grid2x2.png")}<div class="notes"><p><span class="kicker">The trade-off.</span> Moving 4.7° north, from the Alps band to southern Canada, costs about 2 °C. Climbing about 1.8 km costs about 7.7 °C, at both latitudes.</p></div></div>"""))

# 06 ocean
plates.append(("ocean", head("ocean", "The ocean", "The third control: distance to the sea",
  "Seawater changes temperature slowly, so in summer it is colder than the land and cools everything near it. North of 33°N a lake on the coast is several degrees colder than one far inland at the same latitude and altitude.") + f"""
{fig(12, report="r12_coast.png")}"""))

# 07 models
mrows = "".join(f"<tr><td class='em'>{nm}</td><td class='num'>{H[k]['r2']*100:.1f}%</td><td class='num'>{H[k]['typical']:.2f}</td><td class='num'>{H[k]['within1']*100:.0f}%</td><td class='num'>{H[k]['within2']*100:.0f}%</td></tr>"
                for k, nm in [("M3", "Model 1 · 3 variables + continent"), ("M4", "Model 2 · Model 1 + nearby lakes"), ("M7", "Model 3 · 7 variables"), ("MA", "Model 4 · all variables + nearby lakes")])
plates.append(("models", head("models", "Four prediction models", "From three variables to the full model, tested on lakes they never saw",
  "Each model is an equation: start from a number, add something for latitude, altitude, distance to the sea and so on. To test them fairly, the lakes were split into five groups by location and each group was predicted by an equation built only from the other four. The nearby-lakes correction adds the average miss of known lakes around the one you want.") + f"""
<div class="tablewrap"><table><thead><tr><th>Model</th><th class="num">Variation explained</th><th class="num">Typical error (°C)</th><th class="num">Within ±1 °C</th><th class="num">Within ±2 °C</th></tr></thead><tbody>{mrows}</tbody></table></div>
<p class="caption">Accuracy on 1,067,869 lakes, each predicted by a model that was not fitted to it.</p>
{fig(13, report="r13_predicted_vs_actual.png")}
<div class="fig-pair">{fig(14, report="r14_error_curve.png")}{fig(15, report="r15_error_by_latitude.png")}</div>
<details class="howto big"><summary>The four equations, with every coefficient</summary><div class="eqs">{eqs}</div></details>"""))

# 08 big lakes
plates.append(("big", head("big", "Big lakes", "Lakes of 500 km² or more stay colder than their place suggests",
  "A huge, deep lake is like a giant bathtub that takes all summer to warm up. The simple model expects it to be as warm as the small lakes around it, so it guesses about 5 °C too warm; a correction for size and depth halves that.") + f"""
{fig(16, report="r16_big_lakes.png")}"""))

# 09 south
plates.append(("south", head("south", "The Southern Hemisphere", "January, the southern summer, for 30,203 lakes",
  "Does the same story hold south of the equator? Mostly: altitude costs the same, and the tropics are flat again. But the break comes earlier and the coast matters less, because there is little land at those latitudes and all of it is near cold ocean.") + f"""
{fig(17, report="r17_hemispheres.png")}
<div class="tablewrap"><table><thead><tr><th></th><th>North (July)</th><th>South (January)</th></tr></thead><tbody>
<tr><td class="em">Break latitude</td><td>{HM['break_north']['bp']:.1f}°</td><td>{HM['break_south']['bp']:.1f}°</td></tr>
<tr><td class="em">Cooling per degree beyond the break</td><td>{HM['break_north']['after']:.2f} °C</td><td>{HM['break_south']['after']:.2f} °C</td></tr>
<tr><td class="em">Altitude explains (once latitude is known)</td><td>{HM['r2_north']['alt_unique']*100:.0f}%</td><td>{HM['r2_south']['alt_unique']*100:.0f}%</td></tr>
<tr><td class="em">Northern equation used on southern lakes</td><td>—</td><td>R² {HM['transfer']['r2']:.2f}, {abs(HM['transfer']['bias']):.1f} °C too warm</td></tr></tbody></table></div>"""))

# 10 year
M_, A_, P_, O_ = SJ["mean"]["coef"], SJ["amp"]["coef"], SJ["peak"]["coef"], SJ["open_days"]["coef"]
def t(c, s): return (" − " if c < 0 else " + ") + f"{abs(c):.3f}".rstrip("0").rstrip(".") + (" " + s if s else "")
eqM = f"{M_['const']:.2f}" + t(M_['alat'], "φ") + t(M_['alat_past_17.5'], "(φ − 17.5)<sup>+</sup>") + t(M_['h'], "h") + t(M_['C'], "C") + t(M_['D'], "D") + t(M_['A'], "A") + t(M_['south'], "S")
eqA = f"{A_['const']:.2f}" + t(A_['alat'], "φ") + t(A_['alat_past_39.0'], "(φ − 39)<sup>+</sup>") + t(A_['h'], "h") + t(A_['C'], "C") + t(A_['D'], "D") + t(A_['A'], "A") + t(A_['south'], "S")
eqP = f"{P_['const']:.2f}" + t(P_['alat'], "φ") + t(P_['h'], "h") + t(P_['C'], "C") + t(P_['D'], "D") + t(P_['A'], "A") + t(P_['south'], "S")
eqO = f"{O_['const']:.1f}" + t(O_['alat'], "φ") + t(O_['alat_past_49.5'], "(φ − 49.5)<sup>+</sup>") + t(O_['h'], "h") + t(O_['C'], "C") + t(O_['D'], "D") + t(O_['A'], "A") + t(O_['south'], "S")
plates.append(("year", head("year", "Through the whole year", "One wave per lake, and when lakes freeze",
  "A lake that never freezes warms and cools along one smooth wave each year. Three numbers describe it: the yearly average, how far the summer peak sits above it, and when the peak comes. Each of those has its own equation, so the whole year can be predicted from where the lake is.") + f"""
<div class="eqbox"><p class="label">Any month m (January = 1; southern lakes shift by six months)</p><div class="formula">T(m) = T̄ + a · cos(2π(m − p) / 12)</div>
<p class="eqline"><span class="label">Yearly average</span> T̄ = {eqM}</p>
<p class="eqline"><span class="label">Half-swing</span> a = {eqA}</p>
<p class="eqline"><span class="label">Warmest month</span> p = {eqP}</p>
<p class="eqline"><span class="label">Ice-free days</span> N = {eqO}</p>
<p class="small">φ = distance from the equator (°), h = altitude (km), C = log₁₀(km to sea + 10), D = log₁₀(depth m) − log₁₀(3.3), A = log₁₀(area km²) − log₁₀(0.23), S = 1 for southern lakes, (x)<sup>+</sup> = x if positive, else 0. On unseen lakes the wave predicts every month with R² {SJ['year_curve']['r2']:.2f} (typical error {SJ['year_curve']['mae']:.1f} °C); the ice-free-days equation has R² {SJ['open_days']['r2']:.2f}.</p></div>
{fig(18, report="r18_yearly_cycle.png")}
{fig(19, report="r19_timing_ice.png")}"""))

# 11 everything found
plates.append(("findings", head("findings", "Everything found", "Every result, each with its equation",
  "This is the whole project in one list. Each item is one finding, with the numbers and, where there is one, the equation behind it.") + f'<div class="catalogue">{cat}</div>'))

# 12 downloads
plates.append(("files", head("files", "Report, data and code", "Everything needed to check or rebuild the results",
  "The full report explains every figure and equation. The MATLAB and Python code rebuild every number and figure from the LakeTEMP data.") + """
<div class="cols">
<div><h3>Read</h3><ul>
<li><a href="downloads/Lake_Temperature_Report.pdf">Full report (PDF, 27 pages)</a>: every figure explained, all equations, accuracy tables</li>
<li><a href="downloads/Lake_Report_Overleaf.zip">LaTeX source</a> for the report (Overleaf-ready)</li></ul></div>
<div><h3>Rebuild</h3><ul>
<li><a href="matlab/">MATLAB code</a>: one script per figure, plus the loading and model-testing steps (see <code>matlab/README.txt</code>)</li>
<li><a href="python/">Python analysis</a>: the scripts behind every model, figure and this website</li>
<li><a href="downloads/">CSV tables</a>: zone equations, correction map, named lakes</li>
<li>Data: LakeTEMP (Korver et al., 2024, <i>Remote Sensing of Environment</i>), <a href="https://www.hydrosheds.org/products/hydrolakes">HydroLAKES</a> (Messager et al., 2016), Natural Earth coastline</li></ul></div>
</div>
<div class="notes wide"><p><span class="kicker">Limits.</span> Landsat measures the top fraction of a millimetre of water in the late morning on clear days. 2013–2021 is a snapshot, not a trend. Most lakes are in Canada and Scandinavia, so hemisphere-wide numbers lean toward them. The models predict typical lakes well but the largest and deepest lakes worst. The yearly and ice predictions in the calculator extend equations fitted on never-frozen lakes and are approximate.</p></div>"""))

body = "\n".join(plate(pid, inner, k + 1) for k, (pid, inner) in enumerate(plates)).replace("/ NN", f"/ {len(plates):02d}")
nav = "".join(f'<a href="#{pid}">{lbl}</a>' for pid, lbl in [("calculator", "Calculator"), ("which", "Latitude vs altitude"), ("break", "33°N"), ("alps", "Alps"), ("ocean", "Ocean"),
             ("models", "Models"), ("big", "Big lakes"), ("south", "South"), ("year", "Year & ice"), ("findings", "Findings"), ("files", "Files")])
html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Altitude or Latitude? · Lake temperature calculator</title>
<meta name="description" content="What sets the surface temperature of the world's lakes, with a calculator for any lake: July temperature, every month of the year, and ice.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=STIX+Two+Text:ital@0;1&display=swap">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="sheet">
<div class="topbar">
  <span class="src">LakeTEMP · Landsat 8 · HydroLAKES</span>
  <div class="tb-right">
    <button id="theme-toggle" class="theme-btn" type="button" aria-pressed="false"><svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.2"/><path d="M8 1.8 A6.2 6.2 0 0 1 8 14.2 Z"/></svg><span>Dark mode</span></button>
    <span class="who">NASA Space Apps 2026</span>
  </div>
</div>
<nav class="toc">{nav}</nav>
{body}
<footer class="foot small">Data: LakeTEMP (Korver et al., 2024, <i>Remote Sensing of Environment</i>), HydroLAKES (Messager et al., 2016), Natural Earth. Built for the NASA Space Apps Challenge 2026, Earth System Trend Detective.</footer>
</div>
<script src="assets/data.js"></script>
<script src="assets/app.js"></script>
<script src="assets/calc.js"></script>
</body>
</html>"""
open("/home/claude/site/index.html", "w").write(html)
print(len(plates), "plates,", len(html) // 1000, "kB")
