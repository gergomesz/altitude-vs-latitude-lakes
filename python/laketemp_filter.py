# cuts LakeTEMP_aggregated_v1.csv down to good-quality natural lakes and the columns we need
# streams one row at a time, so it won't run out of memory
#
#   python laketemp_filter.py "path/to/LakeTEMP_aggregated_v1.csv"
#   python laketemp_filter.py "path/to/LakeTEMP_aggregated_v1.csv" 1   <- optional: only lakes >= 1 km2 (smaller file)
#
# quality rules are the ones the LakeTEMP tech doc recommends:
#   stat_method == 0 (trendline), intermittency == 0, n_obs >= 46
# plus: natural lakes only (Lake_type == 1)

import csv
import gzip
import sys
from pathlib import Path

src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("LakeTEMP_aggregated_v1.csv")
MIN_AREA = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
out = src.with_name("laketemp_clean.csv.gz")

BASE = ["Hylak_id", "center_lat", "center_long", "Lake_name", "Country", "Continent",
        "Lake_type", "Lake_area", "Depth_avg", "Elevation", "n_obs",
        "Tyear_mean", "Tyear_mean_open", "Tyear_min", "Tyear_max", "ice_days"]
TEMP_X100 = {"Tyear_mean", "Tyear_mean_open", "Tyear_min", "Tyear_max"}  # stored as degC * 100


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


with open(src, newline="", encoding="utf-8", errors="replace") as f_in, \
        gzip.open(out, "wt", newline="", encoding="utf-8") as f_out:
    reader = csv.DictReader(f_in)
    months = [c for c in reader.fieldnames if c.startswith("Tmonth_mean_")]  # all 12 monthly means
    cols = [c for c in BASE if c in reader.fieldnames] + months
    missing = [c for c in BASE if c not in reader.fieldnames]
    if missing:
        print("note: not in file:", missing)
    temp_cols = TEMP_X100 | set(months)

    w = csv.writer(f_out)
    w.writerow(cols)
    total = kept = 0
    for row in reader:
        total += 1
        if total % 200000 == 0:
            print(f"  read {total:,} lakes, kept {kept:,}...")
        if num(row.get("stat_method")) != 0:
            continue
        if num(row.get("intermittency")) != 0:
            continue
        if (num(row.get("n_obs")) or 0) < 46:
            continue
        if num(row.get("Lake_type")) != 1:
            continue
        if (num(row.get("Lake_area")) or 0) < MIN_AREA:
            continue
        vals = []
        for c in cols:
            v = row.get(c)
            if c in temp_cols:
                v = num(v)
                v = "" if v is None else round(v / 100, 2)
            vals.append(v)
        w.writerow(vals)
        kept += 1

print(f"done: kept {kept:,} of {total:,} lakes")
print("saved to", out)
