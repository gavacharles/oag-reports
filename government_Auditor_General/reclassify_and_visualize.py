import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Create output directory
import os
output_dir = '/Users/charlesgava/Downloads/Temporal Analysis Research /output/results/government_Auditor_General/plots_png'
os.makedirs(output_dir, exist_ok=True)

print("="*80)
print("COMPREHENSIVE DISPUTE DRIVER RECLASSIFICATION & VISUALIZATION")
print("="*80)

# ===========================
# STEP 1: RECLASSIFY "OTHER" CATEGORY
# ===========================
print("\n[1/6] Reclassifying 'other' category into subtypes...")

corpus = pd.read_csv('/Users/charlesgava/Downloads/Temporal Analysis Research /output/results/government_Auditor_General/oag_infrastructure_sentence_corpus_2017_2025.csv')

def categorize_other(row):
    """Reclassify 'other' into specific subtypes"""
    if row['driver_label'] != 'other':
        return row['driver_label']
    
    sentence_lower = str(row['sentence']).lower()
    
    # Prioritized classification rules
    if any(word in sentence_lower for word in ['delay', 'late', 'behind schedule', 'overrun', 'extension', 'postpone']):
        return 'delays_and_time_overruns'
    elif any(word in sentence_lower for word in ['budget', 'fund', 'unspent', 'absorption', 'release', 'disbursement', 'allocation']):
        return 'budget_and_funding_issues'
    elif any(word in sentence_lower for word in ['compliance', 'regulation', 'law', 'legal', 'statutory', 'policy', 'framework']):
        return 'compliance_and_regulatory'
    elif any(word in sentence_lower for word in ['staff', 'personnel', 'capacity', 'training', 'recruitment', 'human resource']):
        return 'human_resources'
    elif any(word in sentence_lower for word in ['infrastructure', 'equipment', 'facility', 'building', 'installation', 'machinery']):
        return 'infrastructure_and_equipment'
    elif 'project' in sentence_lower:
        return 'general_project_issues'
    else:
        return 'miscellaneous_administrative'

# Apply reclassification
corpus['driver_label_expanded'] = corpus.apply(categorize_other, axis=1)

# Save reclassified corpus
corpus.to_csv('/Users/charlesgava/Downloads/Temporal Analysis Research /output/results/government_Auditor_General/oag_infrastructure_sentence_corpus_2017_2025_expanded.csv', index=False)
print(f"✓ Reclassified {len(corpus)} sentences")
print(f"✓ Saved: oag_infrastructure_sentence_corpus_2017_2025_expanded.csv")

# ===========================
# STEP 2: CREATE EXPANDED TAXONOMY
# ===========================
print("\n[2/6] Creating expanded taxonomy...")

expanded_taxonomy = corpus['driver_label_expanded'].value_counts().reset_index()
expanded_taxonomy.columns = ['driver', 'count']
expanded_taxonomy = expanded_taxonomy.sort_values('count', ascending=False)

# Save expanded taxonomy
expanded_taxonomy.to_csv('/Users/charlesgava/Downloads/Temporal Analysis Research /output/results/government_Auditor_General/national_dispute_risk_taxonomy_2017_2025_expanded.csv', index=False)
print(f"✓ Created taxonomy with {len(expanded_taxonomy)} categories")
print(f"✓ Saved: national_dispute_risk_taxonomy_2017_2025_expanded.csv")

# Print summary
print("\nExpanded Taxonomy Summary:")
print(expanded_taxonomy.to_string(index=False))

# ===========================
# STEP 3: CREATE EXPANDED YEARLY TRENDS
# ===========================
print("\n[3/6] Creating expanded yearly trends...")

# Create year x driver matrix
expanded_trends = corpus.groupby(['year', 'driver_label_expanded']).size().unstack(fill_value=0)

# Save expanded trends
expanded_trends.to_csv('/Users/charlesgava/Downloads/Temporal Analysis Research /output/results/government_Auditor_General/driver_trend_by_year_2017_2025_expanded.csv')
print(f"✓ Created trends matrix: {expanded_trends.shape}")
print(f"✓ Saved: driver_trend_by_year_2017_2025_expanded.csv")

