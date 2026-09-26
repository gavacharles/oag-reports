# -*- coding: utf-8 -*-
"""Build the full manuscript as a Word document."""
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = "/Users/charlesgava/Documents/Projects /OAG Reports/paper_geography_of_infrastructure_disputes"
OUT = "/Users/charlesgava/Downloads/Geography_of_Infrastructure_Disputes_DRAFT.docx"

d = docx.Document()

# ---------------- styles ----------------
normal = d.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(11)

for lvl, size, bold in [("Title", 16, True), ("Heading 1", 13, True), ("Heading 2", 12, True), ("Heading 3", 11, True)]:
    st = d.styles[lvl]
    st.font.name = "Times New Roman"
    st.font.size = Pt(size)
    st.font.bold = bold
    st.font.color.rgb = RGBColor(0, 0, 0)


def h1(text):
    d.add_heading(text, level=1)


def h2(text):
    d.add_heading(text, level=2)


def h3(text):
    d.add_heading(text, level=3)


def p(text, italic=False, bold=False, align=None, size=None):
    para = d.add_paragraph()
    run = para.add_run(text)
    run.italic = italic
    run.bold = bold
    if size:
        run.font.size = Pt(size)
    if align:
        para.alignment = align
    return para


def caption(text):
    para = d.add_paragraph()
    run = para.add_run(text)
    run.italic = True
    run.font.size = Pt(10)
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return para


def figure(path, width=6.3, cap=None):
    d.add_picture(path, width=Inches(width))
    d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if cap:
        caption(cap)


def add_table(headers, rows, widths=None):
    t = d.add_table(rows=1, cols=len(headers))
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, htext in enumerate(headers):
        hdr[i].text = str(htext)
        for para in hdr[i].paragraphs:
            for run in para.runs:
                run.bold = True
                run.font.size = Pt(9.5)
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)
            for para in cells[i].paragraphs:
                for run in para.runs:
                    run.font.size = Pt(9.5)
    return t


# ==================================================================
# TITLE PAGE
# ==================================================================
title = d.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title.add_run("The Geography of Infrastructure Disputes: A Spatio-Temporal Analysis "
                   "of Delay, Cost Overrun and Claims Drivers in Uganda's Public Projects, 2017–2025")
r.bold = True
r.font.size = Pt(15)

p("Charles Gavamukulya¹*, Clinton Aigbavboa¹", align=WD_ALIGN_PARAGRAPH.CENTER)
p("¹ Department of Construction Management and Quantity Surveying, University of Johannesburg, South Africa",
  italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=10)
p("*Corresponding author: gavacharles85@gmail.com", align=WD_ALIGN_PARAGRAPH.CENTER, size=10)
d.add_paragraph()

h2("Abstract")
p(
    "Construction dispute research treats projects as though they had no location. In Uganda, remoteness, "
    "terrain, land tenure, district administrative capacity and political attention all vary sharply across "
    "the country, yet no study has asked whether dispute drivers cluster in ways that call for regional "
    "management strategies. This paper text-mines Uganda's Office of the Auditor General (OAG) annual reports "
    "to Parliament (2017/18–2024/25), geocodes 238 of 283 identifiable public-infrastructure projects named "
    "in the resulting corpus, and tests whether eight audit-derived dispute-driver categories – delay, cost "
    "overrun, claims and disputes, land/right-of-way, contract management, delayed payments, governance and "
    "procurement irregularity – are spatially random or clustered across Uganda's 135 districts. Global "
    "Moran's I shows significant positive spatial autocorrelation for five of eight categories (strongest for "
    "delayed payments, I = 0.336, and land/right-of-way, I = 0.333; both p = 0.001), and Getis-Ord Gi* "
    "hot-spot analysis maps a Kampala–Wakiso–Mukono–Luwero corridor for land and delay disputes that is "
    "geographically distinct from separate cost-overrun clusters in the Hoima/Buliisa oil region and the "
    "Mbale/Manafwa/Kween Elgon highlands. A district-level spatial regression finds that dependency ratio, "
    "population and a historic land-tenure proxy (mailo versus customary versus freehold) explain most of the "
    "observed clustering – so much so that, for overall dispute intensity, a global model is statistically "
    "indistinguishable from a geographically weighted one (GWR bandwidth selected at 133 of 135 districts). For "
    "land/right-of-way disputes specifically, however, geographically weighted regression does improve on the "
    "global model (ΔAICc = 4.25) and reveals an east–west gradient in how distance from Kampala and mailo "
    "tenure relate to dispute intensity. The paper is explicit about what audit-derived text can and cannot "
    "support: OAG coverage is not a census of disputes, contractor and funding-source information is almost "
    "never stated (identified for under 5% of projects), and the project-extraction step is a careful reading "
    "exercise rather than a deterministic algorithm. Within those limits, the results indicate that Uganda's "
    "infrastructure dispute landscape is genuinely place-based, that land acquisition and delay disputes "
    "concentrate in the central mailo-tenure corridor around the capital for reasons that a purely institutional "
    "or contractual account would miss, and that a district-level spatial risk screen is a practical, "
    "low-cost addition to project appraisal in a data-scarce environment.",
)
p("Keywords: construction disputes; spatial analysis; Uganda; Getis-Ord Gi*; geographically weighted "
  "regression; land tenure; infrastructure governance; text mining", italic=True, size=10)
