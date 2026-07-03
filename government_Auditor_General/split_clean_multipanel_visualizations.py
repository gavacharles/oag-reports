from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


BASE = Path('/Users/charlesgava/Downloads/Temporal Analysis Research /output/results/government_Auditor_General')
PLOTS = BASE / 'plots_png'
PLOTS.mkdir(parents=True, exist_ok=True)

sns.set_theme(style='whitegrid', context='talk')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['savefig.facecolor'] = 'white'


def save_clean(fig, stem: str):
    fig.tight_layout()
    fig.savefig(PLOTS / f'{stem}.png', dpi=220, bbox_inches='tight', pad_inches=0.25)
    plt.close(fig)
    print(f'Saved: {stem}.png')


def labelize(s: str) -> str:
    return ' '.join('&' if p == 'and' else p.capitalize() for p in s.split('_'))


# ─────────────────────────────────────────────────────────────────────────────
# Load core data
# ─────────────────────────────────────────────────────────────────────────────
corpus = pd.read_csv(BASE / 'oag_infrastructure_sentence_corpus_2017_2025.csv')
corpus_exp = pd.read_csv(BASE / 'oag_infrastructure_sentence_corpus_2017_2025_expanded.csv')
trends = pd.read_csv(BASE / 'driver_trend_by_year_2017_2025.csv').set_index('year')
trends_exp = pd.read_csv(BASE / 'driver_trend_by_year_2017_2025_expanded.csv').set_index('year')
classifications = pd.read_csv(BASE / 'audit_infrastructure_classifications_improved.csv')
pfa_scores = pd.read_csv(BASE / 'pfa_factor_scores_2017_2025.csv')
effects = pd.read_csv(BASE / 'effects_summary_table.csv', index_col=0)
location_summary = pd.read_csv(BASE / 'spatial_location_summary.csv')
region_summary = pd.read_csv(BASE / 'spatial_region_summary.csv', index_col=0)
centrality_df = pd.read_csv(BASE / 'actor_centrality_metrics.csv')
edges_df = pd.read_csv(BASE / 'actor_edges.csv')
network_stats = pd.read_json(BASE / 'network_analysis_statistics.json', typ='series')
loadings_terms = pd.read_csv(BASE / 'pfa_factor_loadings_terms.csv')

# ─────────────────────────────────────────────────────────────────────────────
# 1. Split effects_financial_exposure into two clean visuals
# ─────────────────────────────────────────────────────────────────────────────
plot_fin = effects.sort_values('weighted_exposure_index', ascending=True)
labels = [labelize(i) for i in plot_fin.index]

fig, ax = plt.subplots(figsize=(13, 8))
colors = ['#c0392b' if v >= plot_fin['weighted_exposure_index'].median() else '#f39c12' for v in plot_fin['weighted_exposure_index']]
bars = ax.barh(labels, plot_fin['weighted_exposure_index'], color=colors, edgecolor='white', height=0.72)
for bar, val in zip(bars, plot_fin['weighted_exposure_index']):
    ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height()/2, f'{val:.1f}', va='center', fontsize=9)
ax.set_title('Breadth-Adjusted Financial Exposure by Driver', fontweight='bold', pad=14)
ax.set_xlabel(
    'Weighted Exposure Index  =  Flagged Cases  ×  log(1 + Median UGX Billions)',
    labelpad=10,
)
ax.set_ylabel('Dispute Driver', labelpad=10)
ax.tick_params(axis='y', labelsize=10)
ax.tick_params(axis='x', labelsize=9)
ax.grid(axis='x', alpha=0.25)
fig.subplots_adjust(left=0.28, bottom=0.12, right=0.95, top=0.92)
fig.savefig(PLOTS / 'effects_financial_exposure_index.png', dpi=220, bbox_inches='tight', pad_inches=0.3)
plt.close(fig)
print('Saved: effects_financial_exposure_index.png')

fig, ax = plt.subplots(figsize=(10, 7))
scatter = ax.scatter(
    plot_fin['median_effect_bn'].replace(0, np.nan),
    plot_fin['financial_coverage_pct'],
    s=plot_fin['high_impact_cases_100bn'].replace(0, 1) * 180,
    c=plot_fin['weighted_exposure_index'],
    cmap='YlOrRd',
    alpha=0.82,
    edgecolors='black',
)
for driver, row in plot_fin.iterrows():
    if row['median_effect_bn'] > 0:
        if driver == 'land_and_right_of_way':
            ax.annotate(
                labelize(driver),
                (row['median_effect_bn'], row['financial_coverage_pct']),
                xytext=(-58, 14),
                textcoords='offset points',
                ha='right',
                va='center',
                fontsize=8,
                bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.80),
                arrowprops=dict(arrowstyle='->', color='#555555', lw=0.8),
            )
        else:
            ax.annotate(
                labelize(driver),
                (row['median_effect_bn'], row['financial_coverage_pct']),
                xytext=(6, 4),
                textcoords='offset points',
                fontsize=8,
            )
