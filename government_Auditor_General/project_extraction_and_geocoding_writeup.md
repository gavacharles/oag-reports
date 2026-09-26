# Project Extraction and Geocoding: Methodology, Results, and Limitations

## 1. Methodology

**This extraction was done by direct human-equivalent reading of every sentence, not by a Named Entity Recognition (NER) model, regex, or any automated pipeline.** Each of the 792 sentences in `oag_infrastructure_sentence_corpus_2017_2025_FINAL.csv` was read in context (batches of ~40-80 rows, cross-checked against neighboring rows and, where needed, the full report text in `cache/{year}_text_FULL.txt`) and judged against the question: "does this sentence name a specific, identifiable infrastructure project or facility, as opposed to an institution or a generic reference?"

This has real implications for reproducibility:
- The judgment calls (what counts as "specific enough," how to split a name from surrounding OCR prose, what district to infer) reflect one reader's (Claude's, under human direction) interpretation. A different analyst could reasonably draw the line differently on ambiguous cases, especially the ~90 "medium" and 11 "low" confidence extractions.
- Because this is not a deterministic algorithm, the extraction is not exactly reproducible by re-running a script. It is auditable (every row traces back to a specific sentence and a `confidence` rating) but not mechanically reproducible.
- The prior regex-based attempt failed for exactly the reason this approach was chosen: regex cannot distinguish "Busega-Mpigi Expressway" (a project) from "Uganda Road Fund" (an institution matching a similar surface pattern). Reading each sentence in context resolves this, at the cost of speed and perfect consistency.

Extraction rule of thumb applied: a project only counts as "named" if the specific name appears in that literal sentence (not merely inferable from a neighboring sentence in the same finding). A small number of exceptions were made only where a table row's own text made the identity unambiguous (e.g., a sub-bullet immediately under a named entity's header row within the same OCR-extracted "sentence").

## 2. How much of the corpus names a specific project?

- **792** sentences in the cleaned, construction-relevant corpus (2017/18–2024/25 OAG reports).
- **217 sentences (27.4%)** name at least one specific, identifiable infrastructure project or facility.
- The remaining **575 sentences (72.6%)** are about generic/institutional matters: sector-wide findings ("delays in land acquisition affect infrastructure projects"), institutions rather than projects ("Uganda National Roads Authority," "Uganda Road Fund"), or district-level summaries that don't name a specific facility.
- Because a number of sentences are OCR-flattened table rows that bundle multiple named entities into one "sentence" (a known artifact of PDF table extraction), 217 named-project sentences yielded **334 individual project mentions** (some rows named 2-7 distinct projects at once, e.g. a table row listing several bridge defects across different bridges).

**This 27:73 ratio is itself a finding, not just a filtering step.** It means most of what OAG's audit narrative says about "infrastructure disputes" in Uganda is expressed at the level of the responsible institution, the sector, or the district — not tied to an individually named, mappable project. A spatio-temporal analysis built only from named-project sentences necessarily covers a minority of the audited findings, and is skewed toward the kinds of projects (large national ones like Karuma/Isimba/Entebbe Airport, or itemized district-level infrastructure sub-projects reported in inspection tables) that happen to get named. Cost overrun and claims/disputes findings, in particular, were disproportionately reported at the institutional/sectoral level rather than tied to named projects (see driver breakdown below).

## 3. Canonicalization: how many distinct projects?

The 334 project mentions were grouped into **283 distinct canonical projects**, after merging a small number of known aliases across report years (e.g., "Busega-Mpigi Road Project" [2018] and "Busega-Mpigi Expressway" [2024] are the same project; "Kiruddu Referral Hospital" and "Kiruddu National Referral Hospital" are the same facility). This N=283 is the actual base for any spatial analysis — **not** 334 (mentions) and **not** 792 (sentences).

