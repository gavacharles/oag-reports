"""
Rainfall covariate from CHIRPS v2.0 (Climate Hazards Group InfraRed
Precipitation with Station data), Africa monthly product, UCSB CHC.

Computed as: mean annual total rainfall (mm) at each project's
representative point, averaged over a 5-year climatological baseline
(2018-2022, centred on the study period) rather than a separate figure
per study year. This is a deliberate simplification -- rainfall is used
here as a static geographic covariate (like terrain/distance-to-Kampala),
not as a hypothesised time-varying driver of year-to-year dispute
fluctuation. If a reviewer wants year-specific rainfall (e.g. an
anomalous flood year), that would need per-year extraction from the same
source and is a straightforward extension of this script.
"""
import gzip
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
import requests

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes/05_covariates"
PROJECTS = f"{BASE}/project_level_with_covariates.csv"
CACHE_DIR = Path(f"{BASE}/chirps_cache")
CACHE_DIR.mkdir(exist_ok=True)

YEARS = [2018, 2019, 2020, 2021, 2022]
MONTHS = range(1, 13)
BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/africa_monthly/tifs"


def fetch_and_unzip(year, month):
    fname = f"chirps-v2.0.{year}.{month:02d}.tif"
    gz_path = CACHE_DIR / f"{fname}.gz"
    tif_path = CACHE_DIR / fname
    if tif_path.exists():
        return tif_path
    url = f"{BASE_URL}/{fname}.gz"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    gz_path.write_bytes(r.content)
    with gzip.open(gz_path, "rb") as f_in, open(tif_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    gz_path.unlink()
    return tif_path


df = pd.read_csv(PROJECTS)
points = list(zip(df["repr_lon"], df["repr_lat"]))  # rasterio wants (x, y) = (lon, lat)
valid_mask = df["repr_lat"].notna() & df["repr_lon"].notna()
valid_points = [(lo, la) for lo, la, ok in zip(df["repr_lon"], df["repr_lat"], valid_mask) if ok]
valid_idx = df.index[valid_mask].tolist()

monthly_values = {i: [] for i in valid_idx}  # will hold list of (year_total_so_far)

for year in YEARS:
    year_sum = {i: 0.0 for i in valid_idx}
    for month in MONTHS:
        tif_path = fetch_and_unzip(year, month)
        with rasterio.open(tif_path) as src:
            nodata = src.nodata
            samples = list(src.sample(valid_points))
        for i, val in zip(valid_idx, samples):
            v = float(val[0])
            if nodata is not None and v == nodata:
                v = 0.0
            if v < 0:
                v = 0.0
            year_sum[i] += v
    for i in valid_idx:
        monthly_values[i].append(year_sum[i])
    print(f"year {year} done")

mean_annual_rainfall = {i: round(float(np.mean(monthly_values[i])), 1) for i in valid_idx}

df["mean_annual_rainfall_mm"] = df.index.map(lambda i: mean_annual_rainfall.get(i))
df.to_csv(PROJECTS, index=False)

print(f"\nSaved -> {PROJECTS}")
print(f"coverage: {df['mean_annual_rainfall_mm'].notna().sum()} / {len(df)}")
print(df["mean_annual_rainfall_mm"].describe())

# clean up cache (keep raw tifs is ~60MB*5 = large; remove after extraction)
shutil.rmtree(CACHE_DIR, ignore_errors=True)
print("cleaned up raster cache")
