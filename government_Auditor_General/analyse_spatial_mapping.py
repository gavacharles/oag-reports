"""
Heuristic spatial mapping for Uganda infrastructure dispute mentions.
Matches curated Uganda place names in project names and sentence text,
then plots a bubble map over a simplified Uganda outline.
"""

import os
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(BASE, 'oag_infrastructure_sentence_corpus_2017_2025_expanded.csv')
OUTDIR = os.path.join(BASE, 'plots_png')
os.makedirs(OUTDIR, exist_ok=True)

# Approximate location coordinates (longitude, latitude) and macro-region
GAZETTEER = {
    'Kampala': {'lon': 32.58, 'lat': 0.35, 'region': 'Central'},
    'Entebbe': {'lon': 32.46, 'lat': 0.06, 'region': 'Central'},
    'Namanve': {'lon': 32.70, 'lat': 0.35, 'region': 'Central'},
    'Mukono': {'lon': 32.75, 'lat': 0.35, 'region': 'Central'},
    'Masaka': {'lon': 31.74, 'lat': -0.34, 'region': 'Central'},
    'Kalangala': {'lon': 32.29, 'lat': -0.32, 'region': 'Central'},
    'Jinja': {'lon': 33.20, 'lat': 0.44, 'region': 'Eastern'},
    'Tororo': {'lon': 34.18, 'lat': 0.69, 'region': 'Eastern'},
    'Mbale': {'lon': 34.17, 'lat': 1.08, 'region': 'Eastern'},
    'Soroti': {'lon': 33.61, 'lat': 1.71, 'region': 'Eastern'},
    'Isimba': {'lon': 33.16, 'lat': 0.59, 'region': 'Eastern'},
    'Bukedea': {'lon': 34.05, 'lat': 1.32, 'region': 'Eastern'},
    'Budaka': {'lon': 33.93, 'lat': 1.01, 'region': 'Eastern'},
    'Gulu': {'lon': 32.30, 'lat': 2.77, 'region': 'Northern'},
    'Lira': {'lon': 32.90, 'lat': 2.25, 'region': 'Northern'},
    'Arua': {'lon': 30.91, 'lat': 3.02, 'region': 'Northern'},
    'Moroto': {'lon': 34.67, 'lat': 2.53, 'region': 'Northern'},
    'Karuma': {'lon': 32.25, 'lat': 2.25, 'region': 'Northern'},
    'Kotido': {'lon': 34.11, 'lat': 2.98, 'region': 'Northern'},
    'Ngenge': {'lon': 34.37, 'lat': 1.37, 'region': 'Northern'},
    'Namalu': {'lon': 34.43, 'lat': 2.26, 'region': 'Northern'},
    'Hoima': {'lon': 31.35, 'lat': 1.43, 'region': 'Western'},
    'Muzizi': {'lon': 31.16, 'lat': 1.79, 'region': 'Western'},
    'Mbarara': {'lon': 30.65, 'lat': -0.61, 'region': 'Western'},
    'Kabale': {'lon': 29.99, 'lat': -1.25, 'region': 'Western'},
    'Kasese': {'lon': 30.10, 'lat': 0.18, 'region': 'Western'},
    'Fort Portal': {'lon': 30.27, 'lat': 0.66, 'region': 'Western'},
    'Nkenda': {'lon': 30.10, 'lat': 0.25, 'region': 'Western'},
}
REGION_COLORS = {
    'Central': '#4c78a8',
    'Eastern': '#f58518',
    'Northern': '#54a24b',
    'Western': '#e45756',
}

# Simplified Uganda outline polygon (approximate lon/lat)
UGANDA_POLYGON = [
    (29.58, -1.48), (30.15, -1.47), (31.00, -1.43), (31.90, -1.45),
    (33.05, -1.02), (34.22, 0.95), (34.45, 1.72), (34.25, 3.58),
    (33.80, 4.22), (33.20, 4.20), (32.60, 3.55), (31.90, 3.48),
    (31.42, 3.86), (30.72, 3.62), (30.38, 3.20), (29.74, 2.25),
    (29.60, 1.35), (29.60, 0.30), (29.58, -1.48),
]


def make_label(driver_key: str) -> str:
    return ' '.join('&' if part == 'and' else part.capitalize() for part in driver_key.split('_'))


df = pd.read_csv(CORPUS)
combined_text = (df['project_name'].fillna('') + ' ' + df['sentence'].fillna('')).str.lower()

location_rows = []
region_sentence_hits = {idx: set() for idx in df.index}
for place, meta in GAZETTEER.items():
    mask = combined_text.str.contains(r'\b' + re.escape(place.lower()) + r'\b', regex=True)
    matched = df.loc[mask].copy()
    if matched.empty:
        continue
    for idx in matched.index:
        region_sentence_hits[idx].add(meta['region'])
    driver_counts = matched['driver_label_expanded'].value_counts()
    dominant_driver = driver_counts.idxmax()
    location_rows.append({
        'location': place,
        'region': meta['region'],
        'lon': meta['lon'],
        'lat': meta['lat'],
        'matched_sentences': int(mask.sum()),
        'dominant_driver': dominant_driver,
        'dominant_driver_label': make_label(dominant_driver),
    })

location_df = pd.DataFrame(location_rows).sort_values('matched_sentences', ascending=False)
location_df.to_csv(os.path.join(BASE, 'spatial_location_summary.csv'), index=False)

region_rows = []
for idx, regions in region_sentence_hits.items():
    for region in regions:
        region_rows.append({'idx': idx, 'region': region, 'driver': df.loc[idx, 'driver_label_expanded']})
