import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as mticker

# ============================================================
# 1. FIXED PARAMETERS
# ============================================================

PLANT_CAPACITY = 26_280          # t/year (fixed total biomass)
CAPEX          = 14_460_000      # £
PLANT_LIFE     = 20              # years
CAPEX_ANN      = CAPEX / PLANT_LIFE
OPEX           = 6_164_000       # £/year

# Pyrolysis product yields (fractions)
YIELDS = {
    400: {
        'husk':  {'oil': 0.1126, 'char': 0.8422, 'gas': 0.0452},
        'straw': {'oil': 0.3592, 'char': 0.4706, 'gas': 0.1702},
    },
    500: {
        'husk':  {'oil': 0.3450, 'char': 0.3800, 'gas': 0.2750},
        'straw': {'oil': 0.6800, 'char': 0.1500, 'gas': 0.1700},
    }
}

# Base case parameters
BASE = {
    'carbon_price':        70,    # £/tCO2
    'straw_cost':          25,    # £/t straw
    'biochar_price':      200,    # £/t
    'biooil_price':       400,    # £/t
    'carbon_factor_400':  1.30,
    'carbon_factor_500':  0.92,
}

# Sensitivity scenario values
SENSITIVITY = {
    'Carbon Price\n(£/tCO₂)': {
        'param_400': 'carbon_price',
        'param_500': 'carbon_price',
        'Low':    {'carbon_price': 30},
        'Medium': {'carbon_price': 70},
        'High':   {'carbon_price': 120},
    },
    'Straw Collection\nCost (£/t)': {
        'param_400': 'straw_cost',
        'param_500': 'straw_cost',
        'Low':    {'straw_cost': 10},
        'Medium': {'straw_cost': 25},
        'High':   {'straw_cost': 50},
    },
    'Biochar\nPrice (£/t)': {
        'Low':    {'biochar_price': 100},
        'Medium': {'biochar_price': 200},
        'High':   {'biochar_price': 300},
    },
    'Bio-oil\nPrice (£/t)': {
        'Low':    {'biooil_price': 200},
        'Medium': {'biooil_price': 400},
        'High':   {'biooil_price': 600},
    },
    'Carbon Factor\n(tCO₂/t_prod)': {
        'Low':    {'carbon_factor_400': 1.1, 'carbon_factor_500': 0.70},
        'Medium': {'carbon_factor_400': 1.3, 'carbon_factor_500': 0.92},
        'High':   {'carbon_factor_400': 1.5, 'carbon_factor_500': 1.10},
    },
}

# ============================================================
# 2. CORE CALCULATION FUNCTION
# ============================================================

def calculate_revenue(straw_frac, temp,
                      carbon_price, straw_cost,
                      biochar_price, biooil_price,
                      carbon_factor):
    """
    Calculate total revenue and product mix for a given
    straw fraction and temperature.

    straw_frac : 0.0 → 1.0 (fraction of total biomass that is straw)
    Returns dict with revenue components and product tonnes.
    """
    total = PLANT_CAPACITY
    t_straw = total * straw_frac
    t_husk  = total * (1 - straw_frac)

    y = YIELDS[temp]

    # Product tonnes
    char_husk  = t_husk  * y['husk']['char']
    char_straw = t_straw * y['straw']['char']
    oil_husk   = t_husk  * y['husk']['oil']
    oil_straw  = t_straw * y['straw']['oil']
    gas_husk   = t_husk  * y['husk']['gas']
    gas_straw  = t_straw * y['straw']['gas']

    total_char = char_husk + char_straw
    total_oil  = oil_husk  + oil_straw
    total_gas  = gas_husk  + gas_straw
    total_prod = total_char + total_oil + total_gas

    # Bio-oil fraction of total output
    biooil_frac = total_oil / total_prod if total_prod > 0 else 0
    
    # Straw logistics cost (only on straw portion)
    straw_logistics = t_straw * straw_cost

    # Revenue streams
    carbon_credits = total_char * carbon_factor * carbon_price
    biochar_sales  = total_char * biochar_price
    biooil_sales   = total_oil  * biooil_price
    total_revenue  = carbon_credits + biochar_sales + biooil_sales - straw_logistics

    return {
        'total_revenue':   total_revenue,
        'carbon_credits':  carbon_credits,
        'biochar_sales':   biochar_sales,
        'biooil_sales':    biooil_sales,
        'straw_logistics': straw_logistics,
        'total_char':      total_char,
        'total_oil':       total_oil,
        'biooil_frac':     biooil_frac,
    }

# ============================================================
# 3. GRAPH 1 — Revenue curves + Bio-oil fraction
# ============================================================

straw_pcts = np.linspace(0, 100, 200)   # 0% to 100% straw
straw_fracs = straw_pcts / 100

# Arrays to fill
rev_400, rev_500       = [], []
biooil_frac_400, biooil_frac_500 = [], []