ax.set_xscale('log')
ax.set_title('Financial Severity vs Coverage by Driver', fontweight='bold', pad=12)
ax.set_xlabel('Median effect amount (UGX billions, log scale)')
ax.set_ylabel('Coverage (% of driver sentences)', labelpad=10, fontsize=9)
ax.grid(alpha=0.25)
cbar = plt.colorbar(scatter, ax=ax, shrink=0.52, fraction=0.04, pad=0.03, aspect=24)
cbar.set_label('Weighted exposure index')
cbar.ax.tick_params(labelsize=7)
fig.subplots_adjust(left=0.24, right=0.90, bottom=0.12, top=0.92)
fig.savefig(PLOTS / 'effects_financial_exposure_severity_coverage.png', dpi=220, bbox_inches='tight', pad_inches=0.32)
plt.close(fig)
print('Saved: effects_financial_exposure_severity_coverage.png')

# ─────────────────────────────────────────────────────────────────────────────
# 2. Split effects_normalised_trends into four clean visuals
# ─────────────────────────────────────────────────────────────────────────────
clusters = {
    'procurement_compliance': ['procurement_irregularities', 'compliance_and_regulatory', 'contract_management'],
    'delays_finance': ['delays_and_time_overruns', 'delayed_payments', 'budget_and_funding_issues'],
    'governance_hr': ['governance_and_controls', 'human_resources', 'claims_and_liabilities'],
    'infrastructure_admin': ['infrastructure_and_equipment', 'miscellaneous_administrative', 'general_project_issues', 'land_and_right_of_way'],
}
yearly_totals = trends_exp.sum(axis=1)
norm = trends_exp.div(yearly_totals, axis=0) * 100
palette_map = {
    'procurement_compliance': '#1f77b4',
    'delays_finance': '#d62728',
    'governance_hr': '#9467bd',
    'infrastructure_admin': '#2ca02c',
}
line_styles = ['-', '--', '-.', ':']
for cluster_key, drivers in clusters.items():
    fig, ax = plt.subplots(figsize=(10, 6.5))
    for idx, driver in enumerate(drivers):
        if driver in norm.columns:
            ax.plot(norm.index, norm[driver], marker='o', linestyle=line_styles[idx % len(line_styles)], color=palette_map[cluster_key], alpha=min(0.55 + 0.12 * idx, 0.95), linewidth=2.2, label=labelize(driver))
    ax.set_title(f"Normalized Trend Share — {cluster_key.replace('_', ' ').title()}", fontweight='bold', pad=12)
    ax.set_xlabel('Year')
    ax.set_ylabel('Share of annual mentions (%)')
    ax.set_xticks(norm.index)
    ax.grid(axis='y', alpha=0.25)
    ax.legend(fontsize=9, frameon=True)
    save_clean(fig, f'effects_normalised_trends_{cluster_key}')

# ─────────────────────────────────────────────────────────────────────────────
# 3. Split spatial map figure into map and region totals
# ─────────────────────────────────────────────────────────────────────────────
UGANDA_POLYGON = [
    (29.58, -1.48), (30.15, -1.47), (31.00, -1.43), (31.90, -1.45),
    (33.05, -1.02), (34.22, 0.95), (34.45, 1.72), (34.25, 3.58),
    (33.80, 4.22), (33.20, 4.20), (32.60, 3.55), (31.90, 3.48),
    (31.42, 3.86), (30.72, 3.62), (30.38, 3.20), (29.74, 2.25),
    (29.60, 1.35), (29.60, 0.30), (29.58, -1.48),
]
REGION_COLORS = {'Central': '#4c78a8', 'Eastern': '#f58518', 'Northern': '#54a24b', 'Western': '#e45756'}
fig, ax = plt.subplots(figsize=(9.5, 8))
poly_x = [p[0] for p in UGANDA_POLYGON]
poly_y = [p[1] for p in UGANDA_POLYGON]
ax.fill(poly_x, poly_y, color='#f5f5f5', edgecolor='#444444', linewidth=1.2, zorder=1)
ax.plot(poly_x, poly_y, color='#444444', linewidth=1.2, zorder=2)
for _, row in location_summary.head(18).iterrows():
    ax.scatter(row['lon'], row['lat'], s=55 + row['matched_sentences'] * 14, color=REGION_COLORS[row['region']], alpha=0.78, edgecolors='black', linewidths=0.8, zorder=3)
    ax.text(row['lon'] + 0.05, row['lat'] + 0.03, f"{row['location']} ({row['matched_sentences']})", fontsize=8)
