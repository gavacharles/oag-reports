from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import fitz
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns
from bs4 import BeautifulSoup
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import FactorAnalysis
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC


BASE_URL = "https://www.oag.go.ug"
CONSOLIDATED_URL = f"{BASE_URL}/consolidatedreports"
TARGET_YEARS = set(range(2017, 2026))

ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT
CACHE_DIR = ROOT / "cache"
PLOTS_DIR = ROOT / "plots_png"

CACHE_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


INFRA_TERMS = [
   "road",
   "bridge",
   "highway",
   "construction",
   "infrastructure",
   "water",
   "sewerage",
   "rail",
   "energy",
   "electricity",
   "power",
   "procurement",
   "contract",
   "variation",
   "delayed",
   "delay",
]

DRIVER_PATTERNS = {
   "procurement_irregularities": r"procurement|bid|tender|evaluation",
   "delayed_payments": r"delayed payment|arrears|outstanding payment|certificate unpaid",
   "cost_overruns": r"cost overrun|budget overrun|variation order|price escalation",
   "contract_management": r"contract management|supervision|defect|non-compliance",
   "land_and_right_of_way": r"land acquisition|right of way|compensation",
   "governance_and_controls": r"internal control|oversight|accountability|governance",
   "claims_and_liabilities": r"contingent liabilit|unresolved claim|nugatory expenditure|nurgatory expenditure",
}


@dataclass
class ReportRef:
   year: int
   megareport_url: str
   pdf_url: str
   file_name: str


def fetch_html(url: str, timeout: int = 45) -> str:
   r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
   r.raise_for_status()
   return r.text


def absolute_url(href: str) -> str:
   if href.startswith("http"):
      return href
   return f"{BASE_URL}{href}"


def extract_year(text: str) -> int | None:
   candidates = re.findall(r"(20\d{2})", text)
   if not candidates:
      return None
   year = int(max(candidates))
   if year in TARGET_YEARS:
      return year
   return None


def scrape_megareport_links() -> List[str]:
   html = fetch_html(CONSOLIDATED_URL)
   soup = BeautifulSoup(html, "html.parser")
   urls = []
   for a in soup.select("a[href]"):
      href = a.get("href", "")
      if "viewmegareport" in href:
         urls.append(absolute_url(href))
   urls = sorted(set(urls))
   (RESULTS_DIR / "report_links_scraped.json").write_text(json.dumps(urls, indent=2), encoding="utf-8")
   return urls


def scrape_consolidated_pdfs(megareport_urls: List[str]) -> List[ReportRef]:
   refs: List[ReportRef] = []
   for url in megareport_urls:
      try:
         html = fetch_html(url)
         soup = BeautifulSoup(html, "html.parser")
         embed = soup.find("embed", attrs={"type": "application/pdf"})
         if not embed:
            continue
         src = embed.get("src", "")
         if not src:
            continue
         pdf_url = absolute_url(src)
         file_name = Path(src).name
         year = extract_year(file_name) or extract_year(url)
         if year is None or year not in TARGET_YEARS:
            continue
         refs.append(ReportRef(year=year, megareport_url=url, pdf_url=pdf_url, file_name=file_name))
      except Exception:
         continue

   refs = sorted(refs, key=lambda x: (x.year, x.file_name))
   dedup = {}
   for r in refs:
      dedup[r.year] = r
   final_refs = [dedup[y] for y in sorted(dedup)]

   pd.DataFrame([r.__dict__ for r in final_refs]).to_csv(
      RESULTS_DIR / "consolidated_report_index_2017_2025.csv", index=False
   )
   return final_refs


def download_pdf(url: str, out_path: Path) -> None:
   if out_path.exists() and out_path.stat().st_size > 0:
      return
   r = requests.get(url, timeout=90, headers={"User-Agent": "Mozilla/5.0"})
   r.raise_for_status()
   out_path.write_bytes(r.content)


def pdf_to_text(pdf_path: Path, max_pages: int = 120) -> str:
   doc = fitz.open(pdf_path)
   pages = min(max_pages, len(doc))
   chunks = []
   for i in range(pages):
      chunks.append(doc[i].get_text("text"))
   doc.close()
   return "\n".join(chunks)


def clean_text(text: str) -> str:
   text = text.replace("\xa0", " ")
   text = re.sub(r"\s+", " ", text)
   return text.strip()


def split_sentences(text: str) -> List[str]:
   sents = re.split(r"(?<=[.!?])\s+", text)
   return [s.strip() for s in sents if len(s.strip()) > 40]


def infra_filter(sentences: List[str]) -> List[str]:
   pattern = re.compile(r"\b(" + "|".join(map(re.escape, INFRA_TERMS)) + r")\b", re.I)
   return [s for s in sentences if pattern.search(s)]


