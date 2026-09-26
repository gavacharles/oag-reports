"""Shared, validated (CVD-safe) palette and style constants for every map
and chart in this paper, so figures read as one consistent system. Values
from the project's dataviz skill reference palette (light mode; these are
static print/PDF figures, not interactive)."""
import matplotlib as mpl

# categorical (fixed hue order -- never cycled/reassigned per-plot)
CATEGORICAL = {
    "blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "yellow": "#eda100",
    "magenta": "#e87ba4", "green": "#008300", "violet": "#4a3aa7", "red": "#e34948",
}
CATEGORICAL_ORDER = ["blue", "orange", "aqua", "yellow", "magenta", "green", "violet", "red"]

DRIVER_COLORS = {
    "land_and_right_of_way": CATEGORICAL["blue"],
    "delay_time_overrun": CATEGORICAL["orange"],
    "procurement_irregularities": CATEGORICAL["aqua"],
    "delayed_payments": CATEGORICAL["yellow"],
    "contract_management": CATEGORICAL["magenta"],
    "cost_overrun": CATEGORICAL["green"],
    "governance_and_controls": CATEGORICAL["violet"],
    "claims_and_disputes": CATEGORICAL["red"],
}
DRIVER_LABELS = {
    "land_and_right_of_way": "Land / Right-of-Way",
    "delay_time_overrun": "Delay / Time Overrun",
    "procurement_irregularities": "Procurement Irregularities",
    "delayed_payments": "Delayed Payments",
    "contract_management": "Contract Management",
    "cost_overrun": "Cost Overrun",
    "governance_and_controls": "Governance & Controls",
    "claims_and_disputes": "Claims & Disputes",
}

# sequential (blue, light->dark; step 100-700)
SEQUENTIAL_BLUE = [
    "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7",
    "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b",
]

# diverging: blue <-> red, neutral gray midpoint -- used for hot/cold spot
# maps (red=hot, blue=cold, gray=not significant) and GWR coefficient maps
DIVERGING_BLUE_RED = ["#1c5cab", "#5598e7", "#b7d3f6", "#f0efec", "#f3b3ac", "#eb6f66", "#c62a29"]
NEUTRAL_GRAY = "#f0efec"

# chrome & ink
SURFACE = "#fcfcfb"
PAGE = "#f9f9f7"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"

FONT = "DejaVu Sans"  # closest available to system-ui sans in matplotlib


def apply_style():
    mpl.rcParams.update({
        "font.family": FONT,
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": BASELINE,
        "axes.labelcolor": INK_SECONDARY,
        "text.color": INK_PRIMARY,
        "xtick.color": INK_MUTED,
        "ytick.color": INK_MUTED,
        "grid.color": GRIDLINE,
        "axes.titlecolor": INK_PRIMARY,
        "legend.frameon": False,
    })
