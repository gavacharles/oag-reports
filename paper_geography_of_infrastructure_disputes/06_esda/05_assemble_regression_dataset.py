"""
Assemble the full 135-district cross-sectional regression dataset:
outcome (project/driver counts from the ESDA stage) + environmental
covariates (this stage) + population/access/RAI (district-level, direct
from source, not project-derived) + land tenure proxy (all 135 districts,
not just the 90 with projects).
"""
import pandas as pd

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
OUT = f"{BASE}/06_esda/district_regression_dataset.csv"

counts = pd.read_csv(f"{BASE}/06_esda/district_driver_counts.csv")
env = pd.read_csv(f"{BASE}/06_esda/district_environmental_covariates.csv")

pop = pd.read_csv("/tmp/uga_admpop_adm2.csv")[["ADM2_PCODE", "T_TL"]].rename(
    columns={"ADM2_PCODE": "adm2_pcode", "T_TL": "district_population_2022"}
)
vuln = pd.read_csv("/tmp/uga_vulnerability.csv")[["ADM2_PCODE", "dependency_ratio", "rural_pop_perc"]].rename(
    columns={"ADM2_PCODE": "adm2_pcode"}
)
rai = pd.read_csv("/tmp/uga_rai.csv")[["ADM2_PCODE", "RAI_total_pop"]].rename(
    columns={"ADM2_PCODE": "adm2_pcode", "RAI_total_pop": "rural_access_index_pct"}
)

MAILO_BUGANDA = {
    "Buikwe", "Butambala", "Gomba", "Kalangala", "Kampala", "Kayunga", "Kiboga",
    "Kyankwanzi", "Luwero", "Masaka", "Mityana", "Mpigi", "Mubende", "Mukono",
    "Nakaseke", "Rakai", "Wakiso", "Kyotera", "Buvuma", "Sembabule", "Lwengo",
    "Bukomansimbi", "Kalungu", "Lyantonde", "Nakasongola",
}
FREEHOLD_ANKOLE_KIGEZI = {
    "Mbarara", "Isingiro", "Kiruhura", "Bushenyi", "Kazo", "Mitooma", "Rubirizi",
    "Ntungamo", "Ibanda", "Sheema", "Buhweju", "Kabale", "Kanungu", "Kisoro",
    "Rubanda", "Rukiga", "Rukungiri",
}


def tenure(d):
    if d in MAILO_BUGANDA:
        return "mailo"
    if d in FREEHOLD_ANKOLE_KIGEZI:
        return "freehold"
    return "customary"


df = counts.merge(env, on=["district", "adm2_pcode"], how="left") \
    .merge(pop, on="adm2_pcode", how="left") \
    .merge(vuln, on="adm2_pcode", how="left") \
    .merge(rai, on="adm2_pcode", how="left")
df["land_tenure_proxy"] = df["district"].apply(tenure)
df["log_population"] = df["district_population_2022"].apply(lambda x: __import__("math").log(x) if x > 0 else None)

df.to_csv(OUT, index=False)
print(f"Saved -> {OUT}")
print(f"\n{len(df)} districts, columns: {df.columns.tolist()}")
print(f"\nmissing-value check:\n{df.isna().sum()}")
print(f"\nland_tenure_proxy distribution:\n{df['land_tenure_proxy'].value_counts()}")
