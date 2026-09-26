"""
District-centroid environmental covariates (elevation, rainfall, distance
to Kampala) for ALL 135 districts, not just the 90 with observed
projects -- the regression stage needs a value for zero-count districts
too, not just where projects happen to have been audited.
"""
import gzip
import math
import shutil
import time
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import requests

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
DISTRICTS = f"{BASE}/05_covariates/boundaries/uga_admin2.geojson"
OUT = f"{BASE}/06_esda/district_environmental_covariates.csv"
KAMPALA_LAT, KAMPALA_LON = 0.3136, 32.5811


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(min(1, a ** 0.5))


districts = gpd.read_file(DISTRICTS)[["adm2_name", "adm2_pcode", "geometry"]].rename(columns={"adm2_name": "district"})
districts["centroid"] = districts.geometry.centroid
districts["cen_lat"] = districts["centroid"].y
districts["cen_lon"] = districts["centroid"].x
districts["distance_to_kampala_km"] = districts.apply(
    lambda r: round(haversine_km(r["cen_lat"], r["cen_lon"], KAMPALA_LAT, KAMPALA_LON), 1), axis=1
)

# elevation
coords = list(zip(districts["cen_lat"], districts["cen_lon"]))
elevations = []
BATCH = 40
for start in range(0, len(coords), BATCH):
    chunk = coords[start:start + BATCH]
    loc_str = "|".join(f"{la},{lo}" for la, lo in chunk)
    r = requests.get("https://api.open-elevation.com/api/v1/lookup", params={"locations": loc_str}, timeout=30)
    elevations.extend([res.get("elevation") for res in r.json()["results"]])
    print(f"elevation {start}-{start+len(chunk)} done")
    time.sleep(1)
districts["elevation_m"] = elevations

# rainfall: reuse the same CHIRPS 2018-2022 monthly climatology approach
CACHE_DIR = Path(f"{BASE}/06_esda/chirps_cache_district")
CACHE_DIR.mkdir(exist_ok=True)
YEARS = [2018, 2019, 2020, 2021, 2022]
BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/africa_monthly/tifs"


def fetch_and_unzip(year, month):
    fname = f"chirps-v2.0.{year}.{month:02d}.tif"
    tif_path = CACHE_DIR / fname
    if tif_path.exists():
        return tif_path
    gz_path = CACHE_DIR / f"{fname}.gz"
    url = f"{BASE_URL}/{fname}.gz"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    gz_path.write_bytes(r.content)
    with gzip.open(gz_path, "rb") as f_in, open(tif_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    gz_path.unlink()
    return tif_path


points = list(zip(districts["cen_lon"], districts["cen_lat"]))
year_sums = {i: [] for i in range(len(districts))}
for year in YEARS:
    totals = {i: 0.0 for i in range(len(districts))}
    for month in range(1, 13):
        tif_path = fetch_and_unzip(year, month)
        with rasterio.open(tif_path) as src:
            nodata = src.nodata
            samples = list(src.sample(points))
        for i, val in enumerate(samples):
            v = float(val[0])
            if nodata is not None and v == nodata:
                v = 0.0
            totals[i] += max(v, 0.0)
    for i in range(len(districts)):
        year_sums[i].append(totals[i])
    print(f"rainfall year {year} done")

districts["mean_annual_rainfall_mm"] = [round(float(np.mean(year_sums[i])), 1) for i in range(len(districts))]
shutil.rmtree(CACHE_DIR, ignore_errors=True)

out = districts.drop(columns=["geometry", "centroid"])
out.to_csv(OUT, index=False)
print(f"\nSaved -> {OUT}")
print(out[["district", "distance_to_kampala_km", "elevation_m", "mean_annual_rainfall_mm"]].describe())
