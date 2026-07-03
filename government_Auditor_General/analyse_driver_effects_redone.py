"""
Redone dispute driver effects analysis with a stricter financial exposure method.
"""

import os
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

BASE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(BASE, 'oag_infrastructure_sentence_corpus_2017_2025_expanded.csv')
TREND = os.path.join(BASE, 'driver_trend_by_year_2017_2025_expanded.csv')
OUTDIR = os.path.join(BASE, 'plots_png')
os.makedirs(OUTDIR, exist_ok=True)

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


def make_label(driver_key: str) -> str:
    return ' '.join('&' if part == 'and' else part.capitalize() for part in driver_key.split('_'))


LABELS = {d: make_label(d) for d in DRIVER_ORDER}
PALETTE = {'escalating': '#d62728', 'de-escalating': '#2ca02c'}

IMPACT_RE = re.compile(
    r'\b(?:cost|costs|costing|payment|payments|paid|arrears|unpaid|liabilit(?:y|ies)|'
    r'claim(?:s)?|compensation|interest|penalt(?:y|ies)|fine(?:s)?|overpayment|'
    r'wasteful|nugatory|loss(?:es)?|idle|delay(?:ed)?|standby|escalation|'
    r'additional|surcharge(?:s)?|receivable(?:s)?|refund(?:s)?|disbursement|'
    r'underfund(?:ed|ing)?|undisbursed|unutili[sz]ed|outstanding|overrun(?:s)?|variation(?:s)?)\b',
    re.I,
)
EXCLUDE_RE = re.compile(
    r'\b(?:debt stock|public debt|warrant(?:s)?|budget support|revised budget|'
    r'budget allocation|programme warrants|sum of total|sum of revised budget|'
    r'statement of financial performance|profit after tax|financial year ended|'
    r'table\s*\d+[: ])\b',
    re.I,
)
AMOUNT_RE = re.compile(
    r'(?:UGX[.\s]*([\d,]+(?:\.\d+)?)\s*(Bn|Tn|billion|trillion)'
    r'|UGX[.\s]*([\d,]{7,15})'
    r'|USD[.\s]*([\d,]+(?:\.\d+)?))',
    re.I,
)


def extract_amounts_ugx(text: str):
    values = []
    if not isinstance(text, str):
        return values
    for match in AMOUNT_RE.finditer(text):
        bn_tn_value = match.group(1)
        unit = match.group(2)
        raw_ugx = match.group(3)
        usd_value = match.group(4)
        if bn_tn_value:
            value = float(bn_tn_value.replace(',', ''))
            amount = value * (1e9 if unit.lower() in ('bn', 'billion') else 1e12)
        elif raw_ugx:
            amount = float(raw_ugx.replace(',', ''))
        else:
            amount = float(usd_value.replace(',', '')) * 3884
        if amount <= 5e13:
            values.append(amount)
    return values


df = pd.read_csv(CORPUS)
trend = pd.read_csv(TREND).set_index('year')
N = len(df)

df['text'] = df['sentence'].fillna('')
df['amounts_ugx'] = df['text'].apply(extract_amounts_ugx)
df['n_amounts'] = df['amounts_ugx'].str.len()
df['has_impact_keyword'] = df['text'].str.contains(IMPACT_RE, regex=True)
df['is_table_like'] = df['text'].str.contains(EXCLUDE_RE, regex=True)
df['effect_amount_ugx'] = df.apply(
    lambda row: max(row['amounts_ugx']) if row['has_impact_keyword'] and not row['is_table_like'] and 1 <= row['n_amounts'] <= 4 else 0.0,
    axis=1,
)
df['effect_flag'] = df['effect_amount_ugx'] > 0

flagged = df[df['effect_flag']].copy()
q95 = flagged['effect_amount_ugx'].quantile(0.95) if not flagged.empty else 0
flagged['effect_amount_ugx_w'] = flagged['effect_amount_ugx'].clip(upper=q95)