d.add_page_break()

# ==================================================================
# 1. INTRODUCTION
# ==================================================================
h1("1. Introduction")
p(
    "Dispute research in construction management is, with rare exceptions, geographically blind. Studies ask "
    "which factors predict delay, cost overrun or claims, but almost never ask where those factors bite hardest, "
    "or whether the answer to 'where' changes what the answer to 'why' should be. This is a real omission in "
    "Uganda's case. The country's infrastructure programme spans a coastal-forest west, a semi-arid northeast, "
    "a mountainous southwest and a densely populated central corridor around Kampala; district administrative "
    "capacity, land tenure regime, terrain and political attention vary as sharply across this geography as "
    "any of the contractual variables the literature usually tests. If dispute drivers are randomly scattered "
    "across this variation, a national procurement policy is the right instrument. If they cluster, a regional "
    "one might do more."
)
p(
    "This paper asks three questions. First, where do dispute drivers concentrate? Second, how has their "
    "pattern shifted over 2017–2025, a period spanning the Government of Uganda's 2021 decision to fold the "
    "Uganda National Roads Authority (UNRA) back into the Ministry of Works and Transport (MoWT) – a "
    "rationalisation policy formally implemented through repeal legislation in November 2024, after a "
    "multi-year transitional period [UNRA repeal reporting, 2024]? Third, which place-based factors explain "
    "the clustering that is found? The paper answers these questions using Uganda's Office of the Auditor "
    "General (OAG) annual reports to Parliament, text-mined and geocoded to the project level, and tested "
    "with the standard exploratory spatial data analysis (ESDA) and explanatory spatial regression toolkit "
    "used elsewhere in construction and transportation research but, to the authors' knowledge, never yet "
    "applied to a Sub-Saharan African infrastructure dispute corpus."
)

h1("2. Literature and Theory")
h2("2.1 Dispute-driver taxonomies")
p(
    "The dominant taxonomies of construction dispute causation are built from expert surveys, Delphi panels "
    "and litigation-record reviews concentrated in North America, the United Kingdom, Australia and parts of "
    "Asia (Naji, Mansour, & Gunduz, 2020). These taxonomies travel poorly: a category list built from Gulf "
    "Cooperation Council contract litigation, or from UK arbitration awards, encodes the institutional "
    "assumptions of those jurisdictions – functioning courts, published case law, standard-form contracts with "
    "settled interpretation – that do not hold in a market where formal arbitration is rare and land is held "
    "under four constitutionally distinct tenure regimes. A parallel and companion paper by the present authors "
    "(Gavamukulya & Aigbavboa, in preparation) applies text mining to this same OAG corpus to derive and "
    "validate the driver taxonomy used here; that paper's classifier and validation statistics are the source "
    "of the project-level driver labels this analysis builds on, and are only summarised, not re-derived, in "
    "Section 3 below."
)
h2("2.2 Spatial analysis in construction management")
p(
    "A small but growing literature applies geographic information systems (GIS) and spatial statistics to "
    "construction outcomes, almost entirely in a US roadway-programme setting. Yun, Ryu and Ham (2022) fuse "
    "machine learning with GIS to map socio-geographic correlates of cost-overrun occurrence across US state "
    "roadway projects, finding that management district, commuting behaviour and local population "
    "characteristics predict overrun risk independently of project-level contract variables. Shamshiri, Ryu, "
    "Shahandashti and colleagues (2025) extend this to schedule-overrun occurrence using a comparable "
    "geospatial machine-learning pipeline on Florida roadway data. Both studies establish that where a project "
    "sits is informative net of what it is – the premise this paper tests for Uganda – but neither uses formal "
    "spatial-autocorrelation statistics (Moran's I, Getis-Ord Gi*) or a developing-country, audit-derived data "
    "source; both work from complete administrative project registers, a condition this paper's data source "
    "explicitly does not meet (Section 3)."
)
h2("2.3 Institutional theory and subnational state capacity")
p(
    "Scott's (2001) three-pillar model of institutions – regulative, normative and cultural-cognitive – "
    "provides the framework for interpreting what a spatial pattern in dispute-driver reporting indexes about "
    "the state of subnational governance. In much of Sub-Saharan Africa, the regulative pillar is not uniform "
    "across territory: colonial and postcolonial administration built what Mamdani (1996) calls 'decentralised "
    "despotism' – a bifurcated state in which urban, formally governed space coexists with rural areas "
    "administered through customary authority structures with distinct rules for land, dispute resolution and "
    "accountability. Uganda's land law gives this theoretical claim direct empirical content: the 1995 "
    "Constitution (Article 237) and the Land Act 1998 recognise four tenure types – mailo, freehold, leasehold "
    "and customary – with materially different compensation, consultation and dispute-resolution pathways. "
    "Mailo tenure, concentrated in the historic Buganda Kingdom districts surrounding Kampala, creates a "
    "landlord–tenant (bibanja) structure that Transaction Cost Economics (Williamson, 1985) would predict is "
    "more hold-up-prone than customary tenure's community-consent process, because mailo separates the "
    "registered titleholder from the occupant with a use right, multiplying the parties whose consent a "
    "project needs. If this account is right, land and delay disputes should concentrate disproportionately in "
    "mailo-tenure districts independent of their distance from the capital or their population size – a "
    "testable, falsifiable prediction this paper's regression is built to check (Section 4.3)."
)
h2("2.4 The gap and hypotheses")
p(
    "No study has spatially modelled construction dispute drivers in Sub-Saharan Africa using formal ESDA and "
    "explanatory spatial regression. This paper closes that gap and tests three hypotheses drawn from the "
    "theory above: (H1) districts with higher Rural Access Index scores (less remote) show lower delay-dispute "
    "intensity, net of population and tenure; (H2) mailo-tenure districts show elevated land/right-of-way "
    "dispute intensity relative to customary-tenure districts, net of distance and population; (H3) the "
    "spatial pattern of dispute drivers is not uniform across the country – i.e. a geographically weighted "
    "model improves materially on a global one for at least one driver category. Sections 4–6 test each in "
    "turn."
)

