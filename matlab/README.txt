LAKE TEMPERATURE: HEIGHT OR LATITUDE?  -  MATLAB version of every graph

WHAT YOU NEED
  MATLAB R2019b or newer. No toolboxes.
  laketemp_clean.csv.gz  (the 50 MB file laketemp_filter.py made)

STEPS
  1. Unzip this folder somewhere, e.g. Documents/lake-matlab
  2. Copy laketemp_clean.csv.gz into that folder
  3. Open MATLAB. In the Current Folder panel (left), go into lake-matlab
  4. Type   step0_load_data   and press Enter   (once only, ~1 minute, makes lakes.mat)
  5. Type   run_all           and press Enter   (makes all 11 figures, a few minutes)
     or run one at a time, e.g.   fig05_zone_coefficients
  6. The PNGs appear in the "figures" folder. The numbers print in the Command Window.

FILES, IN ORDER (figure number = figure on the website)
  step0_load_data.m          read the csv, filter, save lakes.mat
  fig01_world_map.m          Figure I    every lake coloured by July temperature
  fig02_zone_widths.m        Figure II   2.5 / 5 / 10 degree zones compared
  fig03_lat_alt_grid.m       Figure III  latitude x elevation grid with isotherms
  fig04_variance_shares.m    Figure IV   R squared: latitude vs altitude
  fig05_zone_coefficients.m  Figure V    the 5 degree zone equation (prints Table I)
  fig06_sliding_band.m       Figure VI   sliding 2 degree band + 33 N breakpoint
  fig07_robustness.m         Figure VII  July vs yearly open-water lapse rate
  fig08_alps_scatter.m       Figure VIII Alps band: temperature vs height by region
  fig09_alps_region_slopes.m Figure IX   Alps band lapse rates with 95% CIs
  fig10_alps_residual_map.m  Figure X    warmer / colder than predicted map
  fig11_alps_vs_canada.m     Figure XI   2x2: Alps latitude vs southern Canada
  run_all.m                  runs all of the above in order

HELPER FUNCTIONS (the figure scripts call these; don't run them on their own)
  ols_cl.m        least squares + standard errors clustered by 1x1 degree cell
  zone_fit.m      fits the zone equation in uniform zones of any width
  slide_fit.m     fits the altitude slope in a sliding 2 degree band
  broken_stick.m  two straight lines joined at a breakpoint
  dummies.m       0/1 columns for the six longitude regions
  pct.m           percentile without the Statistics Toolbox
  lake_style.m    colours (Alps = orange, Canada = blue) and fonts
  draw_land.m     grey land from coast.csv
  save_fig.m      saves the current figure to figures/<name>.png
  coast.csv       coastline outlines for the maps

COLOURS ARE THE SAME IN EVERY FIGURE
  orange = Alps band (45.8-47.8 N), blue = southern Canada band (50-53 N),
  black = data and fitted lines, grey = error bars and second lines.

NOTE
  The breakpoint range in Figure VI comes from 500 random resamples, so its
  edges can differ by half a degree from the website (31.5-34.5 vs 31.5-35.0).
  Every other number matches the website exactly.

ADDED LATER (figure numbers now match the report)
  step0_load_south.m            reads the southern lakes (January) -> south.mat
  step0_load_year.m             reads all 12 months + ice days, both hemispheres -> year.mat
  step1_heldout_models.m        fits Models 1-4 and tests them on unseen lakes -> heldout.mat
  step2_yearly_fit.m            yearly wave + its equations, prints them -> yearfit.mat
  fig04_variance_shares.m       Figure 4   now shows both hemispheres
  fig13_predicted_vs_actual.m   Figure 13  predicted vs actual, four models
  fig15_error_by_latitude.m     Figure 15  typical error by latitude
  fig16_big_lakes.m             Figure 16  lakes of 500 km2 or more (was fig14_big_lakes)
  fig17_hemispheres.m           Figure 17  north July vs south January (was fig13_hemispheres)
  fig18_yearly_cycle.m          Figure 18  yearly cycle of lakes that never freeze
  fig19_timing_ice_prediction.m Figure 19  warmest point, ice-free season, whole-year prediction
  helpers: model_split.m, model_zones.m, model_nearby.m, cv_ols.m, best_break.m,
           binned.m, r2_shares.m, commas.m