financial = pd.DataFrame(index=DRIVER_ORDER)
financial['total_mentions'] = df['driver_label_expanded'].value_counts().reindex(DRIVER_ORDER).fillna(0).astype(int)
financial['financial_flagged_sentences'] = flagged['driver_label_expanded'].value_counts().reindex(DRIVER_ORDER).fillna(0).astype(int)
financial['financial_coverage_pct'] = (financial['financial_flagged_sentences'] / financial['total_mentions'] * 100).fillna(0).round(1)
financial['median_effect_bn'] = (flagged.groupby('driver_label_expanded')['effect_amount_ugx_w'].median().reindex(DRIVER_ORDER).fillna(0) / 1e9).round(2)
financial['p75_effect_bn'] = (flagged.groupby('driver_label_expanded')['effect_amount_ugx_w'].quantile(0.75).reindex(DRIVER_ORDER).fillna(0) / 1e9).round(2)
financial['high_impact_cases_100bn'] = flagged.groupby('driver_label_expanded')['effect_amount_ugx'].apply(lambda x: int((x >= 1e11).sum())).reindex(DRIVER_ORDER).fillna(0).astype(int)
financial['weighted_exposure_index'] = (financial['financial_flagged_sentences'] * np.log1p(financial['median_effect_bn'])).round(2)

plot_fin = financial.sort_values('weighted_exposure_index', ascending=True)
labels_fin = [LABELS[d] for d in plot_fin.index]
fig, axes = plt.subplots(1, 2, figsize=(15, 7), gridspec_kw={'width_ratios': [1.15, 1]})
fig.suptitle(
    'Financial Exposure by Dispute Driver\nConservative effect-based extraction: monetary figure + fiscal-impact language, 2018–2025',
    fontsize=13,
    fontweight='bold',
    y=1.02,
)

ax1 = axes[0]
colors = ['#c0392b' if v >= plot_fin['weighted_exposure_index'].median() else '#f39c12' for v in plot_fin['weighted_exposure_index']]
ax1.barh(labels_fin, plot_fin['weighted_exposure_index'], color=colors, edgecolor='white', height=0.72)
for i, (_, row) in enumerate(plot_fin.iterrows()):
    ax1.text(row['weighted_exposure_index'] + 0.8, i, f"{row['weighted_exposure_index']:.1f}", va='center', fontsize=8)
ax1.set_xlabel('Weighted exposure index = flagged cases × log(1 + median UGX billions)')
ax1.set_title('Breadth-adjusted Financial Exposure')
ax1.grid(axis='x', alpha=0.25)

ax2 = axes[1]
scatter = ax2.scatter(
    plot_fin['median_effect_bn'].replace(0, np.nan),
    plot_fin['financial_coverage_pct'],
    s=plot_fin['high_impact_cases_100bn'].replace(0, 1) * 140,
    c=plot_fin['weighted_exposure_index'],
    cmap='YlOrRd',
    alpha=0.82,
    edgecolors='black',
)
for driver, row in plot_fin.iterrows():
    if row['median_effect_bn'] > 0:
        ax2.annotate(LABELS[driver], (row['median_effect_bn'], row['financial_coverage_pct']), xytext=(6, 4), textcoords='offset points', fontsize=8)
ax2.set_xscale('log')
ax2.set_xlabel('Median effect amount (UGX billions, log scale)')
ax2.set_ylabel('Coverage: % of driver sentences with qualifying financial effect')
ax2.set_title('Magnitude vs Coverage\nBubble size = number of ≥ UGX 100Bn cases')
ax2.grid(alpha=0.25)
plt.colorbar(scatter, ax=ax2, shrink=0.8, label='Weighted exposure index')
plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, 'effects_financial_exposure.png'), dpi=180, bbox_inches='tight')
plt.close()
print('Saved effects_financial_exposure.png')

