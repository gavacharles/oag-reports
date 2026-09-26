# Triangulation against the Observer newspaper corpus

## Method
The Observer newspaper study (companion paper, same research team, entirely
different source documents and extraction pipeline) maintains a curated
29-place gazetteer of dispute-relevant article mentions, 2016-2025. 7 of
these are sub-regional or cross-border (Karamoja, Bunyoro, Nile, Kenya,
Tanzania, South Sudan, DRC) and don't map to a single Uganda district, so
are excluded. The remaining 23 place names collapse to 16 distinct
districts (e.g. Kampala + Nakawa + Nakivubo all fall within Kampala
district; Entebbe + Lubowa + Wakiso + Namboole all fall within Wakiso
district). District mapping used direct knowledge of Uganda administrative
geography, including reusing this paper's own disambiguation of "Kabaale"
(the Hoima oil-region site) from "Kabale" (the southwestern district) --
the same distinction Section 3.2 already had to resolve for OAG project
geocoding.

16 districts appear in both the OAG audit-derived data (project counts,
2017-2025) and the Observer newspaper data (article mentions, 2016-2025).

## Result
Spearman rank correlation across all 16 districts: **rho = 0.369, p = 0.160**
-- positive but not statistically significant.

Both sources agree emphatically that Kampala and Wakiso dominate (Kampala:
1,081 newspaper mentions / 31 OAG projects; Wakiso: 510 / 18 -- both far
ahead of every other district in both sources). Excluding just these two
districts, the correlation among the remaining 14 collapses to **rho =
0.051, p = 0.861** -- essentially zero.

## Interpretation
The two independent, differently-constructed data sources agree strongly
on the single largest fact about Uganda's dispute geography (the Central
corridor around the capital dominates) but do not agree on the finer-
grained ranking of secondary districts. This is genuine, useful external
validation of the paper's headline finding (the Kampala-Wakiso-Mukono-
Luwero corridor concentration reported in Section 5.2) from a source with
no shared extraction methodology. It is simultaneously evidence *against*
over-reading the paper's district-level fine structure beyond that
headline pattern: a newspaper's geographic salience and an auditor's
geographic coverage are different lenses, and where they diverge (e.g.
Jinja ranks 3rd in newspaper mentions but only 6th in OAG project count;
Kayunga ranks low in newspaper mentions but mid-table in OAG projects)
that divergence is informative about each source's own selection bias
rather than a contradiction to resolve.

## For the manuscript
This becomes a new Section 5.8 (or folds into 6.1) plus one figure. Recommended
framing: "external validation for the headline pattern, appropriate caution
against the district-level fine structure" -- consistent with how the rest
of the paper already treats audit-coverage-as-not-a-census.
