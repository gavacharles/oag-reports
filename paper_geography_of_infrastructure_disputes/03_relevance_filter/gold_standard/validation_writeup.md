# Gold-Standard Validation of the OAG Multi-Label Driver Classifier

## 1. Methodology and disclosure

This is a **single-rater, AI-assisted validation**, not a human inter-coder
reliability study. All "gold" labels in `gold_labels.csv` were produced by
one AI rater (Claude, via Claude Code) reading each sampled sentence against
a written codebook (`codebook.md`) and judging, independently and blind to
the classifier's own output, which of the classifier's 8 driver categories
genuinely applied. No second human or AI rater cross-checked these labels,
so **no inter-rater reliability statistic (e.g. Cohen's kappa) can be or is
reported here**, and this exercise cannot claim the same evidentiary weight
as a dual-human-coder validation with adjudicated disagreements. It should
be read as a disciplined, disclosed sanity check against systematic
classifier failure modes — not as a certification that the "gold" labels
are themselves ground truth in an absolute sense. Coding decisions and
uncertainty are recorded per-sentence in `gold_labels.csv` (`confidence`,
`notes` columns): 250/362 sentences (69%) were coded at `high` confidence,
99 (27%) at `medium`, and 13 (4%) at `low`.

**Procedure.** A sample was drawn from the 792-sentence analysis corpus
(`oag_infrastructure_sentence_corpus_2017_2025_FINAL.csv`), stratified by
the classifier's `primary_driver` field (used only for sampling balance,
never as ground truth), capped at 50 sentences per category (all available
sentences taken for the two categories with fewer than 50:
`claims_and_disputes`, 47, and `cost_overrun`, 15). Sampling used a fixed
seed (42) via `pandas.DataFrame.sample`, implemented in `sample_blinded.py`.
The rater coded from `sample_blinded.csv` (sentence text + year only, no
classifier labels) and only after finalizing `gold_labels.csv` were labels
joined back to the classifier's `all_drivers` field, via the sample's
carried `orig_index`, for scoring (`score_validation.py`).

## 2. Sample size and composition

**362 sentences** (roughly 46% of the 792-sentence corpus), distributed
across the classifier's `primary_driver` strata as follows: `delayed_payments`
50, `procurement_irregularities` 50, `contract_management` 50,
`delay_time_overrun` 50, `land_and_right_of_way` 50, `governance_and_controls`
50, `claims_and_disputes` 47, `cost_overrun` 15.

A striking, and important, structural fact surfaced during coding: **85 of
362 sampled sentences (23%)** were judged to genuinely carry **none** of the
8 categories — mostly table-of-contents/appendix header dumps, financial
appendix tables, and generic strategic-plan boilerplate that survived the
front-matter stripping step and the construction-relevance filter but do
not describe a substantive audit finding. By construction, the classifier
itself never produces a zero-label sentence in this corpus (the extraction
script drops any sentence with no regex match before it enters
`FINAL.csv`), so the classifier's false-positive rate on "should this
sentence have been in the corpus at all" cannot be under-stated by this
validation — it is a real, separately worth noting, contamination of the
corpus with un-codable noise.

## 3. Results

| category | n_gold_pos | n_classifier_pos | TP | FP | FN | precision | recall | F1 |
|---|---|---|---|---|---|---|---|---|
| delay_time_overrun | 125 | 50 | 50 | 0 | 75 | 1.000 | 0.400 | 0.571 |
| cost_overrun | 32 | 15 | 13 | 2 | 19 | 0.867 | 0.406 | 0.553 |
| claims_and_disputes | 47 | 49 | 36 | 13 | 11 | 0.735 | 0.766 | 0.750 |
| land_and_right_of_way | 64 | 53 | 49 | 4 | 15 | 0.925 | 0.766 | 0.838 |
| contract_management | 83 | 60 | 43 | 17 | 40 | 0.717 | 0.518 | 0.601 |
| delayed_payments | 42 | 69 | 27 | 42 | 15 | 0.391 | 0.643 | 0.487 |
| governance_and_controls | 28 | 54 | 18 | 36 | 10 | 0.333 | 0.643 | 0.439 |
| procurement_irregularities | 65 | 76 | 55 | 21 | 10 | 0.724 | 0.846 | 0.780 |

**Macro-averaged: precision = 0.711, recall = 0.624, F1 = 0.627.**
Micro-averaged (pooled TP/FP/FN across categories): precision = 0.683,
recall = 0.599, F1 = 0.638.

## 4. Headline: macro-F1 = 0.627

This is a **moderate, not strong, result**, and it is not uniform — it
hides a wide and informative spread from F1 = 0.838 (`land_and_right_of_way`)
down to F1 = 0.439 (`governance_and_controls`). The two-decimal macro number
should not be read as "the classifier is 63% accurate"; it averages two very
different failure modes that pull in opposite directions (see §5), and a
paper built on these labels should treat the underlying category counts as
directionally informative, not precisely quantified.

## 5. Strongest and weakest categories, and why