years = trend.index.values.astype(float)
trend_summary = {}
for driver in DRIVER_ORDER:
    slope, intercept, r_value, p_value, std_err = stats.linregress(years, trend[driver].values.astype(float))
    trend_summary[driver] = {
        'trend_slope': round(slope, 3),
        'trend_r2': round(r_value ** 2, 3),
        'trend_p': round(p_value, 3),
        'direction': 'escalating' if slope > 0 else 'de-escalating',
        'significant': p_value < 0.10,
    }
trend_summary = pd.DataFrame(trend_summary).T.reindex(DRIVER_ORDER)
counts = df['driver_label_expanded'].value_counts().reindex(DRIVER_ORDER)

fig, ax = plt.subplots(figsize=(12.5, 8))
ax.axhline(0, color='grey', linewidth=0.8, linestyle='--')
ax.axvline(counts.mean(), color='grey', linewidth=0.8, linestyle=':')
point_rows = []
for driver in DRIVER_ORDER:
    x_val = counts[driver]
    y_val = trend_summary.loc[driver, 'trend_slope']
    bubble_size = max(financial.loc[driver, 'weighted_exposure_index'] * 18, 60)
    color = PALETTE[trend_summary.loc[driver, 'direction']]
    ax.scatter(x_val, y_val, s=bubble_size, color=color, alpha=0.68, edgecolors='black', linewidths=1.4 if trend_summary.loc[driver, 'significant'] else 0.6, zorder=3)
    point_rows.append({
        'driver': driver,
        'x': float(x_val),
        'y': float(y_val),
        'direction': trend_summary.loc[driver, 'direction'],
    })

points_df = pd.DataFrame(point_rows)
y_min = points_df['y'].min()
y_max = points_df['y'].max()
y_span = max(y_max - y_min, 0.2)
min_gap = y_span * 0.11


def spread_group_y(df_group: pd.DataFrame) -> dict:
    ordered = df_group.sort_values('y')
    out = {}
    last_y = None
    for _, row in ordered.iterrows():
        yv = row['y']
        if last_y is not None and yv - last_y < min_gap:
            yv = last_y + min_gap
        out[row['driver']] = yv
        last_y = yv
    return out


y_labels = {}
for direction in ['de-escalating', 'escalating']:
    g = points_df[points_df['direction'] == direction]
    if not g.empty:
        y_labels.update(spread_group_y(g))

for _, row in points_df.iterrows():
    driver = row['driver']
    x_val, y_val = row['x'], row['y']
    if row['direction'] == 'de-escalating':
        x_text = x_val * 0.90
        ha = 'right'
    else:
        x_text = x_val * 1.08
        ha = 'left'
    ax.annotate(
        LABELS[driver],
        (x_val, y_val),
        xytext=(x_text, y_labels[driver]),
        textcoords='data',
        ha=ha,
        va='center',
        fontsize=8.2,
        bbox=dict(boxstyle='round,pad=0.16', fc='white', ec='none', alpha=0.80),
        arrowprops=dict(arrowstyle='-', color='#666666', lw=0.65, alpha=0.8),
    )
legend_handles = [
    mpatches.Patch(color=PALETTE['escalating'], label='Escalating trend'),
    mpatches.Patch(color=PALETTE['de-escalating'], label='De-escalating trend'),
    plt.scatter([], [], s=220, color='grey', alpha=0.5, label='Bubble = weighted financial exposure'),
]
ax.legend(handles=legend_handles, loc='upper left', fontsize=9)
ax.set_xlabel('Frequency (total mentions, 2018–2025)')
ax.set_ylabel('Trend slope (mentions per year)')
ax.set_title('Dispute Driver Effect Profile\nFrequency × Escalation × Breadth-adjusted Financial Exposure', fontsize=13, fontweight='bold')
ax.text(0.97, 0.97, 'HIGH FREQUENCY\nESCALATING', transform=ax.transAxes, ha='right', va='top', fontsize=8, color='#d62728', alpha=0.55)
ax.text(0.97, 0.03, 'HIGH FREQUENCY\nDE-ESCALATING', transform=ax.transAxes, ha='right', va='bottom', fontsize=8, color='#2ca02c', alpha=0.55)
ax.text(0.03, 0.97, 'LOW FREQUENCY\nESCALATING', transform=ax.transAxes, ha='left', va='top', fontsize=8, color='#d62728', alpha=0.55)
ax.set_ylim(min(y_min, min(y_labels.values())) - y_span * 0.16, max(y_max, max(y_labels.values())) + y_span * 0.16)
plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, 'effects_bubble_profile.png'), dpi=180, bbox_inches='tight')
plt.close()
print('Saved effects_bubble_profile.png')

