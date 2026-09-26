# ESDA and Explanatory Modelling: Results Summary

Covers Methods section 4 (Exploratory spatial analysis, Explanatory modelling) of the outline, run on the 135-district cross-section derived from 261 geocoded, district-assigned OAG audit projects (2017-2025).

## 1. Global spatial autocorrelation (Moran's I)

Queen contiguity weights, 999 permutations, one test per driver category (project counts per district). See `global_morans_i_results.csv`.

Significant positive spatial autocorrelation (p<0.01): **delayed_payments** (I=0.336, strongest), **land_and_right_of_way** (I=0.333), **procurement_irregularities** (I=0.226), **contract_management** (I=0.189), **delay_time_overrun** (I=0.165). Not significant: cost_overrun, claims_and_disputes, governance_and_controls -- all three have only 6-14 non-zero districts, a genuine power limitation, reported rather than hidden.

**Answers RQ1's first half plainly: dispute drivers are not spatially random.**

## 2. Local hot spots (Getis-Ord Gi*)

FDR-corrected within each category. See `getis_ord_hotspots.csv` and `hotspot_maps.png`.

- **Land/right-of-way and delay** cluster heavily in the Kampala-Wakiso-Mukono-Luwero corridor.
- **Cost overrun** clusters separately in two places: the Hoima/Buliisa oil region and the Mbale/Manafwa/Kween Elgon highlands -- a genuinely different geography from the land/delay cluster, worth its own discussion paragraph.
- **Delayed payments**: sharp Kampala-Wakiso spike plus an isolated Kapchorwa outlier.

Note on interpretation: a handful of *zero-count* districts appear as significant hot spots (e.g. Mukono for claims_and_disputes). This is correct Gi* behaviour, not an error -- Gi* measures the neighbourhood-weighted local mean, so a zero-count district embedded among high-count neighbours still reads as "in a hot region." Read this as consistent with the audit-coverage-is-not-a-census limitation (that specific district's projects may simply not have been audited that year), not as evidence the pattern is wrong.

## 3. Explanatory spatial regression

OLS -> Moran's I / LM diagnostics on residuals -> ML spatial lag and spatial error models. Three DVs (log1p-transformed district counts): overall project intensity, land_and_right_of_way, delay_time_overrun. See `spatial_regression_results.csv`.

**Diagnostics finding, itself substantive:** for n_projects and delay_time_overrun, the district-level covariates (distance to Kampala, population, dependency ratio, rurality, RAI, rainfall, elevation, land-tenure proxy) fully absorb the residual spatial autocorrelation -- Moran's I on OLS residuals drops to ~0.01-0.04 (not significant), and the spatial lag coefficient is essentially zero and non-significant. **Plain OLS is adequate for these two; the spatial models add nothing.** land_and_right_of_way keeps some residual dependence (Moran's I=0.068, LM-lag p=0.074) -- a spatial process not captured by the modelled covariates, worth a sentence in the discussion (candidate explanations: informal land-market spillovers between adjacent districts, or an omitted variable correlated across neighbours).

**Substantive coefficients** (standardised IVs, so magnitudes are comparable within a model):
- **delay_time_overrun** rises with distance to Kampala (remoteness) and with the mailo land-tenure proxy (both consistent with the outline's stated hypotheses), and falls with dependency ratio, across all three model specifications.
- **land_and_right_of_way**: tenure_mailo positive but modest and not consistently significant (p=0.16 in the spatial error model) -- weaker support than the raw ESDA crosstab suggested (Section 05).
- **n_projects** (overall): population and mailo tenure positive, dependency ratio negative, distance to Kampala positive.

Read as exploratory association on a small (n=135), zero-inflated cross-section -- not causal, and said so throughout rather than only in a disclaimer paragraph.

## 4. Random Forest + SHAP robustness check

Leave-one-out cross-validated R²: n_projects=0.276 (moderate), land=0.119 (weak), delay=0.057 (essentially no out-of-sample predictive signal). See `rf_feature_importance.csv`, `rf_shap_summary.csv`.

Mostly **confirms** the linear models: dependency_ratio and distance_to_kampala are the top two SHAP-ranked variables for n_projects, both negative/negative respectively, matching the spatial regression's signs. tenure_mailo positive for delay in both approaches.

**One real disagreement, reported rather than smoothed over:** SHAP's direction for distance_to_kampala on delay_time_overrun is *negative* (more remote associated with *fewer* delay disputes in the RF), the opposite sign from the linear models' positive, marginally-significant coefficient. Given the delay model's near-zero leave-one-out R² (0.057), the honest reading is that this relationship is not yet well-pinned-down by the available sample -- not that one model is right and the other wrong. This is exactly the kind of finding a small-n cross-sectional study should surface, not hide, and it argues for the validation/expert-interview step (Section 4.5 of the outline) before leaning on this specific coefficient in the paper's claims.

## What this does and doesn't establish

- Real, defensible evidence that dispute drivers cluster spatially (RQ1), with a specific and mappable geography per category (Section 2).
- Suggestive, not conclusive, evidence on *why* (RQ3) -- distance-to-Kampala and land tenure show up consistently across two independent methods for some categories, but the RF/SHAP check's low predictive power for delay and land means these associations should be presented as candidate explanations for expert-panel discussion (outline Section 4, "Validation"), not settled findings.
- Not yet done: space-time emerging hot-spot analysis (year-by-year animated maps) and geographically weighted regression (GWR) -- both listed as alternatives/extensions in the outline's Methods 4, not strictly required given the spatial lag/error diagnostics already showed the global models are adequate for 2 of 3 DVs.
