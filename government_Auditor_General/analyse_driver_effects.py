"""
Dispute Driver Effects Analysis
================================
Analyses the *effect* of each dispute driver across four dimensions:
  1. Financial Exposure  – UGX amounts explicitly mentioned near each driver
  2. Temporal Escalation – OLS trend slope (mentions/year, 2018-2025)
  3. Co-occurrence       – Pearson correlation between drivers (annual counts)
  4. Proportional Share  – Each driver's normalised share of total mentions/year

Outputs
  plots_png/effects_financial_exposure.png
  plots_png/effects_bubble_profile.png
  plots_png/effects_correlation_heatmap.png
  plots_png/effects_normalised_trends.png
  effects_summary_table.csv
"""

import re, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats

# ── Paths ────────────────────────────────────────────────────────────────────
BASE   = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(BASE, 'oag_infrastructure_sentence_corpus_2017_2025_expanded.csv')
TREND  = os.path.join(BASE, 'driver_trend_by_year_2017_2025_expanded.csv')
OUTDIR = os.path.join(BASE, 'plots_png')
os.makedirs(OUTDIR, exist_ok=True)

# ── Load data ────────────────────────────────────────────────────────────────
df    = pd.read_csv(CORPUS)
trend = pd.read_csv(TREND).set_index('year')
N     = len(df)   # 1,233

DRIVER_ORDER = [
    'procurement_irregularities',
    'delays_and_time_overruns',
    'miscellaneous_administrative',
    'budget_and_funding_issues',
    'infrastructure_and_equipment',
    'general_project_issues',
    'human_resources',
    'delayed_payments',
    'compliance_and_regulatory',
    'contract_management',
    'governance_and_controls',
    'land_and_right_of_way',
    'claims_and_liabilities',
]
def make_label(d):
    """Convert snake_case driver key to display label, preserving 'land'."""
    words = d.split('_')
    # Replace standalone 'and' tokens only (not inside a word like 'land')
    parts = ['&' if w == 'and' else w.capitalize() for w in words]
    return ' '.join(parts)

LABELS = {d: make_label(d) for d in DRIVER_ORDER}

PALETTE = {
    'escalating':    '#d62728',   # red
    'de-escalating': '#2ca02c',   # green
    'neutral':       '#7f7f7f',   # grey
}

# ══════════════════════════════════════════════════════════════════════════════
# 1. FINANCIAL EXPOSURE
# ══════════════════════════════════════════════════════════════════════════════
def max_single_ugx(text):
    """Return the largest single financial figure in a sentence, in UGX."""
    if not isinstance(text, str):
        return 0.0
    vals = []
    # UGX with Bn/Tn suffix
    for m in re.finditer(r'UGX[.\s]*([\d,]+(?:\.\d+)?)\s*(Bn|Tn|billion|trillion)', text, re.I):
        v    = float(m.group(1).replace(',', ''))
        mult = 1e9 if m.group(2).lower() in ('bn', 'billion') else 1e12
        vals.append(v * mult)
    # Raw UGX 10-15 digit numbers (hundreds of millions to low trillions)
    for m in re.finditer(r'UGX[.\s]*([\d,]{10,15})', text):
        v = float(m.group(1).replace(',', ''))
        if v <= 5e13:
            vals.append(v)
    # USD converted at 3,884 UGX/USD
    for m in re.finditer(r'USD[.\s]*([\d,]+(?:\.\d+)?)', text):
        v = float(m.group(1).replace(',', '')) * 3884
        if v <= 5e13:
            vals.append(v)
    return max(vals) if vals else 0.0

df['max_ugx']    = df['sentence'].apply(max_single_ugx)
df['has_amount'] = df['max_ugx'] > 0

fin = (
    df.groupby('driver_label_expanded')
    .agg(
        n              = ('sentence',    'size'),
        n_flagged      = ('has_amount',  'sum'),
        median_ugx_Bn  = ('max_ugx',     lambda x: x[x > 0].median() / 1e9 if (x > 0).any() else 0),
        max_ugx_Bn     = ('max_ugx',     lambda x: x.max() / 1e9),
    )
    .assign(pct_flagged=lambda d: (d['n_flagged'] / d['n'] * 100).round(1))
    .reindex(DRIVER_ORDER)
)

# ── Figure 1: Financial exposure bar chart ───────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Financial Exposure by Dispute Driver\n(UGX amounts explicitly cited in OAG audit sentences, 2018–2025)',
             fontsize=13, fontweight='bold', y=1.02)

short_labels = [LABELS[d] for d in DRIVER_ORDER]

