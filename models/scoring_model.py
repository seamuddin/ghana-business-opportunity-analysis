"""
Weighted scoring model for the five shortlisted opportunities.

Seven criteria, each scored 1 (worst) to 5 (best):

  Derived from model outputs (formula-based, so they cannot be "tuned" by hand):
    * Investment affordability  - linear on initial investment: $5,000 -> 5, $20,000 -> 1
    * Profitability potential    - linear on BASE-case month-12 run-rate annual ROI:
                                   0% or less -> 1, 150% or more -> 5
    * Risk level                 - linear on the mean likelihood x impact score in
                                   risk_register.csv: 4 or less -> 5 (low risk), 16 or more -> 1
  Analyst-scored with written rationale (scoring_qualitative.csv):
    * Market demand, Competitive intensity (5 = least intense), Operational feasibility,
      Scalability

Weights come from scoring_weights.csv. Three weight sets are run to test whether the
ranking is robust: the brief's recommended weights, equal weights and a risk-averse set.

Usage:  python models/scoring_model.py   (run financial_model.py first)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "data" / "datasets" / "inputs"
OUTPUTS = ROOT / "data" / "datasets" / "outputs"

# Anchors for the formula-based criteria (documented in strategic-analysis/final-recommendation.md)
AFFORD_BEST, AFFORD_WORST = 5_000.0, 20_000.0
ROI_FLOOR, ROI_CEILING = 0.0, 1.5
RISK_LOW, RISK_HIGH = 4.0, 16.0


def linear_score(x: float, worst: float, best: float) -> float:
    """Map x onto 1..5 where `worst` -> 1 and `best` -> 5, clipped."""
    t = (x - worst) / (best - worst)
    return round(1 + 4 * min(max(t, 0.0), 1.0), 2)


def build_scores() -> pd.DataFrame:
    summary = pd.read_csv(OUTPUTS / "summary_metrics.csv")
    base = summary[summary["scenario"] == "base"].set_index("business_id")
    risks = pd.read_csv(INPUTS / "risk_register.csv")
    risks["score"] = risks["likelihood"] * risks["impact"]
    mean_risk = risks.groupby("business_id")["score"].mean()
    qual = pd.read_csv(INPUTS / "scoring_qualitative.csv")

    rows = []
    for bid, r in base.iterrows():
        rows += [
            {"business_id": bid, "criterion": "Investment affordability",
             "score": linear_score(r["initial_investment"], AFFORD_WORST, AFFORD_BEST),
             "rationale": f"Initial investment ${r['initial_investment']:,.0f}"},
            {"business_id": bid, "criterion": "Profitability potential",
             "score": linear_score(r["run_rate_annual_roi_pct"], ROI_FLOOR, ROI_CEILING),
             "rationale": f"Base-case month-12 run-rate ROI {r['run_rate_annual_roi_pct']:.0%}"},
            {"business_id": bid, "criterion": "Risk level",
             "score": linear_score(mean_risk[bid], RISK_HIGH, RISK_LOW),
             "rationale": f"Mean risk-register score {mean_risk[bid]:.1f} / 25"},
        ]
    derived = pd.DataFrame(rows)
    scores = pd.concat([qual[["business_id", "criterion", "score", "rationale"]], derived], ignore_index=True)
    names = base["business"].to_dict()
    scores["business"] = scores["business_id"].map(names)
    return scores


def rank(scores: pd.DataFrame, weights: pd.DataFrame, weight_col: str) -> pd.DataFrame:
    w = weights.set_index("criterion")[weight_col]
    if abs(w.sum() - 1.0) > 1e-9:
        raise ValueError(f"{weight_col} weights sum to {w.sum()}, expected 1.0")
    s = scores.copy()
    s["weight"] = s["criterion"].map(w)
    if s["weight"].isna().any():
        raise ValueError(f"Missing weight for {s.loc[s['weight'].isna(), 'criterion'].unique()}")
    s["weighted"] = s["score"] * s["weight"]
    table = s.pivot_table(index=["business_id", "business"], columns="criterion", values="score")
    table = table[list(w.index)]
    table["weighted_score"] = s.groupby(["business_id", "business"])["weighted"].sum()
    table = table.sort_values("weighted_score", ascending=False)
    table["rank"] = range(1, len(table) + 1)
    return table.reset_index()


SCREEN_CRITERIA = ["demand_evidence", "budget_fit", "margin_potential", "competitive_intensity", "access_regulation"]
SCREEN_VARIANTS = {
    "equal_weights (method used)": {c: 1.0 for c in SCREEN_CRITERIA},
    "demand_double_weighted": {**{c: 1.0 for c in SCREEN_CRITERIA}, "demand_evidence": 2.0},
    "local_investor_only (access excluded)": {**{c: 1.0 for c in SCREEN_CRITERIA}, "access_regulation": 0.0},
    "margin_double_weighted": {**{c: 1.0 for c in SCREEN_CRITERIA}, "margin_potential": 2.0},
}


def screening_robustness() -> pd.DataFrame:
    """Re-run the Stage 2 long-list screen under alternative criterion weights."""
    df = pd.read_csv(INPUTS / "opportunity_screening.csv")
    rows = []
    for name, w in SCREEN_VARIANTS.items():
        total_w = sum(w.values())
        score = sum(df[c] * wt for c, wt in w.items()) / total_w
        ranked = df.assign(score=score.round(3)).sort_values(["score", "demand_evidence"], ascending=False)
        for pos, (_, r) in enumerate(ranked.iterrows(), start=1):
            rows.append({"variant": name, "rank": pos, "id": r["id"], "opportunity": r["opportunity"],
                         "score": r["score"], "in_top5": pos <= 5})
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "screening_robustness.csv", index=False)
    return out


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    sr = screening_robustness()
    print("Stage 2 top five under alternative screening weights:")
    for v, g in sr[sr["in_top5"]].groupby("variant", sort=False):
        print(f"  {v}: {', '.join(g['id'])}")
    print()

    weights = pd.read_csv(INPUTS / "scoring_weights.csv")
    scores = build_scores()
    scores.to_csv(OUTPUTS / "criterion_scores.csv", index=False)

    main_rank = rank(scores, weights, "weight_recommended")
    main_rank.round(3).to_csv(OUTPUTS / "weighted_ranking.csv", index=False)

    robustness = []
    for col in [c for c in weights.columns if c.startswith("weight_")]:
        r = rank(scores, weights, col)
        for _, row in r.iterrows():
            robustness.append({"weight_set": col.replace("weight_", ""), "business": row["business"],
                               "weighted_score": round(row["weighted_score"], 3), "rank": row["rank"]})
    pd.DataFrame(robustness).to_csv(OUTPUTS / "ranking_robustness.csv", index=False)

    print(main_rank[["rank", "business", "weighted_score"]].round(2).to_string(index=False))
    print("\nRank under each weight set:")
    print(pd.DataFrame(robustness).pivot(index="business", columns="weight_set", values="rank").to_string())


if __name__ == "__main__":
    main()