# ==================================================================
# 3. DATA
# ==================================================================
h1("3. Data")
h2("3.1 Primary source: the OAG corpus")
p(
    "The primary source is Uganda's Office of the Auditor General annual reports to Parliament, financial "
    "years 2017/18–2024/25 (eight reports; the 2020 file in the OAG archive is an internal strategic-planning "
    "document rather than an audit report, and contributes negligible substantive content, a point that "
    "matters for the space-time analysis in Section 5.3). Full text was extracted from all eight cached PDFs "
    "(164–784 pages each); an earlier extraction pass had capped extraction at 120 pages per report, silently "
    "discarding 70–85% of each report's content, which explains why a first-pass classifier returned zero "
    "sentences for the cost-overrun category despite the term appearing routinely once the cap was removed. "
    "Document front matter (tables of contents, glossaries, table/figure captions) was stripped before "
    "sentence splitting after a 12.8% contamination rate was measured and verified by spot-check in the "
    "original, capped corpus. The resulting sentence corpus was screened for infrastructure relevance and "
    "classified into eight dispute-driver categories – delay/time overrun, cost overrun, claims and disputes, "
    "land/right-of-way, contract management, delayed payments, governance and oversight, and procurement "
    "irregularity – using the multi-label weak-supervision classifier developed and validated in the companion "
    "paper (Gavamukulya & Aigbavboa, in preparation). A construction-relevance filter, requiring a specific "
    "infrastructure noun, a named infrastructure agency, or construction-contract-specific terminology, "
    "removed generic public-sector content (drug procurement, academic staffing, research-programme findings) "
    "that an earlier, more permissive filter had let through; 792 of 1,762 driver-labelled sentences (44.9%) "
    "pass this filter and form the analysis corpus for the present paper."
)

h2("3.2 Project identification and geocoding")
p(
    "Named, geocodable projects cannot be extracted from OAG narrative by keyword pattern alone: a preliminary "
    "regular-expression pass extracted 'Uganda' as a road-project name because the phrase 'Uganda Road Fund' "
    "(an institution) matched the same surface pattern as a genuine project name. Project identification was "
    "therefore done by direct reading of every sentence in the 792-sentence analysis corpus against the "
    "question 'does this sentence name a specific, identifiable infrastructure project, as opposed to an "
    "institution or a generic reference?' Only 217 sentences (27.4%) do; a further 692 project mentions "
    "recovered by tracing these sentences back to their full, untruncated report context canonicalise to 283 "
    "distinct projects. Table 1 summarises the extraction and geocoding funnel."
)

add_table(
    ["Stage", "n", "% of prior stage"],
    [
        ["Driver-labelled sentences (full-text re-extraction, 8 reports)", "1,762", "—"],
        ["Construction-relevant (infrastructure noun / agency / contract term)", "792", "44.9%"],
        ["Sentences naming a specific, identifiable project", "217", "27.4%"],
        ["Canonical distinct projects (after deduplication across mentions/years)", "283", "—"],
        ["Successfully geocoded (OpenStreetMap Nominatim)", "238", "84.1%"],
        ["  — point-precision facilities", "212", "—"],
        ["  — line-geometry road/transmission corridors (straight-line endpoint proxy)", "46", "—"],
    ],
)
caption("Table 1. Project extraction and geocoding funnel.")

p(
    "Geocoding used OpenStreetMap Nominatim, with point facilities (hospitals, schools, dams, airports, water "
    "schemes) geocoded to their named place, and road or transmission-line projects geocoded as a straight "
    "line between their two named endpoints – an explicit proxy for, not a measurement of, the true alignment, "
    "since no digitised MoWT project-alignment layer was accessible for this study. Manual verification caught "
    "two classes of geocoding error worth reporting because they recur in any toponym-based pipeline applied "
    "to Uganda: same-named-place confusion (Nominatim's first match for 'Kabaale International Airport' was a "
    "village in Rakai District, roughly 500 km from the actual airport site under construction near Hoima) and "
    "no-match fallback (the Isimba Hydropower Plant has no correctly sited OpenStreetMap node; its coordinate "
    "is a district centroid, flagged as such in the released data rather than silently accepted). District "
    "assignment used a spatial join against current OCHA Common Operational Dataset – Administrative Boundaries "
    "(135 districts, valid as of 2020-08-24), cross-checked against the reading-extracted district recorded "
    "during project identification; the two agree for 172 of 253 projects with both values (68%), and the "
    "reading-extracted value is preferred where they disagree, since disagreement traces almost entirely to "
    "the same-named-place geocoding failure mode above rather than to an error in reading."
)

