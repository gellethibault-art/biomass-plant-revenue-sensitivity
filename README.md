# Biomass Pyrolysis Revenue Optimisation

## Context
Academic project developed as part of the MSc Sustainable Energy Futures
at Imperial College London. The model evaluates the economic performance
of a biomass pyrolysis plant processing rice husk and straw feedstocks,
comparing two pyrolysis temperatures (400°C and 500°C) across varying
market conditions.

## Objectives
- Model revenue streams from biochar sales, bio-oil sales and carbon credits
- Identify the optimal feedstock composition (husk vs. straw ratio)
  and pyrolysis temperature for a given set of market parameters
- Quantify sensitivity of results to key economic drivers

## Plant Specifications
- Total biomass capacity: 26,280 t/year
- CAPEX: £14.46M (annualised over 20-year plant life)
- OPEX: £6.16M/year
- Feedstock: rice husk and/or wheat straw
- Temperatures modelled: 400°C and 500°C

## Methodology

### Revenue Model
Three revenue streams are modelled:
- **Biochar sales** — based on char yield per feedstock and market price
- **Bio-oil sales** — based on oil yield per feedstock and market price
- **Carbon credits** — based on char yield, carbon sequestration factor
  and carbon price (£/tCO₂)

Straw logistics costs are deducted as a function of straw fraction
and collection cost per tonne.

### Sensitivity Analysis
Five parameters are stress-tested across Low / Medium / High scenarios:
- Carbon price (£30 / £70 / £120 per tCO₂)
- Straw collection cost (£10 / £25 / £50 per tonne)
- Biochar price (£100 / £200 / £300 per tonne)
- Bio-oil price (£200 / £400 / £600 per tonne)
- Carbon sequestration factor (tCO₂ per tonne of product)

400°C is evaluated at 100% husk; 500°C at 100% straw.

## Outputs
- **Figure 1** — Total annual revenue vs. feedstock composition (0–100% straw),
  with bio-oil fraction overlay and crossover point identification
- **Figure 2** — Sensitivity analysis table showing optimal temperature
  and revenue differential across all scenarios

## Tools
- Python, NumPy, Matplotlib

## Key Findings
- At base case parameters, 400°C with 100% husk outperforms 500°C with
  100% straw due to higher carbon credit and biochar revenue
- The crossover point shifts significantly with carbon price and
  biochar market assumptions
- Bio-oil price is the dominant driver of 500°C competitiveness

## Repository Structure
biomass-pyrolysis/
│
├── pyrolysis_model.py        # Full model and visualisation
└── README.md