for region, color in REGION_COLORS.items():
    ax.scatter([], [], s=140, color=color, alpha=0.78, edgecolors='black', label=region)
ax.legend(loc='upper left', fontsize=9, title='Macro-region')
ax.set_xlim(29.3, 34.9)
ax.set_ylim(-1.7, 4.5)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Spatial Distribution of Matched Dispute Mentions', fontweight='bold', pad=12)
ax.grid(alpha=0.15)
save_clean(fig, 'spatial_dispute_map_locations_only')

fig, ax = plt.subplots(figsize=(8.5, 6))
rs = region_summary.iloc[:, 0] if isinstance(region_summary, pd.DataFrame) else region_summary
bars = ax.bar(rs.index, rs.values, color=[REGION_COLORS[r] for r in rs.index], edgecolor='white')
for bar, value in zip(bars, rs.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, str(int(value)), ha='center', va='bottom', fontsize=10)
ax.set_title('Regional Distribution of Spatially Matched Sentences', fontweight='bold', pad=12)
ax.set_ylabel('Unique matched sentences')
ax.grid(axis='y', alpha=0.25)
save_clean(fig, 'spatial_dispute_region_totals_only')

# ─────────────────────────────────────────────────────────────────────────────
# 4. Split trends with breakdown
# ─────────────────────────────────────────────────────────────────────────────
other_df = corpus[corpus['driver_label'] == 'other'].copy()
def categorize_other(sentence):
    s = str(sentence).lower()
    if 'delay' in s or 'late' in s or 'behind' in s:
        return 'Delays & Time Overruns'
    elif 'budget' in s or 'fund' in s or 'unspent' in s:
        return 'Budget & Funding Issues'
    elif 'compliance' in s or 'regulation' in s or 'law' in s:
        return 'Compliance & Regulatory'
    elif 'staff' in s or 'personnel' in s or 'capacity' in s:
        return 'Human Resources'
    elif 'infrastructure' in s or 'equipment' in s or 'facility' in s:
        return 'Infrastructure & Equipment'
    elif 'project' in s:
        return 'General Project Issues'
    return 'Miscellaneous Administrative'
other_df['other_category'] = other_df['sentence'].apply(categorize_other)
other_breakdown = other_df.groupby(['year', 'other_category']).size().unstack(fill_value=0)

fig, ax = plt.subplots(figsize=(11, 7))
trends.T.plot(ax=ax, marker='o', linewidth=2.2, markersize=7)
ax.set_title('Dispute Driver Trends by Year (Including Other)', fontweight='bold', pad=12)
ax.set_xlabel('Dispute driver')
ax.set_ylabel('Frequency')
ax.legend(title='Year', bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8)
ax.grid(alpha=0.25)
ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha='right', fontsize=10)
save_clean(fig, 'dispute_driver_trends_main_only')

fig, ax = plt.subplots(figsize=(10.5, 6.5))
other_breakdown.plot(kind='bar', stacked=False, ax=ax, width=0.8, color=sns.color_palette('Set2', len(other_breakdown.columns)))
ax.set_title('Other Category Breakdown by Sub-Type', fontweight='bold', pad=12)
ax.set_xlabel('Year')
ax.set_ylabel('Frequency')
ax.legend(title='Other sub-category', bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8)
ax.grid(axis='y', alpha=0.25)
ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=10)
save_clean(fig, 'dispute_driver_other_breakdown_only')

# ─────────────────────────────────────────────────────────────────────────────
# 5. Split comprehensive pies and comparison
# ─────────────────────────────────────────────────────────────────────────────
expanded_tax = corpus_exp['driver_label_expanded'].value_counts().rename_axis('driver').reset_index(name='count')
colors_pie = sns.color_palette('Set3', len(expanded_tax))
fig, ax = plt.subplots(figsize=(10, 8.5))
wedges, texts, autotexts = ax.pie(expanded_tax['count'], labels=[labelize(d) for d in expanded_tax['driver']], autopct='%1.1f%%', colors=colors_pie, startangle=90, textprops={'fontsize': 9})
for autotext in autotexts:
    autotext.set_color('white'); autotext.set_fontweight('bold'); autotext.set_fontsize(8)