# Left: median UGX per financially-flagged sentence
ax1 = axes[0]
bars = ax1.barh(short_labels, fin['median_ugx_Bn'], color='#1f77b4', edgecolor='white', height=0.7)
for bar, val in zip(bars, fin['median_ugx_Bn']):
    if val > 0:
        ax1.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                 f'{val:.1f} Bn', va='center', fontsize=8)
ax1.set_xlabel('Median cited amount (UGX Billions)')
ax1.set_title('Median Single-Sentence Financial Figure\n(flagged sentences only)')
ax1.invert_yaxis()

# Right: % sentences with explicit financial citation
ax2 = axes[1]
bars2 = ax2.barh(short_labels, fin['pct_flagged'], color='#ff7f0e', edgecolor='white', height=0.7)
for bar, val in zip(bars2, fin['pct_flagged']):
    ax2.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
             f'{val:.0f}%', va='center', fontsize=8)
ax2.set_xlabel('% of sentences with explicit UGX/USD figure')
ax2.set_title('Financial Citation Rate\n(share of sentences with explicit amounts)')
ax2.invert_yaxis()

plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, 'effects_financial_exposure.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Saved effects_financial_exposure.png")


# ══════════════════════════════════════════════════════════════════════════════
# 2. TEMPORAL ESCALATION (OLS per driver)
# ══════════════════════════════════════════════════════════════════════════════
years = trend.index.values.astype(float)

slope_records = {}
for col in DRIVER_ORDER:
    if col not in trend.columns:
        continue
    s, intercept, r, p, se = stats.linregress(years, trend[col].values.astype(float))
    direction = 'escalating' if s > 0 else 'de-escalating'
    slope_records[col] = dict(
        slope=round(s, 3),
        r2=round(r**2, 3),
        p_value=round(p, 3),
        direction=direction,
        significant=(p < 0.10),
    )

slope_df = pd.DataFrame(slope_records).T


# ══════════════════════════════════════════════════════════════════════════════
# 3. EFFECT PROFILE BUBBLE CHART
#    x = frequency (count), y = trend slope, bubble = median financial Bn
# ══════════════════════════════════════════════════════════════════════════════
counts = df['driver_label_expanded'].value_counts()

fig, ax = plt.subplots(figsize=(12, 8))
ax.axhline(0, color='grey', linewidth=0.8, linestyle='--')
ax.axvline(counts.mean(), color='grey', linewidth=0.8, linestyle=':')

for drv in DRIVER_ORDER:
    if drv not in slope_df.index:
        continue
    x     = counts.get(drv, 0)
    y     = slope_df.loc[drv, 'slope']
    size  = max(fin.loc[drv, 'median_ugx_Bn'] * 1.5, 30) if drv in fin.index else 30
    size  = min(size, 3000)
    color = PALETTE['escalating'] if y > 0 else PALETTE['de-escalating']
    sig   = slope_df.loc[drv, 'significant']

    ax.scatter(x, y, s=size, color=color, alpha=0.65, edgecolors='black',
               linewidths=1.5 if sig else 0.5, zorder=3)
    ax.annotate(LABELS[drv], (x, y),
                xytext=(8, 4), textcoords='offset points',
                fontsize=8.5, wrap=True)

legend_handles = [
    mpatches.Patch(color=PALETTE['escalating'],    label='Escalating trend (↑)'),
    mpatches.Patch(color=PALETTE['de-escalating'], label='De-escalating trend (↓)'),
    plt.scatter([], [], s=100,  color='grey', alpha=0.5, label='Bubble = median UGX cited (Bn)'),
]
ax.legend(handles=legend_handles, loc='upper left', fontsize=9)

ax.set_xlabel('Frequency (total mentions, 2018–2025)', fontsize=11)
ax.set_ylabel('Trend slope (mentions added per year)', fontsize=11)
ax.set_title('Dispute Driver Effect Profile\nFrequency × Escalation × Financial Magnitude',
             fontsize=13, fontweight='bold')

# Quadrant labels
ax.text(0.97, 0.97, 'HIGH FREQUENCY\nESCALATING', transform=ax.transAxes,
        ha='right', va='top', fontsize=8, color='#d62728', alpha=0.5)
ax.text(0.97, 0.03, 'HIGH FREQUENCY\nDE-ESCALATING', transform=ax.transAxes,
        ha='right', va='bottom', fontsize=8, color='#2ca02c', alpha=0.5)
ax.text(0.03, 0.97, 'LOW FREQUENCY\nESCALATING', transform=ax.transAxes,
        ha='left', va='top', fontsize=8, color='#d62728', alpha=0.5)

plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, 'effects_bubble_profile.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Saved effects_bubble_profile.png")


# ══════════════════════════════════════════════════════════════════════════════
# 4. DRIVER CORRELATION HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
corr_data  = trend[DRIVER_ORDER].rename(columns=LABELS)
corr_matrix = corr_data.corr()

