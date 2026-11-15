/* Lake temperature calculator: July models 1-4, month-by-month prediction and freeze check.
   All numbers come from window.LAKE_DATA (assets/data.js), built by python/build_site_data.py. */
(function () {
  "use strict";
  const DATA = window.LAKE_DATA;
  const $ = (id) => document.getElementById(id);
  const LOG10 = Math.log10;
  const fmt = (x, p = 1) => (x < 0 ? "−" : "") + Math.abs(x).toFixed(p);
  const sgn = (x, p = 2) => (x < 0 ? "− " : "+ ") + Math.abs(x).toFixed(p);
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const fold = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const EDGES = [-100, -60, -15, 40, 100];
  const NAMES = ["Model 1", "Model 2", "Model 3", "Model 4"];
  const SUB = ["3 variables + continent", "Model 1 + nearby lakes", "7 variables", "all variables + nearby lakes"];
  const COUNTRY = (c) => c.replace("United States of America", "United States");

  const lakes = DATA.lakes.map((r, i) => ({ i, name: r[0], country: r[1], lat: r[2], lon: r[3], elev: r[4], coast: r[5], depth: r[6], area: r[7],
    actual: r[8], months: r[9], ice: r[10], named: r[11] === 1, key: fold(r[0] + " " + r[1]) }));

  /* ---------- distance to the sea, from the 0.5 degree grid ---------- */
  const G = DATA.grid;
  const gridVals = (() => { const b = atob(G.b64), a = new Uint16Array(b.length / 2); for (let i = 0; i < a.length; i++) a[i] = b.charCodeAt(2 * i) | (b.charCodeAt(2 * i + 1) << 8); return a; })();
  function coastAt(lat, lon) {
    const fy = (lat - G.lat0) / G.step, fx = (lon - G.lon0) / G.step;
    const y0 = Math.max(0, Math.min(G.nlat - 2, Math.floor(fy))), x0 = Math.max(0, Math.min(G.nlon - 2, Math.floor(fx)));
    const ty = Math.min(1, Math.max(0, fy - y0)), tx = Math.min(1, Math.max(0, fx - x0));
    const v = (y, x) => gridVals[y * G.nlon + x];
    return (1 - ty) * ((1 - tx) * v(y0, x0) + tx * v(y0, x0 + 1)) + ty * ((1 - tx) * v(y0 + 1, x0) + tx * v(y0 + 1, x0 + 1));
  }

  /* ---------- July: Models 1-4 ---------- */
  function july(L) {
    const side = L.lat > 33 ? "1" : "0";
    const h = L.elev / 1000, hp = Math.max(h - 1.5, 0), C = LOG10(L.coast + 10);
    const D = LOG10(Math.max(L.depth, 0.3)) - LOG10(3.3), A = LOG10(Math.max(L.area, 0.01)) - LOG10(0.23);
    const ci = EDGES.filter((e) => L.lon >= e).length, cont = DATA.cont[ci];
    const cell = Math.floor(L.lat) + "|" + Math.floor(L.lon), corr = DATA.corr[cell] || [0, 0];
    const big = (k) => { if (L.area < 500) return 0; const b = DATA.big[k]; return b.const + b.logarea * (LOG10(L.area) - LOG10(500)) + b.logdepth * D + b.lat50 * (L.lat - 50); };
    const b1 = DATA.M1[side], b3 = DATA.M3[side];
    const K1 = ci ? b1["K_" + cont] : 0, K3 = ci ? b3["K_" + cont] : 0;
    const half = L.lat > 33 ? "north of 33°N" : "south of 33°N";
    const m1 = [["Constant", "starting value " + half, b1.const], ["+ latitude", b1.lat.toFixed(3) + " × " + L.lat.toFixed(2) + "°", b1.lat * L.lat],
      ["+ altitude", b1.h.toFixed(2) + " × " + h.toFixed(3) + " km", b1.h * h], ["+ distance to sea", b1.C.toFixed(2) + " × C (" + C.toFixed(3) + ")", b1.C * C],
      ["+ continent shift", cont + (ci ? "" : " (baseline)"), K1]];
    const eq1 = m1.reduce((s, r) => s + r[2], 0);
    if (L.area >= 500) m1.push(["+ big-lake adjustment", "area " + Math.round(L.area).toLocaleString("en") + " km²", big("M3")]);
    const m2 = [["Model 1 equation", "before its big-lake adjustment", eq1], ["+ nearby-lakes correction", "1° square " + cell + (DATA.corr[cell] ? "" : " (no known lakes nearby)"), corr[0]]];
    if (L.area >= 500) m2.push(["+ big-lake adjustment", "Model 2 version", big("M4")]);
    const m3 = [["Constant", "starting value " + half, b3.const], ["+ latitude", b3.lat.toFixed(3) + " × " + L.lat.toFixed(2) + "°", b3.lat * L.lat],
      ["+ altitude", b3.h.toFixed(2) + " × h" + (hp > 0 ? " " + sgn(b3.h_plus) + " × h⁺" : ""), b3.h * h + b3.h_plus * hp],
      ["+ distance to sea", b3.C.toFixed(2) + " × C", b3.C * C],
      ["+ depth and size", b3.D.toFixed(2) + " × D (" + D.toFixed(2) + ") " + sgn(b3.A) + " × A (" + A.toFixed(2) + ")", b3.D * D + b3.A * A],
      ["+ continent shift", cont, K3]];
    const zone = 5 * Math.floor((L.lat - 1e-9) / 5), z = DATA.zt[zone + "|" + ci];
    const m4 = [["Starting value", "zone " + zone + "–" + (zone + 5) + "°N, " + cont + (z[0] ? "" : " (uses Model 3's numbers)"), z[1] + z[2] * (L.lat - (zone + 2.5))],
      ["+ altitude", z[3].toFixed(2) + " × h" + (hp > 0 ? " " + sgn(z[4]) + " × h⁺" : ""), z[3] * h + z[4] * hp], ["+ distance to sea", z[5].toFixed(2) + " × C", z[5] * C],
      ["+ depth and size", z[6].toFixed(2) + " × D " + sgn(z[7]) + " × A", z[6] * D + z[7] * A], ["+ nearby-lakes correction", "1° square " + cell, corr[1]]];
    const tot = (rows) => rows.reduce((s, r) => s + r[2], 0);
    return { steps: [m1, m2, m3, m4], preds: [m1, m2, m3, m4].map(tot), v: { h, hp, C, D, A, cont, cell, half } };
  }

  /* ---------- the year: yearly wave, freeze check, monthly equations ---------- */
  function year(L, v, julyM4) {
    const S = DATA.season, phi = Math.abs(L.lat), s = L.lat < 0 ? 1 : 0;
    const lin = (c, brk) => { const kb = Object.keys(c).find((k) => k.startsWith("alat_past_"));
      return c.const + c.alat * phi + (kb ? c[kb] * Math.max(phi - brk, 0) : 0) + c.h * v.h + c.C * v.C + c.D * v.D + c.A * v.A + c.south * s; };
    const Tbar = lin(S.mean, S.mean_brk), a = Math.max(lin(S.amp, S.amp_brk), 0), p = lin(S.peak, 0);
    const geo = MON.map((_, m) => Tbar + a * Math.cos(2 * Math.PI * (m + 1 - p) / 12));
    // one equation per month, fitted to all lakes (frozen months count as 0 C): it decides whether the lake freezes
    const x = [1, phi, ...S.knots.map((k) => Math.max(phi - k, 0)), v.h, v.hp, v.C, v.D, v.A, s, s * phi];
    const monthly = S.monthly.map((c) => Math.max(0, c.reduce((t, b, j) => t + b * x[j], 0)));
    const freezes = Math.min(...monthly) < 1;
    let temps, method, ice = new Array(12).fill(false), openDays = null;
    if (!freezes) {
      const r7 = julyM4 - geo[6];
      temps = geo.map((g, m) => g + S.k[m] * r7);
      method = "wave";
    } else {
      temps = monthly;
      openDays = Math.min(365, Math.max(0, lin(S.open, S.open_brk)));
      // mark as ice the coldest months, as many as the ice-free-days equation says (so the chart and the number agree)
      const nIce = Math.min(12, Math.max(1, Math.round((365 - openDays) / 30.4)));
      const order = temps.map((t, m) => [t, m]).sort((p, q) => p[0] - q[0]).slice(0, nIce).map((p) => p[1]);
      order.forEach((m) => (ice[m] = true));
      method = "monthly";
    }
    return { Tbar, a, p, geo, temps, ice, freezes, openDays, method };
  }

  /* ---------- drawing ---------- */
  function julyChart(preds, actual) {
    const vals = preds.concat(actual == null ? [] : [actual]);
    const lo = Math.floor(Math.min(...vals) - 2), hi = Math.ceil(Math.max(...vals) + 2);
    const W = 820, H = 150, x0 = 120, x1 = W - 20, X = (t) => x0 + (t - lo) / (hi - lo) * (x1 - x0);
    let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="July predictions against the measured value">`;
    for (let t = lo; t <= hi; t += (hi - lo > 12 ? 2 : 1)) s += `<line class="grid" x1="${X(t)}" x2="${X(t)}" y1="10" y2="${H - 26}"/><text class="tick" x="${X(t)}" y="${H - 8}" text-anchor="middle">${t}°</text>`;
    if (actual != null) s += `<line class="ln bold" x1="${X(actual)}" x2="${X(actual)}" y1="6" y2="${H - 26}"/><text class="lbl" x="${X(actual) + 6}" y="16">measured ${fmt(actual)} °C</text>`;
    preds.forEach((p, k) => {
      const y = 36 + k * 24;
      s += `<text class="tick" x="0" y="${y + 4}">${NAMES[k]}</text>`;
      if (actual != null) s += `<line class="ln faint dash" x1="${X(actual)}" x2="${X(p)}" y1="${y}" y2="${y}"/>`;
      s += `<circle cx="${X(p)}" cy="${y}" r="5.5" class="${k === 3 ? "fill-ink" : "m-ec"}"/>`;
    });
    return s + "</svg>";
  }
  function yearChart(Y, L) {
    const meas = L.months, all = Y.temps.concat(meas || []);
    const hi = Math.max(5, Math.ceil(Math.max(...all) / 5) * 5 + 2), lo = 0;
    const W = 820, H = 260, x0 = 40, x1 = W - 16, y0 = H - 34, y1 = 14;
    const X = (m) => x0 + (m + 0.5) / 12 * (x1 - x0), Yp = (t) => y0 - (t - lo) / (hi - lo) * (y0 - y1);
    let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Predicted temperature for each month">
      <defs><pattern id="ice-hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" class="hatch-line"/></pattern></defs>`;
    Y.ice.forEach((f, m) => { if (f) s += `<rect x="${X(m) - (x1 - x0) / 24}" y="${y1}" width="${(x1 - x0) / 12}" height="${y0 - y1}" fill="url(#ice-hatch)"/>`; });
    for (let t = 0; t <= hi; t += hi > 20 ? 5 : 2) s += `<line class="grid" x1="${x0}" x2="${x1}" y1="${Yp(t)}" y2="${Yp(t)}"/><text class="tick" x="${x0 - 6}" y="${Yp(t) + 3}" text-anchor="end">${t}°</text>`;
    MON.forEach((m, i) => (s += `<text class="tick" x="${X(i)}" y="${H - 14}" text-anchor="middle">${m}</text>`));
    s += `<line class="axis" x1="${x0}" x2="${x1}" y1="${y0}" y2="${y0}"/>`;
    s += `<polyline class="ln bold" points="${Y.temps.map((t, m) => X(m) + "," + Yp(t)).join(" ")}"/>`;
    if (meas) meas.forEach((t, m) => (s += `<circle cx="${X(m)}" cy="${Yp(t)}" r="4.5" class="${t > 0 ? "fill-ink" : "m-ec"}"/>`));
    Y.temps.forEach((t, m) => (s += `<circle cx="${X(m)}" cy="${Yp(t)}" r="3" class="m-ec"/>`));
    return s + "</svg>";
  }

  /* ---------- the map ---------- */
  const map = $("lake-map"), landD = DATA.land.map((l) => "M" + l.reduce((s, v, i) => s + (i % 2 ? -v / 10 : (i ? " L" : "") + v / 10 + ","), "")).join(""),
        bordD = DATA.borders.map((l) => "M" + l.reduce((s, v, i) => s + (i % 2 ? -v / 10 : (i ? " L" : "") + v / 10 + ","), "")).join("");
  let shown = lakes, current = null;
  function drawMap(list) {
    let x0 = -180, x1 = 180, ya = 0, yb = 72;
    if (list.length && list.length < lakes.length) {
      x0 = Math.min(...list.map((l) => l.lon)); x1 = Math.max(...list.map((l) => l.lon));
      ya = Math.min(...list.map((l) => l.lat)); yb = Math.max(...list.map((l) => l.lat));
      const pad = Math.max(2, 0.12 * Math.max(x1 - x0, yb - ya)); x0 -= pad; x1 += pad; ya -= pad; yb += pad;
      const w = x1 - x0, h = yb - ya, want = 2.1;                   // keep a wide shape
      if (w / h < want) { const e = (h * want - w) / 2; x0 -= e; x1 += e; } else { const e = (w / want - h) / 2; ya -= e; yb += e; }
    }
    const w = x1 - x0, r = w / 260;
    map.setAttribute("viewBox", `${x0} ${-yb} ${w} ${yb - ya}`);
    let s = `<path d="${landD}" class="map-land"/><path d="${bordD}" class="map-border"/>`;
    list.forEach((l) => (s += `<circle data-i="${l.i}" cx="${l.lon}" cy="${-l.lat}" r="${l.named ? r * 1.4 : r}" class="map-dot${l.named ? " named" : ""}${current && current.i === l.i ? " on" : ""}"><title>${esc(l.name)} · ${fmt(l.actual)} °C in July</title></circle>`));
    map.innerHTML = s;
  }
  map.addEventListener("click", (e) => { const c = e.target.closest("circle[data-i]"); if (c) pick(lakes[+c.dataset.i]); });

  /* ---------- list, search and country filter ---------- */
  const sel = $("country"), q = $("q"), list = $("lake-list");
  const counts = {}; lakes.forEach((l) => (counts[l.country] = (counts[l.country] || 0) + 1));
  sel.innerHTML = `<option value="">All countries (${lakes.length.toLocaleString("en")} lakes)</option>` +
    Object.keys(counts).sort((a, b) => COUNTRY(a).localeCompare(COUNTRY(b))).map((c) => `<option value="${esc(c)}">${esc(COUNTRY(c))} (${counts[c]})</option>`).join("");
  function refresh() {
    const c = sel.value, t = fold(q.value.trim()), named = $("named-only").checked;
    shown = lakes.filter((l) => (!c || l.country === c) && (!t || l.key.includes(t)) && (!named || l.named));
    shown.sort((a, b) => b.area - a.area);
    $("list-count").textContent = shown.length.toLocaleString("en") + (shown.length === 1 ? " lake" : " lakes");
    list.innerHTML = shown.slice(0, 300).map((l) => `<button type="button" class="lk${current && current.i === l.i ? " on" : ""}" data-i="${l.i}">
      <span class="lk-n">${esc(l.name)}</span><span class="lk-c">${esc(COUNTRY(l.country))}</span>
      <span class="lk-v">${Math.round(l.elev).toLocaleString("en")} m</span><span class="lk-v">${l.area >= 10 ? Math.round(l.area).toLocaleString("en") : l.area.toFixed(1)} km²</span><span class="lk-v">${fmt(l.actual)}°</span></button>`).join("")
      + (shown.length > 300 ? `<p class="small muted">Showing the 300 largest. Type a name to narrow it down.</p>` : "");
    drawMap(shown);
  }
  list.addEventListener("click", (e) => { const b = e.target.closest(".lk"); if (b) pick(lakes[+b.dataset.i]); });
  sel.addEventListener("change", refresh); q.addEventListener("input", refresh); $("named-only").addEventListener("change", refresh);

  /* ---------- result ---------- */
  function pick(l) {
    current = l;
    refresh();
    render(l, l.name, COUNTRY(l.country) + (l.named ? "" : " · no name in HydroLAKES"));
  }
  function render(L, title, sub) {
    const R = july(L), Y = year(L, R.v, R.preds[3]);
    const fact = (k, v) => `<div><div class="k">${k}</div><div class="v">${v}</div></div>`;
    const err = (p) => (L.actual == null ? "" : `<div class="small">${Math.abs(p - L.actual).toFixed(1)} °C ${p >= L.actual ? "too warm" : "too cold"}</div>`);
    let h = `<div class="res-head"><h3>${esc(title)}</h3><span class="small">${esc(sub)}</span></div>
      <div class="stats six">${fact("Latitude", fmt(L.lat, 2) + "°")}${fact("Longitude", fmt(L.lon, 2) + "°")}${fact("Elevation", Math.round(L.elev).toLocaleString("en") + " m")}
      ${fact("To the sea", Math.round(L.coast).toLocaleString("en") + " km")}${fact("Mean depth", (+L.depth).toFixed(1) + " m")}${fact("Area", L.area >= 10 ? Math.round(L.area).toLocaleString("en") + " km²" : (+L.area).toFixed(2) + " km²")}</div>
      <p class="label">July surface temperature</p>
      <div class="preds">${R.preds.map((p, k) => `<div class="${k === 3 ? "best" : ""}"><div class="k">${NAMES[k]} · ${SUB[k]}</div><div class="big">${fmt(p)}°</div>${err(p)}</div>`).join("")}</div>`;
    if (L.actual != null) h += `<p class="measured">Measured by Landsat (July mean, 2013–2021): <b>${fmt(L.actual)} °C</b></p>`;
    if (L.area >= 500) h += `<div class="note">A very large lake (${Math.round(L.area).toLocaleString("en")} km²). Big, deep lakes stay colder than their position suggests; Models 1 and 2 add a big-lake adjustment, but expect bigger errors than for a typical lake.</div>`;
    h += `<div class="figure">${julyChart(R.preds, L.actual)}</div>`;

    // the year
    // the ice season can run over New Year, so find where the run of ice months starts
    let iceRange = "";
    const nIce = Y.ice.filter(Boolean).length;
    if (nIce && nIce < 12) {
      const first = Y.ice.findIndex((f, m) => f && !Y.ice[(m + 11) % 12]);
      iceRange = nIce === 1 ? ` (roughly ${MON[first]})` : ` (roughly ${MON[first]}–${MON[(first + nIce - 1) % 12]})`;
    } else if (nIce === 12) iceRange = " (all year in this extrapolation)";
    const verdict = !Y.freezes ? `Probably <b>never freezes</b>` :
      `Probably <b>freezes</b> for about <b>${Math.round(365 - Y.openDays)} days</b> a year` + iceRange;
    const truth = L.ice == null ? "" : `<span class="small">Measured: ${L.ice === 0 ? "never freezes" : "ice for about " + L.ice + " days a year"}.</span>`;
    h += `<p class="label">Through the year <span class="tagx">extrapolation</span></p>
      <div class="verdict">${verdict}. ${truth}</div>
      ${(L.depth >= 50 || L.area >= 500) ? `<div class="note">Big or deep lakes store summer heat into the winter, so they stay warmer in winter and freeze less than these equations expect. Treat the ice prediction for this lake as a rough upper bound.</div>` : ""}
      <div class="figure">${yearChart(Y, L)}</div>
      <div class="legend"><span><svg viewBox="0 0 10 10"><line x1="0" y1="5" x2="10" y2="5" class="ln bold"/></svg>predicted</span>
      ${L.months ? `<span><svg viewBox="0 0 10 10"><circle cx="5" cy="5" r="4" class="fill-ink"/></svg>measured</span><span><svg viewBox="0 0 10 10"><circle cx="5" cy="5" r="4" class="m-ec"/></svg>measured 0 °C = frozen</span>` : ""}
      ${Y.freezes ? `<span><svg viewBox="0 0 10 10"><rect width="10" height="10" fill="url(#ice-hatch)" stroke="var(--ink)" stroke-width="0.6"/></svg>ice likely</span>` : ""}</div>
      <div class="tablewrap"><table class="months"><thead><tr><th></th>${MON.map((m) => `<th class="num">${m}</th>`).join("")}</tr></thead><tbody>
      <tr><td class="em">Predicted</td>${Y.temps.map((t, m) => `<td class="num">${Y.ice[m] ? "ice" : fmt(t)}</td>`).join("")}</tr>
      ${L.months ? `<tr><td class="em">Measured</td>${L.months.map((t) => `<td class="num">${t > 0 ? fmt(t) : "0 / ice"}</td>`).join("")}</tr>` : ""}</tbody></table></div>
      <p class="small">${Y.method === "wave" ? `Lakes that never freeze follow one smooth wave: average ${fmt(Y.Tbar)} °C, swing ±${Y.a.toFixed(1)} °C, warmest around ${MON[Math.round(Y.p - 1) % 12]}. The wave is pulled toward the Model 4 July value (${fmt(R.preds[3])} °C), most in June–August and least in winter. Typical error on unseen lakes: about ${DATA.season.stats.blend_mae.toFixed(1)} °C a month.` :
        `At least one month comes out below 1 °C, so the lake is treated as one that freezes. Its months come from a separate equation for each month, fitted to all 1.1 million lakes with frozen months counted as 0 °C (typical error about ${DATA.season.stats.monthly_mae_freezing.toFixed(1)} °C in ice-free months); the length of the ice season, and so how many of the coldest months are marked as ice, comes from the ice-free-days equation (typical error about ${Math.round(DATA.season.stats.open_typical)} days).`}
      Whether a lake freezes is decided by those monthly equations: on lakes not used to fit them, they spot 99% of lakes that freeze and 88% of lakes that never do. Months are this lake's own calendar months.</p>`;

    // how it was worked out
    h += `<p class="label">How each July number was worked out</p><p class="small">${esc(R.v.half)} · continent: ${esc(R.v.cont)} · h = ${R.v.h.toFixed(3)} · C = ${R.v.C.toFixed(3)} · D = ${R.v.D.toFixed(3)} · A = ${R.v.A.toFixed(3)}</p>`;
    R.steps.forEach((rows, k) => {
      h += `<details${k === 0 ? " open" : ""}><summary>${NAMES[k]} · ${SUB[k]}<span>${fmt(R.preds[k])} °C</span></summary><table class="steps">`;
      rows.forEach((r) => (h += `<tr><td>${esc(r[0])}</td><td class="f">${esc(r[1])}</td><td class="num">${r[0].startsWith("+") ? sgn(r[2]) : r[2].toFixed(2)}</td></tr>`));
      h += `<tr class="tot"><td>Prediction</td><td></td><td class="num">${fmt(R.preds[k], 2)} °C</td></tr></table></details>`;
    });
    $("result").innerHTML = h;
    $("result").hidden = false;
  }

  /* ---------- your own lake ---------- */
  const tabs = document.querySelectorAll(".tab");
  tabs.forEach((t) => t.addEventListener("click", () => {
    tabs.forEach((u) => u.setAttribute("aria-selected", String(u === t)));
    $("pane-find").hidden = t.dataset.pane !== "find"; $("pane-own").hidden = t.dataset.pane !== "own";
  }));
  const num = (id) => parseFloat($(id).value);
  let coastEdited = false;
  $("f-coast").addEventListener("input", () => (coastEdited = true));
  const autoCoast = () => { if (coastEdited) return; const la = num("f-lat"), lo = num("f-lon"); if (isFinite(la) && isFinite(lo) && la >= 0 && la <= 70) $("f-coast").value = Math.round(coastAt(la, lo)); };
  $("f-lat").addEventListener("input", autoCoast); $("f-lon").addEventListener("input", autoCoast);
  $("own-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const L = { lat: num("f-lat"), lon: num("f-lon"), elev: num("f-elev"), coast: num("f-coast"), depth: num("f-depth"), area: num("f-area"), actual: null, months: null, ice: null };
    if (![L.lat, L.lon, L.elev, L.coast, L.depth, L.area].every(isFinite)) { $("own-msg").textContent = "Fill in every box."; return; }
    if (L.lat <= 0 || L.lat > 70) { $("own-msg").textContent = "The July models cover 0–70°N. Enter a latitude in that range."; return; }
    $("own-msg").textContent = "";
    current = null; refresh();
    render(L, "Your lake", fmt(L.lat, 2) + "°N, " + fmt(L.lon, 2) + "°E");
  });

  /* start: a well-known lake */
  window.__lake = { july, year, coastAt, lakes };
  refresh();
  const start = lakes.find((l) => l.name === "Red Deer");
  if (start) pick(start);
})();
