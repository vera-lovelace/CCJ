"""
MVPF Calculator
"""

import pandas as pd
import json
import os
from datetime import datetime

from cpi_adjuster import CPIAdjuster
from subcomponents import SubcomponentRegistry
from parameters import ParameterRegistry, ParameterEffectsRegistry
from constants import (
    COMPONENT_TYPES,
    DETAINEE_VALUES,
    SOCIETY_VALUES,
    GOVT_COST,
    INFINITE_MVPF,
    NEUTRAL_MULTIPLIER,
    SIGN_POSITIVE,
    SIGN_NEGATIVE,
    ZERO
)


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

        # Extract weight values (case-insensitive match for 'Weight')
        self.weights = {}
        weight_rows = self.values[self.values['component'].str.lower() == 'weight']

        for _, row in weight_rows.iterrows():
            self.weights[row['row_var']] = float(row['selected_value'])

        # Build lookup dictionaries for fast O(1) access (avoids repeated DataFrame filtering)
        self.name_lookup = {}  # row_var -> name
        self.row_lookup = {}   # row_var -> full row data

        for _, row in self.values.iterrows():
            row_var = row['row_var']
            self.name_lookup[row_var] = row['name']
            self.row_lookup[row_var] = row

        print(f"✓ Loaded {len(self.values)} values, {len(self.scenario_manager.scenarios)} scenarios")
        print(f"✓ Loaded weights: n_detainees={self.weights.get('n_detainees', 0):,.0f}, "
              f"los_days={self.weights.get('los_days', 0):.0f}, "
              f"fel_rate={self.weights.get('fel_rate', 0):.2f}, "
              f"n_society={self.weights.get('n_society', 0):,.0f}")

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
        mvpf = (det_total + soc_total) / gov_total if gov_total != ZERO else INFINITE_MVPF

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
        total = ZERO
        breakdown = {}

        for row_var in row_var_list:
            value = self._calc_one(row_var, params)

            # Get name from lookup dict (O(1) instead of O(n) DataFrame filtering)
            name = self.name_lookup[row_var]

            total += value
            breakdown[name] = value

        return total, breakdown

    def _calc_one(self, row_var, params):
        """Calculate one subcomponent."""
        # Get row from lookup dict (O(1) instead of O(n) DataFrame filtering)
        row = self.row_lookup[row_var]

        # SPECIAL CASE: gov_crime_prevention uses weighted average of min/max based on fel_rate
        if row_var == 'gov_crime_prevention':
            # Get min (for misdemeanors) and max (for felonies)
            min_val = float(row['min']) if pd.notna(row['min']) else 0
            max_val = float(row['max']) if pd.notna(row['max']) else 0

            # Get felony rate and crime_effect from params
            fel_rate = params.get('fel_rate', 0.7) if params else 0.7
            crime_effect = params.get('crime_effect', 0) if params else 0

            # Weighted average: min × (1 - fel_rate) + max × fel_rate
            # This gives more weight to misdemeanor cost when fel_rate is low
            # and more weight to felony cost when fel_rate is high
            weighted_avg = min_val * (1 - fel_rate) + max_val * fel_rate

            # Multiply by crime_effect
            # When crime_effect = 0, value should be 0 (no crime effect cost)
            value = weighted_avg * crime_effect

        # SPECIAL CASE: soc_crime_prevention uses weighted average when crime_effect != 0
        elif row_var == 'soc_crime_prevention':
            # Get crime_effect from params
            crime_effect = params.get('crime_effect', 0) if params else 0

            if crime_effect != 0:
                # Get min (for misdemeanors) and max (for felonies)
                min_val = float(row['min']) if pd.notna(row['min']) else 0
                max_val = float(row['max']) if pd.notna(row['max']) else 0

                # Get felony rate from params (default to 0.7 if not provided)
                fel_rate = params.get('fel_rate', 0.7) if params else 0.7

                # Weighted average: min × (1 - fel_rate) + max × fel_rate
                weighted_avg = min_val * (1 - fel_rate) + max_val * fel_rate

                # Multiply by (-1) × crime_effect
                # This is per detainee value, scaled by crime effect
                # Positive crime_effect (crime increases) → negative society benefit
                # Negative crime_effect (crime decreases) → positive society benefit
                value = weighted_avg * (-1) * crime_effect

                # Apply CPI adjustment now (before sign)
                year = row['source_dollar_year']
                if pd.notna(year):
                    value = self.cpi.adjust(value, int(year))

                # Apply parameter effects (n_detainees_mult)
                if params:
                    value *= self._get_multiplier(row_var, params)

                # Return directly - sign already handled in calculation
                return value
            else:
                # When crime_effect is 0, use selected_value (which is 0)
                value = float(row['selected_value'])

        else:
            # Standard calculation: use selected_value
            value = float(row['selected_value'])

        # Apply sign (for non-special cases)
        sign = SIGN_POSITIVE if str(row['sign']).lower() == 'positive' else SIGN_NEGATIVE
        value = abs(value) * sign

        # Apply CPI adjustment
        year = row['source_dollar_year']
        if pd.notna(year):
            value = self.cpi.adjust(value, int(year))

        # Apply parameter effects
        if params:
            value *= self._get_multiplier(row_var, params)

        return value

    def _get_multiplier(self, row_var, params):
        """
        Get parameter multiplier for a subcomponent.

        For population-based parameters (n_detainees_mult, n_society_mult),
        applies: base_value × multiplier (e.g., 33,945 × 1.0 = 33,945)

        For scale-only parameters (n_detainees_scale_only, n_society_scale_only),
        applies: just the multiplier (e.g., 1.0) without base

        For direct value parameters (los_days, fel_rate),
        applies the value directly (e.g., 70 days, 0.7 rate)
        """
        effects = ParameterEffectsRegistry.get_effects_mapping()  # Single source!

        multiplier = NEUTRAL_MULTIPLIER
        for param in effects.get(row_var, []):
            # For scale-only params, use the corresponding _mult param value without base
            if param == 'n_detainees_scale_only':
                # Just the scale multiplier (0.8/1.0/1.2), no base population
                multiplier *= params.get('n_detainees_mult', 1.0)
            elif param == 'n_society_scale_only':
                # Just the scale multiplier (0.8/1.0/1.2), no base population
                multiplier *= params.get('n_society_mult', 1.0)
            # For full population params, apply base × multiplier
            elif param == 'n_detainees_mult':
                # Use user's baseline input if provided, otherwise use CSV default
                base = params.get('n_detainees_base', self.weights.get('n_detainees', 33945))
                param_value = params.get(param, 1.0)
                multiplier *= base * param_value
            elif param == 'n_society_mult':
                # base_n_society × adjustment_multiplier
                base = self.weights.get('n_society', 5171000)
                param_value = params.get(param, 1.0)
                multiplier *= base * param_value
            else:
                # Direct values (los_days, fel_rate, crime_weight_mult, etc.)
                multiplier *= params.get(param, 1.0)

        return multiplier

    def _flatten_breakdown(self, breakdown_dict, prefix):
        """
        Flatten a breakdown dictionary into a flat dictionary with prefixed keys.

        Args:
            breakdown_dict: Dictionary of component names and values
            prefix: Prefix to add to each key (e.g., 'det_', 'soc_', 'gov_')

        Returns:
            dict: Flattened dictionary with prefixed keys
        """
        return {f'{prefix}{name}': val for name, val in breakdown_dict.items()}

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

            # Add component breakdowns
            row.update(self._flatten_breakdown(result['detainee_breakdown'], 'det_'))
            row.update(self._flatten_breakdown(result['society_breakdown'], 'soc_'))
            row.update(self._flatten_breakdown(result['govt_breakdown'], 'gov_'))

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

            # Add component breakdowns
            row.update(self._flatten_breakdown(r.get('detainee_breakdown', {}), 'det_'))
            row.update(self._flatten_breakdown(r.get('society_breakdown', {}), 'soc_'))
            row.update(self._flatten_breakdown(r.get('govt_breakdown', {}), 'gov_'))

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

            # Add component breakdowns
            row.update(self._flatten_breakdown(r.get('detainee_breakdown', {}), 'det_'))
            row.update(self._flatten_breakdown(r.get('society_breakdown', {}), 'soc_'))
            row.update(self._flatten_breakdown(r.get('govt_breakdown', {}), 'gov_'))

            rows.append(row)

        df = pd.DataFrame(rows)

        # Convert to CSV string
        csv_string = df.to_csv(index=False)
        return csv_string


# ==================== USAGE ====================

if __name__ == '__main__':
    from helpers import dashboard_params

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