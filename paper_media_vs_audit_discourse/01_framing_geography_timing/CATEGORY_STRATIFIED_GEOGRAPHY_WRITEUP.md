# Does audit/media geographic agreement hold up within a single dispute category?

Paper 1's Section 5.4 tested only overall intensity (all categories pooled):
Spearman rho=0.369 (p=0.160) across 16 districts, collapsing to rho=0.051
(p=0.861) once Kampala and Wakiso are excluded. This extends that test to
each of the six categories both classifiers share, to ask a sharper
question: even if the sources don't agree on which *kind* of dispute
matters (see `CATEGORY_FRAMING_WRITEUP.md`, rho approx 0 nationally), do
they at least agree on *where*, category by category?

## Method
Observer has no pre-built district x category table, so one was built for
this check: for each article, which gazetteer places (the same 23-place,
16-district mapping from `11_triangulation/01_observer_triangulation.py`,
reused unchanged) appear in its title+text (word-boundary match), crossed
with which categories its sentences were classified into (from
`sentences_classified.csv`, joined by article URL). An article counts
toward a (district, category) cell if it has both -- this is an
**article-level co-occurrence**, not a claim that the specific sentence
naming the place is the same sentence carrying that category label. That
granularity limitation is real and is why this check is reported as
exploratory, same as the rest of this folder.

OAG side uses the already-computed `06_esda/district_driver_counts.csv`
(the same table the paper's own Moran's I results are built on).

## Result

| Category | 16-district rho | p | OAG total n (16 districts) | 14-district rho (excl. Kampala/Wakiso) | p |
|---|---|---|---|---|---|
| delay_time_overrun | 0.281 | 0.291 | 23 | -0.081 | 0.783 |
| land_and_right_of_way | 0.316 | 0.232 | 18 | -0.017 | 0.954 |
| procurement_irregularities | **0.600** | **0.014** | 33 | 0.391 | 0.167 |
| contract_management | 0.424 | 0.102 | 19 | 0.119 | 0.687 |
| delayed_payments | 0.314 | 0.236 | 23 | -0.086 | 0.770 |
| governance_and_controls | **0.523** | **0.038** | 8 | 0.417 | 0.138 |

Every category's correlation is positive across the full 16-district base,
and two clear the p<0.05 line (procurement, governance). But excluding
just Kampala and Wakiso collapses every single one -- four flip negative
or near-zero, and the two that were "significant" both lose significance
(procurement 0.600->0.391; governance 0.523->0.417). This is the same
collapse pattern Section 5.4 already found for the pooled, all-category
comparison, now shown to hold category by category too.

Worth flagging on its own: OAG's within-category district counts are
extremely thin even before splitting by district -- governance_and_controls
has only 8 total sentences across all 16 districts combined, delay and
delayed_payments only 23 each. A Spearman correlation built on that few
nonzero points, most of it concentrated in one or two districts, is not
a stable estimate regardless of which way it points.

## Interpretation
There is no reliable evidence of category-specific geographic agreement
between audit and media coverage in this data. What looked like
per-category agreement in the full 16-district comparison is, like
Section 5.4's pooled result, almost entirely the fact that Kampala and
Wakiso dominate both sources' counts *for every category*, not a signal
that the two sources independently converge on the same secondary
districts for a given dispute type. Combined with the near-zero national
category-share correlation (`CATEGORY_FRAMING_WRITEUP.md`), the honest
summary across all of this folder's checks is: **the two sources agree on
one thing only -- that the capital region dominates -- and disagree or
show no reliable signal on everything more specific than that**: not
which category matters most, not where a specific category concentrates
beyond the capital, and not when coverage of either tracks the other.

## Caveats
- Article-level place/category co-occurrence, not sentence-level joint
  labeling -- a real granularity limit on what this check can claim.
- OAG's per-category, per-district counts are very sparse (single digits
  to low 30s across 16 districts) -- Spearman rho at this n is descriptive,
  not a stable estimate.
- No correction for multiple comparisons across the six categories tested
  here, or across this folder's several other tests.
