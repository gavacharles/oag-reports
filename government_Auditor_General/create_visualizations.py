import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Create output directory for plots
import os
output_dir = '/Users/charlesgava/Downloads/Temporal Analysis Research /output/results/government_Auditor_General/plots_png'
os.makedirs(output_dir, exist_ok=True)

# ===========================
# 1. NATIONAL DISPUTE RISK TAXONOMY VISUALIZATION
# ===========================
print("Creating dispute taxonomy visualization...")

corpus = pd.read_csv('/Users/charlesgava/Downloads/Temporal Analysis Research /output/results/government_Auditor_General/oag_infrastructure_sentence_corpus_2017_2025.csv')
taxonomy_df = (
    corpus['driver_label']
    .value_counts(dropna=False)
    .rename_axis('driver')
    .reset_index(name='count')
    .sort_values('count', ascending=True)
)

fig, ax = plt.subplots(figsize=(14, 8))
colors = sns.color_palette("rocket_r", len(taxonomy_df))

bars = ax.barh(
    taxonomy_df['driver'].str.replace('_', ' ').str.title(),
    taxonomy_df['count'],
    color=colors,
    edgecolor='black',
    linewidth=1.2,
)

# Add value labels
total_mentions = taxonomy_df['count'].sum()
for i, count in enumerate(taxonomy_df['count']):
    pct = (count / total_mentions) * 100
    ax.text(count + 5, i, f'{count} ({pct:.1f}%)', va='center', fontsize=11, fontweight='bold')