ax.set_title('Overall Dispute Driver Distribution', fontweight='bold', pad=14)
save_clean(fig, 'comprehensive_pie_overall_distribution')

recent = corpus_exp[corpus_exp['year'].isin([2024, 2025])]['driver_label_expanded'].value_counts()
fig, ax = plt.subplots(figsize=(10, 8.5))
wedges, texts, autotexts = ax.pie(recent.values, labels=[labelize(d) for d in recent.index], autopct='%1.1f%%', colors=colors_pie[:len(recent)], startangle=90, textprops={'fontsize': 9})
for autotext in autotexts:
    autotext.set_color('white'); autotext.set_fontweight('bold'); autotext.set_fontsize(8)
ax.set_title('Recent Period Distribution (2024–2025)', fontweight='bold', pad=14)
save_clean(fig, 'comprehensive_pie_recent_distribution')

orig_tax = corpus['driver_label'].value_counts(dropna=False).rename_axis('driver').reset_index(name='count').sort_values('count', ascending=False)
fig, ax = plt.subplots(figsize=(10, 7))
colors = sns.color_palette('rocket_r', len(orig_tax))
ax.barh(range(len(orig_tax)), orig_tax['count'], color=colors, edgecolor='black', linewidth=1.1, alpha=0.88)
ax.set_yticks(range(len(orig_tax)))
ax.set_yticklabels([labelize(d) for d in orig_tax['driver']], fontsize=10)
ax.set_xlabel('Count')
ax.set_title('Original Classification (with Other)', fontweight='bold', pad=12)
ax.grid(axis='x', alpha=0.25)
ax.invert_yaxis()
save_clean(fig, 'comprehensive_comparison_original_only')

fig, ax = plt.subplots(figsize=(10, 7))
top_10 = expanded_tax.head(10)
colors = sns.color_palette('viridis', len(top_10))
ax.barh(range(len(top_10)), top_10['count'], color=colors, edgecolor='black', linewidth=1.1, alpha=0.88)
ax.set_yticks(range(len(top_10)))
ax.set_yticklabels([labelize(d) for d in top_10['driver']], fontsize=10)
ax.set_xlabel('Count')
ax.set_title('Expanded Classification (Top 10 Categories)', fontweight='bold', pad=12)
ax.grid(axis='x', alpha=0.25)
ax.invert_yaxis()
save_clean(fig, 'comprehensive_comparison_expanded_only')

# ─────────────────────────────────────────────────────────────────────────────
# 6. Split PFA distributions and correlation/loadings
# ─────────────────────────────────────────────────────────────────────────────
for i in range(1, 7):
    factor = f'factor_{i}'
    fig, ax = plt.subplots(figsize=(10, 6.5))
    for year in sorted(pfa_scores['year'].unique()):
        year_data = pfa_scores[pfa_scores['year'] == year][factor]
        ax.hist(year_data, bins=30, alpha=0.45, label=str(year))
    ax.set_title(f'FA Factor {i} Distribution Across Years', fontweight='bold', pad=12)
    ax.set_xlabel('Factor score')
    ax.set_ylabel('Frequency')
    ax.legend(fontsize=8, ncol=2)
    ax.grid(alpha=0.25)
    save_clean(fig, f'pfa_factor_distribution_factor_{i}')

long_df = pfa_scores.melt(id_vars='year', value_vars=[f'factor_{i}' for i in range(1, 7)], var_name='factor', value_name='score')
fig, ax = plt.subplots(figsize=(10, 7))
sns.boxplot(data=long_df, x='score', y='factor', hue='factor', dodge=False, palette='Set2', linewidth=1, fliersize=2, ax=ax)
if ax.legend_ is not None:
    ax.legend_.remove()
ax.axvline(0, color='black', linewidth=1, linestyle='--', alpha=0.6)
ax.set_title('Distribution of FA Factor Scores', fontweight='bold', pad=12)
ax.set_xlabel('Factor score')
ax.set_ylabel('Factor')
save_clean(fig, 'pfa_factor_score_distribution_boxplot')