for sf in straw_fracs:
    r400 = calculate_revenue(
        sf, 400,
        BASE['carbon_price'], BASE['straw_cost'],
        BASE['biochar_price'], BASE['biooil_price'],
        BASE['carbon_factor_400']
    )
    r500 = calculate_revenue(
        sf, 500,
        BASE['carbon_price'], BASE['straw_cost'],
        BASE['biochar_price'], BASE['biooil_price'],
        BASE['carbon_factor_500']
    )
    rev_400.append(r400['total_revenue'])
    rev_500.append(r500['total_revenue'])
    biooil_frac_400.append(r400['biooil_frac'] * 100)
    biooil_frac_500.append(r500['biooil_frac'] * 100)

rev_400 = np.array(rev_400) / 1e6
rev_500 = np.array(rev_500) / 1e6

# Find crossover point
diff = np.array(rev_400) - np.array(rev_500)
crossover_idx = np.where(np.diff(np.sign(diff)))[0]

fig, ax1 = plt.subplots(figsize=(11, 6))

# --- Left axis: Revenue ---
color_400 = '#1565C0'
color_500 = '#C62828'

l1, = ax1.plot(straw_pcts, rev_400, color=color_400,
               linewidth=2.5, label='Revenue 400°C')
l2, = ax1.plot(straw_pcts, rev_500, color=color_500,
               linewidth=2.5, label='Revenue 500°C')

# Shade region where 400°C wins
ax1.fill_between(straw_pcts, rev_400, rev_500,
                 where=(np.array(rev_400) >= np.array(rev_500)),
                 alpha=0.08, color=color_400, label='400°C advantage')
ax1.fill_between(straw_pcts, rev_400, rev_500,
                 where=(np.array(rev_400) < np.array(rev_500)),
                 alpha=0.08, color=color_500, label='500°C advantage')

# Crossover marker
if len(crossover_idx) > 0:
    cx = straw_pcts[crossover_idx[0]]
    cy = (rev_400[crossover_idx[0]] + rev_500[crossover_idx[0]]) / 2
    ax1.axvline(cx, color='gray', linestyle='--',
                linewidth=1.2, alpha=0.7)
    ax1.annotate(f'Crossover\n≈{cx:.0f}% straw',
                 xy=(cx, cy),
                 xytext=(cx + 5, cy + 0.3),
                 fontsize=11, color='gray',
                 arrowprops=dict(arrowstyle='->', color='gray'))

ax1.set_xlabel('% Straw in Total Feedstock\n(← 100% Husk     100% Straw →)',
               fontsize=12)
ax1.set_ylabel('Total Annual Revenue (£M)', fontsize=12, color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f'£{x:.1f}M'))
ax1.set_xlim(0, 100)

# --- Right axis: Bio-oil fraction ---
ax2 = ax1.twinx()

l3, = ax2.plot(straw_pcts, biooil_frac_400,
               color=color_400, linewidth=1.5,
               linestyle=':', alpha=0.75,
               label='Bio-oil % of output (400°C)')
l4, = ax2.plot(straw_pcts, biooil_frac_500,
               color=color_500, linewidth=1.5,
               linestyle=':', alpha=0.75,
               label='Bio-oil % of output (500°C)')

ax2.set_ylabel('Bio-oil as % of Total Output (tonnes)',
               fontsize=12, color='dimgray')
ax2.tick_params(axis='y', labelcolor='dimgray')
ax2.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f'{x:.0f}%'))
ax2.set_ylim(0, 80)

# Add husk/straw labels at extremes
ax1.axvline(0,   color='green',  alpha=0.3, linewidth=1)
ax1.axvline(100, color='orange', alpha=0.3, linewidth=1)
ax1.text(1,  ax1.get_ylim()[0] + 0.05, '100% Husk',
         fontsize=10, color='green',  alpha=0.8)
ax1.text(90, ax1.get_ylim()[0] + 0.05, '100% Straw',
         fontsize=10, color='orange', alpha=0.8)

# Combined legend
lines  = [l1, l2, l3, l4]
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left',
           fontsize=9, framealpha=0.9)

ax1.set_title(
    'Figure 2 - Total Revenue vs Feedstock Composition\n'
    'Base Case: Carbon £70/tCO₂ | Biochar £200/t | '
    'Bio-oil £400/t | Straw cost £25/t',
    fontsize=13, fontweight='bold'
)
ax1.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('graph1_revenue_curves.png', dpi=150, bbox_inches='tight')
plt.show()

# ============================================================
# 4. GRAPH 2 — Sensitivity Analysis Table
#    400°C tested at 100% HUSK
#    500°C tested at 100% STRAW
# ============================================================

# Fixed feedstock fractions per temperature
STRAW_FRAC_400 = 0.0   # 100% husk for 400°C
STRAW_FRAC_500 = 1.0   # 100% straw for 500°C

fig, ax = plt.subplots(figsize=(18, 9))   # was (13, 6)
ax.axis('off')

levels = ['Low', 'Medium', 'High']
param_labels = list(SENSITIVITY.keys())
n_params = len(param_labels)