**Strongest: `land_and_right_of_way` (F1 = 0.838) and
`procurement_irregularities` (F1 = 0.780).** Both benefit from having a
fairly well-scoped, substantively meaningful vocabulary ("land acquisition",
"right of way", "encroachment", "resettlement" for the first;
"procurement", "bid", "tender", "evaluation committee" for the second) that
maps closely onto how OAG reports actually phrase these findings. Reading
through the sample, `procurement_irregularities` still over-triggers
somewhat on purely descriptive procurement-process sentences (audit
narration of a normal procurement step, not an actual irregularity), but
undershoots less because OAG language on procurement is fairly formulaic.
`land_and_right_of_way` is the classifier's cleanest category.

**Weakest: `governance_and_controls` (F1 = 0.439) and `delayed_payments`
(F1 = 0.487) — both driven by severe over-triggering (precision 0.33 and
0.39 respectively).** `governance_and_controls`'s regex terms ("oversight",
"accountability", "governance", "lack of supervision/monitoring") are
generic English words that appear constantly in OAG boilerplate — strategic
objectives, stakeholder-engagement tables, section headers — with no
institutional-control finding attached; 32 of its 36 false positives were
sentences the gold reading scored as having **no** category at all.
`delayed_payments`'s regex ("arrears", "outstanding payment") fires on any
mention of domestic arrears (pensions, salaries, utility bills, drug
stock-outs) regardless of whether the arrears relate to an infrastructure
contractor — 24 of its 42 false positives were, again, sentences gold
scored as having no category. This is the same failure pattern the prompt
flagged as a concern from the companion newspaper-corpus paper's classifier
(a keyword that is topically generic over-triggers badly): it reproduces
here too, specifically for `governance_and_controls` and `delayed_payments`.

**Also concerning, in the opposite direction: `delay_time_overrun`
(precision 1.0, recall 0.40).** Every sentence the classifier tagged as a
schedule delay genuinely was one (zero false positives across 362
sentences) — but the gold reading found 125 delay-relevant sentences in the
sample and the classifier's narrow regex (`extension of time`, `behind
schedule`, `time overrun`, etc.) caught only 50 of them. The other 75 were
missed because the sentence described a schedule delay using different
surface language while its regex-matched category was
`procurement_irregularities` (27 of the 75 misses), `land_and_right_of_way`
(19), `contract_management` (15), `delayed_payments` (13), or
`claims_and_disputes` (12) — i.e. delay is frequently *caused by* and
narrated through procurement/land/payment/contract language, and the
delay-specific regex doesn't catch it. Given that
`delay_time_overrun` is the paper's most central schedule-delay construct,
this recall gap is arguably the single most important finding of this
validation: **the corpus almost certainly undercounts delay-driver
sentences by more than half.**

`cost_overrun` shows the same undercount pattern (precision 0.867, recall
0.406, n=32 gold positives from only 15 sampled) but its very small n (only
34 in the whole 792-sentence corpus) means this estimate itself is
imprecise; the direction (undercount) is more trustworthy than the exact
recall figure.

`contract_management` (F1 = 0.601) sits in between: it both over-triggers on
generic uses of "supervision"/"defect" (17 FP) and under-triggers because
many defect/quality findings are phrased without those exact terms (40 FN,
missed most often when the sentence's matched category was
`delay_time_overrun`, `procurement_irregularities`, or `delayed_payments`
instead) — consistent with the codebook's own advance warning that this
category was "prone to over-triggering."

## 6. What this means for the paper's downstream spatial results

1. **Category counts by district/year should be interpreted as noisy
   indicators of dispute-driver salience, not as precise counts.** A
   macro-F1 of 0.627, built on precision/recall pairs ranging from
   (1.00, 0.40) to (0.33, 0.64), means that for at least three of the eight
   categories (`delayed_payments`, `governance_and_controls`,
   `delay_time_overrun`) the raw sentence counts that feed the maps,
   regressions, and GWR models are directionally biased in a *known* way:
   `delayed_payments` and `governance_and_controls` counts are inflated by
   generic keyword matches unrelated to any real contractor payment or
   control failure, while `delay_time_overrun` counts are deflated because
   the regex misses delay content phrased through procurement/land/payment
   language.
2. **Any spatial or temporal pattern reported for `delay_time_overrun` in
   particular should be treated as a lower bound and a conservative
   signal**, not a full accounting of schedule-delay content — and any
   comparison of `delay_time_overrun` magnitude against other categories
   (e.g. "procurement irregularities are twice as common as schedule
   delays in region X") is confounded by this differential recall and
   should not be made without a caveat.
3. **`governance_and_controls` and `delayed_payments` results deserve the
   most caution of all eight categories** before being used to support any
   claim about the geography or trend of institutional-control weakness or
   contractor payment delay specifically — roughly a third to a half of
   what the classifier flags in each of those two categories is, on
   independent reading, not actually about that construct at all. The two
   strongest categories, `land_and_right_of_way` and
   `procurement_irregularities`, can be reported with comparatively more
   confidence, though even there roughly a quarter of the true positive
   content is being missed (recall 0.77 and 0.85 respectively) so absolute
   counts should still be treated as undercounts.

Overall: this validation does not invalidate the paper's central spatial
and temporal patterns, but it does mean the paper should (a) report this
macro-F1 and per-category breakdown transparently in a methods/limitations
section, (b) avoid over-precise claims about relative category prevalence,
and (c) flag `delay_time_overrun`, `delayed_payments`, and
`governance_and_controls` explicitly as the categories whose counts are
least reliable, in either direction.
