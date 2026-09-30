# Does media dispute-coverage volume lead, lag, or move with the OAG's annual reporting?

## Method
Two annual series, deliberately kept conceptually distinct:
- **OAG(Y)**: count of dispute-driver sentences in the report FILE dated
  year Y (i.e. that report's own cover year -- close to its Parliament-
  tabling date). OAG reports mostly narrate findings from the fiscal
  year(s) *preceding* Y, so OAG(Y) already carries a built-in lag relative
  to the events it describes.
- **Observer(Y)**: count of dispute-relevant sentences from articles
  actually *published* in calendar year Y -- much closer to real time.

Two OAG years are structurally different documents, not standard annual
audits, and are shown but excluded from the correlation: **2020** (a
strategic-planning document, 15 sentences) and **2021** (a COVID-19
thematic report, 5 sentences). **2017** has zero sentences in the OAG
analysis corpus (no usable extracted content that year). That leaves
**six usable years** (2018, 2019, 2022-2025) for any quantitative check --
stated plainly as underpowered for a confident conclusion; what follows is
a descriptive first look, not a hypothesis test with real power.

## Result

| Year | OAG sentences | OAG report pages | OAG rate /100pg | Observer sentences | OAG report type |
|---|---|---|---|---|---|
| 2018 | 150 | 450 | 33.3 | 1,935 | standard |
| 2019 | 138 | 475 | 29.1 | 1,607 | standard |
| 2020 | 15 | 217 | -- | 2,266 | strategic plan (excluded) |
| 2021 | 5 | 164 | -- | 2,725 | COVID thematic (excluded) |
| 2022 | 91 | 579 | 15.7 | 2,690 | standard |
| 2023 | 134 | 784 | 17.1 | 2,281 | standard |
| 2024 | 133 | 559 | 23.8 | 2,541 | standard |
| 2025 | 126 | 760 | 16.6 | 2,853 | standard |

**Contemporaneous** (OAG(Y) vs Observer(Y), n=6): Spearman rho = **-0.886**
(p=0.019); page-count-normalized rate vs Observer(Y): rho = **-0.829**
(p=0.042). Both negative, and the normalized version rules out the
obvious confound (a longer report mechanically producing more
dispute-driver sentences regardless of actual content) -- 2022 has the
*most* pages of any usable year (579) but the *lowest* sentence count and
rate.

**Lag-1** (OAG(Y) vs Observer(Y-1), i.e. "does last year's media volume
predict this year's audit-report volume," n=6): Spearman rho = **0.029**
(p=0.957) -- no relationship at all, essentially exactly zero.

As a sanity check against "Observer just publishes more content some
years for unrelated reasons": total raw Observer article volume
(dispute-relevant or not) is fairly flat, 478-619 articles/year from 2018
onward, so the dispute-relevant volume trend is not simply riding a
general growth in site output.

## Interpretation
No lead-lag story survives here -- the lag-1 check is exactly null, so
there is no support for "media coverage this year predicts audit volume
next year" in this data. What is more interesting, and more surprising,
is the negative *contemporaneous* relationship: years when the OAG report
devotes proportionally more of its content to dispute-driver findings
tend to be years when Observer's dispute-relevant volume is comparatively
lower, and vice versa (2018-2019 high-OAG/lower-Observer;
2022-2023-2025 low-OAG/higher-Observer). This survives normalizing for
report length, so it is not simply an artifact of some reports being
longer than others.

That said, **this pattern should be held loosely, not reported as a
finding on its own footing**: n=6 is very small, no correction for the
several correlation tests run across this and the category-framing
analysis has been applied, and a single unusual year (2022's unusually
low OAG dispute-content rate, for reasons this data cannot explain) could
be doing most of the work. Plausible readings if the pattern is real --
none of which this design can adjudicate between -- include audit and
media attention behaving as loose substitutes for scrutiny (when one is
quiet, institutional or press attention shifts to the other), or both
series responding to a shared but unmeasured driver (e.g. election cycles,
major project milestones) in offsetting ways. This is flagged as a
genuinely open, small-sample descriptive observation, not a claim.

## Caveats
- n=6 usable years; no multiple-comparison correction across the several
  tests run in this exploratory folder.
- OAG(Y) and Observer(Y) measure different kinds of "year" (report cover
  year vs. real publication date) by construction -- the contemporaneous
  comparison is a convenience alignment, not a claim that the two years
  represent the same underlying time window.
- 2020 and 2021 are excluded as non-standard report types, which further
  shrinks an already small sample and should be disclosed wherever this
  result is cited.
