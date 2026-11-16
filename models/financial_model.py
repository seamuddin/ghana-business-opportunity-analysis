"""
Ghana Business Opportunity Analysis 2026 - 12-month financial model.

Every number used by this model lives in a CSV file under data/datasets/inputs/,
with a `basis` column (Verified fact / Estimate / Assumption) and a `source_ref`
that points to data/sources.md. Nothing is hard-coded here except the mechanics.

Mechanics (documented in financial-analysis/financial-assumptions.md):
  * Revenue lines: volume x price. Volume ramps linearly from `start_month` over
    `ramp_months`, then grows at `monthly_growth`.
  * COGS: volume x unit_cost (inventory is replenished as sold, so cash COGS = P&L COGS;
    the opening inventory is a working-capital investment held in the startup budget).
  * Operating costs: fixed (per month) or variable (% of revenue).
  * Depreciation: straight line on startup items that carry a useful life.
  * Tax: either a turnover tax (% of revenue) or corporate income tax on profit with
    loss carry-forward, as set per business in businesses.csv.
  * Money can be entered in GHS or USD; GHS is converted at the FX rate in
    global_assumptions.csv. An FX shock divides every GHS amount by (1 + shock)
    to show the effect of cedi depreciation without price pass-through.

Usage:
    python models/financial_model.py
Outputs (data/datasets/outputs/):
    monthly_projections.csv, summary_metrics.csv, investment_breakdown.csv,
    sensitivity_analysis.csv
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "data" / "datasets" / "inputs"
OUTPUTS = ROOT / "data" / "datasets" / "outputs"

SCENARIOS = ["conservative", "base", "optimistic"]
MONTHS = 12
PAYBACK_CAP_MONTHS = 60

STARTUP_CATEGORIES = [
    "Registration & legal",
    "Equipment & infrastructure",
    "Initial inventory",
    "Rent & utilities",
    "Transportation & logistics",
    "Marketing & customer acquisition",
    "Staffing (pre-opening)",
    "Working capital",
    "Contingency reserve",
]
# Startup categories that remain as cash on hand at launch (used for the cash-balance check).
LIQUID_CATEGORIES = {"Working capital", "Contingency reserve"}


@dataclass
class Shocks:
    """Multipliers applied on top of a scenario (used for sensitivity analysis)."""

    price: float = 1.0
    volume: float = 1.0
    unit_cost: float = 1.0
    fixed_opex: float = 1.0
    fx_depreciation: float = 0.0  # 0.20 = cedi loses 20% against USD, no price pass-through
    label: str = "none"


@dataclass
class Inputs:
    businesses: pd.DataFrame
    globals_: dict
    startup: pd.DataFrame
    revenue: pd.DataFrame
    opex: pd.DataFrame
    fx: float = field(init=False)

    def __post_init__(self) -> None:
        self.fx = float(self.globals_["fx_ghs_per_usd"])


def load_inputs() -> Inputs:
    g = pd.read_csv(INPUTS / "global_assumptions.csv")
    return Inputs(
        businesses=pd.read_csv(INPUTS / "businesses.csv"),
        globals_=dict(zip(g["parameter"], g["value"])),
        startup=pd.read_csv(INPUTS / "startup_costs.csv"),
        revenue=pd.read_csv(INPUTS / "revenue_drivers.csv"),
        opex=pd.read_csv(INPUTS / "operating_costs.csv"),
    )


def to_usd(amount: float, currency: str, fx: float, fx_dep: float = 0.0) -> float:
    """Convert an amount to USD. GHS amounts are hit by any FX depreciation shock."""
    if str(currency).upper() == "GHS":
        return float(amount) / (fx * (1.0 + fx_dep))
    return float(amount)


def volume_for_month(month: int, start: int, ramp: int, steady: float, growth: float) -> float:
    """Units sold in a given operating month (1-based)."""
    if month < start:
        return 0.0
    k = month - start + 1  # months since the line went live, 1-based
    if ramp > 0 and k <= ramp:
        return steady * k / ramp
    return steady * (1.0 + growth) ** (k - max(ramp, 0))


def startup_items(inp: Inputs, bid: str) -> pd.DataFrame:
    """Startup budget in USD. The contingency reserve is calculated, never typed in:
    contingency_rate x (all other startup items)."""
    s = inp.startup[inp.startup["business_id"] == bid].copy()
    s["amount_usd"] = [to_usd(a, c, inp.fx) for a, c in zip(s["amount"], s["currency"])]
    unknown = set(s["category"]) - set(STARTUP_CATEGORIES)
    if unknown:
        raise ValueError(f"{bid}: unknown startup categories {unknown}")
    if "Contingency reserve" in set(s["category"]):
        raise ValueError(f"{bid}: contingency is calculated by the model - remove it from startup_costs.csv")
    rate = float(inp.globals_["contingency_rate"])
    contingency = {
        "business_id": bid, "category": "Contingency reserve",
        "item": f"Contingency reserve ({rate:.0%} of other startup costs)",
        "amount": round(rate * s["amount_usd"].sum(), 2), "currency": "USD", "useful_life_months": None,
        "basis": "Assumption", "source_ref": "-", "amount_usd": round(rate * s["amount_usd"].sum(), 2),
    }
    return pd.concat([s, pd.DataFrame([contingency])], ignore_index=True)


def run_business(inp: Inputs, bid: str, scenario: str, shocks: Shocks | None = None) -> pd.DataFrame:
    """Return a 12-row monthly projection for one business and scenario."""
    shocks = shocks or Shocks()
    biz = inp.businesses.set_index("business_id").loc[bid]
    fx = inp.fx
    dep = shocks.fx_depreciation

    # --- revenue lines --------------------------------------------------------------
    rev = inp.revenue[inp.revenue["business_id"] == bid]
    lines = {}
    for line, grp in rev.groupby("line", sort=False):
        p = grp.set_index("parameter")
        lines[line] = {
            "price": to_usd(p.loc["price", scenario], p.loc["price", "currency"], fx, dep) * shocks.price,
            "unit_cost": to_usd(p.loc["unit_cost", scenario], p.loc["unit_cost", "currency"], fx, dep)
            * shocks.unit_cost,
            "steady": float(p.loc["steady_volume", scenario]) * shocks.volume,
            "start": int(p.loc["start_month", scenario]),
            "ramp": int(p.loc["ramp_months", scenario]),
            "growth": float(p.loc["monthly_growth", scenario]),
        }

    # --- operating costs -------------------------------------------------------------
    ox = inp.opex[inp.opex["business_id"] == bid]
    known = {"fixed_month", "payroll_month", "variable_pct_revenue"}
    if set(ox["cost_type"]) - known:
        raise ValueError(f"{bid}: unknown cost_type {set(ox['cost_type']) - known}")
    ssnit = 1.0 + float(inp.globals_["ssnit_employer_rate"])
    fixed = ox[ox["cost_type"] == "fixed_month"]
    payroll = ox[ox["cost_type"] == "payroll_month"]
    variable = ox[ox["cost_type"] == "variable_pct_revenue"]
    fixed_usd = (
        sum(to_usd(v, c, fx, dep) for v, c in zip(fixed[scenario], fixed["currency"]))
        + sum(to_usd(v, c, fx, dep) * ssnit for v, c in zip(payroll[scenario], payroll["currency"]))
    ) * shocks.fixed_opex
    var_pct = float(variable[scenario].sum())

    # --- depreciation ------------------------------------------------------------------
    s = startup_items(inp, bid)
    depreciable = s[s["useful_life_months"].fillna(0) > 0]
    monthly_dep = float((depreciable["amount_usd"] / depreciable["useful_life_months"]).sum())

    tax_mode = str(biz["tax_mode"]).strip().lower()
    tax_rate = float(biz["tax_rate"])

    rows, loss_cf = [], 0.0
    for m in range(1, MONTHS + 1):
        revenue = cogs = 0.0
        units = {}
        for name, L in lines.items():
            v = volume_for_month(m, L["start"], L["ramp"], L["steady"], L["growth"])
            units[name] = v
            revenue += v * L["price"]
            cogs += v * L["unit_cost"]
        gross = revenue - cogs
        var_opex = var_pct * revenue
        opex_total = fixed_usd + var_opex
        ebitda = gross - opex_total
        ebit = ebitda - monthly_dep

        if tax_mode == "turnover":
            tax = tax_rate * revenue
        elif tax_mode == "cit":
            if ebit <= 0:
                loss_cf += -ebit
                tax = 0.0
            else:
                used = min(loss_cf, ebit)
                loss_cf -= used
                taxable = ebit - used
                tax = tax_rate * taxable
        else:
            raise ValueError(f"{bid}: unknown tax_mode {tax_mode}")

        net = ebit - tax
        ocf = net + monthly_dep
        rows.append(
            {
                "business_id": bid,
                "business": biz["short_name"],
                "scenario": scenario,
                "month": m,
                "revenue": revenue,
                "cogs": cogs,
                "gross_profit": gross,
                "fixed_opex": fixed_usd,
                "variable_opex": var_opex,
                "operating_expenses": opex_total,
                "ebitda": ebitda,
                "depreciation_amortisation": monthly_dep,
                "net_operating_profit": ebit,
                "tax": tax,
                "net_profit": net,
                "operating_cash_flow": ocf,
                **{f"units_{k}": v for k, v in units.items()},
            }
        )

    df = pd.DataFrame(rows)
    invest = float(s["amount_usd"].sum())
    liquid = float(s.loc[s["category"].isin(LIQUID_CATEGORIES), "amount_usd"].sum())
    df["cumulative_cash_flow"] = df["operating_cash_flow"].cumsum()
    df["investment_recovered_pct"] = df["cumulative_cash_flow"] / invest
    df["cash_balance"] = liquid + df["cumulative_cash_flow"]
    df.attrs.update(investment=invest, liquid=liquid, fixed_usd=fixed_usd, var_pct=var_pct,
                    monthly_dep=monthly_dep, tax_mode=tax_mode, tax_rate=tax_rate)
    return df


def summarise(df: pd.DataFrame) -> dict:
    a = df.attrs
    invest = a["investment"]
    last = df.iloc[-1]

    # Operating break-even month: first month from which net operating profit stays >= 0.
    be_month = None
    for m in df["month"]:
        if (df.loc[df["month"] >= m, "net_operating_profit"] >= 0).all():
            be_month = int(m)
            break

    # Payback: first month cumulative operating cash flow >= initial investment.
    hit = df[df["cumulative_cash_flow"] >= invest]
    if not hit.empty:
        payback, payback_note = float(hit["month"].iloc[0]), "within 12 months"
    elif last["operating_cash_flow"] > 0:
        remaining = invest - last["cumulative_cash_flow"]
        payback, payback_note = 12 + remaining / last["operating_cash_flow"], "extrapolated at month-12 run-rate"
        if payback > PAYBACK_CAP_MONTHS:  # extrapolation beyond five years is not meaningful
            payback, payback_note = float("nan"), f"beyond {PAYBACK_CAP_MONTHS} months at month-12 run-rate"
    else:
        payback, payback_note = float("nan"), "not reached (negative month-12 cash flow)"

    # Monthly break-even revenue at the month-12 cost structure.
    rev12 = last["revenue"]
    turnover_tax = a["tax_rate"] if a["tax_mode"] == "turnover" else 0.0
    cm_ratio = (rev12 - last["cogs"] - last["variable_opex"] - turnover_tax * rev12) / rev12 if rev12 else float("nan")
    fixed_plus_dep = a["fixed_usd"] + a["monthly_dep"]
    be_revenue = fixed_plus_dep / cm_ratio if cm_ratio and cm_ratio > 0 else float("nan")

    return {
        "business_id": last["business_id"],
        "business": last["business"],
        "scenario": last["scenario"],
        "initial_investment": invest,
        "revenue_12m": df["revenue"].sum(),
        "cogs_12m": df["cogs"].sum(),
        "gross_profit_12m": df["gross_profit"].sum(),
        "gross_margin_pct": df["gross_profit"].sum() / df["revenue"].sum() if df["revenue"].sum() else float("nan"),
        "operating_expenses_12m": df["operating_expenses"].sum(),
        "net_operating_profit_12m": df["net_operating_profit"].sum(),
        "tax_12m": df["tax"].sum(),
        "net_profit_12m": df["net_profit"].sum(),
        "operating_cash_flow_12m": df["operating_cash_flow"].sum(),
        "month12_revenue": rev12,
        "month12_net_profit": last["net_profit"],
        "roi_12m_pct": df["net_profit"].sum() / invest,
        "run_rate_annual_roi_pct": last["net_profit"] * 12 / invest,
        "operating_breakeven_month": be_month,
        "breakeven_monthly_revenue": be_revenue,
        "contribution_margin_pct": cm_ratio,
        "payback_months": payback,
        "payback_note": payback_note,
        "min_cash_balance": df["cash_balance"].min(),
        "min_cash_month": int(df.loc[df["cash_balance"].idxmin(), "month"]),
    }


def sensitivity(inp: Inputs, bid: str) -> list[dict]:
    """One-at-a-time +/-20% shocks on the base case, plus a 20% cedi depreciation stress."""
    base = summarise(run_business(inp, bid, "base"))["net_profit_12m"]
    tests = [
        Shocks(price=0.8, label="Price -20%"), Shocks(price=1.2, label="Price +20%"),
        Shocks(volume=0.8, label="Volume -20%"), Shocks(volume=1.2, label="Volume +20%"),
        Shocks(unit_cost=1.2, label="Unit cost +20%"), Shocks(unit_cost=0.8, label="Unit cost -20%"),
        Shocks(fixed_opex=1.2, label="Fixed opex +20%"), Shocks(fixed_opex=0.8, label="Fixed opex -20%"),
        Shocks(fx_depreciation=0.20, label="FX shock: GHS/USD +20%"),
    ]
    out = []
    for t in tests:
        np12 = summarise(run_business(inp, bid, "base", t))["net_profit_12m"]
        out.append({"business_id": bid, "test": t.label, "base_net_profit_12m": base,
                    "shocked_net_profit_12m": np12, "delta": np12 - base})
    return out


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    inp = load_inputs()
    monthly, summary, sens, breakdown = [], [], [], []

    for bid in inp.businesses["business_id"]:
        s = startup_items(inp, bid)
        total = s["amount_usd"].sum()
        lo, hi = float(inp.globals_["budget_min_usd"]), float(inp.globals_["budget_max_usd"])
        if not lo <= total <= hi:
            raise ValueError(f"{bid}: startup budget ${total:,.0f} is outside ${lo:,.0f}-${hi:,.0f}")
        cat = s.groupby("category")["amount_usd"].sum().reindex(STARTUP_CATEGORIES, fill_value=0.0)
        for c, v in cat.items():
            breakdown.append({"business_id": bid, "category": c, "amount_usd": round(v, 2),
                              "share_pct": round(v / total, 4)})

        for sc in SCENARIOS:
            df = run_business(inp, bid, sc)
            monthly.append(df)
            summary.append(summarise(df))
        sens.extend(sensitivity(inp, bid))

    pd.concat(monthly, ignore_index=True).round(2).to_csv(OUTPUTS / "monthly_projections.csv", index=False)
    pd.DataFrame(summary).round(4).to_csv(OUTPUTS / "summary_metrics.csv", index=False)
    pd.DataFrame(breakdown).to_csv(OUTPUTS / "investment_breakdown.csv", index=False)
    pd.DataFrame(sens).round(2).to_csv(OUTPUTS / "sensitivity_analysis.csv", index=False)

    sm = pd.DataFrame(summary)
    view = sm.pivot(index="business", columns="scenario", values="net_profit_12m")[SCENARIOS]
    print("12-month net profit (USD) by scenario")
    print(view.round(0).to_string())
    print("\nWrote outputs to", OUTPUTS)


if __name__ == "__main__":
    main()