# ── Combined effects profile (frequency + finance + trend + connectivity) ──
corr_raw = trend[DRIVER_ORDER].corr()
connectivity_strength = {}
for d in DRIVER_ORDER:
    others = corr_raw.loc[d, [x for x in DRIVER_ORDER if x != d]]
    strong_links = others[others.abs() >= 0.65]
    connectivity_strength[d] = float(strong_links.abs().sum())

combined = pd.DataFrame(index=DRIVER_ORDER)
combined['label'] = [LABELS[d] for d in DRIVER_ORDER]
combined['frequency_mentions'] = counts.reindex(DRIVER_ORDER).astype(float)
combined['financial_exposure_index'] = financial['weighted_exposure_index'].reindex(DRIVER_ORDER).astype(float)
combined['trend_slope'] = trend_summary['trend_slope'].reindex(DRIVER_ORDER).astype(float)
combined['trend_escalation_only'] = combined['trend_slope'].clip(lower=0)
combined['connectivity_strength'] = pd.Series(connectivity_strength).reindex(DRIVER_ORDER).fillna(0).astype(float)


def minmax_100(series: pd.Series) -> pd.Series:
    s_min, s_max = float(series.min()), float(series.max())
    if s_max - s_min < 1e-12:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - s_min) / (s_max - s_min) * 100


combined['score_frequency'] = minmax_100(combined['frequency_mentions'])
combined['score_financial'] = minmax_100(combined['financial_exposure_index'])
combined['score_trend'] = minmax_100(combined['trend_escalation_only'])
combined['score_connectivity'] = minmax_100(combined['connectivity_strength'])

# Weighted synthesis for policy-facing prioritisation
w_freq, w_fin, w_trend, w_conn = 0.35, 0.25, 0.20, 0.20
combined['combined_effect_score'] = (
    w_freq * combined['score_frequency']
    + w_fin * combined['score_financial']
    + w_trend * combined['score_trend']
    + w_conn * combined['score_connectivity']
)

combined_sorted = combined.sort_values('combined_effect_score', ascending=True)

fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(18, 10),
    gridspec_kw={'width_ratios': [1.2, 1]},
)

# Left panel: weighted combined score ranking
rank_colors = ['#b2182b' if s >= combined['combined_effect_score'].median() else '#ef8a62'
               for s in combined_sorted['combined_effect_score']]
ax1.barh(combined_sorted['label'], combined_sorted['combined_effect_score'],
         color=rank_colors, edgecolor='white', height=0.72)
for y_idx, val in enumerate(combined_sorted['combined_effect_score'].values):
    ax1.text(val + 0.9, y_idx, f'{val:.1f}', va='center', fontsize=8.5)
ax1.set_xlabel('Combined effect score (0–100 weighted index)')
ax1.set_title('Combined Effects Ranking')
ax1.grid(axis='x', alpha=0.25)

