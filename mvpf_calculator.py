"""
MVPF Calculator - Simple
"""

import pandas as pd
import json
import os
from datetime import datetime

from cpi_adjuster import CPIAdjuster
from helpers import convert_dashboard_params
from subcomponents import SubcomponentRegistry
from parameters import ParameterRegistry, ParameterEffectsRegistry


param_registry = ParameterRegistry()


class MVPFCalculator:
    """Simple MVPF Calculator - does everything you need."""

    def __init__(self, data_dir='Data'):
        """Load data once at startup."""
        # Load CSVs
        self.values = pd.read_csv(os.path.join(data_dir, 'subcomponent_values.csv'))
        self.values.columns = self.values.columns.str.strip()  # Clean column names

        # Use CPIAdjuster
        self.cpi = CPIAdjuster(data_dir=data_dir)

        # Load scenarios
        from scenarios import EnhancedScenarioManager
        self.scenario_manager = EnhancedScenarioManager(
            scenarios_path=os.path.join(data_dir, 'alternative_calculations.json')
        )

        print(f"✓ Loaded {len(self.values)} values, {len(self.scenario_manager.scenarios)} scenarios")

    def calculate(self, scenario='baseline', params=None):
        """
        Calculate MVPF.

        Args:
            scenario: which scenario to use
            params: dict of parameter multipliers

        Returns:
            dict with all results
        """
        # Get scenario definition
        if isinstance(scenario, str):
            scenario_def = self.scenario_manager.get_scenario(scenario)
        else:
            scenario_def = scenario

        # Get subcomponent lists
        subcomps = scenario_def.get_all_subcomponents()
        detainee_list = subcomps['detainee_values']
        society_list = subcomps['society_values']
        govt_list = subcomps['govt_cost']

        # Get parameters (scenario defaults + overrides)
        if params is None:
            params = scenario_def.get_parameters()
        else:
            # Merge: start with scenario defaults, apply user overrides
            scenario_params = scenario_def.get_parameters()
            scenario_params.update(params)
            params = scenario_params

        # Calculate each component
        det_total, det_breakdown = self._calc_component(detainee_list, params)
        soc_total, soc_breakdown = self._calc_component(society_list, params)
        gov_total, gov_breakdown = self._calc_component(govt_list, params)

        # Calculate MVPF
        mvpf = (det_total + soc_total) / gov_total if gov_total != 0 else float('inf')

        return {
            'scenario': scenario_def.key,
            'scenario_name': scenario_def.name,
            'mvpf': mvpf,
            'detainee_values': det_total,
            'society_values': soc_total,
            'govt_cost': gov_total,
            'detainee_breakdown': det_breakdown,
            'society_breakdown': soc_breakdown,
            'govt_breakdown': gov_breakdown,
            'parameters_used': params,  # Include for transparency
            'subcomponents_used': {
                'detainee_values': detainee_list,
                'society_values': society_list,
                'govt_cost': govt_list
            }
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
            value = self.cpi.adjust(value, int(year))

        # Apply parameter effects
        if params:
            value *= self._get_multiplier(row_var, params)

        return value

    def dashboard_params(**kwargs):
        """Convert dashboard inputs to parameters."""
        return param_registry.convert_dashboard_input(**kwargs)

    def _get_multiplier(self, row_var, params):
        """Get parameter multiplier for a subcomponent."""
        effects = ParameterEffectsRegistry.get_effects_mapping()  # Single source!

        multiplier = 1.0
        for param in effects.get(row_var, []):
            multiplier *= params.get(param, 1.0)

        return multiplier

    def calculate_all_scenarios(self, params=None):
        """Calculate all scenarios."""
        results = []
        for scenario in self.scenario_manager.list_scenarios():
            results.append(self.calculate(scenario, params))
        return results

    def calculate_and_save_all(self, params=None, filename='mvpf_all_scenarios.csv'):
        """
        Calculate all scenarios with all components and save to CSV.

        Args:
            params: Optional parameter dict (uses defaults if None)
            filename: Output CSV filename

        Returns:
            pd.DataFrame: Results dataframe
        """
        rows = []

        for scenario_key in self.scenario_manager.list_scenarios():
            result = self.calculate(scenario_key, params)

            # Build row with all data
            row = {
                'scenario_key': result['scenario'],
                'scenario_name': result['scenario_name'],
                'mvpf': result['mvpf'],
                'detainee_total': result['detainee_values'],
                'society_total': result['society_values'],
                'govt_total': result['govt_cost'],
                'numerator': result['detainee_values'] + result['society_values'],
            }

            # Add detainee breakdown
            for name, val in result['detainee_breakdown'].items():
                row[f'det_{name}'] = val

            # Add society breakdown
            for name, val in result['society_breakdown'].items():
                row[f'soc_{name}'] = val

            # Add govt breakdown
            for name, val in result['govt_breakdown'].items():
                row[f'gov_{name}'] = val

            # Add parameters used
            for param_key, param_val in result['parameters_used'].items():
                row[f'param_{param_key}'] = param_val

            rows.append(row)

        # Create DataFrame and save
        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False)
        print(f"✓ Saved {len(rows)} scenarios to {filename}")

        return df

    def export_csv(self, results, filename='results.csv', include_metadata=True):
        """
        Export results to CSV with full details.

        Args:
            results: Single result dict or list of results
            filename: Output filename
            include_metadata: Include parameters and subcomponents used
        """
        # Handle single result
        if isinstance(results, dict):
            results = [results]

        rows = []
        for r in results:
            row = {
                'timestamp': datetime.now().isoformat(),
                'scenario': r.get('scenario', 'unknown'),
                'scenario_name': r.get('scenario_name', r.get('scenario', 'unknown')),
                'mvpf': r.get('mvpf', 0),
                'detainee_total': r.get('detainee_values', 0),
                'society_total': r.get('society_values', 0),
                'govt_total': r.get('govt_cost', 0)
            }

            # Add parameters used (if available)
            if include_metadata and 'parameters_used' in r:
                for param_key, param_val in r['parameters_used'].items():
                    row[f'param_{param_key}'] = param_val

            # Add breakdowns
            for name, val in r.get('detainee_breakdown', {}).items():
                row[f'det_{name}'] = val
            for name, val in r.get('society_breakdown', {}).items():
                row[f'soc_{name}'] = val
            for name, val in r.get('govt_breakdown', {}).items():
                row[f'gov_{name}'] = val

            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False)
        print(f"✓ Saved to {filename}")
        return df

    def export_to_string(self, results, include_metadata=True):
        """
        Export results to CSV string (for dashboard download).

        Returns:
            str: CSV formatted string
        """
        import io

        # Handle single result
        if isinstance(results, dict):
            results = [results]

        rows = []
        for r in results:
            row = {
                'timestamp': datetime.now().isoformat(),
                'scenario': r.get('scenario', 'unknown'),
                'scenario_name': r.get('scenario_name', r.get('scenario', 'unknown')),
                'mvpf': r.get('mvpf', 0),
                'detainee_total': r.get('detainee_values', 0),
                'society_total': r.get('society_values', 0),
                'govt_total': r.get('govt_cost', 0)
            }

            # Add parameters used (if available)
            if include_metadata and 'parameters_used' in r:
                for param_key, param_val in r['parameters_used'].items():
                    row[f'param_{param_key}'] = param_val

            # Add breakdowns
            for name, val in r.get('detainee_breakdown', {}).items():
                row[f'det_{name}'] = val
            for name, val in r.get('society_breakdown', {}).items():
                row[f'soc_{name}'] = val
            for name, val in r.get('govt_breakdown', {}).items():
                row[f'gov_{name}'] = val

            rows.append(row)

        df = pd.DataFrame(rows)

        # Convert to CSV string
        csv_string = df.to_csv(index=False)
        return csv_string


# ==================== HELPER FUNCTION ====================

def dashboard_params(crime_rate, detainee_pop, community_size, length_of_stay):
    """Convert dashboard dropdowns to parameter dict."""
    maps = {
        'minimal': 0.8,
        'below': 0.8,
        'moderate': 1.0,
        'average': 1.0,
        'above': 1.2,
        'large': 1.2,
        'significant': 1.5
    }

    return {
        'crime_rate_mult': maps.get(crime_rate, 1.0),
        'detainee_pop_mult': maps.get(detainee_pop, 1.0),
        'community_size_mult': maps.get(community_size, 1.0),
        'length_of_stay_mult': maps.get(length_of_stay, 1.0),
        'crime_weight_mult': maps.get(crime_rate, 1.0)  # Use crime_rate for crime_weight
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