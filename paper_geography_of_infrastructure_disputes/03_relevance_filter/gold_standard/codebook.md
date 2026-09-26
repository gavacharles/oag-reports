# Codebook for Gold-Standard Validation of the OAG Driver Classifier

## Purpose and scope

This codebook governs independent (AI-assisted, single-rater) coding of a
stratified sample of 362 sentences drawn from the OAG infrastructure
sentence corpus (2017-2025, 792 sentences total). Each sentence is judged
against 8 categories. A sentence may receive **zero, one, or multiple**
labels — this is a multi-label task, not a forced choice.

The categories below are anchored on the substantive audit-finding concept
each is meant to capture, using the classifier's own regex terms
(`DRIVER_PATTERNS` in `02_full_reextraction/oag_full_reextraction.py`) only
as a starting reference for vocabulary — not as the coding rule itself. The
question asked for each category is: **"does this sentence report or assert
this kind of problem/fact, in substance, about an infrastructure project?"**
Surface keyword matches without substantive meaning (e.g. "supervision" used
in an unrelated administrative sense) should NOT be coded positive.

Coding is done blind to the classifier's own labels (`all_drivers`), working
only from `sample_blinded.csv` (sample_id, year, sentence).

---

## 1. delay_time_overrun
**Concept:** The project's physical/schedule timeline has slipped — works
are behind schedule, incomplete, stalled, or suspended relative to the
planned completion date. This is about TIME, not money.

**Example anchor phrases:** "extension of time", "behind schedule", "delayed
completion", "works were halted", "not yet completed", "abandoned works".

**Watch for:** A sentence citing a specific overdue percentage of physical
progress, or an EOT (extension of time) request/grant, counts even without
the literal word "delay". Do not code positive merely because the sentence
mentions a project age or a completion date in passing with no overrun
implied.

## 2. cost_overrun
**Concept:** The project's cost has exceeded budget/contract sum — a
financial/budgetary overrun, not a payment-timing issue (see
delayed_payments) and not a compensation claim (see claims_and_disputes).

**Example anchor phrases:** "cost overrun", "budget overrun/variance",
"cost/price escalation", "supplementary budget required", "additional cost
over and above the contract sum".

**Watch for:** A sentence merely stating a contract's value (a neutral
fact) is NOT a cost overrun. It must assert that actual/expected cost
exceeded what was budgeted or contracted.

## 3. claims_and_disputes
**Concept:** A live or unresolved legal/contractual dispute — litigation,
arbitration, contested claims, liquidated damages, breach of contract, or
a contingent liability arising from such a dispute.

**Example anchor phrases:** "unresolved claim", "arbitration", "breach of
contract", "liquidated damages", "sued/court case", "contingent
liability/nugatory expenditure".

**Watch for:** Nugatory expenditure or a contingent liability counts only
when tied to a dispute/claim context, not any wasteful spending. A simple
statement that a contractor was terminated is contract_management unless a
subsequent claim/legal action is also described.

## 4. land_and_right_of_way
**Concept:** Problems acquiring land or right-of-way needed for the
project — compensation of project-affected persons (PAPs), resettlement,
encroachment, or way-leave disputes that impede construction.

**Example anchor phrases:** "land acquisition", "right of way / way-leave",
"resettlement", "compensation of project-affected persons", "encroachment".

**Watch for:** A generic mention of "land" with no acquisition/compensation/
encroachment problem does not qualify. The sentence must link land/way-leave
issues to project delay, dispute, or unresolved compensation.

## 5. contract_management
**Concept:** Problems in how a contract was administered/supervised after
award — poor workmanship, substandard/non-compliant works, inadequate
supervision, defects, or general mismanagement of contract execution. This
is the "quality/administration" category, distinct from procurement
(pre-award) issues.

**Example anchor phrases:** "poor workmanship", "substandard/shoddy works",
"defects", "inadequate supervision", "non-compliance with contract terms".

**Watch for:** This category is prone to over-triggering because
"supervision" and "defect" appear in many administrative contexts (e.g.
"supervision of staff", "internal control deficiency/defect in a system").
Code positive only when the supervision/defect/workmanship problem is about
a specific construction contract's execution, not a generic
governance/internal-control statement (see governance_and_controls) or an
unrelated administrative process.

## 6. delayed_payments
**Concept:** Money owed to a contractor/supplier has not been paid on time
— arrears, unpaid certificates, withheld payments. This is a
CASH-FLOW/payment-timing problem, distinct from cost_overrun (total cost
exceeding budget).

**Example anchor phrases:** "delayed payment", "arrears", "unpaid
certificate", "withheld payment".

**Watch for:** A sentence about outstanding arrears to staff/pensioners
unrelated to a construction contractor should not be coded here unless the
underlying arrears are specifically to a contractor/supplier for
infrastructure works.

## 7. governance_and_controls
**Concept:** A systemic weakness in oversight, internal control, or
accountability structures that is stated as an institutional/process
finding, not tied to one specific contract's execution defects (that would
be contract_management) or to a specific procurement irregularity (that
would be procurement_irregularities).

**Example anchor phrases:** "lack of internal control", "weak oversight",
"lack of accountability", "lack of supervision/monitoring" (at an
institutional level, e.g. a Ministry's overall monitoring function).

**Watch for:** This category overlaps heavily in vocabulary with
contract_management ("supervision") and procurement_irregularities
(oversight of the tender process). The distinguishing test: is the finding
about a general institutional control/oversight failure (governance) versus
a specific contract's technical execution (contract_management) versus a
specific tender/bid process (procurement_irregularities)? When a sentence
plausibly fits two of these, code both.

## 8. procurement_irregularities
**Concept:** A problem in the PRE-AWARD process — irregular, non-compliant,
or improper procurement, bidding, tendering, or evaluation-committee
conduct (e.g. splitting purchases to avoid thresholds, single-sourcing
without justification, irregular evaluation, delayed procurement
processing).

**Example anchor phrases:** "procurement irregularity", "irregular
bidding/tendering", "evaluation committee" misconduct, "non-compliance with
PPDA [procurement] regulations".

**Watch for:** This is the classifier's broadest/loosest category (any
sentence containing "procurement", "bid(s)", "tender(s)", or "evaluation
committee" matches, regardless of whether an irregularity is actually
alleged). A neutral, purely descriptive sentence — e.g. "the contract was
awarded through open bidding" or "the procurement process for the project
began in March 2019" — should NOT be coded positive here; only code when
the sentence asserts or implies a compliance problem, delay, or
irregularity in that process.

---

## General coding rules

1. **Multi-label, not mutually exclusive.** Many audit sentences genuinely
   describe two problems at once (e.g. a delayed, defective contract with
   an unresolved claim). Code every category that substantively applies.
2. **Zero labels are valid.** Some sampled sentences (especially from
   procurement_irregularities and governance_and_controls, given how broad
   the underlying regex is) will describe project context, methodology, or
   a finding that does not fit any of the 8 categories as substantively
   defined above. Leave `gold_labels` blank in that case.
3. **Confidence.** Mark `high` when the sentence unambiguously reports (or
   clearly does not report) a category; `medium` when it is a plausible but
   debatable fit; `low` when the sentence is fragmentary, ambiguous, or
   depends on context not present in the single sentence.
4. **Notes** are for non-obvious calls only (e.g. "coded contract_management
   not procurement — defect is post-award", or "borderline claims_and_disputes,
   no explicit litigation term but describes an active counterclaim").
5. Coding is done sentence-by-sentence, from the blinded sample only, with
   no access to the classifier's `all_drivers` labels until after gold
   labels are finalized and saved.
