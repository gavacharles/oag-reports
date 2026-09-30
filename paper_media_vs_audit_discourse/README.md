# Two Watchdogs, Different Bites

**Working title:** Two Watchdogs, Different Bites: Government Audit and Independent Media Framing of Infrastructure Disputes in Uganda, 2016–2025

**Status:** exploratory groundwork done for all three RQs; no manuscript drafted yet.

## Why a separate paper, not a section in the geography paper
`../paper_geography_of_infrastructure_disputes/` is a complete, self-standing spatial-econometrics contribution (ESDA, GWR, space-time analysis, a real institutional event via the UNRA-MoWT difference-in-differences test, RF/SHAP robustness, a disclosed classifier validation, and geographic triangulation against this project's Observer corpus). Its theory is spatial clustering and subnational institutional capacity (Mamdani, transaction-cost land tenure). This paper's theory is different in kind — accountability and agenda-setting, not geography — so it belongs in a different literature and, most likely, a different journal, rather than being bolted onto a paper that already has a clear shape.

## Theoretical frame
Two accountability actors cover the same underlying reality with structurally different incentives: the OAG is a mandated, periodic, technical horizontal-accountability institution (O'Donnell 1998); The Observer is a continuous, newsworthiness-driven, societal-accountability actor. Agenda-setting theory (McCombs & Shaw 1972) and bounded institutional attention (Jones & Baumgartner 2005) both predict the two should diverge systematically in what they emphasize and when — not simply report the same facts in different words. The empirical work below tests that prediction on three fronts: what each source emphasizes (category), where (geography, stratified by category), and when (volume over time).

## Research questions and findings so far
1. **Do audit and media agree on which KIND of dispute is salient?** No. Precision-corrected category shares (correcting each source's raw counts for its own validated classifier precision — OAG macro-F1=0.627, Observer's own gold-standard check gives macro-F1=0.231) show essentially zero rank correlation (ρ=-0.03 to -0.09 across the six shared categories). Observer is dominated by land/right-of-way disputes (44% of its corrected shared-category volume); OAG audits are dominated by procurement and contract-management findings (28%/19%). Each source also has categories the other's classifier never developed (OAG: cost overruns, formal claims/arbitration; Observer: physical build-quality defects) — a scheme mismatch that is itself a finding about what each institution's gaze is built to see.
2. **Do they agree on WHERE, and does that hold within a single category?** No, beyond the trivial fact that both sources' attention converges on the Kampala/Wakiso corridor regardless of category. All six categories show a positive district-level correlation across the full 16-district base (ρ=0.28–0.60, two nominally significant), but excluding just Kampala and Wakiso collapses every one of them toward zero or negative (e.g. procurement 0.60→0.39 n.s.; governance 0.52→0.42 n.s.) — replicating, category by category, the same collapse the geography paper's own Section 5.4 found for the pooled comparison.
3. **Is there a temporal lead-lag relationship?** No lead-lag signal (Observer(Y-1) vs OAG(Y): ρ=0.03, p=0.96 — exactly null). There is a negative *contemporaneous* relationship (ρ=-0.83 to -0.89, n=6 usable years) that survives normalizing for OAG report page count, reported as an open, small-sample descriptive observation rather than a claim.

**The honest one-line summary across all three RQs:** the two sources agree on one thing — that the capital region dominates — and show no reliable signal on anything more specific: not which category matters most, not where a given category concentrates beyond the capital, and not when coverage of either tracks the other.

## Data lineage
- **`01_framing_geography_timing/`** — all three RQs' analysis scripts, write-ups, and output tables (moved from the geography paper's `12_media_vs_audit_framing/` exploratory folder, where this work started before the decision to split it into its own paper). Reuses the geography paper's OAG corpus (`03_relevance_filter/`, `06_esda/`) and the Observer project's full-corpus outputs (`sentences_classified.csv`, `articles_relevant.csv`) as source data rather than duplicating them — see each script's `PAPER1_BASE` / source paths.

## Target journals (quartile confidence noted honestly — verify before submission)
- **Government Information Quarterly** — Q1 **confirmed** directly (Scimago SJR page, Sept 2026). Best scope fit: government/media/information intersection is its core remit.
- **World Development** — Q1 **confirmed** directly. Good fit if framed toward governance-in-developing-countries rather than communication theory specifically.
- **Governance** (Wiley) — not directly quartile-tagged in what could be pulled; ranked 3rd/47 in Public Administration and 4th/169 in Political Science by impact factor, which makes Q1 very likely but **not literally confirmed** — check the current Scimago tag before committing.
- **International Journal of Press/Politics** — same caveat: IF 3.9 (5-yr 6.5), ranked 7th/94 in Communication — very likely Q1, **not literally confirmed**.

## Known limitations to carry into the paper
- The category-framing and category-stratified-geography checks both rely on Observer's classifier, which is markedly weaker (macro-F1=0.231) than OAG's (0.627) and has a dominant category (`land_row_dispute`) at only 0.08 precision — corrected for via precision-deflation, not a full confusion-matrix reallocation, and disclosed as such.
- The category-stratified geography check is an **article-level co-occurrence** (a place mention and a category-labelled sentence appearing anywhere in the same article), not sentence-level joint labeling — a real granularity limit.
- The volume/lead-lag check has n=6 usable years, two OAG years excluded as non-standard document types (2020 strategic plan, 2021 COVID thematic report), and no multiple-comparison correction applied across this project's several tests.
- No RQ here has been run past a first exploratory pass — before drafting, each deserves the same rigor the geography paper gave its own results (robustness checks, a clean write-up of every caveat, and a second look at whether the classifier-precision correction is the right approach or whether a full confusion-matrix correction is worth the extra work).

## Not yet started
Full literature review (agenda-setting and horizontal/societal accountability theory), manuscript drafting, and a decision on whether the category-framing correction should be upgraded from precision-only deflation to a full confusion-matrix-based reallocation before this goes to a journal.
