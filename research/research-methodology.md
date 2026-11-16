# Research Methodology

> **Research period:** November 2026 (sources accessed 16 November 2026)
> **Analyst role:** Business Analyst / Market Research & Investment Feasibility
> **Scope:** Small-business opportunities in Ghana requiring USD 5,000–20,000 of initial investment, assessed for both Ghanaian (local) and foreign entrepreneurs.

[← Back to README](../README.md)

---

## 1. Research question

> *Which small businesses can an entrepreneur realistically establish in Ghana in 2027 with USD 5,000–20,000, and which one offers the best balance of demand, profitability, feasibility and risk?*

Sub-questions:

1. What macroeconomic, regulatory and cost conditions will a new small business face in 2026–2027?
2. Which sectors show **evidenced** demand (imports, supply gaps, price trends, infrastructure failures) rather than assumed demand?
3. Which opportunities can reach a **minimum efficient scale** inside the budget, and which cannot?
4. What are the realistic unit economics, break-even point and payback period for the strongest five?
5. What changes for a **foreign** investor (capital thresholds, reserved activities, permits)?

## 2. Six-stage approach

| Stage | Activity | Output |
|---|---|---|
| 1 | Define methodology; build a long list of opportunities across 10 sector groups | This document; [opportunity-identification.md](../opportunities/opportunity-identification.md) |
| 2 | Validate demand with secondary data; screen the long list against hard gates and five criteria; shortlist five | [opportunity-comparison.md](../opportunities/opportunity-comparison.md), [shortlisted-businesses.md](../opportunities/shortlisted-businesses.md) |
| 3 | Competitor and industry analysis for the shortlist (Porter's Five Forces, PESTLE, TAM/SAM/SOM) | [industry-analysis.md](industry-analysis.md), [competitor-analysis.md](../strategic-analysis/competitor-analysis.md), [market-demand.md](market-demand.md) |
| 4 | Driver-based 12-month financial model with three scenarios and sensitivity tests | [financial-analysis/](../financial-analysis/), [models/financial_model.py](../models/financial_model.py) |
| 5 | SWOT, risk register, weighted scoring, final recommendation | [strategic-analysis/](../strategic-analysis/) |
| 6 | Charts, datasets, reproducible scripts, documentation | [visuals/](../visuals/), [data/](../data/) |

## 3. Source hierarchy

Sources were used in the following order of preference. Every material statistic in this repository carries a source ID (for example `MAC-07`, grouped by topic) that resolves in [data/sources.md](../data/sources.md), with publisher, publication date, URL and verification status.

| Tier | Source type | Examples | Use |
|---|---|---|---|
| 1 | Official Ghanaian statistics and regulators | Ghana Statistical Service, Bank of Ghana, Ministry of Finance, GIPC, GRA, ORC, PURC, Energy Commission, MoFA | Macro data, law, tax, tariffs |
| 2 | Multilateral and research bodies | World Bank, IMF, AfDB, FAO, ITC, UN Comtrade, USDA FAS, IFPRI, peer-reviewed journals | Trade flows, sector data, unit economics |
| 3 | Credible media and industry bodies | Graphic, Citi Newsroom, MyJoyOnline, B&FT, Reuters, TechCabal, law-firm briefings | Recent announcements and prices, cross-checked where possible |
| 4 | Marketplace listings and company websites | Jiji, Tonaton, meQasa, installer price lists | Indicative prices only — never treated as market averages |

## 4. Evidence classification

Every number in the analysis is labelled with one of four classes. This is the single most important convention in the repository.

| Label | Meaning | Example |
|---|---|---|
| **[F] Verified fact** | Published by a Tier 1–3 source and read at the cited URL | Policy rate, CPI, GIPC capital thresholds |
| **[E] Reasonable estimate** | Derived from verified data with a stated method (triangulation, conversion, listing ranges) | Monthly shop rent from several listings |
| **[A] Research assumption** | Analyst judgement where no reliable data exists; always stress-tested in scenarios | Customer conversion rates, ramp-up speed |
| **[P] Financial projection** | Output of the financial model; conditional on the assumptions | 12-month net profit, payback month |

Two further conventions:

- **Search-snippet data** (seen in a search summary but not read on the source page) is not used as an [F] fact. Where it informs an estimate, the limitation is disclosed.
- **Currency.** All financial outputs are in USD. Local costs are entered in Ghana cedis (GHS) and converted at a single model exchange rate (see [financial-assumptions.md](../financial-analysis/financial-assumptions.md)), so readers can re-run the model at a different rate.

## 5. Opportunity screening method (Stage 2)

**Hard gates** — an opportunity is rejected if it fails either:

1. **Budget gate:** a viable, minimum-efficient-scale operation cannot be launched for ≤ USD 20,000 including working capital and a contingency reserve.
2. **Evidence gate:** no credible evidence of unmet or growing demand could be found.

A third check — **foreign-investor access** — does not reject an opportunity (the primary investor profile is a Ghanaian entrepreneur), but it is flagged and scored, because Ghana's investment law sets capital minimums and reserves some activities for Ghanaians.

**Screening criteria** (each scored 1–5, equal weights):

| Criterion | 5 means | 1 means |
|---|---|---|
| Demand evidence | Strong, quantified, growing demand (e.g., import substitution, infrastructure gap) | Anecdotal or declining |
| Budget fit | Comfortably viable at $5–20k | Only viable well above $20k |
| Margin potential | Gross margin and pricing power support profit at small scale | Commodity margins, price-taker |
| Competitive intensity | Fragmented or under-served market with a clear gap | Saturated, low differentiation |
| Access & regulation | Simple licensing, open to all investors | Heavy licensing or reserved activity |

The top five by screening score proceed to financial modelling, subject to analyst review for sector diversity (so the shortlist is not five variants of one idea).

## 6. Financial modelling method (Stage 4)

- **Driver-based monthly model** for months 1–12 after launch: volume × price for each revenue line, unit costs for COGS, fixed and variable operating costs, straight-line depreciation and the applicable small-business tax.
- **Three scenarios** — conservative, base, optimistic — vary price, volume, unit cost, ramp-up speed and selected operating costs. Scenario values are stored side by side in the input CSVs.
- **Sensitivity analysis** — one-at-a-time ±20% shocks to price, volume, unit cost and fixed costs, plus a 20% cedi-depreciation stress test with no price pass-through.
- **Metrics:** revenue, COGS, gross profit, operating expenses, net operating profit, net profit, operating cash flow, operating break-even month, break-even monthly revenue, payback period and ROI (12-month and month-12 run-rate).
- **Owner labour is costed.** Each model includes a salaried manager role at a market wage, so profit is a return on capital, not disguised owner wages.

All inputs live in [`data/datasets/inputs/`](../data/datasets/inputs/) and all outputs are regenerated by one command (see [README](../README.md#reproduce-the-analysis)).

## 7. Final ranking method (Stage 5)

Seven weighted criteria from the project brief: market demand (20%), investment affordability (15%), profitability potential (20%), competitive intensity (10%), operational feasibility (15%), scalability (10%) and risk level (10%).

- Three criteria are **calculated by formula** from model and risk-register outputs (affordability, profitability, risk), so they cannot be adjusted by hand.
- Four are **analyst-scored** with a written rationale and evidence reference.
- The ranking is **re-run under two alternative weight sets** (equal weights; risk-averse) to test robustness. See [final-recommendation.md](../strategic-analysis/final-recommendation.md).

## 8. Limitations

1. **Secondary research only.** No primary customer interviews, supplier quotations or site visits were possible. Prices from marketplace listings are indicative. The recommended next step for any investor is a 4–6 week primary validation sprint (see [final-recommendation.md](../strategic-analysis/final-recommendation.md)).
2. **Data lags.** Some Ghanaian sector statistics are published with a 1–3 year lag; the most recent available year is always stated.
3. **Exchange-rate exposure.** The cedi has moved sharply in both directions since 2022. USD results are sensitive to the rate; the model isolates this in a dedicated stress test.
4. **Informality.** A large share of Ghanaian commerce is informal, so market sizes for small-business segments are estimated top-down and labelled [E].
5. **Projections are not forecasts of certainty.** They describe what happens *if* the stated assumptions hold.