h2("3.3 Explanatory covariate layers")
p(
    "District- and project-level covariates were assembled from public sources, all downloaded for this study "
    "(Table 2); no district- or parcel-level land-tenure GIS layer exists publicly for Uganda, so tenure is "
    "coded as a sub-region-based proxy from the documented geographic concentration of mailo tenure in the "
    "historic Buganda Kingdom districts and native freehold in the Ankole and Kigezi sub-regions (Land Act "
    "1998; Constitution, Art. 237), with all other districts coded customary, the nationally dominant regime. "
    "Contractor origin and funding source were attempted with the same reading-based approach used for project "
    "identification, but coverage is very low – a named contractor is stated for 12 of 283 projects (4.2%) "
    "and a classifiable funding category for 8 (2.8%) – so these variables are discussed qualitatively "
    "(Section 6.4) rather than used as regression covariates."
)

add_table(
    ["Covariate", "Source", "Granularity"],
    [
        ["Population, 2022 projection", "OCHA COD-PS", "District"],
        ["Dependency ratio; rural population %", "HeiGIT / Humanitarian OpenStreetMap Team risk-assessment layers", "District"],
        ["Rural Access Index (% of rural population within 2km of an all-season road)", "HeiGIT/HOT; World Bank RAI methodology", "District"],
        ["Elevation", "SRTM, via Open-Elevation API", "Point / district centroid"],
        ["Mean annual rainfall (2018–2022 climatology)", "CHIRPS v2.0, UCSB Climate Hazards Center", "Point / district centroid"],
        ["Distance to Kampala", "Computed (haversine)", "Point / district centroid"],
        ["Land tenure (mailo / freehold / customary)", "Documented sub-region proxy (Constitution Art. 237; Land Act 1998)", "District"],
        ["Election-year flag", "Electoral Commission polling dates", "Project-year"],
    ],
)
caption("Table 2. Explanatory covariate layers and sources.")

# ==================================================================
# 4. METHODS
# ==================================================================
h1("4. Methods")
h2("4.1 Exploratory spatial data analysis")
p(
    "Global spatial autocorrelation was tested with Moran's I (Queen contiguity weights, row-standardised, "
    "999 conditional permutations) on district-level project counts, run once for total project intensity and "
    "once per driver category. Local hot and cold spots were identified with Getis-Ord Gi* on the same weights "
    "matrix, with p-values false-discovery-rate corrected across the 135 simultaneous district-level tests "
    "within each category. Both statistics were computed on counts of distinct geocoded projects per district "
    "(not sentence counts), since a single project may generate several audit sentences across years and "
    "categories, and the unit of spatial analysis should be the project, not the mention."
)
h2("4.2 Space-time analysis")
p(
    "A year × district panel (2017–2025) was built from each project's audited years, and Getis-Ord Gi* was "
    "recomputed per year on the resulting annual counts (pooled across driver categories, the only "
    "specification with enough non-zero district-years to be worth mapping at all at annual resolution). A "
    "Mann-Kendall trend test was applied to each district's resulting nine-year Gi* z-score series to classify "
    "districts as intensifying, diminishing or showing no detectable trend, following the logic of ESRI's "
    "emerging hot-spot analysis. The nine annual maps are rendered as a supplementary animated GIF."
)
h2("4.3 Explanatory modelling")
p(
    "District-level explanatory models were fitted for three outcomes – total project intensity, "
    "land/right-of-way count, and delay/time-overrun count, each log(1+x)-transformed – against the "
    "standardised covariates in Table 2 (excluding contractor/funding, per Section 3.3) plus mailo and "
    "freehold tenure dummies (customary as reference). For each outcome, an ordinary least squares (OLS) "
    "model was fitted first, followed by Lagrange Multiplier diagnostics for spatial dependence and, "
    "regardless of the diagnostic result, both a maximum-likelihood spatial lag and a maximum-likelihood "
    "spatial error model (Queen contiguity weights), so that the diagnostic outcome itself – whether the "
    "spatial terms add anything – is reported rather than assumed. Geographically weighted regression (GWR; "
    "adaptive bisquare kernel, bandwidth selected by golden-section AICc minimisation) was fitted for the "
    "same three outcomes to test whether the global coefficients are stable across the country or vary "
    "locally; GWR is preferred over the global model only where its AICc is at least three points lower, the "
    "conventional threshold. As a non-parametric robustness check that does not assume linearity or a "
    "particular functional form, a Random Forest (500 trees, max depth 4, minimum leaf size 5) was fitted "
    "for each outcome on the same covariates, with variable importance read from mean absolute SHAP values "
    "and out-of-sample performance assessed by leave-one-out cross-validation, appropriate given the small "
    "(n = 135) sample."
)
h2("4.4 Scope note on validation")
p(
    "The explanatory results in Sections 5.4–5.6 are reported as candidate, testable associations rather "
    "than settled findings. Independent validation of the spatial clusters and candidate explanations against "
    "practitioner or expert judgement is identified as a priority extension in Section 7.2 but is not carried "
    "out in the present paper."
)

