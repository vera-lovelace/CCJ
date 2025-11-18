"""
MVPF Calculator - Simple
"""

import pandas as pd
import json
import os
from datetime import datetime


class MVPFCalculator:
    """Simple MVPF Calculator - does everything you need."""

    def __init__(self, data_dir='Data'):
        """Load data once at startup."""
        # Load CSVs
        self.values = pd.read_csv(os.path.join(data_dir, 'subcomponent_values.csv'))
        self.cpi = pd.read_csv(os.path.join(data_dir, 'cpi.csv'))

        # Load scenarios
        scenario_file = os.path.join(data_dir, 'alternative_calculations.json')
        with open(scenario_file, 'r') as f:
            self.scenarios = json.load(f)

        # Build lookup dicts for speed
        self.cpi_factors = dict(zip(self.cpi['year'], self.cpi['factor_to_2025']))

        print(f"✓ Loaded {len(self.values)} values, {len(self.scenarios)} scenarios")

    def calculate(self, scenario='baseline', params=None):
        """
        Calculate MVPF.

        Args:
            scenario: which scenario to use
            params: dict of parameter multipliers

        Returns:
            dict with all results
        """
        # Get which subcomponents to use for this scenario
        detainee_list = self.scenarios[scenario].get('detainee_values', [])
        society_list = self.scenarios[scenario].get('society_values', [])
        govt_list = self.scenarios[scenario].get('govt_cost', [])

        # Calculate each component
        det_total, det_breakdown = self._calc_component(detainee_list, params)
        soc_total, soc_breakdown = self._calc_component(society_list, params)
        gov_total, gov_breakdown = self._calc_component(govt_list, params)

        # Calculate MVPF
        mvpf = (det_total + soc_total) / gov_total if gov_total != 0 else float('inf')

        return {
            'scenario': scenario,
            'mvpf': mvpf,
            'detainee_values': det_total,
            'society_values': soc_total,
            'govt_cost': gov_total,
            'detainee_breakdown': det_breakdown,
            'society_breakdown': soc_breakdown,
            'govt_breakdown': gov_breakdown
        }

    def _calc_component(self, row_var_list, params):
        """Calculate total and breakdown for a list of subcomponents."""
        total = 0
        breakdown = {}

        for row_var in row_var_list:
            value = self._calc_one(row_var, params)

            # Get name from dataframe
            name = self.values[self.values['row_var'] == row_var]['name'].values[0]

            total += value
            breakdown[name] = value

        return total, breakdown

    def _calc_one(self, row_var, params):
        """Calculate one subcomponent."""
        # Get row from dataframe
        row = self.values[self.values['row_var'] == row_var].iloc[0]

        # Get base value
        value = float(row['selected_value'])

        # Apply sign
        sign = 1 if str(row['sign']).lower() == 'positive' else -1
        value = abs(value) * sign

        # Apply CPI adjustment
        year = row['source_dollar_year']
        if pd.notna(year):
            value *= self.cpi_factors[int(year)]

        # Apply parameter effects
        if params:
            value *= self._get_multiplier(row_var, params)

        return value

    def _get_multiplier(self, row_var, params):
        """Get parameter multiplier for a subcomponent."""
        # Define which params affect which subcomponents
        effects = {
            'det_wtp_freedom': ['crime_rate_mult', 'detainee_pop_mult'],
            'det_harm_during': ['length_of_stay_mult', 'detainee_pop_mult'],
            'det_post_release': ['length_of_stay_mult'],
            'soc_crime_prevention': ['crime_weight_mult', 'community_size_mult'],
            'soc_victimization': ['crime_weight_mult', 'community_size_mult'],
            'soc_spillovers': ['community_size_mult', 'length_of_stay_mult'],
            'gov_operations': ['detainee_pop_mult', 'length_of_stay_mult'],
            'gov_court_admin': ['detainee_pop_mult'],
            'gov_long_term': [],
        }

        multiplier = 1.0
        for param in effects.get(row_var, []):
            multiplier *= params.get(param, 1.0)

        return multiplier

    def calculate_all_scenarios(self, params=None):
        """Calculate all scenarios."""
        results = []
        for scenario in self.scenarios.keys():
            results.append(self.calculate(scenario, params))
        return results

    def export_csv(self, results, filename='results.csv'):
        """Export to CSV."""
        rows = []
        for r in results:
            row = {
                'scenario': r['scenario'],
                'mvpf': r['mvpf'],
                'detainee_total': r['detainee_values'],
                'society_total': r['society_values'],
                'govt_total': r['govt_cost']
            }
            # Add breakdowns
            for name, val in r['detainee_breakdown'].items():
                row[f'det_{name}'] = val
            for name, val in r['society_breakdown'].items():
                row[f'soc_{name}'] = val
            for name, val in r['govt_breakdown'].items():
                row[f'gov_{name}'] = val
            rows.append(row)

        pd.DataFrame(rows).to_csv(filename, index=False)
        print(f"✓ Saved to {filename}")


# ==================== HELPER FUNCTION ====================

def dashboard_params(crime_rate, detainee_pop, community_size, length_of_stay):
    """Convert dashboard dropdowns to parameter dict."""
    maps = {
        'below': 0.8, 'moderate': 1.0, 'average': 1.0,
        'above': 1.2, 'significant': 1.5
    }

    return {
        'crime_rate_mult': maps.get(crime_rate, 1.0),
        'detainee_pop_mult': maps.get(detainee_pop, 1.0),
        'community_size_mult': maps.get(community_size, 1.0),
        'length_of_stay_mult': maps.get(length_of_stay, 1.0),
        'crime_weight_mult': 1.0
    }


# ==================== USAGE ====================

if __name__ == '__main__':
    # Initialize once
    calc = MVPFCalculator()

    # Single calculation
    result = calc.calculate('baseline')
    print(f"MVPF: {result['mvpf']:.2f}")

    # With parameters
    params = dashboard_params('moderate', 'average', 'above', 'average')
    result = calc.calculate('baseline', params)
    print(f"MVPF with params: {result['mvpf']:.2f}")

    # All scenarios
    all_results = calc.calculate_all_scenarios(params)
    calc.export_csv(all_results, 'all_scenarios.csv')