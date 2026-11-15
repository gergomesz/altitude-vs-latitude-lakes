# pulls just the attribute table out of HydroLAKES (no lake outlines) and saves a small csv
# reads one row at a time so it won't run out of memory
#
#   pip install dbfread
#   python hydrolakes_to_csv.py "path/to/HydroLAKES_polys_v10.dbf"
#
# the .dbf is in the same folder as the .shp file (works with the points version too)

import csv
import sys
from pathlib import Path

from dbfread import DBF

MIN_AREA_KM2 = 1.0  # lakes cci only has fairly big lakes, so small ones aren't needed
KEEP = ["Hylak_id", "Lake_name", "Country", "Continent", "Lake_type",
        "Lake_area", "Depth_avg", "Vol_total", "Elevation", "Pour_lat", "Pour_long"]

dbf_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("HydroLAKES_polys_v10.dbf")
out_path = dbf_path.with_name("hydrolakes_big_lakes.csv")

table = DBF(dbf_path, load=False)  # load=False -> streams rows instead of loading everything
cols = [c for c in KEEP if c in table.field_names]
missing = [c for c in KEEP if c not in table.field_names]
if missing:
    print("note: these columns aren't in this file:", missing)

kept = total = 0
with open(out_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(cols)
    for row in table:
        total += 1
        if (row.get("Lake_area") or 0) >= MIN_AREA_KM2:
            w.writerow([row.get(c) for c in cols])
            kept += 1
        if total % 200000 == 0:
            print(f"  read {total:,} lakes...")

print(f"done: kept {kept:,} of {total:,} lakes (area >= {MIN_AREA_KM2} km2)")
print("saved to", out_path)
