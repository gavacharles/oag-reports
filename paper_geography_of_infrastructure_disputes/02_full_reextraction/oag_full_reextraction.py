"""
Full re-extraction and re-classification of the OAG infrastructure sentence
corpus, fixing three compounding problems found in the original pipeline
(OAG reports.py):

1. Text extraction was capped at max_pages=120 per report. Actual reports
   run 164-784 pages; on average ~70-85% of each report's content was never
   read. This alone likely explains why 'cost_overruns' (a defined category)
   returned zero sentences nationally -- that content sits later in the
   document (annex tables, sector-by-sector detail).
2. No front-matter/back-matter stripping before sentence splitting, so
   table-of-contents dot-leaders, table/figure captions, and glossary text
   were classified as if they were audit findings (12.8% of the original
   corpus, verified by spot-check).
3. Category keyword patterns were narrow and single-label (first-match-wins
   by dict order), which both under-counted real content (e.g. no separate
   'delay_time_overrun' category existed at all -- only 'delayed_payments',
   which is financial, not schedule delay) and let earlier, broader
   categories (procurement_irregularities) silently swallow sentences that
   should also/instead have counted toward a later category.

This script re-extracts full text from the already-cached PDFs (no network
calls), strips front/back matter, and classifies with a redesigned,
multi-label taxonomy.
"""
import re
from pathlib import Path

import fitz
import pandas as pd

BASE = Path("/Users/charlesgava/Documents/Projects /OAG Reports/government_Auditor_General")
CACHE = BASE / "cache"
OUT_CSV = BASE / "oag_infrastructure_sentence_corpus_2017_2025_FULLTEXT.csv"

INFRA_TERMS = [
    "road", "bridge", "highway", "construction", "infrastructure", "water",
    "sewerage", "rail", "railway", "energy", "electricity", "power", "dam",
    "hospital", "school", "housing", "stadium", "airport", "building",
    "procurement", "contract", "variation", "delayed", "delay", "project",
]

FRONTMATTER_PATTERNS = [
    r"\.{4,}",
    r"ABBREVIATION|ACRONYM|GLOSSARY OF TERMS|LIST OF TABLES|LIST OF FIGURES|TABLE OF CONTENTS",
    r"^\s*\d{0,4}\s*Table\s+\d+\s*[:.]",
    r"^\s*\d{0,4}\s*Figure\s+\d+\s*[:.]",
    r"^\s*\d{1,4}\s+[A-Z][a-zA-Z\s]{3,60}\.{2,}\s*\d*\s*$",
]
FRONTMATTER_RE = re.compile("|".join(FRONTMATTER_PATTERNS), re.I)

# Redesigned taxonomy. Multi-label: a sentence can match more than one
# category. Order matters only for the 'primary_driver' convenience column
# (first match in this list order), not for the multi-label indicators.
DRIVER_PATTERNS = {
    "delay_time_overrun": r"extension of time|behind schedule|time overrun|delayed completion|"
                           r"delay(?:ed|s)? in completion|failure to complete|incomplete works|"
                           r"abandoned works|\bstalled\b|not yet completed|overdue completion|"
                           r"suspension of works|works? (?:were|was) halted",
    "cost_overrun": r"cost overrun|budget overrun|cost escalation|price escalation|"
                     r"budget variance|excess expenditure|additional cost|cost variation|"
                     r"price variation|supplementary budget|over and above the contract",
    "claims_and_disputes": r"contingent liabilit|unresolved claim|nugatory expenditure|"
                            r"nurgatory expenditure|litigation|arbitration|breach of contract|"
                            r"liquidated damages|compensation claim|counterclaim|court case|"
                            r"\bsued\b|lawsuit|legal suit",
    "land_and_right_of_way": r"land acquisition|right of way|way\s*leave|resettlement|"
                              r"compensation of (?:project affected|affected) persons|encroach",
    "contract_management": r"contract management|supervision|\bdefect(?:s|ive)?\b|"
                            r"non-compliance|poor workmanship|substandard|shoddy",
    "delayed_payments": r"delayed payment|arrears|outstanding payment|certificate unpaid|"
                         r"unpaid certificate|payment delay|withheld payment",
    "governance_and_controls": r"internal control|oversight|accountability|governance|"
                                r"lack of (?:supervision|monitoring)",
    "procurement_irregularities": r"procurement|\bbid(?:s|ding)?\b|\btender(?:s|ing)?\b|evaluation committee",
}
PRIMARY_ORDER = list(DRIVER_PATTERNS.keys())