fig, ax = plt.subplots(figsize=(8, 6.8))
corr = pfa_scores[[f'factor_{i}' for i in range(1, 7)]].corr()
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0, square=True, linewidths=0.5, cbar_kws={'label': 'Correlation', 'shrink': 0.82}, ax=ax)
ax.set_title('Correlation Between FA Factors', fontweight='bold', pad=12)
save_clean(fig, 'pfa_factor_correlation_heatmap_only')

for factor in sorted(loadings_terms['factor'].unique(), key=lambda v: int(v.split('_')[1])):
    factor_num = int(factor.split('_')[1])
    data = loadings_terms[loadings_terms['factor'] == factor].sort_values('loading')
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = data['direction'].map({'Positive': '#1f77b4', 'Negative': '#d62728'})
    ax.barh(data['term'], data['loading'], color=colors, edgecolor='black', linewidth=0.7)
    ax.axvline(0, color='black', linestyle='--', linewidth=1)
    ax.set_title(f'Factor {factor_num} Term Loadings', fontweight='bold', pad=12)
    ax.set_xlabel('Loading')
    ax.set_ylabel('')
    save_clean(fig, f'pfa_loading_factor_{factor_num}')

# ─────────────────────────────────────────────────────────────────────────────
# 7. Split actor-network multi-panel figures
# ─────────────────────────────────────────────────────────────────────────────
# Centrality figure panels
fig, ax = plt.subplots(figsize=(10, 7))
top_actors = centrality_df.head(15)
colors = ['#e74c3c' if d > 10 else '#3498db' if d > 5 else '#95a5a6' for d in top_actors['degree']]
ax.barh(range(len(top_actors)), top_actors['degree'], color=colors)
ax.set_yticks(range(len(top_actors)))
ax.set_yticklabels([a[:40] + '...' if len(a) > 40 else a for a in top_actors['actor']], fontsize=9)
for i, v in enumerate(top_actors['degree']):
    ax.text(v + 0.5, i, str(v), va='center', fontsize=8, fontweight='bold')
ax.set_xlabel('Network degree (connections)')
ax.set_title('Top 15 Actors by Network Centrality', fontweight='bold', pad=12)
ax.invert_yaxis(); ax.grid(axis='x', alpha=0.25)
save_clean(fig, 'network_actor_centrality_top_actors_only')

fig, ax = plt.subplots(figsize=(8.5, 6.8))
type_counts = centrality_df['type'].value_counts()
colors_pie = sns.color_palette('Set2', len(type_counts))
ax.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%', colors=colors_pie, startangle=90, textprops={'fontsize': 10})
ax.set_title('Actor Type Distribution', fontweight='bold', pad=12)
save_clean(fig, 'network_actor_type_distribution_only')

fig, ax = plt.subplots(figsize=(9, 6.5))
type_driver_diversity = centrality_df.groupby('type')['driver_diversity'].mean().sort_values(ascending=False)
ax.bar(range(len(type_driver_diversity)), type_driver_diversity.values, color=sns.color_palette('viridis', len(type_driver_diversity)))
ax.set_xticks(range(len(type_driver_diversity)))
ax.set_xticklabels(type_driver_diversity.index, rotation=35, ha='right', fontsize=10)
for i, v in enumerate(type_driver_diversity.values):
    ax.text(i, v + 0.08, f'{v:.1f}', ha='center', fontsize=9, fontweight='bold')
ax.set_ylabel('Average number of dispute drivers')
ax.set_title('Driver Diversity by Actor Type', fontweight='bold', pad=12)
ax.grid(axis='y', alpha=0.25)
save_clean(fig, 'network_actor_driver_diversity_only')

fig, ax = plt.subplots(figsize=(10, 6.8))
driver_connections = centrality_df['top_driver'].value_counts().head(10)
ax.barh(range(len(driver_connections)), driver_connections.values, color=sns.color_palette('coolwarm', len(driver_connections)))
ax.set_yticks(range(len(driver_connections)))
ax.set_yticklabels([labelize(d)[:30] for d in driver_connections.index], fontsize=10)
for i, v in enumerate(driver_connections.values):
    ax.text(v + 0.2, i, str(v), va='center', fontsize=8, fontweight='bold')
ax.set_xlabel('Count of actors for which the driver is dominant')
ax.set_title('Top Dominant Dispute Drivers Across Actors', fontweight='bold', pad=12)
ax.invert_yaxis(); ax.grid(axis='x', alpha=0.25)
save_clean(fig, 'network_top_drivers_only')