# ===========================
# STEP 4: VISUALIZATIONS
# ===========================
print("\n[4/6] Creating comprehensive visualizations...")

# 4.1: EXPANDED TAXONOMY BAR CHART
print("  → Creating expanded taxonomy chart...")
fig, ax = plt.subplots(figsize=(16, 10))
colors = sns.color_palette("Spectral", len(expanded_taxonomy))

bars = ax.barh(range(len(expanded_taxonomy)), expanded_taxonomy['count'], 
               color=colors, edgecolor='black', linewidth=1.2, alpha=0.85)

ax.set_yticks(range(len(expanded_taxonomy)))
ax.set_yticklabels([d.replace('_', ' ').title() for d in expanded_taxonomy['driver']], fontsize=12)

# Add value labels with percentages
total = expanded_taxonomy['count'].sum()
for i, count in enumerate(expanded_taxonomy['count']):
    pct = (count/total)*100
    ax.text(count + 10, i, f'{count} ({pct:.1f}%)', va='center', fontsize=11, fontweight='bold')

ax.set_xlabel('Count of Mentions (2017-2025)', fontsize=14, fontweight='bold')
ax.set_ylabel('Dispute Driver Category', fontsize=14, fontweight='bold')
ax.set_title('Comprehensive National Dispute Risk Taxonomy\nExpanded Classification with "Other" Breakdown (2017-2025)', 
             fontsize=17, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(f'{output_dir}/comprehensive_taxonomy.png', dpi=300, bbox_inches='tight')
print(f"    ✓ Saved: comprehensive_taxonomy.png")
plt.close()

# 4.2: EXPANDED HEATMAP
print("  → Creating expanded heatmap...")
fig, ax = plt.subplots(figsize=(18, 12))

# Sort drivers by total frequency
driver_totals = expanded_trends.sum(axis=0).sort_values(ascending=False)
sorted_trends = expanded_trends[driver_totals.index]

sns.heatmap(sorted_trends.T, annot=True, fmt='.0f', cmap='RdYlGn_r', 
            linewidths=0.5, linecolor='gray', cbar_kws={'label': 'Frequency'},
            ax=ax, square=False, robust=True, annot_kws={'fontsize': 9})

ax.set_xlabel('Year', fontsize=14, fontweight='bold')
ax.set_ylabel('Dispute Driver (Expanded Classification)', fontsize=14, fontweight='bold')
ax.set_title('Comprehensive Dispute Driver Heat Map\nExpanded Temporal Analysis 2017-2025', 
             fontsize=17, fontweight='bold', pad=20)

# Improve label readability
ax.set_yticklabels([t.get_text().replace('_', ' ').title() for t in ax.get_yticklabels()], 
                    rotation=0, fontsize=11, ha='right')
ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=11)

plt.tight_layout()
plt.savefig(f'{output_dir}/comprehensive_heatmap.png', dpi=300, bbox_inches='tight')
print(f"    ✓ Saved: comprehensive_heatmap.png")
plt.close()

# 4.3: TEMPORAL TRENDS - LINE CHART
print("  → Creating temporal trends line chart...")
fig, ax = plt.subplots(figsize=(18, 10))

# Plot top 10 drivers
top_drivers = expanded_taxonomy.head(10)['driver'].tolist()
for driver in top_drivers:
    if driver in sorted_trends.columns:
        ax.plot(sorted_trends.index, sorted_trends[driver], 
               marker='o', linewidth=2.5, markersize=8, 
               label=driver.replace('_', ' ').title(), alpha=0.8)

ax.set_xlabel('Year', fontsize=13, fontweight='bold')
ax.set_ylabel('Frequency', fontsize=13, fontweight='bold')
ax.set_title('Top 10 Dispute Driver Trends Over Time\nExpanded Classification (2017-2025)', 
             fontsize=16, fontweight='bold', pad=20)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