def weak_label(sentence: str) -> str:
   s = sentence.lower()
   for label, rx in DRIVER_PATTERNS.items():
      if re.search(rx, s):
         return label
   return "other"


def extract_entities_regex(sentence: str) -> Dict[str, str]:
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


def run_pipeline() -> None:
   sns.set_theme(style="whitegrid")

   megareport_urls = scrape_megareport_links()
   refs = scrape_consolidated_pdfs(megareport_urls)

   corpus_rows = []
   mention_rows = []

   for ref in refs:
      pdf_path = CACHE_DIR / f"{ref.year}_{ref.file_name}"
      try:
         download_pdf(ref.pdf_url, pdf_path)
         text = clean_text(pdf_to_text(pdf_path, max_pages=120))
      except Exception:
         continue

      text_path = CACHE_DIR / f"{ref.year}_text.txt"
      text_path.write_text(text, encoding="utf-8")

      sentences = split_sentences(text)
      infra_sents = infra_filter(sentences)

      for s in infra_sents:
         label = weak_label(s)
         ents = extract_entities_regex(s)
         row = {
            "year": ref.year,
            "sentence": s,
            "driver_label": label,
            **ents,
         }
         corpus_rows.append(row)

         if re.search(r"nugatory expenditure|nurgatory expenditure|contingent liabilit|unresolved claim", s, re.I):
            mention_rows.append(row)

   if not corpus_rows:
      raise RuntimeError("No corpus rows generated. Scraping or PDF extraction failed.")

   corpus = pd.DataFrame(corpus_rows)
   mentions = pd.DataFrame(mention_rows)

   corpus.to_csv(RESULTS_DIR / "oag_infrastructure_sentence_corpus_2017_2025.csv", index=False)
   mentions.to_csv(RESULTS_DIR / "oag_target_mentions_2017_2025.csv", index=False)

   # ----------------------------
   # PFA (Factor Analysis)
   # ----------------------------
   vectorizer = TfidfVectorizer(max_features=400, ngram_range=(1, 2), stop_words="english")
   X = vectorizer.fit_transform(corpus["sentence"])
   X_dense = X.toarray()

   n_components = 6 if X_dense.shape[0] > 20 else min(3, X_dense.shape[1])
   fa = FactorAnalysis(n_components=n_components, random_state=42)
   factors = fa.fit_transform(X_dense)

   factor_df = pd.DataFrame(factors, columns=[f"factor_{i+1}" for i in range(n_components)])
   factor_df["year"] = corpus["year"].values
   factor_df.to_csv(RESULTS_DIR / "pfa_factor_scores_2017_2025.csv", index=False)

   # ----------------------------
   # SVM Classification (weakly supervised)
   # ----------------------------
   labeled = corpus[corpus["driver_label"] != "other"].copy()
   report = {"status": "insufficient_labeled_rows"}

   if labeled["driver_label"].nunique() >= 2 and len(labeled) >= 30:
      X_l = vectorizer.fit_transform(labeled["sentence"])
      y_l = labeled["driver_label"]
      X_train, X_test, y_train, y_test = train_test_split(
         X_l, y_l, test_size=0.25, random_state=42, stratify=y_l
      )
      clf = LinearSVC(class_weight="balanced", random_state=42)
      clf.fit(X_train, y_train)
      y_pred = clf.predict(X_test)
      report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

   (RESULTS_DIR / "svm_driver_classification_report.json").write_text(
      json.dumps(report, indent=2), encoding="utf-8"
   )

   # ----------------------------
   # Hierarchical Topic Modelling (proxy)
   # ----------------------------
   yearly_docs = corpus.groupby("year")["sentence"].apply(lambda s: " ".join(s.tolist())).reset_index()

   topic_vectorizer = CountVectorizer(max_features=250, stop_words="english")
   Y = topic_vectorizer.fit_transform(yearly_docs["sentence"])
   terms = np.array(topic_vectorizer.get_feature_names_out())

   link_mat = linkage(Y.toarray(), method="ward")

   plt.figure(figsize=(12, 6))
   dendrogram(link_mat, labels=yearly_docs["year"].astype(str).tolist(), leaf_rotation=0)
   plt.title("Hierarchical Topic Evolution by Audit Year (2017-2025)")
   plt.xlabel("Year")
   plt.ylabel("Ward Distance")
   plt.tight_layout()
   plt.savefig(PLOTS_DIR / "hierarchical_topic_evolution.png", dpi=220)
   plt.close()

   # ----------------------------
   # Driver frequency + heatmap
   # ----------------------------
   trend = (
      corpus.groupby(["year", "driver_label"]).size().reset_index(name="count")
      .pivot(index="year", columns="driver_label", values="count")
      .fillna(0)
      .sort_index()
   )
   trend.to_csv(RESULTS_DIR / "driver_trend_by_year_2017_2025.csv")

   plt.figure(figsize=(12, 5))
   sns.heatmap(trend, cmap="YlOrRd", linewidths=0.3)
   plt.title("Heatmap of Dispute Driver Mentions by Year")
   plt.tight_layout()
   plt.savefig(PLOTS_DIR / "dispute_driver_heatmap.png", dpi=220)
   plt.close()

   plt.figure(figsize=(12, 6))
   for col in trend.columns:
      plt.plot(trend.index, trend[col], marker="o", label=col)
   plt.title("Temporal Change in Infrastructure Dispute Drivers")
   plt.xlabel("Audit Year")
   plt.ylabel("Mention Count")
   plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
   plt.tight_layout()
   plt.savefig(PLOTS_DIR / "dispute_driver_trends.png", dpi=220)
   plt.close()

   # Risk taxonomy (frequency based)
   taxonomy = (
      corpus[corpus["driver_label"] != "other"]["driver_label"].value_counts().reset_index()
      .rename(columns={"index": "driver", "driver_label": "mentions"})
   )
   taxonomy.to_csv(RESULTS_DIR / "national_dispute_risk_taxonomy_2017_2025.csv", index=False)

   # Target mentions summary
   target_summary = (
      mentions.groupby("year").size().reset_index(name="target_mentions")
      if not mentions.empty
      else pd.DataFrame({"year": sorted(corpus["year"].unique()), "target_mentions": 0})
   )
   target_summary.to_csv(RESULTS_DIR / "target_mentions_summary_2017_2025.csv", index=False)

   # Methodology + results writeup
   summary = {
      "years_covered": sorted(corpus["year"].unique().tolist()),
      "total_infrastructure_sentences": int(len(corpus)),
      "total_target_mentions": int(len(mentions)),
      "top_drivers": corpus["driver_label"].value_counts().head(8).to_dict(),
      "plot_files": [
         str(PLOTS_DIR / "hierarchical_topic_evolution.png"),
         str(PLOTS_DIR / "dispute_driver_heatmap.png"),
         str(PLOTS_DIR / "dispute_driver_trends.png"),
      ],
   }
   (RESULTS_DIR / "phd_pipeline_run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

   writeup = f"""
# Text Mining Execution Writeup (OAG Reports, 2017–2025)

## 1) Data Collection and Scraping
The pipeline scraped the OAG consolidated reports page and extracted megareport links. For each megareport, the embedded PDF URL was collected and constrained to years 2017–2025.

## 2) Data Processing
Each annual report PDF was downloaded and converted to machine-readable text (first 120 pages for computational consistency). The corpus was split into sentences, then filtered to infrastructure-related statements using domain terms (roads, water, energy, construction, contracts, procurement, etc.).

## 3) Named Entity Recognition and Information Extraction
A rule-based NER layer extracted four target entities: project names, contractors, statutory bodies, and funding source references.
Information extraction focused specifically on mentions of:
- nugatory/nurgatory expenditure
- contingent liabilities
- unresolved claims

## 4) PFA and SVM
TF-IDF features were generated from the infrastructure corpus. Principal Factor Analysis (PFA) reduced latent dimensions and produced factor scores used for structural interpretation.
SVM classification used weak supervision from dispute-driver lexical rules to classify sentence-level drivers.

## 5) Hierarchical Topic Modelling and Clustering
Yearly corpora were vectorised and clustered using Ward linkage, producing a hierarchical evolution structure of dispute themes across years.

## 6) Key Outputs
- Consolidated index: consolidated_report_index_2017_2025.csv
- Sentence corpus: oag_infrastructure_sentence_corpus_2017_2025.csv
- Target mention extraction: oag_target_mentions_2017_2025.csv
- PFA scores: pfa_factor_scores_2017_2025.csv
- SVM metrics: svm_driver_classification_report.json
- Risk taxonomy: national_dispute_risk_taxonomy_2017_2025.csv
- PNG visualisations in plots_png/

## 7) Methodological Justification
- Consolidated annual OAG reports provide national-scale, longitudinal, institutionally verified evidence.
- Sentence-level filtering preserves audit context while enabling scalable mining.
- Rule-guided NER and IE provide interpretable features tailored to Ugandan public infrastructure governance language.
- PFA captures latent systemic structures; SVM provides reproducible categorisation for dispute drivers.
- Hierarchical modelling is suited to temporal macro-patterns and reveals whether 2025 drivers diverge from 2018 patterns.

## 8) Analytical Note
The outputs are designed as a proactive dispute-risk intelligence layer for contract administration: repeated governance failures can be monitored over time, and high-risk procurement/funding patterns can be targeted before disputes crystallise.
""".strip()

   (RESULTS_DIR / "phd_detailed_writeup_2017_2025.md").write_text(writeup + "\n", encoding="utf-8")


if __name__ == "__main__":
   run_pipeline()
