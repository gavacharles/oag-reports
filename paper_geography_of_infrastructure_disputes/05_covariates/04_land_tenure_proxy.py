"""
Land tenure type: a documented sub-region-based categorical proxy, NOT a
GIS layer -- no district- or parcel-level land tenure dataset is publicly
available for Uganda (checked HDX and web search this session; none
exists in machine-readable form). Uganda's 1995 Constitution (Art. 237)
and Land Act 1998 recognise four tenure types: mailo, freehold, leasehold
and customary. Their geographic concentration is well documented in the
land-law literature:
  - Mailo: historic Buganda Kingdom districts (Central sub-region of
    Buganda), created by the 1900 Buganda Agreement -- roughly 9% of
    national land area but concentrated almost entirely here.
  - Native freehold: the Ankole and Kigezi sub-regions (southwest).
  - Customary: dominant nationally (~80% of land), and the default
    classification for all other sub-regions (Busoga, Bukedi, Bugisu/
    Elgon, Teso, Karamoja, Lango, Acholi, West Nile, Bunyoro, Tooro).
Leasehold is a statutory overlay (conversion from the other three, common
on urban/institutional land) rather than a distinct sub-region and is not
separately coded here.

This is a defensible first-pass proxy, not a precise measure -- flagged
plainly as such. A reviewer will reasonably ask for parcel-level
verification; the write-up says so.
"""
import pandas as pd

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes/05_covariates"
PROJECTS = f"{BASE}/project_level_with_covariates.csv"

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


def classify(district_field: str) -> str:
    if pd.isna(district_field):
        return None
    parts = [d.strip() for d in str(district_field).split(";")]
    labels = set()
    for d in parts:
        if d in MAILO_BUGANDA:
            labels.add("mailo")
        elif d in FREEHOLD_ANKOLE_KIGEZI:
            labels.add("freehold")
        else:
            labels.add("customary")
    if len(labels) > 1:
        return "mixed(" + "+".join(sorted(labels)) + ")"
    return labels.pop()


df = pd.read_csv(PROJECTS)
df["land_tenure_proxy"] = df["district_final"].apply(classify)
df.to_csv(PROJECTS, index=False)

print("land_tenure_proxy distribution:")
print(df["land_tenure_proxy"].value_counts(dropna=False))
print("\nby driver (does land_and_right_of_way concentrate in a tenure type?):")
land_disputes = df[df["drivers_mentioned"].astype(str).str.contains("land_and_right_of_way", na=False)]
print(land_disputes["land_tenure_proxy"].value_counts())