# ==================================================================
# 5. RESULTS
# ==================================================================
h1("5. Results")
h2("5.1 National distribution")
p(
    "Figure 1 maps all 238 geocoded projects, coloured by primary dispute driver. The distribution is not "
    "uniform: projects cluster around Kampala and the road/transmission corridors radiating from it, with a "
    "second concentration of energy-sector projects (dams, transmission lines) in the west along the Nile and "
    "Lake Albert, and a thinner, more dispersed scatter of health and education facilities across the north "
    "and east – consistent with those regions' infrastructure programme being smaller-footprint, "
    "district-level social infrastructure rather than the large linear and energy projects concentrated "
    "closer to the capital."
)
figure(f"{BASE}/07_visualization/figure1_national_distribution.png", width=6.3,
       cap="Figure 1. National distribution of 238 geocoded infrastructure-dispute projects, 2017–2025.")

h2("5.2 Global spatial autocorrelation and hot spots")
p(
    "Global Moran's I is significant (p < 0.01, 999 permutations) for five of eight driver categories: "
    "delayed payments (I = 0.336), land/right-of-way (I = 0.333), procurement irregularity (I = 0.226), "
    "contract management (I = 0.189) and delay/time overrun (I = 0.165). Cost overrun, claims and disputes, "
    "and governance/oversight are not significant, consistent with their small number of non-zero districts "
    "(6, 14 and 14 respectively) – a genuine statistical-power limitation given OAG audit coverage, reported "
    "rather than allowed to imply a null spatial pattern. Dispute drivers, in short, are not spatially random."
)
add_table(
    ["Driver category", "Moran's I", "p (sim.)", "Non-zero districts (of 135)"],
    [
        ["Delayed payments", "0.336", "0.001", "21"],
        ["Land / right-of-way", "0.333", "0.001", "22"],
        ["Procurement irregularity", "0.226", "0.002", "35"],
        ["Contract management", "0.189", "0.002", "29"],
        ["Delay / time overrun", "0.165", "0.002", "51"],
        ["Governance & oversight", "0.060", "0.112", "14"],
        ["Cost overrun", "0.019", "0.266", "6"],
        ["Claims & disputes", "0.009", "0.292", "14"],
        ["Overall project intensity", "0.304", "0.001", "90"],
    ],
)
caption("Table 3. Global Moran's I by driver category (Queen contiguity, 999 permutations).")

p(
    "Local Getis-Ord Gi* hot spots (Figure 2) locate this clustering precisely. Land/right-of-way and delay "
    "disputes cluster heavily in a contiguous Kampala–Wakiso–Mukono–Luwero corridor. Cost overrun clusters "
    "separately in two places with no geographic overlap with the land/delay corridor: the Hoima/Buliisa oil "
    "region in the west, and the Mbale/Manafwa/Kween Elgon highlands in the east. Delayed payments shows a "
    "sharp Kampala–Wakiso spike plus an isolated Kapchorwa outlier. Some zero-count districts (e.g. Mukono for "
    "claims and disputes) appear as significant hot spots; this is expected Gi* behaviour, since the statistic "
    "reflects the neighbourhood-weighted local mean rather than the focal district's own count alone, and is "
    "read here as a district embedded within a hot region rather than as an error."
)
figure(f"{BASE}/07_visualization/figure2_hotspot_maps_all8.png", width=6.5,
       cap="Figure 2. District-level Getis-Ord Gi* hot/cold spots, all eight driver categories "
           "(FDR-corrected, Queen contiguity).")

h2("5.3 Space-time pattern")
p(
    "The animated year-by-year Gi* sequence (Supplementary Material S1) shows the pooled hot-spot region "
    "contracting and shifting within the Central corridor across 2018–2025, from a broader mid-western "
    "extent in 2019 to a tighter Kampala-centred cluster by 2023. 2017 and 2020 have no audit-year references "
    "in the corpus (the 2020 OAG file is a strategic-planning document, not an audit report; see Section 3.1) "
    "and are shown as explicit no-data frames rather than omitted. A Mann-Kendall trend test on each "
    "district's nine-year Gi* series found a significant trend in only one of 135 districts, which is read as "
    "a power limitation of the sparse annual panel (as few as three non-zero districts nationally in some "
    "years) rather than evidence of genuine year-on-year stability."
)

