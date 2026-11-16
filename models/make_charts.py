"""
Generate every chart in visuals/financial-charts/ from the CSV inputs and model outputs.

Charts are drawn only from data that exists in data/datasets/ - no synthetic series.
Colour rules: categorical hues in a fixed order (one per business, never re-ordered),
an ordinal blue ramp for the three scenarios, a blue/red diverging pair for the
sensitivity tornado, one y-axis per plot, solid hairline grids, legend for >= 2 series.

Usage:  python models/make_charts.py   (run financial_model.py and scoring_model.py first)
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "data" / "datasets" / "inputs"
OUTPUTS = ROOT / "data" / "datasets" / "outputs"
CHARTS = ROOT / "visuals" / "financial-charts"

# --- palette (validated reference palette, light mode) ---------------------------------
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
SCENARIO_COLORS = {"conservative": "#86b6ef", "base": "#2a78d6", "optimistic": "#104281"}  # ordinal ramp
POS, NEG = "#2a78d6", "#e34948"  # diverging poles
NEUTRAL = "#c3c2b7"
SEQ_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

FOOTNOTE = "Projections are illustrative estimates, not guaranteed outcomes. Source: author's model (models/financial_model.py)."


def setup() -> None:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "Helvetica Neue", "Arial", "DejaVu Sans"],
        "font.size": 9.5,
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": AXIS, "axes.linewidth": 0.8, "axes.labelcolor": INK2,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.titlesize": 10.5, "axes.titleweight": "semibold", "axes.titlelocation": "left",
        "axes.titlecolor": INK, "axes.titlepad": 8,
        "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelcolor": INK2, "ytick.labelcolor": INK2,
        "xtick.major.size": 0, "ytick.major.size": 0,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.7, "grid.linestyle": "-",
        "axes.axisbelow": True, "lines.linewidth": 2, "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round", "legend.frameon": False, "legend.fontsize": 9,
        "text.color": INK,
    })


def usd(x: float, _pos=None) -> str:
    sign = "-" if x < 0 else ""
    x = abs(x)
    if x >= 10_000:
        k = x / 1000
        return f"{sign}${k:.0f}K" if abs(k - round(k)) < 0.05 else f"{sign}${k:.1f}K"
    if x >= 1_000:
        return f"{sign}${x / 1000:.1f}K".replace(".0K", "K")
    return f"{sign}${x:,.0f}"


def headline(fig, title: str, subtitle: str, foot: str = FOOTNOTE) -> None:
    fig.text(0.012, 0.985, title, ha="left", va="top", fontsize=13.5, fontweight="semibold", color=INK)
    fig.text(0.012, 0.935, subtitle, ha="left", va="top", fontsize=10, color=INK2)
    fig.text(0.012, 0.012, foot, ha="left", va="bottom", fontsize=7.8, color=MUTED)


def save(fig, name: str) -> None:
    CHARTS.mkdir(parents=True, exist_ok=True)
    fig.savefig(CHARTS / name, dpi=160)
    plt.close(fig)
    print("  wrote", name)


def business_colors(businesses: pd.DataFrame) -> dict:
    return {b: SERIES[i] for i, b in enumerate(businesses["short_name"])}


# --- 1. long-list screening -------------------------------------------------------------
def chart_screening() -> None:
    df = pd.read_csv(INPUTS / "opportunity_screening.csv")
    crit = ["demand_evidence", "budget_fit", "margin_potential", "competitive_intensity", "access_regulation"]
    recomputed = df[crit].mean(axis=1).round(2)
    bad = df[(recomputed - df["screening_score"]).abs() > 0.005]
    if not bad.empty:
        raise ValueError(f"Screening score is not the mean of the criteria for: {bad['id'].tolist()}")
    df = df.sort_values(["screening_score", "demand_evidence"])
    n_short = int((df["decision"] == "Shortlisted").sum())
    fig, ax = plt.subplots(figsize=(10, 6.4))
    fig.subplots_adjust(left=0.33, right=0.95, top=0.84, bottom=0.1)
    colors = [SERIES[0] if d == "Shortlisted" else NEUTRAL for d in df["decision"]]
    ax.barh(df["opportunity"], df["screening_score"], height=0.55, color=colors)
    for y, (v, d) in enumerate(zip(df["screening_score"], df["decision"])):
        ax.text(v + 0.04, y, f"{v:.2f}", va="center", fontsize=8.5, color=INK2)
    ax.set_xlim(0, 5.3)
    ax.set_xlabel("Screening score (1 = weak, 5 = strong)")
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Patch(color=SERIES[0], label="Shortlisted for financial analysis"),
                       Patch(color=NEUTRAL, label="Rejected or deferred")], loc="lower right")
    headline(fig, f"Stage 2 screening: {len(df)} opportunities scored, {n_short} shortlisted",
             "Equal-weighted screen on demand evidence, budget fit, margin, competition and access/regulation",
             "Scores are analyst judgements documented in opportunities/opportunity-comparison.md (data/datasets/inputs/opportunity_screening.csv).")
    save(fig, "01_opportunity_screening.png")


# --- 2. investment allocation -----------------------------------------------------------
FOLD = {"Registration & legal": "Legal, licences & recruitment",
        "Staffing (pre-opening)": "Legal, licences & recruitment"}


def chart_investment(businesses: pd.DataFrame) -> None:
    b = pd.read_csv(OUTPUTS / "investment_breakdown.csv")
    b["group"] = b["category"].replace(FOLD)
    order = ["Equipment & infrastructure", "Initial inventory", "Working capital", "Contingency reserve",
             "Rent & utilities", "Transportation & logistics", "Marketing & customer acquisition",
             "Legal, licences & recruitment"]
    pv = b.pivot_table(index="business_id", columns="group", values="amount_usd", aggfunc="sum").reindex(
        columns=order, fill_value=0)
    names = businesses.set_index("business_id")["short_name"]
    pv.index = [names[i] for i in pv.index]
    pv = pv.loc[list(names)[::-1]]

    fig, ax = plt.subplots(figsize=(10, 5.0))
    fig.subplots_adjust(left=0.2, right=0.9, top=0.8, bottom=0.25)
    left = np.zeros(len(pv))
    for i, col in enumerate(order):
        ax.barh(pv.index, pv[col], left=left, height=0.5, color=SERIES[i], edgecolor=SURFACE,
                linewidth=1.6, label=col)
        left += pv[col].values
    for y, total in enumerate(left):
        ax.text(total + 150, y, usd(total), va="center", fontsize=9, color=INK, fontweight="semibold")
    ax.xaxis.set_major_formatter(FuncFormatter(usd))
    ax.set_xlim(0, 21_500)
    ax.axvline(20_000, color=MUTED, linewidth=0.8)
    ax.text(20_000, len(pv) - 0.45, " $20K budget ceiling", fontsize=8, color=MUTED, va="bottom")
    ax.grid(axis="y", visible=False)
    ax.legend(ncol=4, loc="upper left", bbox_to_anchor=(-0.2, -0.1), fontsize=8.5)
    headline(fig, "Initial investment by cost category",
             "All five shortlisted businesses fit inside the USD 5,000-20,000 range, including a contingency reserve",
             "Source: data/datasets/outputs/investment_breakdown.csv; costing basis in financial-analysis/investment-breakdown.md.")
    save(fig, "02_investment_allocation.png")


# --- 3. weighted ranking ----------------------------------------------------------------
def chart_ranking() -> None:
    r = pd.read_csv(OUTPUTS / "weighted_ranking.csv").sort_values("weighted_score")
    fig, ax = plt.subplots(figsize=(10, 4.4))
    fig.subplots_adjust(left=0.27, right=0.93, top=0.78, bottom=0.15)
    top = r["weighted_score"].max()
    colors = [SERIES[0] if v == top else "#9ec5f4" for v in r["weighted_score"]]
    ax.barh(r["business"], r["weighted_score"], height=0.5, color=colors)
    for y, v in enumerate(r["weighted_score"]):
        ax.text(v + 0.04, y, f"{v:.2f}", va="center", fontsize=9, color=INK, fontweight="semibold")
    ax.set_xlim(0, 5)
    ax.set_xlabel("Weighted score (1-5)")
    ax.grid(axis="y", visible=False)
    headline(fig, "Final investment ranking (weighted scoring model)",
             "Weights: demand 20%, profitability 20%, affordability 15%, feasibility 15%, competition 10%, scalability 10%, risk 10%",
             "Source: data/datasets/outputs/weighted_ranking.csv; method in strategic-analysis/final-recommendation.md.")
    save(fig, "03_weighted_ranking.png")


# --- 4. revenue vs costs (small multiples) ---------------------------------------------
def small_multiples(n: int, figsize=(12, 7.2)):
    fig, axes = plt.subplots(2, 3, figsize=figsize, sharex=True)
    axes = axes.flatten()
    for ax in axes[n:]:
        ax.set_visible(False)
    return fig, axes


def label_x(axes, n: int, label: str | None = "Operating month", ncols: int = 3) -> None:
    """Show x tick labels (and an axis label) on every panel with no visible panel beneath it."""
    for i in range(n):
        if i + ncols >= n:
            axes[i].tick_params(labelbottom=True)
            if label:
                axes[i].set_xlabel(label)


def chart_revenue_vs_costs(businesses: pd.DataFrame) -> None:
    m = pd.read_csv(OUTPUTS / "monthly_projections.csv")
    m = m[m["scenario"] == "base"]
    m["total_costs"] = m["cogs"] + m["operating_expenses"] + m["depreciation_amortisation"] + m["tax"]
    fig, axes = small_multiples(len(businesses))
    fig.subplots_adjust(left=0.06, right=0.98, top=0.83, bottom=0.12, hspace=0.42, wspace=0.22)
    for ax, (_, b) in zip(axes, businesses.iterrows()):
        d = m[m["business_id"] == b["business_id"]]
        ax.plot(d["month"], d["revenue"], color=SERIES[0], label="Revenue")
        ax.plot(d["month"], d["total_costs"], color=SERIES[1], label="Total costs (COGS + opex + depreciation + tax)")
        ax.fill_between(d["month"], d["revenue"], d["total_costs"], where=d["revenue"] >= d["total_costs"],
                        color=SERIES[0], alpha=0.10, linewidth=0, interpolate=True)
        ax.set_title(b["short_name"])
        ax.yaxis.set_major_formatter(FuncFormatter(usd))
        ax.set_xticks(range(1, 13))
        ax.set_ylim(bottom=0)
    label_x(axes, len(businesses))
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper left", bbox_to_anchor=(0.012, 0.915), ncol=2)
    headline(fig, "Base case: monthly revenue vs total costs",
             "The shaded gap is monthly net profit; each panel has its own y-scale")
    save(fig, "04_revenue_vs_costs.png")


# --- 5. break-even / payback -----------------------------------------------------------
def chart_breakeven(businesses: pd.DataFrame) -> None:
    m = pd.read_csv(OUTPUTS / "monthly_projections.csv")
    s = pd.read_csv(OUTPUTS / "summary_metrics.csv")
    fig, axes = small_multiples(len(businesses))
    fig.subplots_adjust(left=0.06, right=0.98, top=0.83, bottom=0.12, hspace=0.42, wspace=0.22)
    for ax, (_, b) in zip(axes, businesses.iterrows()):
        inv = s[(s["business_id"] == b["business_id"])]["initial_investment"].iloc[0]
        for sc, col in SCENARIO_COLORS.items():
            d = m[(m["business_id"] == b["business_id"]) & (m["scenario"] == sc)]
            ax.plot(d["month"], d["cumulative_cash_flow"], color=col, label=sc.capitalize())
        ax.axhline(inv, color=INK2, linewidth=1)
        ax.axhline(0, color=AXIS, linewidth=0.8)
        ax.text(1, inv, f"Investment {usd(inv)}", fontsize=8, color=INK2, va="bottom")
        ax.set_title(b["short_name"])
        ax.yaxis.set_major_formatter(FuncFormatter(usd))
        ax.set_xticks(range(1, 13))
    label_x(axes, len(businesses))
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper left", bbox_to_anchor=(0.012, 0.915), ncol=3)
    headline(fig, "Payback: cumulative operating cash flow vs initial investment",
             "Payback occurs where a scenario line crosses the investment line; lines below it at month 12 pay back later")
    save(fig, "05_break_even_payback.png")


# --- 6. monthly cash flow ----------------------------------------------------------------
def chart_cash_flow(businesses: pd.DataFrame) -> None:
    m = pd.read_csv(OUTPUTS / "monthly_projections.csv")
    m = m[m["scenario"] == "base"]
    fig, axes = small_multiples(len(businesses))
    fig.subplots_adjust(left=0.06, right=0.98, top=0.83, bottom=0.12, hspace=0.42, wspace=0.22)
    colors = business_colors(businesses)
    for ax, (_, b) in zip(axes, businesses.iterrows()):
        d = m[m["business_id"] == b["business_id"]]
        c = [colors[b["short_name"]] if v >= 0 else NEG for v in d["operating_cash_flow"]]
        ax.bar(d["month"], d["operating_cash_flow"], width=0.6, color=c)
        ax.axhline(0, color=AXIS, linewidth=0.8)
        ax.set_title(b["short_name"])
        ax.yaxis.set_major_formatter(FuncFormatter(usd))
        ax.set_xticks(range(1, 13))
        ax.grid(axis="x", visible=False)
        ax.text(12.4, d["operating_cash_flow"].iloc[-1], usd(d["operating_cash_flow"].iloc[-1]),
                fontsize=8, color=INK2, va="center")
    label_x(axes, len(businesses))
    fig.legend(handles=[Patch(color=NEG, label="Negative month (cash outflow)")], loc="upper left",
               bbox_to_anchor=(0.012, 0.915))
    headline(fig, "Base case: monthly operating cash flow",
             "Net profit plus depreciation; ramp-up months are funded from the working-capital reserve")
    save(fig, "06_monthly_cash_flow.png")


# --- 7. scenario comparison -------------------------------------------------------------
def chart_scenarios(businesses: pd.DataFrame) -> None:
    s = pd.read_csv(OUTPUTS / "summary_metrics.csv")
    names = list(businesses["short_name"])
    x = np.arange(len(names))
    w = 0.24
    fig, ax = plt.subplots(figsize=(11, 5.4))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.8, bottom=0.17)
    for i, (sc, col) in enumerate(SCENARIO_COLORS.items()):
        vals = [s[(s["business"] == n) & (s["scenario"] == sc)]["net_profit_12m"].iloc[0] for n in names]
        ax.bar(x + (i - 1) * w, vals, width=w - 0.02, color=col, label=sc.capitalize())
        for xi, v in zip(x + (i - 1) * w, vals):
            ax.text(xi, v + (250 if v >= 0 else -250), usd(v), ha="center", va="bottom" if v >= 0 else "top",
                    fontsize=7.5, color=INK2)
    ax.axhline(0, color=AXIS, linewidth=0.9)
    ax.set_xticks(x, names)
    ax.yaxis.set_major_formatter(FuncFormatter(usd))
    ax.grid(axis="x", visible=False)
    ax.set_ylabel("12-month net profit (USD)")
    ax.legend(loc="upper left", bbox_to_anchor=(0, 1.12), ncol=3)
    headline(fig, "Year-1 net profit by scenario", "Includes ramp-up months; month-12 run-rate is higher (see summary table)")
    save(fig, "07_scenario_net_profit.png")


# --- 8. risk heatmap ----------------------------------------------------------------------
def chart_risk(businesses: pd.DataFrame) -> None:
    r = pd.read_csv(INPUTS / "risk_register.csv")
    r["score"] = r["likelihood"] * r["impact"]
    pv = r.pivot_table(index="business_id", columns="category", values="score", aggfunc="max")
    cat_order = ["Demand", "Price & competition", "Operations & people", "Supply & input costs",
                 "Financial & FX", "Regulatory", "Hazard"]
    pv = pv.reindex(columns=[c for c in cat_order if c in pv.columns])
    names = businesses.set_index("business_id")["short_name"]
    pv = pv.reindex(list(names.index))
    pv.index = [names[i] for i in pv.index]
    fig, ax = plt.subplots(figsize=(11, 4.8))
    fig.subplots_adjust(left=0.2, right=0.9, top=0.78, bottom=0.2)
    from matplotlib.colors import ListedColormap, BoundaryNorm
    cmap = ListedColormap(SEQ_RAMP[1:6])
    norm = BoundaryNorm([0, 5, 9, 13, 17, 26], cmap.N)
    data = pv.values.astype(float)
    im = ax.imshow(np.nan_to_num(data, nan=0), cmap=cmap, norm=norm, aspect="auto")
    for (i, j), v in np.ndenumerate(data):
        if np.isnan(v):
            ax.text(j, i, "-", ha="center", va="center", color=MUTED)
        else:
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=9,
                    color="#ffffff" if v >= 13 else INK)
    wrapped = [c.replace(" & ", " &" + chr(10)) for c in pv.columns]  # two-line labels avoid collisions
    ax.set_xticks(range(pv.shape[1]), wrapped, rotation=0, fontsize=8.5)
    ax.set_yticks(range(pv.shape[0]), pv.index)
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xticks(np.arange(-0.5, pv.shape[1]), minor=True)
    ax.set_yticks(np.arange(-0.5, pv.shape[0]), minor=True)
    ax.grid(which="minor", color=SURFACE, linewidth=2)
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02, ticks=[2.5, 7, 11, 15, 21.5])
    cb.ax.set_yticklabels(["1-4 low", "5-8", "9-12", "13-16", "17-25 high"], fontsize=8)
    cb.outline.set_visible(False)
    headline(fig, "Risk comparison: highest likelihood x impact score per risk category",
             "Scale 1-25; darker = more severe. Full register with mitigations in strategic-analysis/risk-assessment.md",
             "Source: data/datasets/inputs/risk_register.csv (analyst assessment).")
    save(fig, "08_risk_heatmap.png")


# --- 9. sensitivity tornado ---------------------------------------------------------------
def chart_tornado(businesses: pd.DataFrame) -> None:
    sens = pd.read_csv(OUTPUTS / "sensitivity_analysis.csv")
    rank = pd.read_csv(OUTPUTS / "weighted_ranking.csv")
    names = businesses.set_index("business_id")["short_name"]
    fig, axes = small_multiples(len(businesses), figsize=(13, 7.6))
    fig.subplots_adjust(left=0.12, right=0.98, top=0.84, bottom=0.08, hspace=0.38, wspace=0.62)
    order = rank["business_id"].tolist()
    for ax, bid in zip(axes, order):
        d = sens[sens["business_id"] == bid].copy()
        d["abs"] = d["delta"].abs()
        d = d.sort_values("abs")
        ax.barh(d["test"], d["delta"], height=0.55, color=[POS if v >= 0 else NEG for v in d["delta"]])
        ax.axvline(0, color=AXIS, linewidth=0.9)
        ax.xaxis.set_major_formatter(FuncFormatter(usd))
        ax.tick_params(axis="y", labelsize=7.8)
        ax.grid(axis="y", visible=False)
        base = d["base_net_profit_12m"].iloc[0]
        r = int(rank.loc[rank["business_id"] == bid, "rank"].iloc[0])
        ax.set_title(f"#{r} {names[bid]}  (base {usd(base)})", fontsize=9.5)
    fig.legend(handles=[Patch(color=POS, label="Raises year-1 net profit"),
                        Patch(color=NEG, label="Lowers year-1 net profit")],
               loc="upper left", bbox_to_anchor=(0.012, 0.915), ncol=2)
    label_x(axes, len(order), label=None)
    headline(fig, "Sensitivity: change in year-1 net profit from one-at-a-time shocks (base case)",
             "FX test: GHS/USD rate +20% for 12 months; cedi prices are not raised, USD-priced (imported) inputs cost more")
    save(fig, "09_sensitivity_tornado.png")


def main() -> None:
    setup()
    businesses = pd.read_csv(INPUTS / "businesses.csv")
    chart_screening()
    chart_investment(businesses)
    chart_ranking()
    chart_revenue_vs_costs(businesses)
    chart_breakeven(businesses)
    chart_cash_flow(businesses)
    chart_scenarios(businesses)
    chart_risk(businesses)
    chart_tornado(businesses)


if __name__ == "__main__":
    main()
