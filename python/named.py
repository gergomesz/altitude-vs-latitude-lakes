import json, numpy as np, pandas as pd
df = pd.read_parquet("laketemp_clean.parquet")
d = df[(df.center_lat > 0) & (df.center_lat <= 70) & (df.Tmonth_mean_7 > 0) & (df.Tmonth_mean_7 < 40)].reset_index(drop=True)
d["coast_km"] = pd.read_parquet("coast_km.parquet").coast_km.values
J = json.load(open("models.json")); CM = pd.read_csv("correction_map.csv").set_index("key"); ZT = pd.read_csv("zone_continent_equations.csv").set_index("key")
CONT = J["continents"]
names = ["Superior", "Great Bear", "Geneva", "Constance", "Neuchatel", "Luzern", "Garda", "Balaton", "Ohrid", "Ladoga", "Vattern", "Inari", "Michigan", "Huron", "Erie",
         "Champlain", "Winnipegosis", "Manitoba", "Great Slave", "Great Salt", "Yellowstone Lake", "Crater Lake", "Chapala",
         "Sevan", "Van", "Issyk Kul", "Qinghai", "Khanka", "Dongting", "Tonle Sap", "Tana", "Turkana"]
rows = []
for n in names:
    m = d[d.Lake_name == n]
    if not len(m): print("missing", n); continue
    r = m.sort_values("Lake_area", ascending=False).iloc[0]
    rows.append(dict(lake=n.replace("Neuchatel", "Neuchâtel").replace("Luzern", "Lucerne").replace("Vattern", "Vättern"), country=r.Country,
                     lat=round(r.center_lat, 3), lon=round(r.center_long, 3), elev_m=float(r.Elevation), coast_km=round(float(r.coast_km), 1),
                     depth_m=round(float(r.Depth_avg), 1), area_km2=round(float(r.Lake_area), 1), actual=round(float(r.Tmonth_mean_7), 2)))
N = pd.DataFrame(rows)
def pred(r):
    lat, h = r.lat, r.elev_m / 1000; hp = max(h - 1.5, 0); C = np.log10(r.coast_km + 10)
    D = np.log10(max(r.depth_m, 0.3)) - np.log10(3.3); A = np.log10(max(r.area_km2, 0.01)) - np.log10(0.23)
    c = int(np.digitize(r.lon, [-100, -60, -15, 40, 100])); s = "1" if lat > 33 else "0"
    b3 = J["M3"][s]; m3 = b3["const"] + b3["lat"] * lat + b3["h"] * h + b3["C"] * C + (0 if c == 0 else b3[f"K_{CONT[c]}"])
    key = f"{int(np.floor(lat))}|{int(np.floor(r.lon))}"
    corr = CM.loc[key] if key in CM.index else None
    def adj(k):
        if r.area_km2 < 500: return 0.0
        a = J["big_adj"][k]
        return a["const"] + a["logarea"] * (np.log10(r.area_km2) - np.log10(500)) + a["logdepth"] * D + a["lat50"] * (lat - 50)
    m4 = m3 + (corr.corr_M4 if corr is not None else 0) + adj("M4")
    m3 = m3 + adj("M3")
    b7 = J["M7"][s]; K = 0 if c == 0 else b7[f"K_{CONT[c]}"]
    m7 = b7["const"] + b7["lat"] * lat + b7["h"] * h + b7["h_plus"] * hp + b7["C"] * C + b7["D"] * D + b7["A"] * A + K
    z = int(np.floor((lat - 1e-9) / 5)) * 5; t = ZT.loc[f"{z}|{c}"]
    ma = t.a + t.per_deg * (lat - (z + 2.5)) + t.per_km * h + t.extra_per_km_above_1500 * hp + t.coast * C + t.depth * D + t.area * A + t.coast_x_km * C * h
    ma += corr.corr_all if corr is not None else 0
    return pd.Series(dict(continent=CONT[c], M1=m3, M2=m4, M3=m7, M4=ma))
N = pd.concat([N, N.apply(pred, axis=1)], axis=1)
N.to_csv("named_lakes.csv", index=False)
pd.set_option("display.width", 220); print(N[["lake", "country", "actual", "M1", "M2", "M3", "M4"]].round(1).to_string())
for k in ["M1", "M2", "M3", "M4"]: print(k, "median abs err", round(np.median(abs(N.actual - N[k])), 2))