def pdf_to_full_text(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    chunks = [page.get_text("text") for page in doc]
    return "\n".join(chunks)


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def split_sentences(text: str) -> list:
    # split on paragraph-ish boundaries first (page.get_text keeps some line
    # structure) then on sentence punctuation
    text = re.sub(r"\n+", " ", text)
    sents = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sents if len(s.strip()) > 40]


def is_frontmatter(sentence: str) -> bool:
    return bool(FRONTMATTER_RE.search(sentence))


def infra_filter(sentences: list) -> list:
    pattern = re.compile(r"\b(" + "|".join(map(re.escape, INFRA_TERMS)) + r")\b", re.I)
    return [s for s in sentences if pattern.search(s)]


def multi_label(sentence: str) -> list:
    s = sentence.lower()
    return [label for label, rx in DRIVER_PATTERNS.items() if re.search(rx, s, re.I)]


def extract_entities_regex(sentence: str) -> dict:
    contractor = re.findall(r"\b(?:M\/S\.?|Ltd\.?|Limited|Company|Consortium)\b[^.]{0,80}", sentence, flags=re.I)
    statutory = re.findall(r"\b(?:Ministry|Authority|Corporation|Agency|Commission|Parliament|UGANDA NATIONAL ROADS AUTHORITY)\b[^.]{0,80}", sentence, flags=re.I)
    funding = re.findall(r"\b(?:World Bank|AfDB|KfW|EU|Danida|DFID|loan|grant)\b[^.]{0,60}", sentence, flags=re.I)
    project = re.findall(r"\b(?:Project|Programme|Program)\b[^.]{0,90}", sentence, flags=re.I)
    return {
        "project_name": "; ".join(project[:2]),
        "contractor": "; ".join(contractor[:2]),
        "statutory_body": "; ".join(statutory[:2]),
        "funding_source": "; ".join(funding[:2]),
    }


def extract_year(filename: str) -> int:
    return int(filename.split("_")[0])


rows = []
page_count_report = []
for pdf_path in sorted(CACHE.glob("*.pdf")):
    year = extract_year(pdf_path.name)
    doc = fitz.open(pdf_path)
    n_pages = doc.page_count
    text = clean_text(pdf_to_full_text(pdf_path))
    (CACHE / f"{year}_text_FULL.txt").write_text(text, encoding="utf-8")

    sentences = split_sentences(text)
    n_before_fm = len(sentences)
    sentences = [s for s in sentences if not is_frontmatter(s)]
    n_after_fm = len(sentences)

    infra_sents = infra_filter(sentences)

    n_labeled = 0
    for s in infra_sents:
        labels = multi_label(s)
        if not labels:
            continue
        n_labeled += 1
        primary = next((l for l in PRIMARY_ORDER if l in labels), "other")
        ents = extract_entities_regex(s)
        rows.append({
            "year": year,
            "source_pdf": pdf_path.name,
            "n_pdf_pages": n_pages,
            "sentence": s,
            "primary_driver": primary,
            "all_drivers": "|".join(labels),
            "n_drivers_matched": len(labels),
            **ents,
        })

    page_count_report.append((pdf_path.name, n_pages, n_before_fm, n_after_fm, len(infra_sents), n_labeled))
    print(f"{pdf_path.name}: {n_pages} pages (FULL, was capped at 120) -> "
          f"{n_before_fm} sentences -> {n_after_fm} after front-matter strip -> "
          f"{len(infra_sents)} infra-relevant -> {n_labeled} driver-labeled")

corpus = pd.DataFrame(rows)
corpus.to_csv(OUT_CSV, index=False)
print(f"\nTotal labeled sentences: {len(corpus)} (was 1,233 under the old capped/narrow pipeline)")
print(f"Saved -> {OUT_CSV}")

print("\n=== primary_driver distribution (new taxonomy) ===")
print(corpus["primary_driver"].value_counts())

print("\n=== multi-label: how many sentences match >1 category ===")
print((corpus["n_drivers_matched"] > 1).sum(), "/", len(corpus))

summary = pd.DataFrame(page_count_report, columns=[
    "report", "pdf_pages", "sentences_before_frontmatter_strip",
    "sentences_after_frontmatter_strip", "infra_relevant_sentences", "driver_labeled_sentences"])
summary.to_csv(BASE / "oag_reextraction_summary.csv", index=False)
print(f"\nPer-report summary saved -> {BASE / 'oag_reextraction_summary.csv'}")