fig, ax = plt.subplots(figsize=(13, 11))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
sns.heatmap(
    corr_matrix,
    mask=mask,
    annot=True,
    fmt='.2f',
    cmap='RdYlGn',
    vmin=-1, vmax=1,
    linewidths=0.5,
    square=True,
    ax=ax,
    annot_kws={'size': 8},
    cbar_kws={'shrink': 0.7, 'label': 'Pearson r'},
)
ax.set_title('Inter-Driver Co-occurrence Correlation\n(Pearson r on annual mention counts, 2018–2025)',
             fontsize=13, fontweight='bold', pad=16)
ax.tick_params(axis='x', rotation=40, labelsize=9)
ax.tick_params(axis='y', rotation=0,  labelsize=9)
plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, 'effects_correlation_heatmap.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Saved effects_correlation_heatmap.png")


# ══════════════════════════════════════════════════════════════════════════════
# 5. NORMALISED PROPORTIONAL TRENDS
# ══════════════════════════════════════════════════════════════════════════════
# Show each driver's share of annual mentions (not absolute count)
yearly_totals = trend[DRIVER_ORDER].sum(axis=1)
norm = trend[DRIVER_ORDER].div(yearly_totals, axis=0) * 100

# Group into 4 thematic clusters for readability
clusters = {
    'Procurement & Compliance': ['procurement_irregularities', 'compliance_and_regulatory', 'contract_management'],
    'Delays & Finance':         ['delays_and_time_overruns', 'delayed_payments', 'budget_and_funding_issues'],
    'Governance & HR':          ['governance_and_controls', 'human_resources', 'claims_and_liabilities'],
    'Infrastructure & Admin':   ['infrastructure_and_equipment', 'miscellaneous_administrative',
                                 'general_project_issues', 'land_and_right_of_way'],
}
cluster_colors = {
    'Procurement & Compliance': '#1f77b4',
    'Delays & Finance':         '#d62728',
    'Governance & HR':          '#9467bd',
    'Infrastructure & Admin':   '#2ca02c',
}
line_styles = ['-', '--', '-.', ':']

fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharey=False)
fig.suptitle('Proportional Share of Annual Audit Mentions by Driver Group\n(normalised % of annual total, 2018–2025)',
             fontsize=13, fontweight='bold')

for ax, (cluster, drivers) in zip(axes.flatten(), clusters.items()):
    color = cluster_colors[cluster]
    for i, drv in enumerate(drivers):
        if drv not in norm.columns:
            continue
        ls = line_styles[i % len(line_styles)]
        ax.plot(norm.index, norm[drv], marker='o', linestyle=ls, color=color,
                alpha=min(0.5 + 0.15 * i, 0.95), linewidth=1.8, label=LABELS[drv])
    ax.set_title(cluster, fontsize=11, fontweight='bold')
    ax.set_xlabel('Year')
    ax.set_ylabel('Share of annual mentions (%)')
    ax.legend(fontsize=8, loc='upper left')
    ax.set_xticks(norm.index)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, 'effects_normalised_trends.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Saved effects_normalised_trends.png")


# ══════════════════════════════════════════════════════════════════════════════
# 6. SUMMARY EFFECTS TABLE (CSV)
# ══════════════════════════════════════════════════════════════════════════════
summary = pd.DataFrame(index=DRIVER_ORDER)
summary['label']                  = [LABELS[d] for d in DRIVER_ORDER]
summary['total_mentions']         = [counts.get(d, 0)                          for d in DRIVER_ORDER]
summary['pct_of_corpus']          = (summary['total_mentions'] / N * 100).round(1)
summary['trend_slope']            = slope_df.reindex(DRIVER_ORDER)['slope']
summary['trend_r2']               = slope_df.reindex(DRIVER_ORDER)['r2']
summary['trend_p']                = slope_df.reindex(DRIVER_ORDER)['p_value']
summary['direction']              = slope_df.reindex(DRIVER_ORDER)['direction']
summary['pct_sentences_w_amount'] = fin.reindex(DRIVER_ORDER)['pct_flagged']
summary['median_cited_ugx_Bn']    = fin.reindex(DRIVER_ORDER)['median_ugx_Bn'].round(2)
summary['max_cited_ugx_Bn']       = fin.reindex(DRIVER_ORDER)['max_ugx_Bn'].round(2)

summary.to_csv(os.path.join(BASE, 'effects_summary_table.csv'), index=True)
print("Saved effects_summary_table.csv")

print("\n=== EFFECTS SUMMARY TABLE ===")
print(summary[['label','total_mentions','pct_of_corpus','trend_slope','direction',
               'pct_sentences_w_amount','median_cited_ugx_Bn']].to_string())
