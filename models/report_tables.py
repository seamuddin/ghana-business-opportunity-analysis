"""
Build the markdown tables used in the write-up directly from model inputs and outputs,
then inject them into the documents between marker comments:

    <!-- BEGIN TABLE: table_name -->
    ...generated content...
    <!-- END TABLE: table_name -->

This keeps every number in the prose documents identical to the model. Re-running
`python models/run_all.py` refreshes all tables after an assumption changes.

Generated tables are also saved to data/datasets/outputs/tables/<name>.md.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "data" / "datasets" / "inputs"
OUTPUTS = ROOT / "data" / "datasets" / "outputs"
TABLES = OUTPUTS / "tables"
SCEN = ["conservative", "base", "optimistic"]


# --- formatting helpers -----------------------------------------------------------------
def usd(x) -> str:
    if pd.isna(x):
        return "n/a"
    return f"-${abs(x):,.0f}" if x < 0 else f"${x:,.0f}"


def pct(x, digits: int = 0) -> str:
    return "n/a" if pd.isna(x) else f"{x * 100:.{digits}f}%"


def months(x, note: str = "") -> str:
    if pd.isna(x):
        return "> 60" if "beyond" in note else "not reached"
    return f"{x:.0f}" if float(x).is_integer() else f"{x:.1f}"


def md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(str(v) for v in r.values) + " |")
    return "\n".join(lines)


# --- table builders -----------------------------------------------------------------------
def build(tables: dict) -> None:
    biz = pd.read_csv(INPUTS / "businesses.csv")
    names = biz.set_index("business_id")["short_name"].to_dict()
    order = list(biz["business_id"])
    g = pd.read_csv(INPUTS / "global_assumptions.csv")
    fx = float(g.loc[g["parameter"] == "fx_ghs_per_usd", "value"].iloc[0])
    s = pd.read_csv(OUTPUTS / "summary_metrics.csv")
    m = pd.read_csv(OUTPUTS / "monthly_projections.csv")
    inv = pd.read_csv(OUTPUTS / "investment_breakdown.csv")
    sens = pd.read_csv(OUTPUTS / "sensitivity_analysis.csv")
    startup = pd.read_csv(INPUTS / "startup_costs.csv")
    rev = pd.read_csv(INPUTS / "revenue_drivers.csv")
    opex = pd.read_csv(INPUTS / "operating_costs.csv")
    base = s[s["scenario"] == "base"].set_index("business_id")

    # Headline comparison (base case)
    rows = []
    for b in order:
        r = base.loc[b]
        rows.append({
            "Business": names[b], "Initial investment": usd(r["initial_investment"]),
            "Year-1 revenue": usd(r["revenue_12m"]), "Gross margin": pct(r["gross_margin_pct"]),
            "Year-1 net profit": usd(r["net_profit_12m"]), "Year-1 ROI": pct(r["roi_12m_pct"]),
            "Month-12 run-rate ROI": pct(r["run_rate_annual_roi_pct"]),
            "Operating break-even month": months(r["operating_breakeven_month"]),
            "Payback (months)": months(r["payback_months"], r["payback_note"]),
        })
    tables["financial_comparison_base"] = md_table(pd.DataFrame(rows))

    # Scenario comparison
    rows = []
    for b in order:
        for sc in SCEN:
            r = s[(s["business_id"] == b) & (s["scenario"] == sc)].iloc[0]
            rows.append({
                "Business": names[b] if sc == "conservative" else "", "Scenario": sc.capitalize(),
                "Year-1 revenue": usd(r["revenue_12m"]), "Year-1 net profit": usd(r["net_profit_12m"]),
                "Year-1 ROI": pct(r["roi_12m_pct"]), "Month-12 net profit": usd(r["month12_net_profit"]),
                "Run-rate ROI": pct(r["run_rate_annual_roi_pct"]),
                "Break-even month": months(r["operating_breakeven_month"]),
                "Payback (months)": months(r["payback_months"], r["payback_note"]),
            })
    tables["scenario_detail"] = md_table(pd.DataFrame(rows))

    np_pivot = s.pivot(index="business_id", columns="scenario", values="net_profit_12m").loc[order, SCEN]
    tables["scenario_net_profit"] = md_table(pd.DataFrame({
        "Business": [names[b] for b in order],
        **{sc.capitalize(): [usd(v) for v in np_pivot[sc]] for sc in SCEN},
        "Spread (optimistic - conservative)": [usd(np_pivot.loc[b, "optimistic"] - np_pivot.loc[b, "conservative"]) for b in order],
    }))

    # Investment by category
    pv = inv.pivot(index="category", columns="business_id", values="amount_usd")[order]
    cat_order = list(dict.fromkeys(inv["category"]))
    pv = pv.loc[cat_order]
    out = pd.DataFrame({"Category": pv.index})
    for b in order:
        out[names[b]] = [usd(v) for v in pv[b]]
    total = pd.DataFrame([{"Category": "**Total initial investment**",
                           **{names[b]: f"**{usd(pv[b].sum())}**" for b in order}}])
    tables["investment_by_category"] = md_table(pd.concat([out, total], ignore_index=True))

    # Item-level startup budgets
    for b in order:
        it = startup[startup["business_id"] == b].copy()
        it["usd"] = [a / fx if c == "GHS" else a for a, c in zip(it["amount"], it["currency"])]
        sub = it["usd"].sum()
        cont_rate = float(g.loc[g["parameter"] == "contingency_rate", "value"].iloc[0])
        rows = [{
            "Category": r["category"], "Item": r["item"].replace(";", ","),
            "Amount (local)": f"GHS {r['amount']:,.0f}" if r["currency"] == "GHS" else usd(r["amount"]),
            "USD": usd(r["usd"]),
            "Life (months)": "" if pd.isna(r["useful_life_months"]) else f"{r['useful_life_months']:.0f}",
            "Basis": r["basis"], "Source": "" if r["source_ref"] == "-" else str(r["source_ref"]).replace(";", ", "),
        } for _, r in it.iterrows()]
        rows.append({"Category": "Contingency reserve", "Item": f"{cont_rate:.0%} of the items above (calculated)",
                     "Amount (local)": "", "USD": usd(sub * cont_rate), "Life (months)": "", "Basis": "Assumption", "Source": ""})
        rows.append({"Category": "**Total**", "Item": "", "Amount (local)": "", "USD": f"**{usd(sub * (1 + cont_rate))}**",
                     "Life (months)": "", "Basis": "", "Source": ""})
        tables[f"investment_items_{b}"] = md_table(pd.DataFrame(rows))

    # Monthly P&L and cash flow (base case) per business
    for b in order:
        d = m[(m["business_id"] == b) & (m["scenario"] == "base")]
        out = pd.DataFrame({
            "Month": d["month"].astype(int), "Revenue": d["revenue"].map(usd), "COGS": d["cogs"].map(usd),
            "Gross profit": d["gross_profit"].map(usd), "Operating expenses": d["operating_expenses"].map(usd),
            "D&A": d["depreciation_amortisation"].map(usd), "Net operating profit": d["net_operating_profit"].map(usd),
            "Tax": d["tax"].map(usd), "Net profit": d["net_profit"].map(usd),
            "Operating cash flow": d["operating_cash_flow"].map(usd),
            "Cumulative cash flow": d["cumulative_cash_flow"].map(usd),
        })
        tot = {"Month": "**Year 1**", "Revenue": f"**{usd(d['revenue'].sum())}**", "COGS": usd(d["cogs"].sum()),
               "Gross profit": usd(d["gross_profit"].sum()), "Operating expenses": usd(d["operating_expenses"].sum()),
               "D&A": usd(d["depreciation_amortisation"].sum()),
               "Net operating profit": usd(d["net_operating_profit"].sum()), "Tax": usd(d["tax"].sum()),
               "Net profit": f"**{usd(d['net_profit'].sum())}**", "Operating cash flow": usd(d["operating_cash_flow"].sum()),
               "Cumulative cash flow": ""}
        tables[f"monthly_{b}_base"] = md_table(pd.concat([out, pd.DataFrame([tot])], ignore_index=True))

    # Monthly revenue, all businesses, base case
    rv = m[m["scenario"] == "base"].pivot(index="month", columns="business_id", values="revenue")[order]
    out = pd.DataFrame({"Month": rv.index})
    for b in order:
        out[names[b]] = [usd(v) for v in rv[b]]
    tables["monthly_revenue_base"] = md_table(out)

    # Break-even analysis
    rows = []
    for b in order:
        r = base.loc[b]
        mos = (r["month12_revenue"] - r["breakeven_monthly_revenue"]) / r["month12_revenue"]
        be = {sc: s[(s["business_id"] == b) & (s["scenario"] == sc)].iloc[0] for sc in SCEN}
        rows.append({
            "Business": names[b], "Contribution margin": pct(r["contribution_margin_pct"]),
            "Break-even revenue / month": usd(r["breakeven_monthly_revenue"]),
            "Month-12 revenue": usd(r["month12_revenue"]), "Margin of safety": pct(mos),
            "Break-even month (cons / base / opt)": " / ".join(months(be[sc]["operating_breakeven_month"]) for sc in SCEN),
            "Payback months (cons / base / opt)": " / ".join(months(be[sc]["payback_months"], be[sc]["payback_note"]) for sc in SCEN),
        })
    tables["breakeven"] = md_table(pd.DataFrame(rows))

    # Cash adequacy
    rows = []
    for b in order:
        for sc in SCEN:
            d = m[(m["business_id"] == b) & (m["scenario"] == sc)]
            r = s[(s["business_id"] == b) & (s["scenario"] == sc)].iloc[0]
            start_cash = d["cash_balance"].iloc[0] - d["operating_cash_flow"].iloc[0]
            gap = min(0.0, r["min_cash_balance"])
            rows.append({"Business": names[b] if sc == "conservative" else "", "Scenario": sc.capitalize(),
                         "Cash reserve at launch": usd(start_cash), "Lowest cash balance": usd(r["min_cash_balance"]),
                         "Month of lowest balance": int(r["min_cash_month"]),
                         "Month-12 cash balance": usd(d["cash_balance"].iloc[-1]),
                         "Extra funding needed": "none" if gap == 0 else f"**{usd(-gap)}**"})
    tables["cash_adequacy"] = md_table(pd.DataFrame(rows))

    # Sensitivity
    pv = sens.pivot(index="test", columns="business_id", values="delta")[order]
    test_order = list(dict.fromkeys(sens["test"]))
    pv = pv.loc[test_order]
    out = pd.DataFrame({"Shock (one at a time, base case)": pv.index})
    for b in order:
        out[names[b]] = [usd(v) for v in pv[b]]
    basel = pd.DataFrame([{"Shock (one at a time, base case)": "*Base-case year-1 net profit*",
                           **{names[b]: f"*{usd(base.loc[b, 'net_profit_12m'])}*" for b in order}}])
    tables["sensitivity"] = md_table(pd.concat([basel, out], ignore_index=True))

    # Unit economics (base case, first revenue line of each business)
    rows = []
    for b in order:
        rb = rev[rev["business_id"] == b]
        for line in dict.fromkeys(rb["line"]):
            p = rb[rb["line"] == line].set_index("parameter")
            price = p.loc["price", "base"] / (fx if p.loc["price", "currency"] == "GHS" else 1)
            cost = p.loc["unit_cost", "base"] / (fx if p.loc["unit_cost", "currency"] == "GHS" else 1)
            rows.append({"Business": names[b], "Revenue line": line, "Unit": p.loc["price", "unit"],
                         "Price (base)": f"{usd(price)} (GHS {price * fx:,.0f})" if price >= 10 else f"${price:,.2f} (GHS {price * fx:,.2f})",
                         "Unit cost (base)": f"{usd(cost)}" if cost >= 10 else f"${cost:,.2f}",
                         "Unit margin": pct((price - cost) / price),
                         "Steady volume / month (base)": f"{p.loc['steady_volume', 'base']:,.0f}"})
    tables["unit_economics"] = md_table(pd.DataFrame(rows))

    # Assumption tables per business
    for b in order:
        rb = rev[rev["business_id"] == b]
        out = pd.DataFrame({
            "Revenue line": rb["line"], "Parameter": rb["parameter"].str.replace("_", " "),
            "Conservative": rb["conservative"], "Base": rb["base"], "Optimistic": rb["optimistic"],
            "Unit": [f"{c} {u}".replace("- ", "").replace("units ", "").strip() if c not in ("-", "units") else u
                     for c, u in zip(rb["currency"], rb["unit"])],
            "Basis": rb["basis"], "Source": rb["source_ref"].replace("-", "").str.replace(";", ", "),
        })
        tables[f"assumptions_revenue_{b}"] = md_table(out)
        ob = opex[opex["business_id"] == b]
        fmt = lambda v, t: f"{v:.1%}" if t == "variable_pct_revenue" else f"{v:,.0f}"
        out = pd.DataFrame({
            "Cost line": ob["item"].str.replace(";", ","),
            "Type": ob["cost_type"].map({"payroll_month": "Payroll (GHS/month, +13% SSNIT)",
                                         "fixed_month": "Fixed (GHS/month)",
                                         "variable_pct_revenue": "Variable (% of revenue)"}),
            "Conservative": [fmt(v, t) for v, t in zip(ob["conservative"], ob["cost_type"])],
            "Base": [fmt(v, t) for v, t in zip(ob["base"], ob["cost_type"])],
            "Optimistic": [fmt(v, t) for v, t in zip(ob["optimistic"], ob["cost_type"])],
            "Basis": ob["basis"], "Source": ob["source_ref"].replace("-", "").str.replace(";", ", "),
        })
        tables[f"assumptions_opex_{b}"] = md_table(out)

    # Ranking tables
    wr = pd.read_csv(OUTPUTS / "weighted_ranking.csv")
    crit = [c for c in wr.columns if c not in ("business_id", "business", "weighted_score", "rank")]
    out = wr[["rank", "business"] + crit + ["weighted_score"]].copy()
    for c in crit + ["weighted_score"]:
        out[c] = out[c].map(lambda v: f"{v:.2f}")
    out["weighted_score"] = "**" + out["weighted_score"] + "**"
    out.columns = ["Rank", "Business"] + crit + ["Weighted score"]
    tables["weighted_ranking"] = md_table(out)

    rr = pd.read_csv(OUTPUTS / "ranking_robustness.csv")
    pr = rr.pivot(index="business", columns="weight_set", values="rank")
    ps = rr.pivot(index="business", columns="weight_set", values="weighted_score")
    pr = pr.loc[wr["business"]]
    tables["ranking_robustness"] = md_table(pd.DataFrame({
        "Business": pr.index,
        **{f"{c.replace('_', ' ').capitalize()} weights": [f"#{int(pr.loc[i, c])} ({ps.loc[i, c]:.2f})" for i in pr.index]
           for c in ["recommended", "equal", "risk_averse"]},
    }))

    cs = pd.read_csv(OUTPUTS / "criterion_scores.csv")
    derived = cs[cs["criterion"].isin(["Investment affordability", "Profitability potential", "Risk level"])]
    out = derived.pivot(index="business", columns="criterion", values="rationale").loc[wr["business"]]
    sc = derived.pivot(index="business", columns="criterion", values="score").loc[wr["business"]]
    tables["derived_scores"] = md_table(pd.DataFrame({
        "Business": out.index,
        **{c: [f"{sc.loc[i, c]:.2f} — {out.loc[i, c]}" for i in out.index] for c in out.columns},
    }))

    qual = cs[~cs["criterion"].isin(["Investment affordability", "Profitability potential", "Risk level"])].copy()
    qual["order"] = qual["business"].map({b: i for i, b in enumerate(wr["business"])})
    qual = qual.sort_values(["order", "criterion"])
    tables["qualitative_scores"] = md_table(pd.DataFrame({
        "Business": qual["business"], "Criterion": qual["criterion"],
        "Score": qual["score"].map(lambda v: f"{v:g}"), "Rationale": qual["rationale"],
    }))

    # Risk register (full) per business
    rk = pd.read_csv(INPUTS / "risk_register.csv")
    rk["score"] = rk["likelihood"] * rk["impact"]
    for b in order:
        d = rk[rk["business_id"] == b].sort_values("score", ascending=False)
        tables[f"risk_register_{b}"] = md_table(pd.DataFrame({
            "ID": d["risk_id"], "Category": d["category"], "Risk": d["risk"],
            "L": d["likelihood"], "I": d["impact"], "Score": d["score"].map(lambda v: f"**{v}**" if v >= 12 else str(v)),
            "Mitigation": d["mitigation"], "Evidence": d["evidence_ref"].replace("-", "").str.replace(";", ", "),
        }))
    summ = rk.groupby("business_id")["score"].agg(["mean", "max"]).loc[order]
    hi = rk[rk["score"] >= 12].groupby("business_id").size().reindex(order, fill_value=0)
    tables["risk_summary"] = md_table(pd.DataFrame({
        "Business": [names[b] for b in order], "Mean score (1-25)": [f"{v:.1f}" for v in summ["mean"]],
        "Highest score": summ["max"].astype(int), "Risks scored 12 or more": hi.values,
        "Top risk": [rk[rk["business_id"] == b].sort_values("score", ascending=False)["risk"].iloc[0] for b in order],
    }))


def inject(tables: dict) -> list[str]:
    """Replace marker blocks in every markdown file with the generated tables."""
    pattern = re.compile(r"(<!-- BEGIN TABLE: (\w+) -->)(.*?)(<!-- END TABLE: \2 -->)", re.S)
    touched, missing = [], set()
    for md in ROOT.rglob("*.md"):
        if "outputs" in md.parts:
            continue
        text = md.read_text(encoding="utf-8")

        def repl(mt):
            name = mt.group(2)
            if name not in tables:
                missing.add(name)
                return mt.group(0)
            return f"{mt.group(1)}\n{tables[name]}\n{mt.group(4)}"

        new = pattern.sub(repl, text)
        if new != text:
            md.write_text(new, encoding="utf-8")
            touched.append(str(md.relative_to(ROOT)))
    if missing:
        raise KeyError(f"Unknown table markers: {sorted(missing)}")
    return touched


def main() -> None:
    tables: dict[str, str] = {}
    build(tables)
    TABLES.mkdir(parents=True, exist_ok=True)
    for name, body in tables.items():
        (TABLES / f"{name}.md").write_text(body + "\n", encoding="utf-8")
    touched = inject(tables)
    print(f"Built {len(tables)} tables; refreshed {len(touched)} document(s).")


if __name__ == "__main__":
    main()