h2("5.4 Explanatory spatial regression")
p(
    "Table 4 reports standardised OLS coefficients for the three modelled outcomes (spatial lag and error "
    "models return materially the same coefficients and are omitted from the table for brevity; full results "
    "for all three specifications are in the replication data). For overall project intensity, population "
    "(β = 0.29, p < 0.001), dependency ratio (β = −0.24, p < 0.001) and mailo tenure (β = 0.18, p = 0.013) are "
    "the only variables clearing conventional significance. Crucially, Moran's I on the OLS residuals falls "
    "to 0.009 (not significant) and both Lagrange Multiplier tests are non-significant (p = 0.87–0.99): the "
    "covariates fully absorb the spatial clustering documented in Section 5.2, and the spatial lag term itself "
    "is statistically indistinguishable from zero. For land/right-of-way, population is again significant "
    "(β = 0.08, p = 0.017) but dependency ratio only reaches significance in the OLS specification (β = −0.07, "
    "p = 0.029); residual spatial dependence is not fully absorbed here (Moran's I on residuals = 0.068, "
    "LM-lag p = 0.074), a result taken up in Section 5.5. For delay/time overrun, dependency ratio (β = −0.13, "
    "p = 0.002) and mailo tenure (β = 0.15, p = 0.003) are robust across every specification; distance to "
    "Kampala is positive (β ≈ 0.09–0.10) but only marginally significant (p = 0.08–0.10), and rainfall reaches "
    "conventional significance only in the lag/error specifications (β ≈ 0.09, p ≈ 0.05)."
)
add_table(
    ["Variable", "Project intensity β (p)", "Land/right-of-way β (p)", "Delay/time overrun β (p)"],
    [
        ["Distance to Kampala", "0.123 (0.121)", "−0.052 (0.262)", "0.093 (0.098)"],
        ["Elevation", "0.014 (0.821)", "−0.038 (0.262)", "0.022 (0.621)"],
        ["Mean annual rainfall", "0.078 (0.224)", "0.016 (0.649)", "0.087 (0.056)"],
        ["Log population", "0.293 (<0.001)", "0.080 (0.017)", "0.092 (0.039)"],
        ["Dependency ratio", "−0.238 (<0.001)", "−0.069 (0.029)", "−0.131 (0.002)"],
        ["Rural population %", "0.061 (0.377)", "−0.009 (0.801)", "0.049 (0.321)"],
        ["Rural Access Index", "0.031 (0.577)", "0.000 (0.991)", "−0.006 (0.869)"],
        ["Mailo tenure", "0.176 (0.013)", "0.050 (0.196)", "0.147 (0.004)"],
        ["Freehold tenure", "−0.045 (0.492)", "−0.014 (0.690)", "−0.047 (0.316)"],
        ["Moran's I, OLS residuals", "0.009 (n.s.)", "0.068 (p=0.074, LM-lag)", "0.038 (n.s.)"],
    ],
)
caption("Table 4. Standardised OLS coefficients (p-values in parentheses), 135 districts. "
        "Spatial lag/error coefficients and standard errors for all three outcomes are in the replication data.")

h2("5.5 Geographically weighted regression")
p(
    "For overall project intensity, GWR selects a bandwidth of 133 of 135 districts — effectively the whole "
    "country — and its AICc (253.5) is higher than the global model's (251.0): GWR is not preferred, and the "
    "relationship between the covariates and overall dispute intensity is statistically indistinguishable "
    "from spatially constant. For land/right-of-way, by contrast, GWR selects a tighter 91-district bandwidth "
    "and its AICc (82.8) beats the global model's (87.0) by 4.25 points, exceeding the conventional "
    "threshold for preferring the local model. Figure 3 maps the resulting local coefficients: distance to "
    "Kampala and mailo tenure both show a marked east–west gradient in their relationship with land-dispute "
    "intensity, with the mailo effect strongest and most reliably positive in the corridor's eastern and "
    "central districts and attenuating, or reversing sign but losing significance, further west. The local "
    "freehold-tenure coefficient is numerically unstable (local β ranging from −7.6 to +2.8 across districts) "
    "because freehold districts are themselves geographically clustered in the far southwest, leaving many "
    "local regression windows elsewhere with few or no freehold neighbours to estimate from; this instability "
    "is shown by hatching in Figure 3 rather than smoothed over or omitted."
)
figure(f"{BASE}/08_gwr/figure3_gwr_land_coefficients.png", width=6.5,
       cap="Figure 3. GWR local coefficients for land/right-of-way dispute intensity "
           "(hatched = not significant at that location).")

h2("5.6 Random Forest / SHAP robustness check")
p(
    "Leave-one-out cross-validated R² is 0.276 for overall project intensity, 0.119 for land/right-of-way and "
    "0.057 for delay/time overrun – the last essentially indistinguishable from a model with no predictive "
    "power out of sample, given the small district-level n. Where the model has any signal at all, it mostly "
    "confirms the linear results: dependency ratio and distance to Kampala are the two highest-SHAP-ranked "
    "variables for overall intensity, with the same negative and negative sign as the linear models. One "
    "disagreement is reported rather than resolved by picking a side: SHAP's direction for distance to Kampala "
    "on delay/time overrun is negative (more remote associated with fewer delay disputes in the Random "
    "Forest), the opposite sign from the linear models' positive, marginally significant coefficient. Given "
    "that model's near-zero leave-one-out R², the honest reading is that this specific relationship is not "
    "yet well identified by the available sample, not that either method is right."
)