# Right panel: component profile heatmap-style matrix
matrix_cols = ['score_frequency', 'score_financial', 'score_trend', 'score_connectivity']
matrix_labels = ['Frequency', 'Financial', 'Escalation', 'Co-occurrence']
heat_df = combined_sorted[matrix_cols]
sns.heatmap(
    heat_df,
    ax=ax2,
    cmap='YlOrRd',
    vmin=0,
    vmax=100,
    annot=True,
    fmt='.0f',
    linewidths=0.4,
    cbar_kws={'label': 'Normalised component score (0–100)', 'shrink': 0.78},
    annot_kws={'fontsize': 8},
)
ax2.set_title('Component Contributions by Driver')
ax2.set_xticklabels(matrix_labels, rotation=30, ha='right')
ax2.set_yticklabels(combined_sorted['label'], rotation=0)

fig.suptitle(
    'Combined Effects Profile\nFrequency + Financial Exposure + Escalation + Co-occurrence Connectivity (2018–2025)',
    fontsize=14, fontweight='bold', y=0.98,
)
fig.tight_layout(rect=[0, 0, 1, 0.965])
fig.savefig(os.path.join(OUTDIR, 'effects_combined_profile.png'), dpi=220, bbox_inches='tight', pad_inches=0.25)
plt.close()

# Standalone panel B export
fig_b, ax_b = plt.subplots(figsize=(9.5, 8.8))
sns.heatmap(
    heat_df,
    ax=ax_b,
    cmap='YlOrRd',
    vmin=0,
    vmax=100,
    annot=True,
    fmt='.0f',
    linewidths=0.4,
    cbar_kws={'label': 'Normalised component score (0–100)', 'shrink': 0.82},
    annot_kws={'fontsize': 8},
)
ax_b.set_title('Panel B. Component Contributions by Driver', fontsize=13, fontweight='bold', pad=12)
ax_b.set_xticklabels(matrix_labels, rotation=30, ha='right')
ax_b.set_yticklabels(combined_sorted['label'], rotation=0)
fig_b.tight_layout()
fig_b.savefig(os.path.join(OUTDIR, 'effects_combined_profile_panel_b.png'), dpi=220, bbox_inches='tight', pad_inches=0.22)
plt.close(fig_b)
combined.sort_values('combined_effect_score', ascending=False).to_csv(
    os.path.join(BASE, 'effects_combined_profile_scores.csv'), index=True
)
print('Saved effects_combined_profile.png')
print('Saved effects_combined_profile_panel_b.png')
print('Saved effects_combined_profile_scores.csv')

corr_data = trend[DRIVER_ORDER].rename(columns=LABELS)
corr_matrix = corr_data.corr()
fig, ax = plt.subplots(figsize=(16, 14))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
sns.heatmap(
    corr_matrix, mask=mask, annot=True, fmt='.2f',
    cmap='RdYlGn', vmin=-1, vmax=1,
    linewidths=0.5, square=True, ax=ax,
    annot_kws={'size': 9},
    cbar_kws={'shrink': 0.65, 'label': 'Pearson r'},
)
ax.set_title(
    'Inter-Driver Co-occurrence Correlation\n(Pearson r on annual mention counts, 2018–2025)',
    fontsize=13, fontweight='bold', pad=16,
)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9.5)
ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=9.5)
fig.subplots_adjust(left=0.20, bottom=0.22, right=0.95, top=0.92)
fig.savefig(os.path.join(OUTDIR, 'effects_correlation_heatmap.png'), dpi=180, bbox_inches='tight', pad_inches=0.3)
plt.close()
print('Saved effects_correlation_heatmap.png')

# ── Co-occurrence cluster network ──────────────────────────────────────────
import matplotlib.lines as mlines
corr_raw = trend[DRIVER_ORDER].corr()

CLUSTER_DEF = {
    'Contractual Compliance Cluster': {
        'members': ['compliance_and_regulatory', 'contract_management', 'delayed_payments', 'general_project_issues'],
        'color': '#1f77b4',
    },
    'Admin–Procurement Linkage': {
        'members': ['miscellaneous_administrative', 'procurement_irregularities'],
        'color': '#e67e00',
    },
    'Finance–Delays Nexus': {
        'members': ['budget_and_funding_issues', 'delays_and_time_overruns', 'infrastructure_and_equipment'],
        'color': '#c0392b',
    },
    'Independent Drivers': {
        'members': ['governance_and_controls', 'human_resources', 'land_and_right_of_way', 'claims_and_liabilities'],
        'color': '#555555',
    },
}

