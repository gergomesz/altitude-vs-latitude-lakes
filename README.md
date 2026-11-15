# Height or Latitude? What sets the surface temperature of the world's lakes

**NASA Space Apps Challenge 2026 · Earth System Trend Detective**

Going north and going uphill both make a lake colder, but by how much each? This project uses Landsat 8 surface temperatures for about a million lakes (LakeTEMP, 2013–2021) to measure how latitude, height and the ocean set lake temperature. It turns the results into equations that predict any lake's July temperature, every month of its year, and whether it freezes.


## What's on the site

- **Lake calculator**
  - Pick a country to see its lakes on a map and in a list, or search by name. The list holds 3,590 lakes in 137 countries: every named lake, plus the 25 largest unnamed lakes in each country.
  - You can also enter your own lake. Distance to the sea fills in automatically from the latitude and longitude.
  - For each lake it shows:
    - the four July models, with every step of the arithmetic;
    - a month-by-month prediction for the whole year;
    - whether the lake is likely to freeze, and for how long.
  - Lakes from the list also show what Landsat measured, so you can see how close the predictions are.
- **Every result**, as plates with figures (light and dark versions). Each figure has a short "how to read it / what it shows" note.
- **The full report, spreadsheet, MATLAB code and Python code** to check or rebuild everything.

## Main findings

| | |
|---|---|
| Where latitude starts to cool July lakes | **33°N**; flat from the equator up to there |
| Lake-to-lake variation explained, latitude vs height | **41% vs 3%** in the north; **28% vs 16%** in the south |
| Height equal to one degree of latitude (north of 33°N) | about **80–130 m** |
| Inland vs coastal lakes (north of 33°N) | up to **5 °C** warmer inland |
| Best July model on lakes it never saw | R² **0.91**, typical error **0.8 °C** |
| Big lakes (≥ 500 km²) | about 5 °C colder than the simple model; the size adjustment halves the error |
| Whole year, lakes that never freeze | one yearly wave; geography predicts every month with R² **0.93** |
| Southern Hemisphere | same cooling with height; break earlier (27.5°S); weaker coast effect |

The [full report](downloads/Lake_Temperature_Report.pdf) has all 25 findings with their equations.

## Put it online with GitHub Pages

1. Create a new **public** repository on GitHub.
2. Upload everything in this folder, keeping the folders as they are. On the repository page, choose **Add file → Upload files** and drag the contents in.
3. Go to **Settings → Pages**.
   - Source: **Deploy from a branch**.
   - Branch: **main**, folder **/ (root)**.
   - Click **Save**.
4. After a minute the site is live at the address shown on that page.

To try it on your own computer, just open `index.html`.

## Folders

```
index.html            the website
assets/               style.css, app.js (dark mode, "?" boxes), calc.js (calculator), data.js (lakes and every model)
figures/light, dark   figures in both colour themes
figures/report        figures from the report
downloads/            report (PDF), spreadsheet (Excel), LaTeX source, CSV tables
matlab/               MATLAB code: one script per figure, plus loading and model-testing steps (see matlab/README.txt)
python/               the Python analysis behind every number, figure and this site
.nojekyll             tells GitHub Pages to serve the files as they are
```

## How the calculator works

- **July (Models 1–4).** Straight-line equations in latitude, height, distance to the sea, depth, area and continent, split at 33°N.
  - Models 2 and 4 add a nearby-lakes correction: the average miss of known lakes in the surrounding 3 × 3 block of 1° squares, scaled by n / (n + 20).
  - Every model was tested on lakes it was not fitted to (5-fold cross-validation by 1° square).
- **Freezing.** One equation per month, fitted to all 1.1 million lakes with frozen months counted as 0 °C.
  - If any month comes out below 1 °C, the lake is treated as one that freezes.
  - This spots 99% of lakes that freeze and 88% of lakes that never do.
  - The length of the ice season comes from the ice-free-days equation (typical error about 15 days).
- **Every month.**
  - Lakes that never freeze: a yearly wave whose average, size and timing come from three equations. It is pulled toward the Model 4 July value. Typical error about 1.4 °C a month.
  - Lakes that freeze: their ice-free months come from the monthly equations. Typical error about 2.0 °C.
  - The year and ice predictions extend equations beyond the lakes they were built on, so treat them as approximate. Big, deep lakes hold summer heat and freeze less than predicted.

## Rebuilding

- **Python** (`python/`):
  - The scripts read `laketemp_clean.parquet`, made from the LakeTEMP CSV by `laketemp_filter.py`.
  - `models.py` and `bigadj.py` build the July models.
  - `seas_prep.py`, `seas_fit.py`, `seas_extra.py` and `monthly_model.py` build the yearly and ice models.
  - `build_site_data.py` and `build_site.py` write this website.
- **MATLAB** (`matlab/`): see `matlab/README.txt`. `run_all` makes every figure in the same order as the report.

## Data

- **LakeTEMP:** Korver, M. C. et al. (2024), *Remote Sensing of Environment*. Monthly Landsat 8 lake surface temperatures, 2013–2021.
- **HydroLAKES:** Messager, M. L. et al. (2016), *Nature Communications*. Lake outlines, names, depth and area.
- **Natural Earth:** 1:50m coastline and country borders.

## Limits

- **What Landsat measures:** the top fraction of a millimetre of water, in the late morning, on clear days.
- **Time span:** 2013–2021 is a snapshot, not a trend.
- **Where the lakes are:** most are in Canada and Scandinavia, so hemisphere-wide numbers lean toward them.
- **Where the models are weakest:** they predict typical lakes well, but the largest and deepest lakes worst.