# ==================================================================
# 6. DISCUSSION
# ==================================================================
d.add_page_break()
h1("6. Discussion")
h2("6.1 A place-based, not a purely contractual, dispute landscape")
p(
    "The central finding is that Uganda's audit-visible infrastructure disputes are not evenly spread across "
    "the country's institutional and physical variation: they cluster, and different driver categories "
    "cluster in different places for reasons that map onto real economic geography rather than administrative "
    "noise. Cost overrun's two disconnected hot spots – the Hoima/Buliisa oil region and the Mbale/Manafwa/"
    "Kween highlands – sit either side of the country's two most distinctive terrain-and-investment contexts "
    "(the Albertine oil development corridor, and steep highland road construction), a pattern a purely "
    "contractual account (poor estimating, weak supervision) would have no reason to predict but a "
    "geography-aware one would."
)
h2("6.2 Land tenure as a transaction-cost variable, read through Mamdani")
p(
    "H2 – that mailo tenure predicts elevated land-dispute intensity net of population and distance – is "
    "supported in the district-level regression (β = 0.18, p = 0.013 for overall intensity; β = 0.15, "
    "p = 0.004 for delay) and, more precisely, in the GWR result: the mailo effect on land disputes is not "
    "uniform but strongest in the corridor's eastern and central reach. Read through Williamson's (1985) "
    "transaction-cost lens, this is consistent with mailo's landlord–tenant structure multiplying the parties "
    "whose consent a compulsory-acquisition process needs, each a potential hold-up point; read through "
    "Mamdani's (1996) account of bifurcated colonial and postcolonial governance, it is consistent with mailo "
    "areas sitting inside the 'urban', formally-titled part of that bifurcation, where disputes are more "
    "likely to be formally registered, escalated and ultimately audited in the first place – a genuine "
    "identification problem this paper cannot resolve with the available data, and returns to in Section 7.1. "
    "Both readings agree that land tenure regime, not merely distance or population, is doing real "
    "explanatory work, which is itself the more defensible and portable claim."
)
h2("6.3 When a global model is enough, and when it isn't")
p(
    "The GWR results (Section 5.5) sharpen H3 rather than confirming it wholesale: spatial non-stationarity "
    "is real for land/right-of-way but not for overall project intensity or, on this evidence, for delay. "
    "This matters for how the paper's findings should be used. A single national coefficient for 'how "
    "remoteness relates to dispute intensity' is an adequate summary for overall audit activity, but a single "
    "national coefficient for 'how land tenure relates to land disputes' is not — the same tenure regime "
    "appears to operate differently in the corridor's east than its west, plausibly reflecting the interaction "
    "of mailo tenure with more specific local factors (proximity to major named projects, particular "
    "compensation disputes) that a district-level model averages over. This is precisely the argument for "
    "reporting both a global and a local model rather than either alone."
)
h2("6.4 Procurement risk allocation, dispute-board strategy, and what the data cannot say")
p(
    "For MoWT and the Ministry of Local Government, the practical implication of Section 5.2's hot-spot map "
    "is that risk-allocation and dispute-board strategy could reasonably be differentiated by corridor rather "
    "than applied uniformly: right-of-way and delay risk concentrated in the Central mailo corridor calls for "
    "front-loaded land compensation and independent valuation capacity specifically there, while the two "
    "cost-overrun clusters call for a different response — technical-design and quantity-verification capacity "
    "in the Albertine oil corridor, and terrain-appropriate estimating standards in the Elgon highlands. The "
    "data cannot say whether contractor origin or financing source (GoU versus donor) moderates any of this: "
    "coverage for both variables is under 5% of projects (Section 3.3), because OAG audit narrative almost "
    "never names a contracting firm or a specific funder outside a handful of flagship projects (Entebbe "
    "International Airport's China EXIM Bank financing and China Communications Construction Company contract "
    "being the clearest named example in the corpus). This is a genuine data-limitations finding, not a null "
    "result to be explained away, and it means the paper's contribution is about where disputes concentrate "
    "and why in a place-based sense, not about who is contracted to deliver them."
)

