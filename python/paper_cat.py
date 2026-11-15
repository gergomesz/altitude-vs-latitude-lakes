# key findings box + full catalogue of findings with equations (executed inside build_paper2.py)
def _beq(v):
    return f(v[0]) + term(v[1], "φ") + term(v[2], "h") + term(v[3], "C")
SEQ = {"n0": _beq(HM["B_north"]["0"]), "n1": _beq(HM["B_north"]["1"]), "s0": _beq(HM["B_south"]["0"]), "s1": _beq(HM["B_south"]["1"])}
R = json.load(open("results.json"))
al = {r["region"]: r for r in R["alps_by_region"]}
M7n, M7s = M3["1"], M3["0"]
KEY = f"""<div class="keybox"><b>Key findings</b><ol class="key">
<li>Latitude explains far more of the lake-to-lake variation in July temperature than height ({HM['r2_north']['lat_unique']*100:.0f}% vs {HM['r2_north']['alt_unique']*100:.0f}%), but height is the stronger control per unit: north of 33°N, roughly 80–130 m of height cools a lake as much as one degree of latitude.</li>
<li>Latitude does nothing to July lake temperature until <b>33°N</b>; beyond it lakes cool about 0.45 °C per degree.</li>
<li>Height cools lakes by about 2.5–4 °C per km at every latitude, less than the air's 6.5 °C/km, and by about the same amount in both hemispheres.</li>
<li>North of 33°N the ocean is the third major control: coastal lakes are 1–5 °C colder than inland lakes, the gap widening toward the Arctic.</li>
<li>Four prediction models explain {H['M3']['r2']*100:.0f}%, {H['M4']['r2']*100:.0f}%, {H['M7']['r2']*100:.0f}% and {H['MA']['r2']*100:.0f}% of July temperature in lakes they were not fitted to; curved terms add almost nothing.</li>
<li>Lakes of 500 km² or more are about 5 °C colder than the simple model predicts; a size-and-depth adjustment halves the error.</li>
<li>In the Southern Hemisphere height matters far more: once latitude is known it explains {HM['r2_south']['alt_unique']*100:.0f}% of the variation, against {HM['r2_north']['alt_unique']*100:.0f}% in the north (latitude: {HM['r2_south']['lat_unique']*100:.0f}% vs {HM['r2_north']['lat_unique']*100:.0f}%). The cooling per km is the same; the south simply has many more high lakes (Andes, East Africa).</li>
<li>In the Southern Hemisphere the break comes earlier ({HM['break_south']['bp']:.1f}°S), cooling beyond it is steeper, and the coast matters less, because there is little land.</li>
<li>Lakes that never freeze follow one smooth yearly wave. Their yearly average starts falling at {SJ['mean']['brk']:g}° (not 33°), their summer–winter swing grows from under 2 °C at the equator to about 25 °C at 35–40°N, and the sea flattens the swing.</li>
<li>Deep lakes reach their warmest point later (about two weeks for a 50 m lake) and stay free of ice longer.</li>
<li>Geography alone predicts every month of a never-frozen lake with R² = {SJ['year_curve']['r2']:.2f}; knowing July improves the neighbouring months but not winter.</li>
</ol></div>"""
alps_txt = ", ".join(f"{k} {g(v['slope'], 1)}" for k, v in al.items())
CAT = f"""
<h2 class="pb">11. Everything found, with its equation</h2>
<p>A complete list of the results in this report. Symbols: φ = latitude, or distance from the equator in the Southern Hemisphere and yearly sections; h = elevation (km);
h<sup>+</sup> = max(h − 1.5, 0); C = log<sub>10</sub>(km to ocean + 10); D = log<sub>10</sub>(depth m) − log<sub>10</sub>(3.3); A = log<sub>10</sub>(area km²) − log<sub>10</sub>(0.23); S = 1 for
a Southern Hemisphere lake; (x)<sup>+</sup> = x if positive, otherwise 0. Accuracy figures are for lakes not used in fitting.</p>

<h3>A. July temperature, Northern Hemisphere</h3>
<ol class="cat">
<li><b>Latitude matters more overall, height more per unit.</b> Once the other is known, latitude explains {HM['r2_north']['lat_unique']*100:.0f}% of the variation and height
{HM['r2_north']['alt_unique']*100:.0f}% (Fig. 4). High lakes are mostly at low latitudes, so height alone explains almost nothing. North of 33°N, 1° of latitude equals about
130 m of height in the raw median grid (Fig. 3), or {abs(M1['1']['lat'])/abs(M1['1']['h'])*1000:.0f} m once coast and continent are held fixed (Model 1: {g(M1['1']['lat'], 3)} °C per degree ÷ {g(M1['1']['h'])} °C per km).</li>
<li><b>Latitude switches on at 33°N.</b> Sea-level July temperature is flat from the equator to 33.0°N, then falls about 0.45 °C per degree (Fig. 6). In Model 1:
<div class="eq">south of 33°N: {g(M1['0']['lat'], 3, True)} °C per degree &nbsp;·&nbsp; north of 33°N: {g(M1['1']['lat'], 3)} °C per degree</div></li>
<li><b>Altitude effect.</b> 2.5–4 °C per km within each 5° zone (Step 1), against 6.5 °C/km for air. In Model 3 it bends at 1,500 m:
<div class="eq">south of 33°N: {g(M7s['h'])} °C/km below 1.5 km, {g(M7s['h'] + M7s['h_plus'])} °C/km above &nbsp;·&nbsp; north of 33°N: {g(M7n['h'])} °C/km below, {g(M7n['h'] + M7n['h_plus'])} °C/km above</div></li>
<li><b>The coast.</b> Coastal lakes (within 100 km) are colder than inland lakes from 20°N northward, by about 1 °C at 25–35°N rising to 4.4–4.8 °C at 60–70°N (Step 3).
North of 33°N, lakes far inland are up to 2.5 °C warmer than a coast-blind equation predicts, and coastal lakes 2.6 °C colder (Fig. 12). Per unit of C:
<div class="eq">Model 1, south of 33°N: {g(M1['0']['C'], 2, True)} °C &nbsp;·&nbsp; north of 33°N: {g(M1['1']['C'], 2, True)} °C</div></li>
<li><b>Depth and size.</b> Deeper and larger lakes are colder in July. Per tenfold increase in depth: −2 to −3.7 °C in each zone north of 30°N (Step 4). In Model 3,
north of 33°N: {g(M7n['D'], 2, True)} °C per unit D and {g(M7n['A'], 2, True)} °C per unit A.</li>
<li><b>The Alps band (45.8–47.8°N) cools at different rates in different regions</b> (°C per km): {alps_txt}. The difference is significant
(F = {R['alps_slopes_differ']['F']:.0f}); distance to the coast explains part of it (Fig. 12b). Europe cools at nearly the air's rate; East Asia's plateau lakes far less.</li>
<li><b>Alps vs southern Canada.</b> Moving 4.7° north costs about 2 °C; climbing about 1.8 km costs about 7.7 °C. The two height effects are nearly parallel (Fig. 11).</li>
<li><b>Model 1</b> (latitude, height, coast, continent, split at 33°N): R² {H['M3']['r2']:.3f}, typical error {H['M3']['typical']:.2f} °C.
<div class="eq">south: T = {m1s} + K<sub>S</sub> &nbsp;·&nbsp; north: T = {m1n} + K<sub>N</sub></div></li>
<li><b>Model 2</b> = Model 1 + nearby-lakes correction c × n/(n + 20) from the 3 × 3 block of 1° squares: R² {H['M4']['r2']:.3f}, typical error {H['M4']['typical']:.2f} °C.</li>
<li><b>Model 3</b> (seven variables): R² {H['M7']['r2']:.3f}, typical error {H['M7']['typical']:.2f} °C.
<div class="eq">south: T = {m3s}<br>north: T = {m3n}</div></li>
<li><b>Model 4</b> (84 zone × continent equations + correction): R² {H['MA']['r2']:.3f}, typical error {H['MA']['typical']:.2f} °C; {H['MA']['within1']*100:.0f}% of lakes within ±1 °C.</li>
<li><b>Big lakes (≥ 500 km²).</b> Model 1 is {J['big_adj']['M3_err'][0]:.1f} °C off on average for these {J['n_big']} lakes; with the adjustment, {J['big_adj']['M3_err'][1]:.1f} °C. Superior and Great Bear remain
4–7 °C too warm (Fig. 16).
<div class="eq">B<sub>1</sub> = {bigeq('M3')}</div></li>
<li><b>Curved terms barely help.</b> Powers of height, squared terms and products change R² by about one point at most (Section 5.3). A machine-learning model with
the same inputs reaches {IMP['ceiling: machine-learning model, same inputs'][1]*100:.0f}%.</li>
</ol>

<h3>B. Southern Hemisphere (January)</h3>
<ol class="cat" start="14">
<li><b>Same altitude effect</b>, about 3–4 °C per km, and the same flat tropical band (Fig. 17a–b).</li>
<li><b>But height explains much more of the variation.</b> Once latitude is known, height explains {HM['r2_south']['alt_unique']*100:.0f}% of southern lake-to-lake variation vs
{HM['r2_north']['alt_unique']*100:.0f}% in the north; latitude explains {HM['r2_south']['lat_unique']*100:.0f}% vs {HM['r2_north']['lat_unique']*100:.0f}%. About {HM['n_south_above_1000']/HM['n_south']*100:.0f}% of southern lakes lie above 1,000 m, so differences in height
make up a much larger part of the spread, even though each km cools a lake by the same amount.</li>
<li><b>Earlier, steeper break.</b> {HM['break_south']['bp']:.1f}°S (95%: {HM['break_south']['lo']:.1f}–{HM['break_south']['hi']:.1f}) vs {HM['break_north']['bp']:.1f}°N in the same simple model;
beyond it {g(HM['break_south']['after'])} vs {g(HM['break_north']['after'])} °C per degree.</li>
<li><b>Weaker coast effect</b> poleward of 33°: {g(HM['coast_south'][0], 2, True)} vs {g(HM['coast_north'][0], 2, True)} °C per unit of C. There is little land there, and all of it is near cold ocean.</li>
<li><b>The northern equation transfers.</b> Applied unchanged to southern lakes: R² {HM['transfer']['r2']:.2f}, typical error {HM['transfer']['typical']:.1f} °C, {abs(HM['transfer']['bias']):.1f} °C too warm on average.
The south's own equation reaches R² {HM['own_south']['r2']:.2f}.
<div class="eq">South, within 33°: T = {SEQ['s0']}<br>South, beyond 33°: T = {SEQ['s1']}</div></li>
</ol>

<h3>C. Through the year</h3>
<ol class="cat" start="19">
<li><b>One wave per lake.</b> Never-frozen lakes follow T(m) = T̄ + a·cos(2π(m − p)/12); median fit R² {SJ['one_wave_r2_median']:.3f}.</li>
<li><b>Yearly average</b>, flat to {SJ['mean']['brk']:g}° and then falling (R² {SJ['mean']['r2']:.2f}):
<div class="eq">T̄ = {eqM}</div></li>
<li><b>Size of the swing</b>, growing away from the equator and flattened by the sea (R² {SJ['amp']['r2']:.2f}):
<div class="eq">a = {eqA} &nbsp;(full swing 2a)</div></li>
<li><b>Timing of the peak</b>, later for deep and large lakes (R² {SJ['peak']['r2']:.2f}):
<div class="eq">p = {eqP}</div></li>
<li><b>Whole year from geography:</b> R² {SJ['year_curve']['r2']:.2f}, average error {SJ['year_curve']['mae']:.1f} °C per month.</li>
<li><b>Whole year with July known:</b> T(m) = T<sub>geo</sub>(m) + k<sub>m</sub>(July − T<sub>geo</sub>(7)), with k from {min(SJ['july_anchor']['k']):.2f} in winter to 0.88 in June;
R² {SJ['july_anchor']['blend'][0]:.2f}, average error {SJ['july_anchor']['blend'][1]:.1f} °C. Shifting the whole curve to match July is worse.</li>
<li><b>Ice-free season</b> for lakes that freeze (R² {SJ['open_days']['r2']:.2f}, typical error {SJ['open_days']['typical']:.0f} days):
<div class="eq">N = {eqO}</div></li>
</ol>
"""
