# Executive Summary

**Ghana Business Opportunity Analysis 2026 — Profitable small-business opportunities for an investment of US$5,000–20,000**

*Research period: November 2026 · Currency: USD (GHS 11.70 = US$1) · Projections are conditional estimates, not guaranteed returns.*

[← Back to README](../README.md) · Full recommendation: [final-recommendation.md](../strategic-analysis/final-recommendation.md)

---

## The question

Which small business could an entrepreneur realistically establish in Ghana in 2027 with US$5,000–20,000, and which offers the best balance of demand, profitability, feasibility and risk, for both local and foreign investors?

## The answer

**Prioritise a certified, mid-market solar PV installation and maintenance business in Accra**, launched in two stages behind a 6-week validation sprint. In the base case it earns **~US$11.0k net profit in year 1 on ~US$17.0k invested and pays back in about 12 months**. It ranks first under all three weightings tested, although its lead narrows considerably when risk is weighted heavily.

Its main risk is currency: imported equipment priced in USD and sold in cedis. That risk is **operational, not structural**, and is controlled by taking customer deposits before buying equipment and indexing quotes to USD.

**Laundry** is the best alternative for risk-averse and foreign investors. **Broiler grow-out is not recommended** at this budget despite the strongest import-substitution story.

## How the answer was reached

1. **Evidence base:** 188 sources (Bank of Ghana, Ghana Statistical Service, GIPC/GIPA, GRA, PURC, Energy Commission, MoFA, World Bank, IMF, USDA, FAO, credible media, price listings), each labelled as verified fact, estimate, assumption or projection ([sources](../data/sources.md)).
2. **15 opportunities across 10 sector groups** were screened against budget and evidence gates and five criteria. Six were rejected outright (e.g., sachet water, plastic aggregation, mobile money agency) ([comparison](../opportunities/opportunity-comparison.md)).
3. **Five shortlisted businesses** were costed in a reproducible Python model with three scenarios and sensitivity tests ([financial analysis](../financial-analysis/)).
4. **A weighted scoring model** combined formula-based criteria (affordability, profitability, risk) with documented analyst scores (demand, competition, feasibility, scalability), and was tested under alternative weightings.

## Key findings

| # | Finding | Evidence |
|---|---|---|
| 1 | **The macro window is favourable.** Growth ~6%, inflation 5.5%, lending rates down from 24% to 16% in a year, IMF programme completed, sovereign upgrades | MAC-01–12 |
| 2 | **The cedi is the biggest macro risk** for import-dependent businesses: −10.7% in 2026 after +40.7% in 2025 | MAC-03, MAC-06, MAC-07 |
| 3 | **The investment law changed in July 2026.** Act 1173 removed minimum capital for non-trading foreign firms, but trading still needs US$500k and six activities stay reserved for Ghanaians. GIPA fees (US$3,500–5,250) are material at this budget | REG-04–08 |
| 4 | **The best small-capital opportunities are services wrapped around infrastructure gaps** (power, logistics, laundry), not manufacturing. Import-substitution manufacturing needs capital well above US$20k | [opportunity-comparison.md](../opportunities/opportunity-comparison.md) |
| 5 | **Strong demand ≠ good economics.** Chicken is ~82% imported, yet local birds cost ~GHS 49/kg against ~GHS 33–40/kg imported, and 2026 saw a glut | AGR-03, AGR-12, AGR-33, AGR-06 |
| 6 | **Every shortlisted business loses money in the conservative case** (−US$9.7k to −US$14.7k in year 1). Stage gates and a cash reserve are essential | [cash-flow-analysis.md](../financial-analysis/cash-flow-analysis.md) |

## Financial comparison (base case)

<!-- BEGIN TABLE: financial_comparison_base -->
| Business | Initial investment | Year-1 revenue | Gross margin | Year-1 net profit | Year-1 ROI | Month-12 run-rate ROI | Operating break-even month | Payback (months) |
|---|---|---|---|---|---|---|---|---|
| Solar installation | $17,013 | $151,561 | 32% | $10,983 | 65% | 114% | 3 | 12.4 |
| Laundry service | $15,656 | $34,039 | 81% | $2,440 | 16% | 67% | 5 | 18.4 |
| Broiler farm | $17,777 | $82,479 | 25% | $3,955 | 22% | 37% | 3 | 28.9 |
| Delivery fleet | $16,485 | $35,073 | 73% | $1,899 | 12% | 48% | 4 | 20.5 |
| Digital services | $8,505 | $20,923 | 86% | -$2,012 | -24% | 71% | 7 | 26.4 |
<!-- END TABLE: financial_comparison_base -->

## Final ranking

<!-- BEGIN TABLE: weighted_ranking -->
| Rank | Business | Market demand | Investment affordability | Profitability potential | Competitive intensity | Operational feasibility | Scalability | Risk level | Weighted score |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Solar installation | 5.00 | 1.80 | 4.05 | 3.00 | 3.00 | 4.00 | 2.90 | **3.52** |
| 2 | Digital services | 2.00 | 4.07 | 2.88 | 2.00 | 4.00 | 3.00 | 3.71 | **3.06** |
| 3 | Laundry service | 3.00 | 2.16 | 2.78 | 3.00 | 4.00 | 3.00 | 3.67 | **3.05** |
| 4 | Delivery fleet | 4.00 | 1.94 | 2.27 | 2.50 | 3.00 | 4.00 | 2.86 | **2.93** |
| 5 | Broiler farm | 4.00 | 1.59 | 1.98 | 2.00 | 3.00 | 2.00 | 2.43 | **2.53** |
<!-- END TABLE: weighted_ranking -->

## Conditions attached to the recommendation

1. **Validate before investing in full:** ≥ 3 paid customer deposits within 6 weeks (about US$2–3k at risk in this stage).
2. **Control FX:** USD-indexed quotes with 7-day validity; equipment bought only after a 70% deposit.
3. **Hold a reserve of about US$5,800** (the conservative-case funding gap) and agree stop-loss rules in advance.
4. **Secure technical capability:** a certified electrician as owner or profit-sharing partner, and Energy Commission licensing.
5. **Foreign investors:** obtain a legal opinion on whether equipment sales count as "trading" under Act 1173 before investing in solar; otherwise choose laundry (as a JV) or digital services.

## Main limitations

Secondary research only (no interviews, supplier quotes or site visits); several volume and conversion inputs are assumptions; market sizes are order-of-magnitude estimates; 12-month horizon; no seasonality. All are disclosed and stress-tested in the full report.