# Systemic risk figure panels
scatter_data = centrality_df.head(15).copy()
colors_risk = []
for _, row in scatter_data.iterrows():
    if row['degree'] > 10 and row['driver_diversity'] > 3:
        colors_risk.append('#e74c3c')
    elif row['degree'] > 5 or row['driver_diversity'] > 2:
        colors_risk.append('#f39c12')
    else:
        colors_risk.append('#95a5a6')
fig, ax = plt.subplots(figsize=(8.8, 7))
ax.scatter(scatter_data['degree'], scatter_data['driver_diversity'], s=scatter_data['total_mentions'] * 20, c=colors_risk, alpha=0.65, edgecolors='black', linewidth=1)
ax.axvline(x=scatter_data['degree'].median(), color='gray', linestyle='--', alpha=0.5)
ax.axhline(y=scatter_data['driver_diversity'].median(), color='gray', linestyle='--', alpha=0.5)
for _, row in scatter_data.iterrows():
    if row['degree'] > 10 or row['driver_diversity'] > 3:
        ax.annotate(row['actor'][:25], (row['degree'], row['driver_diversity']), fontsize=7, alpha=0.75, xytext=(5, 5), textcoords='offset points')
ax.set_xlabel('Network centrality (degree)')
ax.set_ylabel('Dispute driver diversity')
ax.set_title('Systemic Risk Matrix', fontweight='bold', pad=12)
ax.grid(True, alpha=0.25)
save_clean(fig, 'network_systemic_risk_matrix_only')

fig, ax = plt.subplots(figsize=(9.2, 6.5))
summary_labels = ['Total actors', 'Relationships', 'Density ×1000', 'Avg conn./actor', 'Max connections']
summary_values = [
    float(network_stats['total_actors']),
    float(network_stats['total_relationships']),
    float(network_stats['network_density']) * 1000,
    float(network_stats['avg_connections_per_actor']),
    float(network_stats['max_connections']),
]
bars = ax.bar(summary_labels, summary_values, color=['#4c78a8', '#f58518', '#54a24b', '#e45756', '#72b7b2'], edgecolor='white')
for bar, value in zip(bars, summary_values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(summary_values)*0.02, f'{value:.2f}' if value % 1 else f'{int(value)}', ha='center', va='bottom', fontsize=9)
ax.set_title('Network Summary Metrics', fontweight='bold', pad=12)
ax.set_ylabel('Value')
ax.tick_params(axis='x', rotation=20)
ax.grid(axis='y', alpha=0.25)
save_clean(fig, 'network_summary_metrics_only')

fig, ax = plt.subplots(figsize=(10, 6.8))
type_driver_matrix = pd.crosstab(centrality_df['type'], centrality_df['top_driver'])
sns.heatmap(type_driver_matrix, annot=True, fmt='d', cmap='YlOrRd', cbar_kws={'label': 'Count'}, ax=ax, linewidths=0.5)
ax.set_xlabel('Dominant dispute driver'); ax.set_ylabel('Actor type')
ax.set_title('Actor Type vs Dominant Dispute Driver', fontweight='bold', pad=12)
plt.setp(ax.get_xticklabels(), rotation=35, ha='right', fontsize=9)
plt.setp(ax.get_yticklabels(), rotation=0, fontsize=9)
save_clean(fig, 'network_actor_type_driver_heatmap_only')

centrality_df = centrality_df.copy()
centrality_df['risk_score'] = centrality_df['degree'] * centrality_df['driver_diversity']
top_risk = centrality_df.nlargest(10, 'risk_score')
fig, ax = plt.subplots(figsize=(10.2, 7))
ax.barh(range(len(top_risk)), top_risk['risk_score'], color=sns.color_palette('Reds_r', len(top_risk)))
ax.set_yticks(range(len(top_risk)))
ax.set_yticklabels([f"{a[:35]}..." if len(a) > 35 else a for a in top_risk['actor']], fontsize=9)
for i, (_, row) in enumerate(top_risk.iterrows()):
    ax.text(row['risk_score'] + 1, i, f"{row['risk_score']:.0f} ({row['type'][:10]})", va='center', fontsize=7)
ax.set_xlabel('Risk score (degree × diversity)')
ax.set_title('Top 10 Systemic Risk Nodes', fontweight='bold', pad=12)
ax.invert_yaxis(); ax.grid(axis='x', alpha=0.25)
save_clean(fig, 'network_top_risk_nodes_only')

print('Done splitting major multi-panel visualizations.')
