"""
Terrain proxy: point elevation (metres) via Open-Elevation (SRTM-derived),
at each project's representative point, plus for line-type projects the
elevation difference between endpoints as a crude ruggedness proxy.
"""
import time

import pandas as pd
import requests

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes/05_covariates"
PROJECTS = f"{BASE}/project_level_with_covariates.csv"

df = pd.read_csv(PROJECTS)


def batch_elevation(coords):
    """coords: list of (lat, lon). Returns list of elevations (None on failure)."""
    if not coords:
        return []
    loc_str = "|".join(f"{lat},{lon}" for lat, lon in coords)
    try:
        r = requests.get(
            "https://api.open-elevation.com/api/v1/lookup",
            params={"locations": loc_str}, timeout=30,
        )
        r.raise_for_status()
        results = r.json()["results"]
        return [res.get("elevation") for res in results]
    except Exception as e:
        print(f"  batch failed ({e}), falling back to per-point")
        out = []
        for lat, lon in coords:
            try:
                rr = requests.get(
                    "https://api.open-elevation.com/api/v1/lookup",
                    params={"locations": f"{lat},{lon}"}, timeout=15,
                )
                out.append(rr.json()["results"][0].get("elevation"))
            except Exception:
                out.append(None)
            time.sleep(0.3)
        return out


# representative point elevation
repr_coords = list(zip(df["repr_lat"], df["repr_lon"]))
valid_idx = [i for i, (la, lo) in enumerate(repr_coords) if pd.notna(la) and pd.notna(lo)]
elevations = [None] * len(df)
BATCH = 40
for start in range(0, len(valid_idx), BATCH):
    chunk_idx = valid_idx[start:start + BATCH]
    coords = [repr_coords[i] for i in chunk_idx]
    elevs = batch_elevation(coords)
    for i, e in zip(chunk_idx, elevs):
        elevations[i] = e
    print(f"elevation batch {start}-{start+len(chunk_idx)} done")
    time.sleep(1)

df["elevation_m"] = elevations

# line endpoint elevation difference (ruggedness proxy) for road/power_line projects
has_line = df["lat1"].notna() & df["lon1"].notna() & df["lat2"].notna() & df["lon2"].notna()
line_idx = df[has_line].index.tolist()
elev1, elev2 = [None] * len(df), [None] * len(df)
for start in range(0, len(line_idx), BATCH):
    chunk = line_idx[start:start + BATCH]
    coords1 = [(df.loc[i, "lat1"], df.loc[i, "lon1"]) for i in chunk]
    coords2 = [(df.loc[i, "lat2"], df.loc[i, "lon2"]) for i in chunk]
    e1 = batch_elevation(coords1)
    time.sleep(1)
    e2 = batch_elevation(coords2)
    for i, v in zip(chunk, e1):
        elev1[i] = v
    for i, v in zip(chunk, e2):
        elev2[i] = v
    print(f"line endpoint elevation batch {start}-{start+len(chunk)} done")
    time.sleep(1)

df["elevation_endpoint1_m"] = elev1
df["elevation_endpoint2_m"] = elev2
df["elevation_diff_m"] = (
    (df["elevation_endpoint1_m"] - df["elevation_endpoint2_m"]).abs()
)

df.to_csv(PROJECTS, index=False)
print(f"\nSaved -> {PROJECTS}")
print(f"\nelevation_m coverage: {df['elevation_m'].notna().sum()} / {len(df)}")
print(df["elevation_m"].describe())
print(f"\nline elevation_diff_m coverage: {df['elevation_diff_m'].notna().sum()}")
