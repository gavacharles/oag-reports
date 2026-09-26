"""
District assignment (spatial join against current OCHA COD-AB district
boundaries, valid as of 2020-08-24, 135 districts), distance-to-Kampala,
and election-year encoding for the geocoded project dataset.
"""
import json

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
GEOC = f"{BASE}/04_project_extraction_geocoding/project_level_geocoded.csv"
DISTRICTS = f"{BASE}/05_covariates/boundaries/uga_admin2.geojson"
OUT = f"{BASE}/05_covariates/project_level_with_covariates.csv"

KAMPALA_LAT, KAMPALA_LON = 0.3136, 32.5811  # Kampala city centre (Nakasero)

# Uganda general elections within/adjacent to the study period (2017-2025).
# Only Jan 2021 falls inside the window; 2025 is the immediate pre-election
# run-up to the Jan 2026 poll, which the political-interference literature
# treats as its own regime (patronage/campaign spending surge).
ELECTION_YEARS = {2021}
PRE_ELECTION_YEARS = {2020, 2025}  # year immediately before a Jan poll


def haversine_km(lat1, lon1, lat2, lon2):
    import math
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(min(1, a ** 0.5))


districts = gpd.read_file(DISTRICTS)[["adm2_name", "adm1_name", "adm2_pcode", "geometry"]]
districts = districts.rename(columns={"adm2_name": "district_geocoded", "adm1_name": "region"})
print(f"loaded {len(districts)} district polygons (OCHA COD-AB, valid_on 2020-08-24)")

df = pd.read_csv(GEOC)
df = df.rename(columns={"district": "district_reading_extracted"})
print(f"loaded {len(df)} projects")


def project_geometry_and_repr_point(row):
    """Return (geometry_for_join, repr_lat, repr_lon). Lines use their
    midpoint for district assignment/distance; points use themselves."""
    if pd.notna(row.get("lat")) and pd.notna(row.get("lon")):
        return Point(row["lon"], row["lat"]), row["lat"], row["lon"]
    if all(pd.notna(row.get(c)) for c in ["lat1", "lon1", "lat2", "lon2"]):
        line = LineString([(row["lon1"], row["lat1"]), (row["lon2"], row["lat2"])])
        mid = line.interpolate(0.5, normalized=True)
        return line, mid.y, mid.x
    if pd.notna(row.get("lat1")) and pd.notna(row.get("lon1")):
        return Point(row["lon1"], row["lat1"]), row["lat1"], row["lon1"]
    return None, None, None


geoms, repr_lats, repr_lons = [], [], []
for _, r in df.iterrows():
    g, la, lo = project_geometry_and_repr_point(r)
    geoms.append(g)
    repr_lats.append(la)
    repr_lons.append(lo)

df["repr_lat"] = repr_lats
df["repr_lon"] = repr_lons
gdf = gpd.GeoDataFrame(df, geometry=[Point(lo, la) if pd.notna(la) else None for la, lo in zip(repr_lats, repr_lons)], crs="EPSG:4326")

has_geom = gdf.geometry.notna()
print(f"{has_geom.sum()} / {len(gdf)} projects have a representative point for spatial join")

joined = gpd.sjoin(gdf[has_geom], districts, how="left", predicate="within")
joined = joined.drop(columns=["index_right"])

# a few points may fall just outside polygon edges (coastline/lake simplification);
# fall back to nearest district centroid for those.
missing = joined["district_geocoded"].isna()
if missing.sum() > 0:
    print(f"{missing.sum()} points fell outside all polygons (edge/simplification gaps) -- assigning nearest district")
    districts_proj = districts.copy()
    districts_proj["centroid"] = districts_proj.geometry.centroid
    for idx in joined[missing].index:
        pt = joined.loc[idx, "geometry"]
        dists = districts_proj["centroid"].distance(pt)
        nearest = districts_proj.loc[dists.idxmin()]
        joined.loc[idx, "district_geocoded"] = nearest["district_geocoded"]
        joined.loc[idx, "region"] = nearest["region"]
        joined.loc[idx, "adm2_pcode"] = nearest["adm2_pcode"]

joined["distance_to_kampala_km"] = joined.apply(
    lambda r: round(haversine_km(r["repr_lat"], r["repr_lon"], KAMPALA_LAT, KAMPALA_LON), 1), axis=1
)

result = pd.merge(
    df, joined[["district_geocoded", "region", "adm2_pcode", "distance_to_kampala_km"]],
    left_index=True, right_index=True, how="left"
)
result["district_agrees"] = (
    result["district_reading_extracted"].fillna("").str.strip().str.lower()
    == result["district_geocoded"].fillna("").str.strip().str.lower()
)

# Prefer the reading-extracted district where available: it came from
# contextual reading of the audit finding (same careful process that caught
# the Isimba/Kabaale geocoding errors), whereas district_geocoded is
# vulnerable to Nominatim matching a same-named village in the wrong
# district (verified cases: "Luwero Fruit Factory" -> geocoded Bugiri,
# clearly wrong; Luwero is nowhere near Bugiri). Fall back to the geocoded
# district only when no reading-extracted value exists.
result["district_final"] = result["district_reading_extracted"].where(
    result["district_reading_extracted"].notna() & (result["district_reading_extracted"].str.strip() != ""),
    result["district_geocoded"],
)

result["is_election_year"] = result["years_mentioned"].astype(str).apply(
    lambda ys: any(str(y) in ys for y in ELECTION_YEARS)
)
result["is_pre_election_year"] = result["years_mentioned"].astype(str).apply(
    lambda ys: any(str(y) in ys for y in PRE_ELECTION_YEARS)
)

result.to_csv(OUT, index=False)
print(f"\nSaved -> {OUT}")
print(f"\nDistrict coverage: {result['district_geocoded'].notna().sum()} / {len(result)}")
print(f"Reading-extracted vs geocoded district agreement: {result['district_agrees'].sum()} / {result['district_geocoded'].notna().sum()}")
print("\nProjects by region:")
print(result["region"].value_counts())
print("\nDistance to Kampala (km) summary:")
print(result["distance_to_kampala_km"].describe())
print("\nTop 15 districts by project count (district_final):")
print(result["district_final"].value_counts().head(15))
print(f"\ndistrict_final coverage: {result['district_final'].notna().sum()} / {len(result)}")
print("\n=== rows where reading-extracted and geocoded district disagree (worth a look) ===")
disagree = result[(~result["district_agrees"]) & result["district_geocoded"].notna() & result["district_reading_extracted"].notna()]
print(disagree[["project_name","district_reading_extracted","district_geocoded","geocode_precision"]].to_string())