# Generous node spacing — nodes are rectangular boxes so need more room
NODE_POS = {
    'compliance_and_regulatory':    (-4.2,  2.8),
    'contract_management':           (-1.8,  2.8),
    'delayed_payments':              (-4.2,  1.0),
    'general_project_issues':        (-1.8,  1.0),
    'miscellaneous_administrative':  ( 2.2,  2.8),
    'procurement_irregularities':    ( 4.2,  1.4),
    'budget_and_funding_issues':     (-1.5, -2.0),
    'delays_and_time_overruns':      ( 1.5, -2.0),
    'infrastructure_and_equipment':  ( 0.0, -3.6),
    'governance_and_controls':       ( 0.0,  0.0),
    'human_resources':               (-4.5, -1.5),
    'land_and_right_of_way':         ( 4.5, -1.5),
    'claims_and_liabilities':        ( 0.0, -5.0),
}

driver_to_cluster = {}
driver_to_color = {}
for cname, cinfo in CLUSTER_DEF.items():
    for d in cinfo['members']:
        driver_to_cluster[d] = cname
        driver_to_color[d] = cinfo['color']

THRESH = 0.65
# Node box half-sizes (width, height) in data units — large enough for two-line labels
BOX_W = 1.05
BOX_H = 0.42

fig, ax = plt.subplots(figsize=(18, 14))
ax.set_xlim(-6.2, 6.2)
ax.set_ylim(-6.0, 4.5)
ax.set_facecolor('#f7f8fa')
ax.axis('off')

# ── cluster background halos ──
halo_specs = {
    'Contractual Compliance Cluster': (-3.0,  1.9, 2.15, 1.40),
    'Admin–Procurement Linkage':      ( 3.2,  2.1, 1.55, 1.00),
    'Finance–Delays Nexus':           ( 0.0, -2.5, 1.90, 1.90),
}
# Custom label anchors so cluster titles stay clear of node boxes/edge labels.
cluster_label_pos = {
    'Contractual Compliance Cluster': (-3.0, 4.0),
    'Admin–Procurement Linkage':      ( 3.2, 3.8),
    'Finance–Delays Nexus':           ( 0.0, -0.85),
}
for cname, (cx, cy, rx, ry) in halo_specs.items():
    cinfo = CLUSTER_DEF[cname]
    ell = matplotlib.patches.Ellipse(
        (cx, cy), width=(rx + 0.6) * 2, height=(ry + 0.6) * 2,
        color=cinfo['color'], alpha=0.09, zorder=0,
    )
    ax.add_patch(ell)
    tx, ty = cluster_label_pos.get(cname, (cx, cy + ry + 0.70))
    ax.text(tx, ty, cname,
            ha='center', va='bottom', fontsize=11, fontweight='bold',
            color=cinfo['color'], zorder=5)

# ── edges (drawn before nodes so nodes sit on top) ──
placed_r_labels = []


def inside_any_node_box(xp, yp, pad=0.10):
    for nx, ny in NODE_POS.values():
        if abs(xp - nx) <= (BOX_W + pad) and abs(yp - ny) <= (BOX_H + pad):
            return True
    return False


def too_close_to_existing_r_label(xp, yp, min_dist_sq=0.16):
    for px, py in placed_r_labels:
        if (xp - px) ** 2 + (yp - py) ** 2 < min_dist_sq:
            return True
    return False


