import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TREND_PATH = os.path.join(BASE_DIR, 'driver_trend_by_year_2017_2025_expanded.csv')
OUT_DIR = os.path.join(BASE_DIR, 'plots_png')
os.makedirs(OUT_DIR, exist_ok=True)

# Load data
trend_df = pd.read_csv(TREND_PATH)
trend_df = trend_df.sort_values('year')

# Total mentions per year
driver_cols = [c for c in trend_df.columns if c != 'year']
trend_df['total_mentions'] = trend_df[driver_cols].sum(axis=1)

# Macro periods from writeup
periods = [
    ('Foundation (2018–2019)', 2018, 2019, '#d9edf7'),
    ('Disruption (2020–2021)', 2020, 2021, '#fbeed5'),
    ('Escalation (2022–2024)', 2022, 2024, '#f2dede'),
    ('Stabilization (2025, partial)', 2025, 2025, '#dff0d8'),
]

# Plot
fig, ax = plt.subplots(figsize=(13, 7))

# Background shading by macro period
for label, start, end, color in periods:
    ax.axvspan(start - 0.5, end + 0.5, color=color, alpha=0.6)

# Total trend line
ax.plot(
    trend_df['year'],
    trend_df['total_mentions'],
    color='#1f3b73',
    marker='o',
    linewidth=3,
    markersize=8,
    label='Total dispute mentions per year'
)

# Value labels
for x, y in zip(trend_df['year'], trend_df['total_mentions']):
    ax.text(x, y + 6, f'{int(y)}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Period labels
ymax = trend_df['total_mentions'].max()
for label, start, end, _ in periods:
    xmid = (start + end) / 2
    ax.text(
        xmid,
        ymax * 0.93,
        label,
        ha='center',
        va='center',
        fontsize=10,
        fontweight='bold',
        color='#333333'
    )

ax.set_title('Temporal Trends in Infrastructure Dispute Mentions by Macro Period\nUganda OAG Corpus (2018–2025)', fontsize=14, fontweight='bold')
ax.set_xlabel('Year', fontsize=11)
ax.set_ylabel('Total dispute mentions', fontsize=11)
ax.set_xticks(trend_df['year'])
ax.grid(axis='y', alpha=0.25)
ax.set_ylim(0, ymax * 1.15)
ax.legend(loc='upper right')

# Save
png_path = os.path.join(OUT_DIR, 'temporal_trends_macro_periods.png')
svg_path = os.path.join(OUT_DIR, 'temporal_trends_macro_periods.svg')

plt.tight_layout()
plt.savefig(png_path, dpi=300, bbox_inches='tight')
plt.savefig(svg_path, bbox_inches='tight')
plt.close()

print(f'Saved: {png_path}')
print(f'Saved: {svg_path}')