ax.set_xlabel('Count of Mentions (2017-2025)', fontsize=13, fontweight='bold')
ax.set_ylabel('Dispute Driver Category', fontsize=13, fontweight='bold')
ax.set_title('National Dispute Risk Taxonomy (Pre-Reclassification, Including Other)\nOAG Infrastructure Reports (2017-2025)', 
             fontsize=16, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(f'{output_dir}/dispute_risk_taxonomy.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: dispute_risk_taxonomy.png")
plt.close()

# ===========================
# 2. PROJECT TYPES FOR DISPUTE DRIVERS
# ===========================
print("Creating project types analysis...")

classifications = pd.read_csv('/Users/charlesgava/Downloads/Temporal Analysis Research /output/results/government_Auditor_General/audit_infrastructure_classifications_improved.csv')

# Group by project theme
theme_counts = classifications['primary_theme'].value_counts()

fig, ax = plt.subplots(figsize=(14, 8))
colors_theme = sns.color_palette("viridis", len(theme_counts))

bars = ax.barh(range(len(theme_counts)), theme_counts.values, color=colors_theme, edgecolor='black', linewidth=1.2)
ax.set_yticks(range(len(theme_counts)))
ax.set_yticklabels(theme_counts.index, fontsize=11)

# Add value labels
for i, count in enumerate(theme_counts.values):
    ax.text(count + 0.5, i, f'{count}', va='center', fontsize=10, fontweight='bold')

ax.set_xlabel('Number of Projects', fontsize=13, fontweight='bold')
ax.set_ylabel('Project Type / Theme', fontsize=13, fontweight='bold')
ax.set_title('Distribution of Dispute Drivers Across Project Types\nAudited Infrastructure Projects (2017-2025)', 
             fontsize=16, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(f'{output_dir}/project_types_dispute_drivers.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: project_types_dispute_drivers.png")
plt.close()

# ===========================
# 3. CLEAN DISPUTE DRIVER HEATMAP
# ===========================
print("Creating cleaned dispute driver heatmap...")

# Read driver trends
trends_df = pd.read_csv('/Users/charlesgava/Downloads/Temporal Analysis Research /output/results/government_Auditor_General/driver_trend_by_year_2017_2025.csv')
trends_df = trends_df.set_index('year')

# Transpose for better visualization
trends_matrix = trends_df.T

fig, ax = plt.subplots(figsize=(16, 10))

# Create heatmap with improved labels
sns.heatmap(trends_matrix, annot=True, fmt='.0f', cmap='YlOrRd', 
            linewidths=0.5, linecolor='gray', cbar_kws={'label': 'Frequency'},
            ax=ax, square=False, robust=True)

# Improve axis labels
ax.set_xlabel('Year', fontsize=14, fontweight='bold')
ax.set_ylabel('Dispute Driver', fontsize=14, fontweight='bold')
ax.set_title('Dispute Driver Frequency Heat Map\nTemporal Analysis 2017-2025', 
             fontsize=17, fontweight='bold', pad=20)

# Rotate y-axis labels for better readability
ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=11, ha='right')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontsize=11, ha='right')

plt.tight_layout()
plt.savefig(f'{output_dir}/dispute_driver_heatmap_cleaned.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: dispute_driver_heatmap_cleaned.png")
plt.close()

# ===========================
# 4. BREAKDOWN OF "OTHER" CATEGORY
# ===========================
print("Creating 'other' category breakdown...")

# Filter for "other" category
other_df = corpus[corpus['driver_label'] == 'other'].copy()

# Analyze sentence patterns to categorize "other"
def categorize_other(sentence):
    sentence_lower = str(sentence).lower()
    if 'delay' in sentence_lower or 'late' in sentence_lower or 'behind' in sentence_lower:
        return 'Delays & Time Overruns'
    elif 'budget' in sentence_lower or 'fund' in sentence_lower or 'unspent' in sentence_lower:
        return 'Budget & Funding Issues'
    elif 'compliance' in sentence_lower or 'regulation' in sentence_lower or 'law' in sentence_lower:
        return 'Compliance & Regulatory'
    elif 'staff' in sentence_lower or 'personnel' in sentence_lower or 'capacity' in sentence_lower:
        return 'Human Resources'
    elif 'infrastructure' in sentence_lower or 'equipment' in sentence_lower or 'facility' in sentence_lower:
        return 'Infrastructure & Equipment'
    elif 'project' in sentence_lower:
        return 'General Project Issues'
    else:
        return 'Miscellaneous Administrative'

other_df['other_category'] = other_df['sentence'].apply(categorize_other)

# Count by category and year
other_breakdown = other_df.groupby(['year', 'other_category']).size().unstack(fill_value=0)

# Create stacked area chart
fig, ax = plt.subplots(figsize=(16, 9))

other_breakdown.plot(kind='area', stacked=True, ax=ax, alpha=0.8, 
                      color=sns.color_palette("Set2", len(other_breakdown.columns)))

ax.set_xlabel('Year', fontsize=13, fontweight='bold')
ax.set_ylabel('Frequency Count', fontsize=13, fontweight='bold')
ax.set_title('Breakdown of "Other" Dispute Driver Category\nTemporal Distribution 2017-2025', 
             fontsize=16, fontweight='bold', pad=20)
ax.legend(title='Sub-Category', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
ax.grid(alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(f'{output_dir}/other_category_breakdown.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: other_category_breakdown.png")
plt.close()

# Also create a bar chart breakdown
fig, ax = plt.subplots(figsize=(14, 8))

other_summary = other_df['other_category'].value_counts()
colors_other = sns.color_palette("mako_r", len(other_summary))

bars = ax.barh(range(len(other_summary)), other_summary.values, color=colors_other, 
               edgecolor='black', linewidth=1.2)
ax.set_yticks(range(len(other_summary)))
ax.set_yticklabels(other_summary.index, fontsize=11)

# Add value labels
for i, count in enumerate(other_summary.values):
    ax.text(count + 10, i, f'{count} ({count/other_summary.sum()*100:.1f}%)', 
            va='center', fontsize=10, fontweight='bold')

ax.set_xlabel('Count', fontsize=13, fontweight='bold')
ax.set_ylabel('Sub-Category', fontsize=13, fontweight='bold')
ax.set_title('"Other" Category Detailed Breakdown\nTotal: {} instances (2017-2025)'.format(other_summary.sum()), 
             fontsize=16, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(f'{output_dir}/other_category_detailed.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: other_category_detailed.png")
plt.close()

# ===========================
# 5. DISPUTE DRIVER TRENDS (WITH OTHER BREAKDOWN)
# ===========================
print("Creating improved driver trends visualization...")

# Combine main drivers with other breakdown
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

# Top plot: All drivers including "other"
trends_df.T.plot(ax=ax1, marker='o', linewidth=2.5, markersize=8)
ax1.set_xlabel('Dispute Driver', fontsize=12, fontweight='bold')
ax1.set_ylabel('Frequency', fontsize=12, fontweight='bold')
ax1.set_title('Dispute Driver Trends by Year (Including "Other")\n2017-2025', 
              fontsize=15, fontweight='bold', pad=15)
ax1.legend(title='Year', bbox_to_anchor=(1.05, 1), loc='upper left', ncol=1)
ax1.grid(alpha=0.3, linestyle='--')
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right', fontsize=10)

# Bottom plot: "Other" breakdown over time
other_breakdown.plot(kind='bar', stacked=False, ax=ax2, width=0.8,
                      color=sns.color_palette("Set2", len(other_breakdown.columns)))
ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
ax2.set_ylabel('Frequency', fontsize=12, fontweight='bold')
ax2.set_title('"Other" Category Breakdown by Sub-Type\n2017-2025', 
              fontsize=15, fontweight='bold', pad=15)
ax2.legend(title='Other Sub-Category', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
ax2.grid(axis='y', alpha=0.3, linestyle='--')
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=0, fontsize=10)

plt.tight_layout()
plt.savefig(f'{output_dir}/dispute_driver_trends_with_breakdown.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: dispute_driver_trends_with_breakdown.png")
plt.close()

# ===========================
# 6. HIERARCHICAL TOPIC EVOLUTION
# ===========================
print("Creating hierarchical topic evolution visualization...")

# Create a flow diagram showing evolution
fig, ax = plt.subplots(figsize=(18, 10))

# Prepare data for Sankey-like visualization using line plots
years = trends_df.index.tolist()
drivers = trends_df.columns.tolist()

# Normalize data for better visualization
trends_normalized = trends_df.div(trends_df.sum(axis=1), axis=0) * 100

# Create streamplot-like visualization
for i, driver in enumerate(drivers):
    values = trends_normalized[driver].values
    ax.plot(years, values, marker='o', linewidth=3, markersize=10, 
            label=driver.replace('_', ' ').title(), alpha=0.8)
    
    # Add annotations for significant changes
    for j in range(1, len(years)):
        change = values[j] - values[j-1]
        if abs(change) > 5:  # Significant change threshold
            ax.annotate(f'{change:+.1f}%', 
                       xy=(years[j], values[j]), 
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, alpha=0.6)

ax.set_xlabel('Year', fontsize=13, fontweight='bold')
ax.set_ylabel('Relative Prevalence (%)', fontsize=13, fontweight='bold')
ax.set_title('Hierarchical Topic Evolution: Dispute Driver Dynamics\nProportional Distribution 2017-2025', 
             fontsize=16, fontweight='bold', pad=20)
ax.legend(title='Dispute Drivers', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
ax.grid(alpha=0.3, linestyle='--')
ax.set_xticks(years)

plt.tight_layout()
plt.savefig(f'{output_dir}/hierarchical_topic_evolution.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: hierarchical_topic_evolution.png")
plt.close()

# ===========================
# 7. FA FACTOR VISUALIZATION
# ===========================
print("Creating FA factor visualization...")

pfa_df = pd.read_csv('/Users/charlesgava/Downloads/Temporal Analysis Research /output/results/government_Auditor_General/pfa_factor_scores_2017_2025.csv')

# Aggregate by year
pfa_yearly = pfa_df.groupby('year').mean()

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

for i in range(6):
    factor_col = f'factor_{i+1}'
    
    # Plot distribution
    for year in pfa_yearly.index:
        year_data = pfa_df[pfa_df['year'] == year][factor_col]
        axes[i].hist(year_data, bins=30, alpha=0.5, label=str(year))
    
    axes[i].set_title(f'Factor {i+1} Distribution', fontsize=12, fontweight='bold')
    axes[i].set_xlabel('Factor Score', fontsize=10)
    axes[i].set_ylabel('Frequency', fontsize=10)
    axes[i].legend(fontsize=8, ncol=2)
    axes[i].grid(alpha=0.3, linestyle='--')

plt.suptitle('FA Factor Score Distributions Across Years\nLatent Structure Analysis 2017-2025', 
             fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{output_dir}/pfa_factor_distributions.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: pfa_factor_distributions.png")
plt.close()

print("\n" + "="*60)
print("ALL VISUALIZATIONS CREATED SUCCESSFULLY!")
print("="*60)
print(f"\nOutput directory: {output_dir}")
print("\nGenerated files:")
print("  1. dispute_risk_taxonomy.png")
print("  2. project_types_dispute_drivers.png")
print("  3. dispute_driver_heatmap_cleaned.png")
print("  4. other_category_breakdown.png")
print("  5. other_category_detailed.png")
print("  6. dispute_driver_trends_with_breakdown.png")
print("  7. hierarchical_topic_evolution.png")
print("  8. pfa_factor_distributions.png")
