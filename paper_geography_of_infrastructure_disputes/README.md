# The Geography of Infrastructure Disputes

**Working title:** The Geography of Infrastructure Disputes: A Spatio-Temporal Analysis of Delay, Cost Overrun and Claims Drivers in Uganda's Public Projects, 2017–2025

**Target journals (Q1 confirmed, September 2026):** International Journal of Project Management; Journal of Management in Engineering (ASCE); Engineering, Construction and Architectural Management

## Research questions
1. Where do dispute drivers concentrate?
2. How has their pattern shifted over 2017–2025, including across the UNRA-to-MoWT transition?
3. Which place-based factors explain the clustering?

## Data lineage (this folder)

Each numbered folder is a pipeline stage, in order. Everything traces back to the raw OAG audit-report PDFs in `../government_Auditor_General/cache/` (shared source material, not duplicated here since it also feeds the original text-mining/ML paper).

- **`01_corpus_audit/`** — Found and quantified document front-matter contamination (table-of-contents dot-leaders, glossary/abbreviations pages, table captions) in the original 1,233-sentence corpus: 12.8% of rows were noise, not audit findings. Verified by spot-check. This stage's cleaned output was superseded by `02_full_reextraction/` once a second, bigger problem was found (see below) — kept for the audit trail.
- **`02_full_reextraction/`** — Found that the original extraction pipeline capped PDF text extraction at 120 pages per report, while actual reports run 164–784 pages (on average 70–85% of each report's content was never read). Re-extracted full text from all 8 cached PDFs (no network calls), applied front-matter stripping up front, and redesigned the driver taxonomy: added `delay_time_overrun` as its own category (didn't exist before — `delayed_payments` is financial, not construction schedule delay), broadened `cost_overrun` and `claims_and_disputes` patterns, made classification multi-label. Result: 1,762 driver-labeled sentences (up from 1,233); `cost_overrun` went from 0 sentences to 34.
- **`03_relevance_filter/`** — Found the infra-relevance filter accepted generic words (`delayed`, `project`, `contract`, `power`) as sufficient alone, letting non-construction content through (academic staffing reports, drug procurement, research-project delays). Added a `construction_relevant` flag requiring a specific infrastructure noun, a named infrastructure agency, or construction-contract-specific terminology. 792/1,762 (44.9%) of driver-labeled sentences pass — this is the corpus the paper's findings should be built on.
- **`04_project_extraction_geocoding/`** — A first regex-based attempt to extract named projects failed in instructive ways (e.g. extracted "Uganda" as a road project because "Uganda Road Fund" matched the same surface pattern as a real project name) — kept in `superseded_regex_attempt/` as a methods-section example of why a reading-based approach was used instead. The reading-based extraction found that only 217/792 sentences (27.4%) name a specific, identifiable project; these canonicalize to **283 distinct projects**, of which **238 were successfully geocoded** via OpenStreetMap Nominatim (212 points, 46 road/transmission-line segments as straight-line proxies between named endpoints). Full methodology, limitations, and reproducibility caveats in `project_extraction_and_geocoding_writeup.md`.

## Known limitations to carry into the paper
- Audit coverage is not a census of disputes — OAG doesn't audit every project every year.
- The project-extraction step (04) is reading-based, not a deterministic script or trained NER model: auditable (every row traces to a source sentence with a confidence rating) but not mechanically reproducible. A second independent read of the ~94 medium/low-confidence extractions would let the paper report a real inter-rater agreement number.
- Road/transmission-line geometries are straight-line proxies between named endpoints, not real alignments (would need OSM way-matching or MoWT GIS data).
- Geocoding precision varies by row (`point-exact` / `place-centroid` / `district-centroid` / `failed`) — see `project_level_geocoded.csv`'s `geocode_precision` column before using a given project's coordinates at face value.

## Not yet started
District-level covariates (UBOS population/poverty, distance to Kampala, DEM terrain, CHIRPS rainfall, land tenure type, funding source, contractor origin, election-year dummies), ESDA (Moran's I, Getis-Ord Gi*), space-time analysis, spatial/GWR regression + RF/SHAP robustness check, expert validation.