Of these 283 projects:
- **26** are mentioned in more than one report year (multi-year persistence — useful for tracking a dispute's duration).
- **35** are mentioned more than once (across sentences, possibly within the same year).
- The great majority (say roughly 250) appear only once, in one sentence, in one year. This is expected: most of these come from district-by-district or contract-by-contract inspection tables that appear once in a single report (e.g., a specific USMID road defect list, or a specific seed-school construction delay noted once in the 2019 report).

Project type breakdown (canonical N=283):
- road: 57
- hospital_health: 55
- other_building: 51
- school: 46
- power_transmission: 18
- bridge: 17
- other (rail, pipeline, drainage, irrigation): 13
- water_supply: 11
- market: 4
- power_generation: 3 (Isimba, Karuma, Nalubaale-Kiira)
- airport: 3
- stadium: 3
- dam: 2

Confidence distribution (minimum confidence across all mentions of a project):
- high: 189 (67%)
- medium: 83 (29%)
- low: 11 (4%)

Low-confidence projects are mostly cases where a name had to be partially inferred (e.g., "a Seed secondary school in Katikamu Sub County" with no proper name given in the sentence, so the natural name was inferred) or where an acronym's full identity was uncertain (e.g., "UNMC," "UBFC"). These are flagged in `project_extraction_raw.csv` and `project_level_canonical.csv` and should be spot-checked before being treated as confirmed.

## 4. Geocoding

All 283 canonical projects were geocoded against the live OpenStreetMap Nominatim API (`https://nominatim.openstreetmap.org/search`), sequentially with a 1.1s delay between requests and a descriptive `User-Agent` header identifying this research and a contact email, per Nominatim's usage policy. Point-type projects were queried as `"<place>, Uganda"`; line-type projects (roads, transmission lines) were queried once per named endpoint, so each yields two coordinate pairs (a straight-line proxy between them, **not** a real alignment).

**Status:**
- success: 238 (84.1%)
- partial: 20 (7.1%) — geocoded, but at reduced confidence (district centroid, a subcounty-level proxy, or only one of two line endpoints found)
- failed: 25 (8.8%) — no usable OSM match found at all

**Precision breakdown (283 total):**
- point-exact: 1 (a specific hospital building matched directly in OSM)
- place-centroid (single point projects): 191
- place-centroid, both line endpoints found (roads/transmission lines): 46
- place-centroid, only one of two line endpoints found: 10
- place-centroid via a proxy/subcounty match (exact facility not in OSM, sub-county or co-located landmark used instead): 2
- district-centroid fallback (place-level match unavailable or unreliable): 8
- failed: 25

**A critical, hands-on finding: first-pass Nominatim results contained real errors that a naive automated pipeline would have silently kept.** Uganda has many villages/places that share a name across different, distant districts, and Nominatim's plain-text search sometimes returned the wrong same-named place. A systematic cross-check (comparing each result's returned district against the district recorded during extraction) surfaced 37 candidate mismatches; most were false alarms (e.g. "Entebbe City" vs. "Wakiso" — Entebbe is now its own city, separate from Wakiso district administratively, but it's the right place), but at least 15 were genuine errors that were corrected by re-querying with the district appended for disambiguation, including:
- **Isimba Hydropower Plant**: initially matched to a village called "Isimba" in Hoima District — the real Isimba dam is on the Nile at the Kayunga/Kamuli border. No correctly-located "Isimba" node exists in OSM at all (two wrong ones do, in Hoima and Masindi), so this project was ultimately geocoded to the **Kayunga District centroid** (partial, district-centroid), not a wrong village.
- **Kabaale International Airport / Kabaale Industrial Park / Uganda Oil Refinery Project** (all near Hoima): initially matched to a "Kabaale" village in **Rakai District**, ~500km away. Corrected to the real Kabaale in Hoima District after re-querying with the district appended.
- **Mandela National Stadium (Namboole)**: initially matched to a "Namboole" in Butaleja District (Eastern Uganda) instead of the actual stadium's location in Wakiso District near Kampala. Corrected.
- **Kiruddu National Referral Hospital**: initially matched a "Kiruddu" neighborhood placeholder in Mukono; corrected to the actual hospital building tagged in OSM (Salaama Road, Makindye, Kampala) — this one reached point-exact precision.
- Also corrected: Nalubaale-Kiira hydropower plant (was matched to Buvuma island instead of Jinja), New Kampala Port at Bukasa (was matched to a Bukasa on Kalangala island instead of Kampala's Bukasa peninsula), Gaba Water Treatment Plant (was matched to a Gaba in Butaleja instead of Kampala's Gaba), Natete Police Station (was matched to a Natete in Ibanda instead of Kampala), Lake Katwe Technical Institute (was matched to Kampala's Katwe slum instead of the actual Lake Katwe near Kasese), Kakyeka Stadium (was matched to Isingiro instead of Mbarara), Gombe Hospital, Lusenke Ranch, Nakaseta Primary School, Goma HC III, Elegu One Stop Border Post, Aduku Seed Secondary School, and Loborom HC III (the last resolved only to its sub-county's polytechnic as a proxy, since the health centre itself isn't in OSM).

This matters for the paper: **do not treat the geocoded coordinates as ground truth without spot-checking**, especially anything at "district-centroid" or "proxy" precision. The corrections above were caught because the extraction recorded an independent `district` field to check against — any future geocoding pass on new data should keep doing this cross-check as standard practice, not a one-off audit.

Projects that failed entirely are mostly either (a) genuinely national/dispersed in scope with no single point (Standard Gauge Railway, EACOP pipeline), which is a correct "failure" — they shouldn't be forced onto a point — or (b) small, specific facilities (a particular ranch, a particular swamp-crossing culvert, a specific rural health centre) that simply aren't in OpenStreetMap's Uganda coverage yet.

## 5. Limitations a Q1 reviewer would raise immediately

1. **Not a census of Uganda's public infrastructure projects.** OAG does not audit every project every year; it samples entities and themes. A project's absence from this dataset does not mean it had no disputes, and a project's presence in multiple years may partly reflect OAG's own sampling/thematic choices (e.g., 2019's Karuma/Isimba value-for-money audit) rather than the project being uniquely dispute-prone.
2. **Straight-line road/transmission-line proxies are not real alignments.** For line-type projects (roads, transmission lines), the geocoded points are the named endpoint towns/villages only — a straight line between them (or between the two most-distant named waypoints when more than two are listed) is a crude proxy for the actual corridor, which in reality follows terrain, existing right-of-way, and engineering constraints. True alignment would require OSM way-matching against real road/line geometries or MoWT/UETCL GIS shapefiles — out of scope for this pass and flagged as a clear follow-up need.
3. **Reading-based extraction is not mechanically reproducible.** As noted in the methodology section, a different reader (or the same reader on a different day) could draw slightly different lines on the ~94 medium/low-confidence cases, though the ~189 high-confidence extractions are unambiguous (specific proper names with explicit locations).
4. **Under-counting from generic references.** Some projects are almost certainly under-counted because in some years OAG's report referred to them only generically ("several roads under URF," "some regional referral hospitals") rather than by name, even though the same physical project may be the subject in more specific form elsewhere. The 217/792 sentence-level ratio should be read as a floor, not a ceiling, on how much of the corpus is "about" specific named projects in substance.
5. **Table-flattening inflates some rows' apparent mention density.** Because OCR extraction turns multi-column audit tables into single run-on "sentences," some sentences yielded many project mentions at once (up to 7 in one case), while true independent sentence-level "mentions" of a project in different narrative contexts are comparatively rare. `n_mentions` in the canonical table should be read with this in mind — it is not a clean measure of how many separate audit passes flagged a project.
6. **Near-identical names denote different real places.** Two nearly identical names surfaced during extraction that are genuinely different facilities: "Kabale International Airport" (existing airstrip, Kabale District, southwestern Uganda) and "Kabaale International Airport" (the new international airport under construction near the oil refinery in Kabaale, Hoima District). These were kept distinct based on the district each sentence specified, but this is exactly the kind of near-miss a regex approach would have collapsed, and a human reviewer should double check both.

## 6. Files produced

- `project_extraction_raw.csv` — 909 rows: one row per (source sentence × named project extracted from it), plus all sentences with no named project (has_named_project=False), fully traceable to `oag_infrastructure_sentence_corpus_2017_2025_FINAL.csv` via `src_idx`.
- `project_level_canonical.csv` — 283 rows, one per canonical project, with years_mentioned, n_mentions, drivers_mentioned, and a representative sentence.
- `project_level_geocoded.csv` / `project_level_geocoded.geojson` — the same 283 projects with Nominatim-derived coordinates, geocode_status, geocode_precision, and the raw Nominatim display_name for auditability.
