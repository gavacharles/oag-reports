# RQ2, properly tested: the UNRA-to-MoWT transition

## Method
Difference-in-differences: road-sector (UNRA's domain) project-year mentions
vs. all other sectors, comparing 2017-2020 (pre) against 2021-2025 (post),
break point = 2021 (the policy announcement year; legal dissolution wasn't
until Nov 2024, too close to the window's end to leave usable "after" data
if used as the break instead -- stated explicitly, not silently chosen).
Rates are per-year to account for the unequal window lengths (4 vs 5 years).
DiD design, not a raw pre/post comparison, because it nets out whatever
changed for every sector at once (COVID-era audit-volume growth, report
length, etc.) and isolates what's road-specific.

## Result
- Road:     5.25/yr -> 8.00/yr (**+2.75/yr, +52%**)
- Non-road: 35.50/yr -> 22.20/yr (**-13.30/yr, -37%**)
- Diff-in-diff: **+16.05 mentions/year** in road's favour
- 2x2 (sector x period) chi-square on raw counts: **chi2 = 8.42, p = 0.0037** -- significant

Geographic angle: road-dispute mean distance-to-Kampala fell only modestly
(150.3km -> 143.8km, -6.5km) while non-road fell much more (167.8km ->
147.8km, -20.0km) over the same window -- road disputes were already
closer to the capital before the transition and stayed roughly there,
while non-road disputes' centre of gravity moved noticeably toward Kampala
post-2021.

## Interpretation -- and the causality problem that has to be stated plainly
Road-sector disputes rose, in both absolute and relative terms, right
around the period UNRA's dissolution was announced and (later) enacted,
while every other sector's dispute reporting fell over the identical
window. That is a real, statistically significant, sector-specific pattern
coincident with the institutional transition.

It is NOT evidence that the transition *caused* the rise. The more
plausible reading, worth stating explicitly rather than glossing over, is
the reverse: UNRA's accumulating procurement and delay scandals through
this period were part of the public and political case *for* dissolving
it, not a consequence of the dissolution decision. A single-source,
observational, non-experimental design like this one cannot distinguish
"the transition disrupted delivery, driving more disputes" from "existing
dispute intensity built the political case for the transition" from "an
audit reallocated attention to the road sector specifically because it was
under legislative scrutiny during this period." All three are consistent
with the same DiD number. The paper should report the pattern as real and
report the ambiguity as real, not resolve it by picking the more
publication-friendly story.

## For the manuscript
This becomes a genuine, substantive answer to RQ2 -- currently underserved
by the vague space-time-GIF treatment in Section 5.3. Recommend: expand
Section 5.3 (or add 5.3b) with the DiD table and the explicit
three-way causality caveat above, and reference it again in Section 6
(Discussion) alongside the land-tenure finding as a second concrete,
appropriately-hedged result.