col_labels = ['Parameter', 'Low', 'Medium - Base Case', 'High']
table_data  = []
cell_colors = []

value_labels = {
    'Carbon Price\n(£/tCO₂)':          ['£30', '£70', '£120'],
    'Straw Collection\nCost (£/t)':    ['£10', '£25', '£50'],
    'Biochar\nPrice (£/t)':            ['£100', '£200', '£300'],
    'Bio-oil\nPrice (£/t)':            ['£200', '£400', '£600'],
    'Carbon Factor\n(tCO₂/t_prod)': ['1.1/0.70', '1.3/0.92', '1.5/1.10'],
}

for param_name, param_dict in SENSITIVITY.items():
    row_data   = [param_name.replace('\n', ' ')]
    row_colors = ['#F5F5F5']

    vlabels = value_labels[param_name]

    for idx, level in enumerate(levels):
        # Start from base, override tested parameter
        p = BASE.copy()
        p.update(param_dict[level])

        # 400°C at 100% husk
        r400 = calculate_revenue(
            STRAW_FRAC_400, 400,
            p['carbon_price'],
            p['straw_cost'],
            p['biochar_price'],
            p['biooil_price'],
            p['carbon_factor_400']
        )

        # 500°C at 100% straw
        r500 = calculate_revenue(
            STRAW_FRAC_500, 500,
            p['carbon_price'],
            p['straw_cost'],
            p['biochar_price'],
            p['biooil_price'],
            p['carbon_factor_500']
        )

        chosen   = 400 if r400['total_revenue'] >= r500['total_revenue'] else 500
        diff_m   = abs(r400['total_revenue'] -
                       r500['total_revenue']) / 1e6
        vl       = vlabels[idx]

        cell_text  = (f'[{vl}]\n'
                      f'{"400°C ✓" if chosen == 400 else "500°C ✓"}\n'
                      f'Δ £{diff_m:.2f}M')
        cell_color = '#BBDEFB' if chosen == 400 else '#FFCDD2'

        row_data.append(cell_text)
        row_colors.append(cell_color)

    table_data.append(row_data)
    cell_colors.append(row_colors)

table = ax.table(
    cellText=table_data,
    colLabels=col_labels,
    cellLoc='center',
    loc='center',
    cellColours=cell_colors
)

table.auto_set_font_size(False)
table.set_fontsize(12)          # was 10
table.scale(1.7, 4.3)           # was (1.4, 3.0)

# Style header row
for j in range(4):
    table[0, j].set_facecolor('#1565C0')
    table[0, j].set_text_props(color='white', fontweight='bold')

# Style parameter name column
for i in range(1, n_params + 1):
    table[i, 0].set_facecolor('#E3F2FD')
    table[i, 0].set_text_props(fontweight='bold', fontsize=11)

fig.text(
    0.5, 0.84,   # ← lower this number to move title down
    'Figure 3 - Sensitivity Analysis — Optimal Pyrolysis Temperature\n'
    '400°C tested at 100% Husk  |  500°C tested at 100% Straw  |  '
    'All other parameters at base (medium) values\n'
    '🔵 Blue = 400°C optimal   |   🔴 Red = 500°C optimal   |   '
    'Δ = revenue difference between temperatures',
    ha='center', fontsize=14, fontweight='bold'
)

plt.tight_layout()
plt.savefig('graph2_sensitivity_table.png', dpi=150, bbox_inches='tight')
plt.show()

# --- Console verification ---
print("\n✅ Sensitivity table saved.")
print("\nBase case verification:")
print("  400°C @ 100% husk:")
r400_check = calculate_revenue(
    0.0, 400,
    BASE['carbon_price'], BASE['straw_cost'],
    BASE['biochar_price'], BASE['biooil_price'],
    BASE['carbon_factor_400']
)
print(f"    Carbon credits : £{r400_check['carbon_credits']:,.0f}")
print(f"    Biochar sales  : £{r400_check['biochar_sales']:,.0f}")
print(f"    Bio-oil sales  : £{r400_check['biooil_sales']:,.0f}")
print(f"    Total revenue  : £{r400_check['total_revenue']:,.0f}")

print("\n  500°C @ 100% straw:")
r500_check = calculate_revenue(
    1.0, 500,
    BASE['carbon_price'], BASE['straw_cost'],
    BASE['biochar_price'], BASE['biooil_price'],
    BASE['carbon_factor_500']
)
print(f"    Carbon credits : £{r500_check['carbon_credits']:,.0f}")
print(f"    Biochar sales  : £{r500_check['biochar_sales']:,.0f}")
print(f"    Bio-oil sales  : £{r500_check['biooil_sales']:,.0f}")
print(f"    Total revenue  : £{r500_check['total_revenue']:,.0f}")

winner = '400°C' if r400_check['total_revenue'] >= r500_check['total_revenue'] else '500°C'
print(f"\n  → Base case winner: {winner}")