# ==================================================================
# 7. IMPLICATIONS AND CONCLUSION
# ==================================================================
d.add_page_break()
h1("7. Implications and Conclusion")
h2("7.1 A spatial risk screen for project appraisal")
p(
    "The practical output of this paper is a district-level spatial risk screen: at appraisal stage, a "
    "project's district can be checked against the hot-spot classifications in Figure 2 and the tenure/"
    "distance profile in Table 4 to flag, before contract award, whether it sits in a corridor with an "
    "elevated historical concentration of land, delay or cost-overrun disputes, and to route it toward the "
    "correspondingly differentiated response described in Section 6.4. This is a low-cost complement to, not "
    "a replacement for, project-specific risk assessment, and is only as good as the audit-derived pattern "
    "underlying it (Section 7.2)."
)
h2("7.2 Limitations")
p(
    "Several limitations bear directly on how these results should be used, not only cited. Audit coverage is "
    "not a census of disputes: the OAG does not audit every project every year, so a district's absence from "
    "a hot-spot map may reflect absence of audit attention rather than absence of dispute, a distinction "
    "Section 5.2 flags explicitly for zero-count districts embedded in hot regions. Geocoding carries measured "
    "error (Section 3.2): 45 of 283 projects could not be geocoded at all, and precision for the rest ranges "
    "from point-exact to district-centroid; road and transmission-line geometries are straight-line proxies, "
    "not true alignments. Project identification is a careful reading exercise, not a deterministic algorithm "
    "or a trained named-entity-recognition model — auditable, since every project traces to a specific source "
    "sentence, but not mechanically reproducible by re-running a script, and a second independent read of the "
    "lower-confidence extractions would let a future version of this work report a genuine inter-rater "
    "reliability statistic. The land-tenure variable is a documented regional proxy, not a parcel- or "
    "district-level GIS layer, because no such dataset exists publicly for Uganda. The district-level "
    "regression (n = 135) is small and its outcome variables are zero-inflated counts modelled after a log "
    "transform, a specification chosen for comparability with the standard spatial-econometrics toolkit "
    "(Section 4.3) rather than because it is the ideal model for sparse count data; a negative-binomial or "
    "zero-inflated specification is a natural robustness extension. Finally, the disagreement between the "
    "linear and Random Forest models on distance-to-Kampala's effect on delay (Section 5.6) is left "
    "unresolved rather than adjudicated, because resolving it responsibly requires either more data or "
    "independent expert judgement, neither of which this paper supplies."
)
h2("7.3 Future work")
p(
    "Three extensions follow directly from the limitations above. First, cross-source validation: triangulating "
    "the OAG-derived pattern against Auditor General exception reports, PPDA administrative review decisions, "
    "and, where accessible, court records, would test whether the audit-visible pattern documented here matches "
    "the pattern in formally litigated disputes. Second, true road and transmission-line alignments from MoWT "
    "GIS data or OpenStreetMap way-matching would replace this paper's straight-line proxies. Third, "
    "independent practitioner or expert review of the spatial clusters and candidate explanations in Section 6 "
    "would test whether the associations reported here hold up to domain judgement, particularly for the "
    "unresolved distance-to-Kampala result and the GWR-identified east–west gradient in the mailo-tenure "
    "effect."
)
h2("7.4 Conclusion")
p(
    "Construction dispute drivers in Uganda's public infrastructure programme are not spatially random. Global "
    "Moran's I is significant for five of eight audit-derived driver categories, Getis-Ord Gi* maps distinct, "
    "theoretically interpretable hot-spot geographies for land/delay disputes versus cost overrun, and a "
    "district-level regression shows that population, dependency ratio and a historic land-tenure regime "
    "explain most — though, for land disputes specifically, not all — of that clustering. Geographically "
    "weighted regression shows this explanatory structure itself varies across the country for land disputes "
    "but not for overall dispute intensity, a genuinely mixed and reportable result rather than a uniformly "
    "clean one. Within the real limits of an audit-derived, non-census data source, the evidence supports "
    "treating Uganda's infrastructure dispute landscape as place-based, and treating the historic mailo/"
    "customary/freehold tenure boundary running through the central corridor as a variable procurement policy "
    "should take seriously alongside — not instead of — the standard contractual and institutional factors "
    "the literature already tests."
)

h1("Supplementary Material")
p(
    "S1: animated year-by-year Getis-Ord Gi* hot-spot maps, 2017–2025 (GIF). S2: full analysis code and "
    "pipeline (corpus extraction, geocoding, covariate assembly, ESDA, spatial and geographically weighted "
    "regression, Random Forest/SHAP). S3: the geocoded project-level dataset, with geocoding-precision and "
    "extraction-confidence fields retained for downstream users. All three are maintained in the paper's "
    "version-controlled repository; a public release will accompany journal submission."
)

print("Discussion + conclusion done")
d.save(OUT)

# ==================================================================
# REFERENCES
# ==================================================================
d.add_page_break()
h1("References")

REFS = [
    "Constitution of the Republic of Uganda, 1995, Article 237 (land ownership).",
    "Gavamukulya, C., & Aigbavboa, C. (in preparation). Text mining Uganda's Office of the Auditor General "
    "reports for infrastructure dispute drivers, 2017-2025.",
    "Land Act, 1998 (Cap. 227). Laws of Uganda.",
    "Mamdani, M. (1996). Citizen and Subject: Contemporary Africa and the Legacy of Late Colonialism. "
    "Princeton University Press.",
    "Monitor. (2024, November 6). UNRA to cease after Museveni signs Repeal Bill. Daily Monitor (Uganda).",
    "Naji, K. K., Mansour, M. M., & Gunduz, M. (2020). Methods for modeling and evaluating construction "
    "disputes: A critical review. IEEE Access, 8, 45641-45652.",
    "Scott, W. R. (2001). Institutions and Organizations. Sage Publications.",
    "Shamshiri, A., Ryu, K. R., Shahandashti, M., et al. (2025). Investigating the impacts of socioeconomic "
    "conditions on schedule overrun occurrences in roadway projects: the fusion of machine learning and "
    "geospatial mapping. Innovative Infrastructure Solutions.",
    "Uganda Broadcasting Corporation. (2024, November 7). Parliament dissolves UNRA and Road Fund, integrates "
    "operations into Ministry of Works and Transport.",
    "Williamson, O. E. (1985). The Economic Institutions of Capitalism: Firms, Markets, Relational "
    "Contracting. Free Press.",
    "Yun, J., Ryu, K. R., & Ham, S. P. (2022). Spatial analysis leveraging machine learning and GIS of "
    "socio-geographic factors affecting cost overrun occurrence in roadway projects. Automation in "
    "Construction, 133, 104007.",
]
for ref in REFS:
    para = d.add_paragraph(ref)
    para.paragraph_format.left_indent = Inches(0.3)
    para.paragraph_format.first_line_indent = Inches(-0.3)
    for run in para.runs:
        run.font.size = Pt(10.5)

print("References done. Final save.")
d.save(OUT)
print(f"\nManuscript saved -> {OUT}")