ax.grid(alpha=0.3, linestyle='--')
ax.set_xticks(sorted_trends.index)

plt.tight_layout()
plt.savefig(f'{output_dir}/comprehensive_trends_line.png', dpi=300, bbox_inches='tight')
print(f"    ✓ Saved: comprehensive_trends_line.png")
plt.close()

# 4.4: STACKED AREA CHART
print("  → Creating stacked area chart...")
fig, ax = plt.subplots(figsize=(18, 10))

# Use top 12 for better visualization
top_12_drivers = expanded_taxonomy.head(12)['driver'].tolist()
trends_top12 = sorted_trends[top_12_drivers]

ax.stackplot(trends_top12.index, 
             *[trends_top12[col] for col in trends_top12.columns],
             labels=[col.replace('_', ' ').title() for col in trends_top12.columns],
             alpha=0.8)

ax.set_xlabel('Year', fontsize=13, fontweight='bold')
ax.set_ylabel('Cumulative Frequency', fontsize=13, fontweight='bold')
ax.set_title('Cumulative Dispute Driver Evolution\nTop 12 Categories (2017-2025)', 
             fontsize=16, fontweight='bold', pad=20)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
ax.grid(alpha=0.3, linestyle='--')
ax.set_xticks(trends_top12.index)

plt.tight_layout()
plt.savefig(f'{output_dir}/comprehensive_stacked_area.png', dpi=300, bbox_inches='tight')
print(f"    ✓ Saved: comprehensive_stacked_area.png")
plt.close()