region_df = pd.DataFrame(region_rows)
region_summary = region_df.groupby('region')['idx'].nunique().reindex(['Central', 'Eastern', 'Northern', 'Western']).fillna(0).astype(int)
region_summary.to_csv(os.path.join(BASE, 'spatial_region_summary.csv'), header=['matched_sentences'])

# Plot: Uganda map with collision-avoiding labels for all matched locations
fig, ax = plt.subplots(figsize=(13.5, 10))
fig.suptitle(
    'Spatial Distribution of Matched Dispute Mentions (Uganda Map)\n'
    'Heuristic place-name matching within OAG infrastructure corpus, 2018–2025',
    fontsize=13, fontweight='bold', y=0.98,
)

poly_x = [p[0] for p in UGANDA_POLYGON]
poly_y = [p[1] for p in UGANDA_POLYGON]
ax.fill(poly_x, poly_y, color='#f5f5f5', edgecolor='#444444', linewidth=1.2, zorder=1)
ax.plot(poly_x, poly_y, color='#444444', linewidth=1.2, zorder=2)

xmin, xmax = 29.3, 34.9
ymin, ymax = -1.7, 4.5

if not location_df.empty:
    max_mentions = max(location_df['matched_sentences'].max(), 1)
    location_df = location_df.copy()
    location_df['marker_size'] = 70 + 390 * np.sqrt(location_df['matched_sentences'] / max_mentions)

    # Plot all matched locations
    for _, row in location_df.iterrows():
        ax.scatter(
            row['lon'], row['lat'],
            s=row['marker_size'],
            color=REGION_COLORS[row['region']],
            alpha=0.80,
            edgecolors='black',
            linewidths=0.85,
            zorder=3,
        )

    # Label placement with collision avoidance in map (data) coordinates
    placed_boxes = []

    def est_label_box(xc, yc, label_text):
        # Approximate text box size in lon/lat units
        w = 0.10 + 0.030 * len(label_text)
        h = 0.17
        return (xc - w / 2, xc + w / 2, yc - h / 2, yc + h / 2)

    def overlaps(box, existing_boxes):
        x0, x1, y0, y1 = box
        for bx0, bx1, by0, by1 in existing_boxes:
            if not (x1 < bx0 or x0 > bx1 or y1 < by0 or y0 > by1):
                return True
        return False

    def in_bounds(box):
        x0, x1, y0, y1 = box
        return (x0 >= xmin + 0.03 and x1 <= xmax - 0.03 and y0 >= ymin + 0.03 and y1 <= ymax - 0.03)

    # Prioritize highest-mention labels first
    for _, row in location_df.sort_values('matched_sentences', ascending=False).iterrows():
        x, y = float(row['lon']), float(row['lat'])
        label = f"{row['location']} ({int(row['matched_sentences'])})"

        # Candidate offsets radiating around point
        candidates = [
            (0.18, 0.10), (0.22, -0.10), (-0.22, 0.10), (-0.22, -0.10),
            (0.00, 0.22), (0.00, -0.22), (0.34, 0.18), (0.34, -0.18),
            (-0.34, 0.18), (-0.34, -0.18), (0.46, 0.00), (-0.46, 0.00),
            (0.58, 0.24), (0.58, -0.24), (-0.58, 0.24), (-0.58, -0.24),
        ]

        chosen = None
        chosen_box = None
        for dx, dy in candidates:
            tx, ty = x + dx, y + dy
            box = est_label_box(tx, ty, label)
            if not in_bounds(box):
                continue
            if overlaps(box, placed_boxes):
                continue
            chosen = (tx, ty)
            chosen_box = box
            break

        # Fallback: clamp to map bounds and accept even if near others
        if chosen is None:
            tx = min(max(x + 0.22, xmin + 0.20), xmax - 0.20)
            ty = min(max(y + 0.10, ymin + 0.12), ymax - 0.12)
            chosen = (tx, ty)
            chosen_box = est_label_box(tx, ty, label)

        placed_boxes.append(chosen_box)
        ax.annotate(
            label,
            xy=(x, y), xytext=chosen,
            textcoords='data',
            ha='center', va='center',
            fontsize=8.2,
            bbox=dict(boxstyle='round,pad=0.22', fc='white', ec='#666666', lw=0.65, alpha=0.95),
            arrowprops=dict(arrowstyle='-', color='#666666', lw=0.65, alpha=0.8),
            zorder=5,
        )

for region, color in REGION_COLORS.items():
    ax.scatter([], [], s=160, color=color, alpha=0.80, edgecolors='black', label=region)

ax.legend(loc='upper left', fontsize=9, title='Macro-region', framealpha=0.92)
ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Uganda Map: Matched Dispute Mentions by Location')
ax.grid(alpha=0.16)

fig.text(
    0.5,
    0.02,
    'Map is heuristic: locations are inferred from curated place-name matches in project names and sentence text. Counts are matched sentence mentions, not a full geocoded census of all 1,233 records.',
    ha='center',
    fontsize=9,
    color='#444444',
)

plt.tight_layout(rect=[0, 0.05, 1, 0.95])
plt.savefig(os.path.join(OUTDIR, 'spatial_dispute_map.png'), dpi=220, bbox_inches='tight')
plt.savefig(os.path.join(OUTDIR, 'spatial_dispute_map.svg'), bbox_inches='tight')
plt.close()

print('Saved spatial_location_summary.csv')
print('Saved spatial_region_summary.csv')
print('Saved spatial_dispute_map.png')
print('Saved spatial_dispute_map.svg')
print('\nTop locations:')
print(location_df[['location', 'region', 'matched_sentences', 'dominant_driver_label']].head(12).to_string(index=False))
print('\nRegion summary:')
print(region_summary.to_string())
