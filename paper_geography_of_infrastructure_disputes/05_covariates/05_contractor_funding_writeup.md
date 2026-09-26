# Contractor Origin and Funding Source Extraction — Methodology, Coverage, and Findings

## 1. Purpose

This note documents a second reading-based coding pass over the 283 canonical named
projects in `04_project_extraction_geocoding/project_level_canonical.csv`, adding two
explanatory variables required by the paper's design:

- **Contractor origin**: local (Ugandan-registered), foreign, joint venture, or unknown.
- **Funding source**: GoU, donor_loan, donor_grant, co-financed, or unknown.

Output: `05_covariates/05_contractor_funding_extraction.csv` (283 rows, one per canonical
project, joined on `project_name`).

## 2. Methodology

As with the earlier project-name extraction, this was done by **reading**, not regex.
A crude regex pass had already been tried and discarded for the project-name extraction
because surface-pattern matching produced false positives (e.g. "Uganda" extracted as a
project name from "Uganda Road Fund"). The existing `contractor` and `funding_source`
columns in the FINAL sentence corpus (produced by an older, simpler regex) were treated
strictly as *hints* pointing toward candidate sentences to re-examine — not as ground
truth — per the task brief.

Concretely, for each of the 283 canonical projects:

1. All raw sentences tied to the project (via `project_extraction_raw.csv`'s
   `project_name_clean` field, matched exactly, with a small alias/fuzzy fallback for
   one project whose name was consolidated from three raw variants) were pulled together
   with the old regex `contractor`/`funding_source` hints from the FINAL corpus.
2. Each sentence was traced back, via `src_idx`, to its exact position in the
   corresponding year's full, untruncated OAG report text
   (`02_full_reextraction/cache_full_text/{year}_text_FULL.txt`), and a window of
   surrounding text (500–3,000 characters, whitespace-normalized) was pulled to recover
   context lost to sentence-splitting.
3. All 283 project bundles were read in full (not sampled) to identify candidates with
   genuine contractor/funder signal. A keyword scan (contractor markers like "M/s",
   "Ltd", "EPC contractor", "Joint Venture"; funder markers like "World Bank", "EXIM",
   "IsDB", "DFID", "counterpart funding") was used only to *flag* passages for closer
   reading — never to auto-extract the final label.
4. Every flagged candidate was individually deep-dived against the full report text to
   confirm the sentence genuinely describes *that* project (see §4 — several did not).
5. Everything else was coded `unknown`, honestly, rather than inferring plausible but
   unstated contractors/funders from general knowledge of these projects (e.g. it is
   public knowledge that Isimba and Karuma HPPs were built by Chinese EPC contractors
   under China EXIM Bank loans, but since the *available OAG report text* never states
   this, both are coded `unknown` here).

## 3. Coverage (the honesty check)

| Variable | Identified | Unknown | Coverage |
|---|---|---|---|
| Contractor name stated | 12 / 283 | 271 | **4.2%** |
| Contractor origin classified (local/foreign/JV) | 6 / 283 | 277 | **2.1%** |
| Funding source named | 4 / 283 | 279 | **1.4%** |
| Funding category classified (GoU/donor/co-financed) | 8 / 283 | 275 | **2.8%** |

`contractor_origin` breakdown: foreign = 5, local = 1, unknown = 277.
`funding_category` breakdown: donor_loan = 3, GoU = 3, co-financed = 2, unknown = 275.

This is markedly *lower* coverage than the 27.4% "named project" ratio from the earlier
extraction pass. That is expected and is itself a finding for the paper's
data-limitations section: OAG audit reports focus on financial and compliance
irregularities (delays, overpayments, procurement breaches), and even when a project is
named specifically, the contracting firm and financing arrangement are usually left
implicit (referred to only as "the contractor" or "the Contractors") unless the finding
itself concerns the contract award, a technical/engineering audit, or a Value-for-Money
audit — the small number of report sections that do name firms and financiers.