# 4.5: PROPORTION PIE CHART
print("  → Creating proportion pie chart...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

# Overall distribution
colors_pie = sns.color_palette("Set3", len(expanded_taxonomy))
wedges1, texts1, autotexts1 = ax1.pie(expanded_taxonomy['count'], 
                                        labels=[d.replace('_', ' ').title() for d in expanded_taxonomy['driver']], 
                                        autopct='%1.1f%%',
                                        colors=colors_pie,
                                        startangle=90,
                                        textprops={'fontsize': 9})
ax1.set_title('Overall Distribution\n(2017-2025)', fontsize=14, fontweight='bold', pad=15)

# Make percentage text bold
for autotext in autotexts1:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(8)

# 2024-2025 distribution (most recent)
recent_data = corpus[corpus['year'].isin([2024, 2025])]
recent_taxonomy = recent_data['driver_label_expanded'].value_counts()
wedges2, texts2, autotexts2 = ax2.pie(recent_taxonomy.values, 
                                        labels=[d.replace('_', ' ').title() for d in recent_taxonomy.index], 
                                        autopct='%1.1f%%',
                                        colors=colors_pie[:len(recent_taxonomy)],
                                        startangle=90,
                                        textprops={'fontsize': 9})
ax2.set_title('Recent Period Distribution\n(2024-2025)', fontsize=14, fontweight='bold', pad=15)

for autotext in autotexts2:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(8)

plt.suptitle('Dispute Driver Distribution Comparison', fontsize=17, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig(f'{output_dir}/comprehensive_pie_charts.png', dpi=300, bbox_inches='tight')
print(f"    ✓ Saved: comprehensive_pie_charts.png")
plt.close()

# 4.6: PROJECT TYPES WITH EXPANDED DRIVERS
print("  → Creating project types analysis...")
classifications = pd.read_csv('/Users/charlesgava/Downloads/Temporal Analysis Research /output/results/government_Auditor_General/audit_infrastructure_classifications_improved.csv')

theme_counts = classifications['primary_theme'].value_counts()

fig, ax = plt.subplots(figsize=(16, 9))
colors_theme = sns.color_palette("viridis", len(theme_counts))

bars = ax.barh(range(len(theme_counts)), theme_counts.values, 
               color=colors_theme, edgecolor='black', linewidth=1.2, alpha=0.85)
ax.set_yticks(range(len(theme_counts)))
ax.set_yticklabels(theme_counts.index, fontsize=12)

# Add value labels with percentages
total_projects = theme_counts.sum()
for i, count in enumerate(theme_counts.values):
    pct = (count/total_projects)*100
    ax.text(count + 0.5, i, f'{count} ({pct:.1f}%)', va='center', fontsize=11, fontweight='bold')

ax.set_xlabel('Number of Projects', fontsize=13, fontweight='bold')
ax.set_ylabel('Project Type / Infrastructure Theme', fontsize=13, fontweight='bold')
ax.set_title('Infrastructure Project Distribution by Theme\nComprehensive Analysis (2017-2025)', 
             fontsize=16, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(f'{output_dir}/comprehensive_project_types.png', dpi=300, bbox_inches='tight')
print(f"    ✓ Saved: comprehensive_project_types.png")
plt.close()

# 4.7: HIERARCHICAL EVOLUTION (Normalized)
print("  → Creating hierarchical evolution chart...")
fig, ax = plt.subplots(figsize=(20, 11))

# Normalize for proportion view
trends_normalized = sorted_trends.div(sorted_trends.sum(axis=1), axis=0) * 100

# Plot top 15 for clarity
top_15_drivers = expanded_taxonomy.head(15)['driver'].tolist()
for driver in top_15_drivers:
    if driver in trends_normalized.columns:
        values = trends_normalized[driver].values
        ax.plot(trends_normalized.index, values, 
               marker='o', linewidth=3, markersize=9, 
               label=driver.replace('_', ' ').title(), alpha=0.8)

ax.set_xlabel('Year', fontsize=14, fontweight='bold')
ax.set_ylabel('Relative Prevalence (%)', fontsize=14, fontweight='bold')
ax.set_title('Hierarchical Topic Evolution: Comprehensive Dispute Driver Dynamics\nProportional Distribution 2017-2025', 
             fontsize=17, fontweight='bold', pad=20)
ax.legend(title='Dispute Drivers', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10, ncol=2)
ax.grid(alpha=0.3, linestyle='--')
ax.set_xticks(trends_normalized.index)

plt.tight_layout()
plt.savefig(f'{output_dir}/comprehensive_hierarchical_evolution.png', dpi=300, bbox_inches='tight')
print(f"    ✓ Saved: comprehensive_hierarchical_evolution.png")
plt.close()

# 4.8: DRIVER COMPARISON (Original vs Expanded)
print("  → Creating before/after comparison...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9))

# Original taxonomy (with "other")
original_tax = (
    corpus['driver_label']
    .value_counts(dropna=False)
    .rename_axis('driver')
    .reset_index(name='count')
    .sort_values('count', ascending=False)
)
colors_orig = sns.color_palette("rocket_r", len(original_tax))

ax1.barh(range(len(original_tax)), original_tax['count'], 
         color=colors_orig, edgecolor='black', linewidth=1.2, alpha=0.85)
ax1.set_yticks(range(len(original_tax)))
ax1.set_yticklabels([m.replace('_', ' ').title() for m in original_tax['driver']], fontsize=11)
ax1.set_xlabel('Count', fontsize=12, fontweight='bold')
ax1.set_title('Original Classification\n(with "Other" category)', fontsize=14, fontweight='bold', pad=15)
ax1.grid(axis='x', alpha=0.3, linestyle='--')

# Expanded taxonomy
top_10_expanded = expanded_taxonomy.head(10)
colors_exp = sns.color_palette("viridis", len(top_10_expanded))

ax2.barh(range(len(top_10_expanded)), top_10_expanded['count'], 
         color=colors_exp, edgecolor='black', linewidth=1.2, alpha=0.85)
ax2.set_yticks(range(len(top_10_expanded)))
ax2.set_yticklabels([d.replace('_', ' ').title() for d in top_10_expanded['driver']], fontsize=11)
ax2.set_xlabel('Count', fontsize=12, fontweight='bold')
ax2.set_title('Expanded Classification\n(Top 10 categories)', fontsize=14, fontweight='bold', pad=15)
ax2.grid(axis='x', alpha=0.3, linestyle='--')

plt.suptitle('Classification Comparison: Original vs Expanded Taxonomy', 
             fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig(f'{output_dir}/comprehensive_comparison.png', dpi=300, bbox_inches='tight')
print(f"    ✓ Saved: comprehensive_comparison.png")
plt.close()

# ===========================
# STEP 5: GENERATE STATISTICS
# ===========================
print("\n[5/6] Generating comprehensive statistics...")

stats = {
    'total_sentences': len(corpus),
    'total_categories': len(expanded_taxonomy),
    'years_covered': sorted(corpus['year'].unique().tolist()),
    'total_projects': len(classifications),
    'top_5_drivers': expanded_taxonomy.head(5).to_dict('records'),
    'yearly_totals': sorted_trends.sum(axis=1).to_dict(),
    'driver_growth': {}
}

# Calculate growth rates
for driver in expanded_taxonomy.head(5)['driver']:
    if driver in sorted_trends.columns:
        first_year = sorted_trends[driver].iloc[0]
        last_year = sorted_trends[driver].iloc[-1]
        if first_year > 0:
            growth = ((last_year - first_year) / first_year) * 100
            stats['driver_growth'][driver] = round(growth, 1)

# Save statistics
import json
with open('/Users/charlesgava/Downloads/Temporal Analysis Research /output/results/government_Auditor_General/comprehensive_statistics.json', 'w') as f:
    json.dump(stats, f, indent=2)
print(f"✓ Saved: comprehensive_statistics.json")

# ===========================
# STEP 6: SUMMARY REPORT
# ===========================
print("\n[6/6] Generating summary statistics...")

print("\n" + "="*80)
print("COMPREHENSIVE ANALYSIS SUMMARY")
print("="*80)

print(f"\n📊 DATASET OVERVIEW")
print(f"   • Total sentences analyzed: {len(corpus):,}")
print(f"   • Total dispute categories: {len(expanded_taxonomy)}")
print(f"   • Years covered: {min(corpus['year'])} - {max(corpus['year'])}")
print(f"   • Total infrastructure projects: {len(classifications)}")

print(f"\n🏆 TOP 5 DISPUTE DRIVERS")
for i, row in expanded_taxonomy.head(5).iterrows():
    pct = (row['count'] / total) * 100
    print(f"   {i+1}. {row['driver'].replace('_', ' ').title()}: {row['count']} ({pct:.1f}%)")

print(f"\n📈 YEARLY TRENDS")
for year in sorted(corpus['year'].unique()):
    year_total = sorted_trends.loc[year].sum()
    print(f"   {year}: {int(year_total)} mentions")

print(f"\n🏗️ PROJECT TYPES (Top 5)")
for i, (theme, count) in enumerate(theme_counts.head(5).items(), 1):
    pct = (count / total_projects) * 100
    print(f"   {i}. {theme}: {count} projects ({pct:.1f}%)")

print("\n" + "="*80)
print("✅ ALL TASKS COMPLETED SUCCESSFULLY")
print("="*80)

print(f"\n📁 Output directory: {output_dir}")
print("\n📊 Generated Visualizations:")
viz_files = [
    "comprehensive_taxonomy.png",
    "comprehensive_heatmap.png", 
    "comprehensive_trends_line.png",
    "comprehensive_stacked_area.png",
    "comprehensive_pie_charts.png",
    "comprehensive_project_types.png",
    "comprehensive_hierarchical_evolution.png",
    "comprehensive_comparison.png"
]

for i, vf in enumerate(viz_files, 1):
    print(f"   {i}. {vf}")

print("\n📄 Generated Data Files:")
data_files = [
    "oag_infrastructure_sentence_corpus_2017_2025_expanded.csv",
    "national_dispute_risk_taxonomy_2017_2025_expanded.csv",
    "driver_trend_by_year_2017_2025_expanded.csv",
    "comprehensive_statistics.json"
]

for i, df in enumerate(data_files, 1):
    print(f"   {i}. {df}")

print("\n" + "="*80)