for i, d1 in enumerate(DRIVER_ORDER):
    for j, d2 in enumerate(DRIVER_ORDER):
        if j >= i:
            continue
        r = corr_raw.loc[d1, d2]
        if abs(r) < THRESH:
            continue
        x1, y1 = NODE_POS[d1]
        x2, y2 = NODE_POS[d2]
        same_cluster = driver_to_cluster.get(d1) == driver_to_cluster.get(d2)
        lw = abs(r) * 5.5
        color = driver_to_color.get(d1, '#aaaaaa') if same_cluster else '#bbbbbb'
        alpha = 0.70 if same_cluster else 0.25
        ax.plot([x1, x2], [y1, y2], '-', color=color, lw=lw, alpha=alpha, zorder=1)

        # Collision-aware r-label placement around edge midpoint.
        base_mx, base_my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = (x2 - x1), (y2 - y1)
        norm = np.hypot(dx, dy)
        if norm == 0:
            continue
        nx, ny = (-dy / norm), (dx / norm)

        offsets = [0.18, -0.18, 0.34, -0.34, 0.52, -0.52, 0.72, -0.72, 0.92, -0.92]
        if not same_cluster:
            offsets = [-o for o in offsets]

        chosen = None
        for off in offsets:
            cx = base_mx + nx * off
            cy = base_my + ny * off
            if inside_any_node_box(cx, cy, pad=0.10):
                continue
            if too_close_to_existing_r_label(cx, cy, min_dist_sq=0.16):
                continue
            chosen = (cx, cy)
            break

        if chosen is None:
            # Last-resort fallback: keep it visible, but never inside node boxes.
            cx = base_mx + nx * 1.10
            cy = base_my + ny * 1.10
            if inside_any_node_box(cx, cy, pad=0.10):
                continue
            chosen = (cx, cy)

        mx, my = chosen
        placed_r_labels.append((mx, my))
        ax.text(
            mx, my, f'{r:.2f}',
            ha='center', va='center',
            fontsize=8.5, fontweight='bold', color='#111111',
            bbox=dict(boxstyle='round,pad=0.24', fc='white', ec='#666666', lw=0.7, alpha=0.97),
            zorder=6,
        )

# ── nodes as clearly labelled boxes ──
for d in DRIVER_ORDER:
    x, y = NODE_POS[d]
    clr = driver_to_color.get(d, '#888888')

    # Rounded rectangle background
    fancy = matplotlib.patches.FancyBboxPatch(
        (x - BOX_W, y - BOX_H), BOX_W * 2, BOX_H * 2,
        boxstyle='round,pad=0.08',
        facecolor=clr, edgecolor='white', linewidth=2.2, zorder=3,
    )
    ax.add_patch(fancy)

    # Wrap label into two lines if needed
    words = LABELS[d].split()
    mid = (len(words) + 1) // 2
    line1 = ' '.join(words[:mid])
    line2 = ' '.join(words[mid:]) if len(words) > mid else ''
    label_text = f'{line1}\n{line2}' if line2 else line1

    ax.text(x, y, label_text,
            ha='center', va='center',
            fontsize=8.5, fontweight='bold', color='white',
            linespacing=1.35, zorder=4)

# ── legends ──
# Edge weight legend
edge_handles = []
for r_val, lbl in [(0.90, 'r ≥ 0.90'), (0.75, 'r = 0.75'), (0.65, 'r = 0.65')]:
    edge_handles.append(
        mlines.Line2D([], [], color='#888888', lw=r_val * 5.5, label=lbl)
    )
leg1 = ax.legend(handles=edge_handles, title='Edge weight (Pearson r)',
                 loc='lower left', fontsize=9, title_fontsize=9,
                 framealpha=0.92, edgecolor='#cccccc')
ax.add_artist(leg1)

# Cluster colour legend
cluster_handles = [
    mlines.Line2D([], [], marker='s', color='w',
                  markerfacecolor=ci['color'], markersize=12, label=cn)
    for cn, ci in CLUSTER_DEF.items()
]
ax.legend(handles=cluster_handles, title='Cluster',
          loc='lower right', fontsize=9, title_fontsize=9,
          framealpha=0.92, edgecolor='#cccccc')

