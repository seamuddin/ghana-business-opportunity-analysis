# Financial Assumptions

[← Back to README](../README.md) · Related: [investment-breakdown.md](investment-breakdown.md) · [revenue-projections.md](revenue-projections.md) · [cash-flow-analysis.md](cash-flow-analysis.md) · [break-even-analysis.md](break-even-analysis.md)

> **Every number in this file is generated from the model input CSVs** in [`data/datasets/inputs/`](../data/datasets/inputs/) by [`models/report_tables.py`](../models/report_tables.py). To test a different assumption, edit the CSV and run `python models/run_all.py`; all tables, charts and documents refresh.
>
> Evidence labels follow the [research methodology](../research/research-methodology.md#4-evidence-classification): *Verified fact*, *Estimate*, *Listing* (marketplace or company price, indicative) and *Assumption*. Outputs of the model are **projections, not forecasts or guarantees.**

## 1. Global assumptions

| Parameter | Value | Basis | Source |
|---|---|---|---|
| Exchange rate | **GHS 11.70 per USD**, held constant for 12 months | Verified fact (BoG interbank, 13 Nov 2026) | MAC-07 |
| Investment range | US$5,000–20,000; the model **refuses to run** if any budget falls outside it | Project brief | — |
| Employer SSNIT | 13% of salary, added automatically to every payroll line | Verified fact | REG-20 |
| Company tax | 25% CIT + 2.5% Growth & Sustainability Levy = **27.5% of profit**, with loss carry-forward | Verified fact | REG-13 |
| Small-business tax | Modified Taxation Scheme: **3% of turnover** (individuals; turnover up to GHS 750,000) | Verified fact | REG-16 |
| VAT | 20% effective; registration threshold GHS 750,000. VAT-registered businesses are modelled on prices **excluding VAT** | Verified fact | REG-14 |
| Working days | 26 per month | Assumption | — |
| Rent advance | 12 months prepaid (amortised monthly) | Assumption: the law caps advances at 6 months, but 1–2 years is still commonly demanded | SVC-03, SVC-07 |
| Contingency reserve | 10% of all other startup costs, **calculated by the model** | Assumption | — |
| Financing | 100% equity; no interest cost | Assumption (see [economic-analysis.md §4](../research/economic-analysis.md#4-interest-rates-cheaper-but-debt-is-still-expensive-for-a-start-up)) | MAC-04 |

### Legal form and tax treatment by business

| Business | Legal form | Tax applied in model | VAT status | Why |
|---|---|---|---|---|
| Solar installation | Company limited by shares | CIT 27.5% | Registered (prices ex-VAT) | Base-case turnover exceeds GHS 750k |
| Laundry service | Sole proprietorship | MTS 3% of turnover | Below threshold | Turnover below GHS 750k |
| Broiler farm | Company limited by shares | CIT 27.5% (no tax holiday assumed) | Exempt supplies (local poultry) | Turnover exceeds MTS ceiling; exemption per REG-19 |
| Delivery fleet | Sole proprietorship | MTS 3% of turnover | Below threshold | Turnover below GHS 750k |
| Digital services | Sole proprietorship | MTS 3% of turnover | Below threshold | If GRA treats it as a "professional" service, graduated personal income tax would apply instead |

## 2. Model mechanics

| Element | How it works | Why |
|---|---|---|
| Revenue | For each revenue line: units × price. Units ramp **linearly** from the start month over `ramp_months`, then grow at `monthly_growth` | Transparent; every driver is visible and testable |
| Cost of goods sold | Units × unit cost | Direct costs scale with volume |
| Operating expenses | Payroll (+13% SSNIT), fixed monthly costs, and variable costs as % of revenue | Separates scale-independent from scale-dependent costs |
| Depreciation & amortisation | Straight line over each startup item's useful life; **prepaid rent and insurance are amortised over 12 months** | Avoids double-counting cash paid up front |
| Inventory | Opening stock is a startup investment; afterwards stock is replenished as sold, so cash COGS = P&L COGS | Standard steady-stock simplification |
| Tax | Turnover tax or CIT on profit with loss carry-forward, set per business | Reflects 2026 Ghanaian rules |
| Currency | Inputs in GHS or USD; GHS converted at 11.70. **Imported solar equipment is entered in USD** so FX risk is visible | Lets the FX stress test show real import exposure |
| Owner labour | Every model pays a market-rate manager salary | Profit is a return on capital, not disguised wages |
| Payback | Month cumulative operating cash flow ≥ total initial investment; extrapolated at the month-12 run-rate when beyond 12 months, reported as "> 60" beyond five years | Conservative: includes working capital and contingency in the amount to recover |

### Scenario design

| Scenario | What changes | Intended meaning |
|---|---|---|
| **Conservative** | Lower prices, lower steady volumes, slower ramp-up, higher unit costs and some higher fixed costs | A realistic bad year — not a catastrophe |
| **Base** | Evidence-anchored mid-points | The most likely outcome **if** the business is executed competently |
| **Optimistic** | Higher prices and volumes, faster ramp-up, better unit costs | Strong execution plus favourable market |

Startup budgets are identical across scenarios; any overrun is covered by the contingency reserve.

## 3. Unit economics (base case)

<!-- BEGIN TABLE: unit_economics -->
| Business | Revenue line | Unit | Price (base) | Unit cost (base) | Unit margin | Steady volume / month (base) |
|---|---|---|---|---|---|---|
| Solar installation | 5 kVA hybrid system (installed) | per system excl. VAT | $3,761 (GHS 44,000) | $2,564 | 32% | 2 |
| Solar installation | 3 kVA starter system (installed) | per system excl. VAT | $2,564 (GHS 30,000) | $1,752 | 32% | 2 |
| Solar installation | Maintenance visits and service plans | per visit excl. VAT | $51 (GHS 600) | $13 | 75% | 8 |
| Laundry service | Wash, dry and fold (per kg) | per kg | $1.54 (GHS 18.00) | $0.34 | 78% | 1,400 |
| Laundry service | Washed and pressed garments (per item) | per item | $0.85 (GHS 10.00) | $0.13 | 85% | 1,100 |
| Laundry service | Special items (suits, duvets, traditional wear) | per item | $3.42 (GHS 40.00) | $0.51 | 85% | 120 |
| Broiler farm | Broilers sold (blend of live and dressed) | per bird | $8.97 (GHS 105.00) | $6.84 | 24% | 900 |
| Broiler farm | Poultry manure (bags) | per bag | $1.71 (GHS 20.00) | $0.17 | 90% | 100 |
| Delivery fleet | Same-day scheduled deliveries (per drop) | per drop | $2.14 (GHS 25.00) | $0.60 | 72% | 1,456 |
| Delivery fleet | Cash-on-delivery settlement fee | per COD drop | $0.34 (GHS 4.00) | $0.05 | 85% | 874 |
| Digital services | Digital set-up package (one-off) | per package | $214 (GHS 2,500) | $26 | 88% | 4 |
| Digital services | Monthly social-commerce retainer | per client per month | $103 (GHS 1,200) | $13 | 88% | 14 |
| Digital services | Seller training workshops (per attendee) | per attendee | $26 (GHS 300) | $6.84 | 73% | 12 |
<!-- END TABLE: unit_economics -->

## 4. Business-specific assumptions

### 4.1 Solar installation (SOL)

**Revenue drivers**

<!-- BEGIN TABLE: assumptions_revenue_SOL -->
| Revenue line | Parameter | Conservative | Base | Optimistic | Unit | Basis | Source |
|---|---|---|---|---|---|---|---|
| 5 kVA hybrid system (installed) | price | 40000.0 | 44000.0 | 47000.0 | GHS per system excl. VAT | Estimate | ENE-43, ENE-44, ENE-18 |
| 5 kVA hybrid system (installed) | unit cost | 2650.0 | 2564.0 | 2479.0 | USD per system excl. VAT (imported equipment priced in USD) | Estimate | ENE-17, ENE-18 |
| 5 kVA hybrid system (installed) | steady volume | 1.5 | 2.5 | 3.5 | systems per month | Assumption |  |
| 5 kVA hybrid system (installed) | start month | 1.0 | 1.0 | 1.0 | month | Assumption |  |
| 5 kVA hybrid system (installed) | ramp months | 6.0 | 4.0 | 3.0 | months | Assumption |  |
| 5 kVA hybrid system (installed) | monthly growth | 0.0 | 0.02 | 0.03 | share per month after ramp | Assumption |  |
| 3 kVA starter system (installed) | price | 27000.0 | 30000.0 | 32000.0 | GHS per system excl. VAT | Estimate | ENE-43, ENE-44 |
| 3 kVA starter system (installed) | unit cost | 1795.0 | 1752.0 | 1709.0 | USD per system excl. VAT (imported equipment priced in USD) | Estimate | ENE-18 |
| 3 kVA starter system (installed) | steady volume | 1.0 | 1.5 | 2.5 | systems per month | Assumption |  |
| 3 kVA starter system (installed) | start month | 1.0 | 1.0 | 1.0 | month | Assumption |  |
| 3 kVA starter system (installed) | ramp months | 6.0 | 4.0 | 3.0 | months | Assumption |  |
| 3 kVA starter system (installed) | monthly growth | 0.0 | 0.02 | 0.03 | share per month after ramp | Assumption |  |
| Maintenance visits and service plans | price | 500.0 | 600.0 | 700.0 | GHS per visit excl. VAT | Assumption |  |
| Maintenance visits and service plans | unit cost | 150.0 | 150.0 | 150.0 | GHS per visit | Assumption |  |
| Maintenance visits and service plans | steady volume | 5.0 | 8.0 | 12.0 | visits per month | Assumption |  |
| Maintenance visits and service plans | start month | 3.0 | 3.0 | 2.0 | month | Assumption |  |
| Maintenance visits and service plans | ramp months | 10.0 | 9.0 | 8.0 | months | Assumption |  |
| Maintenance visits and service plans | monthly growth | 0.0 | 0.0 | 0.0 | share per month after ramp | Assumption |  |
<!-- END TABLE: assumptions_revenue_SOL -->

**Operating costs**

<!-- BEGIN TABLE: assumptions_opex_SOL -->
| Cost line | Type | Conservative | Base | Optimistic | Basis | Source |
|---|---|---|---|---|---|---|
| Lead solar technician (certified) | Payroll (GHS/month, +13% SSNIT) | 3,500 | 3,500 | 3,500 | Estimate | SVC-11 |
| Assistant installer | Payroll (GHS/month, +13% SSNIT) | 2,000 | 2,000 | 2,000 | Estimate | SVC-11 |
| Sales and administration officer | Payroll (GHS/month, +13% SSNIT) | 2,200 | 2,200 | 2,200 | Estimate | SVC-09 |
| Owner-manager salary (market rate) | Payroll (GHS/month, +13% SSNIT) | 5,000 | 5,000 | 5,000 | Assumption |  |
| Utilities, internet and phone | Fixed (GHS/month) | 1,000 | 900 | 900 | Estimate | MAC-16 |
| Tricycle fuel and maintenance | Fixed (GHS/month) | 2,200 | 1,800 | 1,800 | Estimate | MAC-19 |
| Digital marketing and referral fees | Fixed (GHS/month) | 2,500 | 2,500 | 2,500 | Assumption |  |
| Liability insurance | Fixed (GHS/month) | 500 | 500 | 500 | Assumption |  |
| Accounting, bank charges and licence renewals | Fixed (GHS/month) | 700 | 700 | 700 | Assumption |  |
| Warranty provision | Variable (% of revenue) | 3.0% | 2.0% | 1.5% | Assumption |  |
| Sales commission | Variable (% of revenue) | 2.0% | 2.0% | 2.0% | Assumption |  |
| Payment and bank charges | Variable (% of revenue) | 1.0% | 1.0% | 1.0% | Assumption |  |
<!-- END TABLE: assumptions_opex_SOL -->

Key judgement calls:

- **Price positioning.** The base price (GHS 52,800 incl. VAT for a 5 kVA / 5 kWh system) sits *below* established Accra installers (GHS 55–85k, ENE-44) and *above* informal marketplace kits (GHS 25–37k, ENE-18). The value proposition is certified installation and warranty at a mid-market price.
- **Volume.** 4 systems per month at steady state, against crew capacity of ~8–10. The constraint is demand, not labour. For context, Ghana had only ~7.6 MW of small residential PV installed at end-2025 (ENE-13), so this is an early market.
- **No customer credit.** Customers pay a deposit before equipment is bought. Financing comes through bank partners (Ecobank, Stanbic; ENE-46, ENE-47), not the business's balance sheet.

### 4.2 Laundry service (LAU)

**Revenue drivers**

<!-- BEGIN TABLE: assumptions_revenue_LAU -->
| Revenue line | Parameter | Conservative | Base | Optimistic | Unit | Basis | Source |
|---|---|---|---|---|---|---|---|
| Wash, dry and fold (per kg) | price | 16.0 | 18.0 | 20.0 | GHS per kg | Estimate | SVC-33, SVC-35 |
| Wash, dry and fold (per kg) | unit cost | 4.5 | 4.0 | 3.8 | GHS per kg | Estimate | SVC-37, MAC-16 |
| Wash, dry and fold (per kg) | steady volume | 1100.0 | 1400.0 | 1700.0 | kg kg per month | Assumption |  |
| Wash, dry and fold (per kg) | start month | 1.0 | 1.0 | 1.0 | month | Assumption |  |
| Wash, dry and fold (per kg) | ramp months | 7.0 | 6.0 | 5.0 | months | Assumption |  |
| Wash, dry and fold (per kg) | monthly growth | 0.0 | 0.01 | 0.02 | share per month after ramp | Assumption |  |
| Washed and pressed garments (per item) | price | 8.0 | 10.0 | 12.0 | GHS per item | Estimate | SVC-32, SVC-33 |
| Washed and pressed garments (per item) | unit cost | 1.7 | 1.5 | 1.4 | GHS per item | Estimate |  |
| Washed and pressed garments (per item) | steady volume | 850.0 | 1100.0 | 1400.0 | items per month | Assumption |  |
| Washed and pressed garments (per item) | start month | 1.0 | 1.0 | 1.0 | month | Assumption |  |
| Washed and pressed garments (per item) | ramp months | 7.0 | 6.0 | 5.0 | months | Assumption |  |
| Washed and pressed garments (per item) | monthly growth | 0.0 | 0.01 | 0.02 | share per month after ramp | Assumption |  |
| Special items (suits, duvets, traditional wear) | price | 32.0 | 40.0 | 45.0 | GHS per item | Estimate | SVC-32, SVC-33, SVC-34 |
| Special items (suits, duvets, traditional wear) | unit cost | 7.0 | 6.0 | 6.0 | GHS per item | Assumption |  |
| Special items (suits, duvets, traditional wear) | steady volume | 90.0 | 120.0 | 160.0 | items per month | Assumption |  |
| Special items (suits, duvets, traditional wear) | start month | 1.0 | 1.0 | 1.0 | month | Assumption |  |
| Special items (suits, duvets, traditional wear) | ramp months | 7.0 | 6.0 | 5.0 | months | Assumption |  |
| Special items (suits, duvets, traditional wear) | monthly growth | 0.0 | 0.01 | 0.02 | share per month after ramp | Assumption |  |
<!-- END TABLE: assumptions_revenue_LAU -->

**Operating costs**

<!-- BEGIN TABLE: assumptions_opex_LAU -->
| Cost line | Type | Conservative | Base | Optimistic | Basis | Source |
|---|---|---|---|---|---|---|
| Laundry attendants (3 x GHS 1800) | Payroll (GHS/month, +13% SSNIT) | 5,400 | 5,400 | 5,400 | Estimate | SVC-12 |
| Pickup and delivery rider | Payroll (GHS/month, +13% SSNIT) | 1,500 | 1,500 | 1,500 | Estimate | SVC-11 |
| Owner-manager salary (market rate) | Payroll (GHS/month, +13% SSNIT) | 4,000 | 4,000 | 4,000 | Assumption |  |
| Generator fuel during outages | Fixed (GHS/month) | 1,600 | 1,200 | 900 | Assumption | ENE-05, MAC-19 |
| Base electricity (lighting, fans) | Fixed (GHS/month) | 500 | 400 | 400 | Estimate | MAC-16 |
| Rider fuel and bike maintenance (free pickup absorbed) | Fixed (GHS/month) | 1,200 | 1,000 | 1,000 | Estimate | MAC-19, SVC-34 |
| Marketing and promotions | Fixed (GHS/month) | 1,500 | 1,500 | 1,500 | Assumption |  |
| Phone, internet and software | Fixed (GHS/month) | 300 | 300 | 300 | Assumption |  |
| Equipment maintenance | Fixed (GHS/month) | 500 | 400 | 400 | Assumption |  |
| Accounting and sundries | Fixed (GHS/month) | 500 | 500 | 500 | Assumption |  |
| Insurance | Fixed (GHS/month) | 250 | 250 | 250 | Assumption |  |
| Damage and loss provision | Variable (% of revenue) | 1.5% | 1.0% | 1.0% | Assumption |  |
| Payment charges (MoMo merchant) | Variable (% of revenue) | 1.0% | 1.0% | 1.0% | Assumption |  |
<!-- END TABLE: assumptions_opex_LAU -->

Key judgement calls:

- **Prices** follow the observed Accra cluster: GHS 17–20/kg wash-and-fold, GHS 8–15 per pressed shirt (SVC-32–35). Free pickup is now standard (SVC-34), so it is costed, not charged.
- **Gross margin looks high (≈80%)** because labour, generator fuel and rent sit in operating expenses. Only consumables and process utilities are COGS. The contribution margin after variable costs is the more useful figure (see [break-even-analysis.md](break-even-analysis.md)).
- **Utilities per kg** use a non-Ghana benchmark for water and wash energy (≈10 L and ≈0.9 kWh per kg including drying), priced at 2026 PURC tariffs (SVC-37, MAC-16). This is a disclosed gap.

### 4.3 Broiler farm (BRO)

**Revenue drivers**

<!-- BEGIN TABLE: assumptions_revenue_BRO -->
| Revenue line | Parameter | Conservative | Base | Optimistic | Unit | Basis | Source |
|---|---|---|---|---|---|---|---|
| Broilers sold (blend of live and dressed) | price | 95.0 | 105.0 | 118.0 | GHS per bird | Estimate | AGR-09, AGR-33, AGR-36 |
| Broilers sold (blend of live and dressed) | unit cost | 90.0 | 80.0 | 72.5 | GHS per bird sold | Estimate | AGR-10, AGR-11, AGR-14, AGR-32, AGR-33 |
| Broilers sold (blend of live and dressed) | steady volume | 800.0 | 900.0 | 1000.0 | birds birds per month | Assumption |  |
| Broilers sold (blend of live and dressed) | start month | 2.0 | 2.0 | 2.0 | month | Assumption |  |
| Broilers sold (blend of live and dressed) | ramp months | 3.0 | 3.0 | 2.0 | months | Assumption |  |
| Broilers sold (blend of live and dressed) | monthly growth | 0.0 | 0.0 | 0.0 | share per month after ramp | Assumption |  |
| Poultry manure (bags) | price | 15.0 | 20.0 | 25.0 | GHS per bag | Assumption |  |
| Poultry manure (bags) | unit cost | 2.0 | 2.0 | 2.0 | GHS per bag | Assumption |  |
| Poultry manure (bags) | steady volume | 80.0 | 100.0 | 120.0 | bags per month | Assumption |  |
| Poultry manure (bags) | start month | 2.0 | 2.0 | 2.0 | month | Assumption |  |
| Poultry manure (bags) | ramp months | 3.0 | 3.0 | 2.0 | months | Assumption |  |
| Poultry manure (bags) | monthly growth | 0.0 | 0.0 | 0.0 | share per month after ramp | Assumption |  |
<!-- END TABLE: assumptions_revenue_BRO -->

**Operating costs**

<!-- BEGIN TABLE: assumptions_opex_BRO -->
| Cost line | Type | Conservative | Base | Optimistic | Basis | Source |
|---|---|---|---|---|---|---|
| Farm hands (2 x GHS 1500) | Payroll (GHS/month, +13% SSNIT) | 3,000 | 3,000 | 3,000 | Estimate | SVC-11 |
| Farm manager / owner (market rate) | Payroll (GHS/month, +13% SSNIT) | 3,500 | 3,500 | 3,500 | Assumption |  |
| Veterinary retainer and lab tests | Fixed (GHS/month) | 500 | 400 | 400 | Assumption |  |
| Utilities (water and power) | Fixed (GHS/month) | 700 | 600 | 600 | Assumption | MAC-16 |
| Marketing and buyer development | Fixed (GHS/month) | 600 | 600 | 600 | Assumption |  |
| Phone and transport to buyers | Fixed (GHS/month) | 800 | 600 | 600 | Assumption |  |
| Repairs and biosecurity consumables | Fixed (GHS/month) | 400 | 300 | 300 | Assumption |  |
| Accounting and sundries | Fixed (GHS/month) | 400 | 400 | 400 | Assumption |  |
| Market levies and middleman commissions | Variable (% of revenue) | 4.0% | 3.0% | 2.0% | Assumption |  |
| Payment charges | Variable (% of revenue) | 0.5% | 0.5% | 0.5% | Assumption |  |
<!-- END TABLE: assumptions_opex_BRO -->

Key judgement calls:

- **Price is the decisive variable.** The minister reports chicken prices of ~GHS 100, with GHS 80 in some areas (AGR-36). Vendors ask GHS 110 live and GHS 120 dressed (AGR-09). The base case uses a blended GHS 105 per bird; the conservative case (GHS 95) leaves almost no gross margin. This is deliberate and is supported by the 2026 off-take evidence (AGR-06).
- **Cost per bird (≈ GHS 80)** re-prices the MoFA 1,000-bird budget (AGR-32) and the FSRP cost build-up (AGR-33) at 2026 chick and feed prices (AGR-09–11). Mortality is set at 8% within the 2.9–10% range in AGR-14.
- **Housing cost** is the weakest-evidenced capital item: published guides disagree by an order of magnitude, so a low-cost open-sided design is assumed and flagged.

### 4.4 Delivery fleet (DEL)

**Revenue drivers**

<!-- BEGIN TABLE: assumptions_revenue_DEL -->
| Revenue line | Parameter | Conservative | Base | Optimistic | Unit | Basis | Source |
|---|---|---|---|---|---|---|---|
| Same-day scheduled deliveries (per drop) | price | 20.0 | 25.0 | 30.0 | GHS per drop | Estimate | ENE-50, ENE-53, ENE-35 |
| Same-day scheduled deliveries (per drop) | unit cost | 8.5 | 7.0 | 6.0 | GHS per drop | Estimate | MAC-19 |
| Same-day scheduled deliveries (per drop) | steady volume | 1040.0 | 1456.0 | 1872.0 | drops per month | Assumption |  |
| Same-day scheduled deliveries (per drop) | start month | 1.0 | 1.0 | 1.0 | month | Assumption |  |
| Same-day scheduled deliveries (per drop) | ramp months | 7.0 | 5.0 | 4.0 | months | Assumption |  |
| Same-day scheduled deliveries (per drop) | monthly growth | 0.0 | 0.01 | 0.02 | share per month after ramp | Assumption |  |
| Cash-on-delivery settlement fee | price | 3.0 | 4.0 | 5.0 | GHS per COD drop | Assumption | ENE-54 |
| Cash-on-delivery settlement fee | unit cost | 0.6 | 0.6 | 0.6 | GHS per COD drop | Assumption |  |
| Cash-on-delivery settlement fee | steady volume | 624.0 | 874.0 | 1123.0 | COD drops per month | Assumption | ENE-54, ENE-55 |
| Cash-on-delivery settlement fee | start month | 1.0 | 1.0 | 1.0 | month | Assumption |  |
| Cash-on-delivery settlement fee | ramp months | 7.0 | 5.0 | 4.0 | months | Assumption |  |
| Cash-on-delivery settlement fee | monthly growth | 0.0 | 0.01 | 0.02 | share per month after ramp | Assumption |  |
<!-- END TABLE: assumptions_revenue_DEL -->

**Operating costs**

<!-- BEGIN TABLE: assumptions_opex_DEL -->
| Cost line | Type | Conservative | Base | Optimistic | Basis | Source |
|---|---|---|---|---|---|---|
| Riders (4 x GHS 1500 base pay) | Payroll (GHS/month, +13% SSNIT) | 6,000 | 6,000 | 6,000 | Estimate | ENE-56, SVC-11 |
| Dispatcher / customer service | Payroll (GHS/month, +13% SSNIT) | 1,800 | 1,800 | 1,800 | Estimate | SVC-09 |
| Owner-manager salary (market rate) | Payroll (GHS/month, +13% SSNIT) | 4,000 | 4,000 | 4,000 | Assumption |  |
| Phones, data, dispatch and tracking software | Fixed (GHS/month) | 1,000 | 900 | 900 | Assumption |  |
| Marketing and seller acquisition | Fixed (GHS/month) | 1,200 | 1,200 | 1,200 | Assumption |  |
| Union/association dues and renewals | Fixed (GHS/month) | 250 | 200 | 200 | Assumption | ENE-33, ENE-34 |
| Accounting and sundries | Fixed (GHS/month) | 500 | 500 | 500 | Assumption |  |
| Damage, loss and COD shortfall provision | Variable (% of revenue) | 2.5% | 1.5% | 1.0% | Assumption | ENE-53 |
| Payment charges | Variable (% of revenue) | 1.0% | 1.0% | 1.0% | Assumption |  |
<!-- END TABLE: assumptions_opex_DEL -->

Key judgement calls:

- **Price per drop (GHS 25)** is a B2B contract rate, well below the GHS 45 consumer average (ENE-35), close to platform and courier floors (Swoove from GHS 15–20, ENE-50).
- **14 drops per bike per day** assumes batched, scheduled routes for repeat sellers. A journalist's model used 8 per day for on-demand work (ENE-35). The conservative case uses 10.
- **COD settlement fee** monetises the main pain point sellers report: cash handling and slow remittance (ENE-53).

### 4.5 Digital services (DIG)

**Revenue drivers**

<!-- BEGIN TABLE: assumptions_revenue_DIG -->
| Revenue line | Parameter | Conservative | Base | Optimistic | Unit | Basis | Source |
|---|---|---|---|---|---|---|---|
| Digital set-up package (one-off) | price | 2000.0 | 2500.0 | 3000.0 | GHS per package | Estimate | ENE-59, ENE-60 |
| Digital set-up package (one-off) | unit cost | 350.0 | 300.0 | 300.0 | GHS per package | Assumption |  |
| Digital set-up package (one-off) | steady volume | 2.5 | 4.0 | 6.0 | packages per month | Assumption |  |
| Digital set-up package (one-off) | start month | 1.0 | 1.0 | 1.0 | month | Assumption |  |
| Digital set-up package (one-off) | ramp months | 6.0 | 4.0 | 3.0 | months | Assumption |  |
| Digital set-up package (one-off) | monthly growth | 0.0 | 0.0 | 0.0 | share per month after ramp | Assumption |  |
| Monthly social-commerce retainer | price | 1000.0 | 1200.0 | 1500.0 | GHS per client per month | Estimate | ENE-57, ENE-58 |
| Monthly social-commerce retainer | unit cost | 150.0 | 150.0 | 150.0 | GHS per client per month | Assumption |  |
| Monthly social-commerce retainer | steady volume | 8.0 | 14.0 | 20.0 | clients active clients | Assumption |  |
| Monthly social-commerce retainer | start month | 2.0 | 2.0 | 2.0 | month | Assumption |  |
| Monthly social-commerce retainer | ramp months | 11.0 | 10.0 | 9.0 | months | Assumption |  |
| Monthly social-commerce retainer | monthly growth | 0.0 | 0.0 | 0.0 | share per month after ramp | Assumption |  |
| Seller training workshops (per attendee) | price | 250.0 | 300.0 | 350.0 | GHS per attendee | Assumption |  |
| Seller training workshops (per attendee) | unit cost | 80.0 | 80.0 | 80.0 | GHS per attendee | Assumption |  |
| Seller training workshops (per attendee) | steady volume | 6.0 | 12.0 | 20.0 | attendees per month | Assumption |  |
| Seller training workshops (per attendee) | start month | 3.0 | 3.0 | 2.0 | month | Assumption |  |
| Seller training workshops (per attendee) | ramp months | 4.0 | 4.0 | 3.0 | months | Assumption |  |
| Seller training workshops (per attendee) | monthly growth | 0.0 | 0.0 | 0.0 | share per month after ramp | Assumption |  |
<!-- END TABLE: assumptions_revenue_DIG -->

**Operating costs**

<!-- BEGIN TABLE: assumptions_opex_DIG -->
| Cost line | Type | Conservative | Base | Optimistic | Basis | Source |
|---|---|---|---|---|---|---|
| Digital marketer | Payroll (GHS/month, +13% SSNIT) | 3,000 | 3,000 | 3,000 | Assumption |  |
| Content creator / designer | Payroll (GHS/month, +13% SSNIT) | 2,500 | 2,500 | 2,500 | Assumption |  |
| Owner-manager salary (market rate) | Payroll (GHS/month, +13% SSNIT) | 4,500 | 4,500 | 4,500 | Assumption |  |
| Co-working desks | Fixed (GHS/month) | 1,500 | 1,500 | 1,500 | Assumption |  |
| Internet and data | Fixed (GHS/month) | 700 | 700 | 700 | Assumption |  |
| Software subscriptions beyond prepaid licences | Fixed (GHS/month) | 300 | 300 | 300 | Assumption |  |
| Own marketing | Fixed (GHS/month) | 1,500 | 1,500 | 1,500 | Assumption |  |
| Transport to clients | Fixed (GHS/month) | 700 | 600 | 600 | Assumption |  |
| Accounting and sundries | Fixed (GHS/month) | 500 | 500 | 500 | Assumption |  |
| Payment gateway fees | Variable (% of revenue) | 1.9% | 1.9% | 1.9% | Verified fact | ENE-61, ENE-62 |
| Sales commissions and referral fees | Variable (% of revenue) | 4.0% | 3.0% | 3.0% | Assumption |  |
<!-- END TABLE: assumptions_opex_DIG -->

Key judgement calls:

- **Retainer price (GHS 1,200/month)** is set below agency entry tiers (GHS 1,500–2,500, ENE-57, ENE-58) to reach micro-sellers.
- **Client ramp is slow (10 months to 14 clients)** because no evidence was found that micro-firms will pay recurring fees. This is the business's main uncertainty.
- **Working capital was increased to GHS 35,000** after the first model run showed the base-case cash balance dipping below zero in month 5. The model's cash check exists precisely to catch this.

## 5. Known limitations of the model

1. **No seasonality.** Festive peaks for chicken, rainy-season delivery disruptions and solar demand spikes during outages are discussed qualitatively but not modelled.
2. **Linear ramp-up** is a simplification of real customer acquisition.
3. **Constant exchange rate and prices** for 12 months. Inflation (5.5%) is low enough that this is reasonable for a one-year view. FX is tested separately.
4. **No debt, no customer credit, no inventory build-up beyond the opening stock.**
5. **Tax simplifications:** monthly provisional tax, no capital allowances schedule (straight-line depreciation used as a proxy) and no agricultural tax incentives.