Six additional `contractor_name` values were captured where a firm name is stated in
text but its national origin could not be determined from the name alone (e.g. "Terrain
Services", "Armpass") — these are coded `contractor_origin = unknown` rather than
guessed, consistent with the brief's instruction that unknown should be the honest
majority outcome.

## 4. A caution surfaced during this pass: source-sentence misattribution

Two flagged candidates initially looked like strong hits but, on tracing to the full
report text, turned out to describe a **different** project than the one they were
attached to in the canonical/raw extraction:

- **Ishasha Bridge**: its attributed sentence ("...23-122 days for GOU portion and
  44-101 days for IsDB portion...") was found, via full-text search, to actually belong
  to a different VFM item, "Upgrading of Tirinyi-Pallisa-Kumi/Pallisa-Kamonkoli Road
  Project." The genuine Ishasha Bridge sentence only says contractors were restricted
  access to the bridge — no funder named.
- **Kapchorwa-Suam Road Project**: its attributed sentence ("DFID funding of GBP
  8.9Mn... GoU counterpart funding...") was confirmed (the GBP figure is unique in the
  2025 report) to actually belong to a later, different heading,
  "Kyenjojo-Hoima-Masindi-Kigumba road (RSSP IV) Project" (itself AfDB + DFID +
  GoU co-financed).

Both are coded `unknown` here rather than inheriting the misattributed detail. This
reinforces the paper's broader methodological point: even a reading-based pipeline needs
source triangulation, because sentence-to-project association in a 900-page,
multi-year, OCR'd PDF corpus is fragile at the seams between adjacent report items.

Several `HINT contractor`/`HINT funding` values from the old regex were likewise
investigated and rejected as unrelated noise (e.g. a "National Enterprises Corporation
(NEC) Construction Works and Engineering Ltd" entity-level finding that shared a page
with, but does not describe, the Hoima City Stadium and Kakyeka Stadium projects; an
"ASAP Grant" reference to an unrelated agriculture project that shared a page with the
Kabalega Industrial Park substation and Kabale International Airport entries).

## 5. Substantive findings

### Contractor origin (identified cases only, n=6)

| Project | Contractor | Origin | Basis |
|---|---|---|---|
| Entebbe International Airport Upgrading & Expansion | China Communications Construction Company (CCCC) | foreign (China) | Named as EPC Contractor; explicit in text |
| Kayunga Hospital Rehabilitation | Arab Contractors (Osman Ahmed Osman) | foreign (Egypt) | 2019 engineering audit |
| Yumbe Hospital Rehabilitation | Sadeem Al-Kuwait General Trading and Contracting Co. | foreign (Kuwait) | 2019 engineering audit |
| Kampala Northern Bypass Phase 2 | M/S Mota-Engil Engenharia e Construção | foreign (Portugal) | 2019 UNRA engineering-audit contractor table |
| Soroti-Katakwi-Akisim Road | China Communications Construction Company (CCCC) | foreign (China) | same UNRA table |
| Kaitabawala-Kisozi-Busota Road | Rock Trust Contractors (U) Limited | local | "(U)" designation |

All five identified foreign contractors are on **hospital rehabilitation, airport, and
road** projects — the categories where the OAG conducts dedicated technical/engineering
audits and Value-for-Money audits with contractor-level detail. This is consistent with
a reporting-visibility effect rather than necessarily a true prevalence pattern: we
cannot claim from this data that foreign contractors are more common on these project
types generally, only that they are more *documented* there, because that is where OAG
publishes engineering-audit annexes.

Every identified foreign contractor in this sample is Chinese, Egyptian, Kuwaiti, or
Portuguese — no Indian or other-European firms surfaced in the read text, contrary to
the general prior that Chinese/Indian contractors dominate. This may simply reflect
which projects happened to receive a dedicated engineering audit in the years covered,
not the true composition of Uganda's infrastructure contractor base.

### Funding category (identified cases only, n=8)

- **donor_loan** (3): Entebbe Airport (EXIM Bank of China, explicit "Government
  Concession Loan Agreement"); Hoima Town Roads and Masindi/Kigumba Town Roads (inferred
  from "certificate of no objection...by the funders" — standard donor-procurement
  language, though the specific institution is not named in text).
- **co-financed** (2): Kayunga and Yumbe Hospital Rehabilitation (IPCs split into
  distinct "foreign" and "GoU" payment components; specific foreign financier not
  named).
- **GoU** (3): Hoima City Stadium and Kakyeka Stadium Redevelopment (funded from the
  National Council of Sports' own GoU budget line, no donor mentioned); Uganda Oil
  Refinery Project (2023 report states the financing model was "restructured to be
  public sector led" after the original investor consortium arrangement stalled).

No `donor_grant` cases were identified as textually distinct from `donor_loan` — the
paper's specified default of treating unspecified donor financing as `donor_loan` was
not needed here since, apart from Entebbe Airport (explicitly a loan), no case had
enough detail to distinguish grant from loan.

### Regional/type patterns (light touch, not a full spatial analysis)

Joining the 8 funding-identified and 6 contractor-identified rows back to
`project_level_with_covariates.csv` shows the handful of foreign-contracted/externally
financed projects are concentrated in **Kampala/Wakiso/Entebbe** (Entebbe Airport,
Kampala Northern Bypass), **Karamoja/eastern sub-region** (Soroti-Katakwi-Akisim,
Kaitabawala-Kisozi-Busota), and single hospital sites (Kayunga, Yumbe). Given n=8–12,
this is far too small a sample to support a regional claim — it is noted only as a
pointer for the later, dedicated spatial-analysis step, which should not lean heavily on
contractor/funding variables given how sparse they are.

## 6. Bottom line for the data-limitations section

Contractor and funding-source coverage (1–4%) is an order of magnitude sparser than the
project-name coverage (27.4%). Any regression or spatial model using
`contractor_origin`/`funding_category` as covariates will need to either (a) treat
`unknown` as its own category and interpret coefficients on the identified categories
with extreme caution given n≈6–8, or (b) restrict this analysis to a secondary,
descriptive role rather than a primary explanatory variable. This should be stated
explicitly alongside the project-name coverage caveat already documented for the
geocoding pass.
