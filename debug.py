"""
Debug and Testing Utilities

This module contains debugging utilities and test code for the MVPF Calculator.
Used for development and troubleshooting purposes.
"""

from mvpf_calculator import MVPFCalculator, dashboard_params
from parameters import ParameterEffectsRegistry

calc = MVPFCalculator()
effects = ParameterEffectsRegistry.get_effects_mapping()

# Get baseline scenario subcomponents
scenario = calc.scenario_manager.get_scenario('baseline')
subcomps = scenario.get_all_subcomponents()

print('=== Baseline scenario subcomponents ===')
all_used = []
for comp, vars in subcomps.items():
    print(f'{comp}: {vars}')
    all_used.extend(vars)

print()
print('=== Checking if used subcomponents have effects defined ===')
for row_var in all_used:
    if row_var in effects:
        print(f'  {row_var}: HAS effects -> {effects[row_var]}')
    else:
        print(f'  {row_var}: NO EFFECTS DEFINED (multipliers wont apply!)')

print()
print('=== Testing with different params ===')
params_low = dashboard_params('below', 'minimal', 'minimal', 'below')
params_high = dashboard_params('significant', 'large', 'large', 'above')
print(f'Low params: {params_low}')
print(f'High params: {params_high}')

result_low = calc.calculate('baseline', params_low)
result_high = calc.calculate('baseline', params_high)
print(f'Low MVPF: {result_low[\"mvpf\"]:.6f}, Det: {result_low[\"detainee_values\"]:,.0f}')
print(f'High MVPF: {result_high[\"mvpf\"]:.6f}, Det: {result_high[\"detainee_values\"]:,.0f}')
"
Debug parameter application


#vol2
params_low =
dashboard_params('below', 'minimal', 'minimal', 'below')
params_high = dashboard_params('significant', 'large', 'large', 'above')

result_low = calc.calculate('baseline', params_low)
result_high = calc.calculate('baseline', params_high)

print('=== LOW params ===')
print(f'  Detainee: {result_low[\"detainee_values\"]:>15,.0f}')
print(f'  Society:  {result_low[\"society_values\"]:>15,.0f}')
print(f'  Govt:     {result_low[\"govt_cost\"]:>15,.0f}')
print(f'  Numerator (Det+Soc): {result_low[\"detainee_values\"] + result_low[\"society_values\"]:>15,.0f}')
print(f'  MVPF = {result_low[\"detainee_values\"] + result_low[\"society_values\"]} / {result_low[\"govt_cost\"]} = {result_low[\"mvpf\"]:.6f}')

print()
print('=== HIGH params ===')
print(f'  Detainee: {result_high[\"detainee_values\"]:>15,.0f}')
print(f'  Society:  {result_high[\"society_values\"]:>15,.0f}')
print(f'  Govt:     {result_high[\"govt_cost\"]:>15,.0f}')
print(f'  Numerator (Det+Soc): {result_high[\"detainee_values\"] + result_high[\"society_values\"]:>15,.0f}')
print(f'  MVPF = {result_high[\"detainee_values\"] + result_high[\"society_values\"]} / {result_high[\"govt_cost\"]} = {result_high[\"mvpf\"]:.6f}')

print()
print('=== Ratios (High/Low) ===')
print(f'  Det ratio: {result_high[\"detainee_values\"] / result_low[\"detainee_values\"]:.2f}x')
print(f'  Soc ratio: {result_high[\"society_values\"] / result_low[\"society_values\"]:.2f}x')
print(f'  Gov ratio: {result_high[\"govt_cost\"] / result_low[\"govt_cost\"]:.2f}x')
"
Debug MVPF calculation



# vol 3 testing

params_low = dashboard_params('below', 'minimal', 'minimal', 'below')
params_high = dashboard_params('significant', 'large', 'large', 'above')

result_low = calc.calculate('baseline', params_low)
result_high = calc.calculate('baseline', params_high)

print('=== LOW params ===')
print(f'  Detainee: {result_low[\"detainee_values\"]:>15,.0f}')
print(f'  Society:  {result_low[\"society_values\"]:>15,.0f}')
print(f'  Govt:     {result_low[\"govt_cost\"]:>15,.0f}')
print(f'  MVPF:     {result_low[\"mvpf\"]:.6f}')

print()
print('=== HIGH params ===')
print(f'  Detainee: {result_high[\"detainee_values\"]:>15,.0f}')
print(f'  Society:  {result_high[\"society_values\"]:>15,.0f}')
print(f'  Govt:     {result_high[\"govt_cost\"]:>15,.0f}')
print(f'  MVPF:     {result_high[\"mvpf\"]:.6f}')

print()
print(f'MVPF changed: {result_low[\"mvpf\"]:.6f} → {result_high[\"mvpf\"]:.6f}')
"
#Test MVPF sensitivity after fix



python3 -c "
  from mvpf_calculator import MVPFCalculator, dashboard_params
  import pandas as pd

  calc =
MVPFCalculator()
params = dashboard_params('average', 'moderate', 'moderate', 'average')

# Get baseline scenario
scenario = calc.scenario_manager.get_scenario('baseline')
subcomps = scenario.get_all_subcomponents()

print('=== GOVT COST CALCULATION PROCESS ===')
print()
print('1. Scenario defines which subcomponents to use:')
print(f'   govt_cost subcomponents: {subcomps[\"govt_cost\"]}')
  print()

  print('2. For each subcomponent, get raw data from CSV:')
  for row_var in subcomps['govt_cost']:
      row =
calc.values[calc.values['row_var'] == row_var].iloc[0]
print(f'   {row_var}:')
print(f'     - name: {row[\"name\"]}')
      print(f'     - raw value: \${float(row[\"selected_value\"]):,.0f}')
      print(f'     - sign: {row[\"sign\"]}')
      print(f'     - source_year: {row[\"source_dollar_year\"]}')
  print()

  print('3. Apply sign (positive=1, negative=-1):')
  for row_var in subcomps['govt_cost']:
      row =
calc.values[calc.values['row_var'] == row_var].iloc[0]
raw = float(row['selected_value'])
sign = 1 if str(row['sign']).lower() == 'positive' else -1
signed = abs(raw) * sign
print(f'   {row_var}: {raw:,.0f} × {sign} = {signed:,.0f}')
print()

print('4. Apply CPI adjustment (source year → 2025):')
for row_var in subcomps['govt_cost']:
    row = calc.values[calc.values['row_var'] == row_var].iloc[0]
raw = float(row['selected_value'])
sign = 1 if str(row['sign']).lower() == 'positive' else -1
signed = abs(raw) * sign
year = int(row['source_dollar_year'])
adjusted = calc.cpi.adjust(signed, year)
print(f'   {row_var}: {signed:,.0f} ({year}) → {adjusted:,.0f} (2025)')
print()

print('5. Apply parameter multipliers:')
from parameters import ParameterEffectsRegistry

effects = ParameterEffectsRegistry.get_effects_mapping()
for row_var in subcomps['govt_cost']:
    effect_params = effects.get(row_var, [])
print(f'   {row_var}: affected by {effect_params if effect_params else \"(none - fixed cost)\"}')
  print()

  print('6. Final calculation:')
  result =
calc.calculate('baseline', params)
print(f'   govt_cost total: \${result[\"govt_cost\"]:,.0f}')
print(f'   breakdown: {result[\"govt_breakdown\"]}')
"
#Show govt cost calculation process
