# Does government audit and independent media agree on WHAT kind of dispute matters?

Section 5.4 (Triangulation) already asked whether the two sources agree on
*where* disputes concentrate. This asks the companion question: do they
agree on *which kind* of dispute matters?

## Method
Both corpora are independently built (different documents, different
classifiers) and both have been through their own disclosed gold-standard
validation, so this is not just "compare two label counts" -- it's "compare
two label counts of very different reliability, and say so."

- **OAG**: 792 sentences, 8 categories, classifier macro-F1 = 0.627
  (paper Section 3.4).
- **Observer**: 24,237 sentences, 7 categories, classifier macro-F1 = 0.231
  (its own `gold_standard/writeup.md`) -- markedly weaker, and its single
  largest category (`land_row_dispute`, 62.6% of the whole corpus) has
  **precision of only 0.08**: 92% of what it labels a land dispute is not
  one on independent reading.

Because of that gap, two comparisons are reported, not one:
1. **Raw shares** -- what each classifier's labels say at face value.
2. **Precision-corrected shares** -- raw count x that category's own
   validated precision, within each source's six shared categories. This
   is a *deflation*, not a reallocation (it does not know which other
   category a false positive really belongs to, only how much of the
   predicted category is real) -- a directionally honest correction, not a
   fully reconstructed distribution.

Six categories map cleanly across the two taxonomies (`delay_time_overrun`,
`land_and_right_of_way`/`land_row_dispute`, `procurement_irregularities`/
`procurement_irregularity`, `contract_management`/`contract_management_failure`,
`delayed_payments`/`payment_financial_dispute`,
`governance_and_controls`/`governance_oversight_failure`). Two OAG categories
(`cost_overrun`, `claims_and_disputes`) and one Observer category
(`quality_technical_defect`) have no counterpart on the other side -- treated
as a finding, not a gap to paper over.

## Result

| Category (OAG name) | OAG raw % | OAG corrected % | Observer raw % | Observer corrected % |
|---|---|---|---|---|
| delay_time_overrun | 17.0 | 25.7 | 14.5 | 22.9 |
| land_and_right_of_way | 11.4 | 15.9 | **62.6** | **43.9** |
| procurement_irregularities | **25.5** | **27.9** | 6.4 | 9.0 |
| contract_management | 17.6 | 19.0 | 3.7 | 5.5 |
| delayed_payments | 12.4 | 7.3 | 2.4 | 7.1 |
| governance_and_controls | 8.3 | 4.2 | 4.3 | 11.7 |

Spearman rank correlation across these six categories: **rho = -0.086
(raw), rho = -0.029 (corrected)** -- both essentially zero, not just
non-significant (n=6, so no p-value here should be over-read, but the
direction is flat, not positive).

**OAG-only:** `claims_and_disputes` (litigation/arbitration language) is
5.9% of the OAG corpus; `cost_overrun` a further 1.9%. Neither has an
Observer counterpart at all.

**Observer-only:** `quality_technical_defect` (physical build-quality
complaints -- cracks, substandard materials) is 6.1% of the Observer
corpus, with no OAG counterpart.

## Interpretation
Audits and media are not describing the same "average" dispute. Even after
correcting for Observer's much weaker classifier, land and right-of-way
disputes remain overwhelmingly what the newspaper writes about (44% of its
corrected shared-category volume) while OAG audits are dominated by
procurement and contract-management process findings (28% and 19%
corrected) -- land ranks near the bottom of the OAG's own list (16%
corrected, 5th of 6). This is a plausible, substantively sensible
divergence rather than a data artifact: land acquisition disputes are
visible, community-facing events (evictions, compensation stand-offs,
protests) that make news; procurement and contract-management
irregularities are technical, paperwork-level audit findings that rarely
generate a story unless they escalate into a scandal. The zero rank
correlation says the two institutions' attention is not just imperfectly
aligned but essentially orthogonal on category emphasis, even while
Section 5.4 already showed they agree strongly on *where* (the Kampala/
Wakiso corridor) the largest volume of activity sits.

The category-scheme mismatch is its own small finding: OAG's audit gaze
captures a financial/legal vocabulary (cost overruns, formal claims and
arbitration) that newspaper coverage apparently never develops into its
own category, while newspaper coverage develops a physical build-quality
vocabulary (cracks, substandard materials) that audit narrative, at least
as classified here, does not surface as a distinct category.

## Caveats
- This is a corpus-level, not an event-matched, comparison -- it says
  nothing about whether the *same* dispute is described differently by
  each source, only whether each source's overall attention allocation
  differs.
- The correction uses precision only, not the full confusion matrix, so
  it is a deflation of each raw count, not a true reconstruction of the
  underlying category distribution.
- Six shared categories is a small base for a rank correlation; the
  rho reported here should be read as "no visible positive alignment,"
  not as a precisely estimated coefficient.