ax.set_title(
    'Co-occurrence Cluster Network\nDispute Drivers by Correlation Structure (Pearson r, 2018–2025)',
    fontsize=14, fontweight='bold', pad=16,
)
fig.savefig(os.path.join(OUTDIR, 'effects_cooccurrence_clusters.png'), dpi=220, bbox_inches='tight', pad_inches=0.35)
plt.close()
print('Saved effects_cooccurrence_clusters.png')

yearly_totals = trend[DRIVER_ORDER].sum(axis=1)
norm = trend[DRIVER_ORDER].div(yearly_totals, axis=0) * 100
clusters = {
    'Procurement & Compliance': ['procurement_irregularities', 'compliance_and_regulatory', 'contract_management'],
    'Delays & Finance': ['delays_and_time_overruns', 'delayed_payments', 'budget_and_funding_issues'],
    'Governance & HR': ['governance_and_controls', 'human_resources', 'claims_and_liabilities'],
    'Infrastructure & Admin': ['infrastructure_and_equipment', 'miscellaneous_administrative', 'general_project_issues', 'land_and_right_of_way'],
}
cluster_colors = {
    'Procurement & Compliance': '#1f77b4',
    'Delays & Finance': '#d62728',
    'Governance & HR': '#9467bd',
    'Infrastructure & Admin': '#2ca02c',
}
line_styles = ['-', '--', '-.', ':']
fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharey=False)
fig.suptitle('Proportional Share of Annual Audit Mentions by Driver Group\n(normalised % of annual total, 2018–2025)', fontsize=13, fontweight='bold')
for ax, (cluster, drivers) in zip(axes.flatten(), clusters.items()):
    color = cluster_colors[cluster]
    for idx, driver in enumerate(drivers):
        ax.plot(norm.index, norm[driver], marker='o', linestyle=line_styles[idx % len(line_styles)], color=color, alpha=min(0.5 + 0.15 * idx, 0.95), linewidth=1.8, label=LABELS[driver])
    ax.set_title(cluster, fontsize=11, fontweight='bold')
    ax.set_xlabel('Year')
    ax.set_ylabel('Share of annual mentions (%)')
    ax.legend(fontsize=8, loc='upper left')
    ax.set_xticks(norm.index)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, 'effects_normalised_trends.png'), dpi=180, bbox_inches='tight')
plt.close()
print('Saved effects_normalised_trends.png')

summary = pd.DataFrame(index=DRIVER_ORDER)
summary['label'] = [LABELS[d] for d in DRIVER_ORDER]
summary['total_mentions'] = counts.values
summary['pct_of_corpus'] = (summary['total_mentions'] / N * 100).round(1)
summary['trend_slope'] = trend_summary['trend_slope']
summary['trend_r2'] = trend_summary['trend_r2']
summary['trend_p'] = trend_summary['trend_p']
summary['direction'] = trend_summary['direction']
summary['financial_flagged_sentences'] = financial['financial_flagged_sentences']
summary['financial_coverage_pct'] = financial['financial_coverage_pct']
summary['median_effect_bn'] = financial['median_effect_bn']
summary['p75_effect_bn'] = financial['p75_effect_bn']
summary['high_impact_cases_100bn'] = financial['high_impact_cases_100bn']
summary['weighted_exposure_index'] = financial['weighted_exposure_index']
summary.to_csv(os.path.join(BASE, 'effects_summary_table.csv'), index=True)
print('Saved effects_summary_table.csv')
print(summary[['label', 'total_mentions', 'trend_slope', 'financial_flagged_sentences', 'financial_coverage_pct', 'median_effect_bn', 'high_impact_cases_100bn', 'weighted_exposure_index']].to_string())
print(f'Global 95th percentile cap (UGX billions): {q95/1e9:.2f}')
