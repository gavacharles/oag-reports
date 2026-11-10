# oag-reports

Python scripts, extracted corpora, results, figures and write-ups for text mining and spatial analysis of Uganda's Office of the Auditor General (OAG) annual reports, 2017–2025, focused on infrastructure disputes.

## Layout

| Folder | What it holds |
|---|---|
| `government_Auditor_General/` | Report collection (`OAG reports.py`, report link lists), dispute-driver classification and factor analysis, model comparisons and benchmarks (factor analysis vs LDA, LDA to SVM), actor-network analysis, spatial mapping, visualisation scripts, JSON summaries, `plots_png/` and write-ups; `cache/` holds intermediate files |
| `paper_geography_of_infrastructure_disputes/` | A numbered pipeline: `01_corpus_audit`, `02_full_reextraction`, `03_relevance_filter`, `04_project_extraction_geocoding`, `05_covariates`, `06_esda`, `07_visualization`, `08_gwr`, `09_space_time`, `10_manuscript`, `11_triangulation` (see its [README](paper_geography_of_infrastructure_disputes/README.md)) |
| `paper_media_vs_audit_discourse/` | Comparison of media and audit discourse: framing, volume lead–lag and stratified geography scripts in `01_framing_geography_timing/` (see its [README](paper_media_vs_audit_discourse/README.md)) |

## Running

Each folder's scripts run from inside that folder. The numbered stages in `paper_geography_of_infrastructure_disputes/` run in order, each reading the outputs of the stage before it.
