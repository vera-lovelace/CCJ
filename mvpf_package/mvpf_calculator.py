"""
MVPF Calculator Module
Contains all calculation logic for Marginal Value of Public Funds
"""

import pandas as pd
import numpy as np
import os

from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import helpers

class MVPFCalculator:
    def __init__(self,
                 baseline_type: str = 'baseline',
                 values_csv: str = None,
                 cpi_csv: str = None):
        """
        Initialize calculator with baseline scenario and data files.

        Args:
            baseline_type (str): 'baseline' or 'optimal'
            values_csv (str): Path to values configuration CSV
            cpi_csv (str): Path to CPI data CSV
        """
        self.baseline_type = baseline_type
        self.target_npv_year = 2025

        # Set default paths
        if values_csv is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            values_csv = os.path.join(script_dir, 'Data', 'subcomponent_values.csv')
        if cpi_csv is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            cpi_csv = os.path.join(script_dir, 'Data', 'cpi.csv')

        self.values_csv = values_csv
        self.cpi_csv = cpi_csv

        # Initialize data structures
        self.coefficient_lookup = {}
        self.year_lookup = {}
        self.unit_lookup = {}
        self.category_groups = defaultdict(list)
        self.parameter_mappings = defaultdict(dict)

        # Lazy-loaded properties
        self._baseline_mult = None

        # CPI data structures
        self.cpi_annual_lookup = {}
        self.factor_to_2025_lookup = {}
        self.npv_cache = {}

        # Load and parse all data
        self._load_data()

    """
    Value retrieval methods
    """
    def _load_data(self):
        """Load and parse all CSV data files."""
        self.values_df = self._load_values_data()
        self.cpi_df = self._load_cpi_data()

        self._parse_values()
        self._parse_cpi()
        self._set_parameter_accessors()

    def _load_values_data(self):
        """Load and validate values CSV."""
        try:
            df = pd.read_csv(self.values_csv)
        except FileNotFoundError:
            raise FileNotFoundError(f"Values CSV not found: {self.values_csv}")

        # Validate required columns
        required_cols = ['row_var', 'component', 'name', 'unit',
                         'source_dollar_year', 'selected_value']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Values CSV missing required columns: {missing}")

        return df

    def _parse_values(self):
        """Parse values CSV into lookup dictionaries."""
        for _, row in self.values_df.iterrows():
            row_var = str(row['row_var']).strip()
            component = str(row['component']).strip()

            # Check if this is a parameter
            is_parameter = 'parameter' in row and pd.notna(row['parameter'])

            if not is_parameter:
                # Regular subcomponent - parse normally
                self.coefficient_lookup[row_var] = float(row['selected_value'])
                # Only store year if not NaN
                if pd.notna(row['source_dollar_year']):
                    self.year_lookup[row_var] = int(row['source_dollar_year'])

                self.unit_lookup[row_var] = str(row['unit']).strip()
                self.category_groups[component].append(row_var)
            else:
                # Parameter - handle separately
                parameter_name = str(row['parameter']).strip()

                if 'level' in row and pd.notna(row['level']):
                    level = str(row['level']).strip()
                    self.parameter_mappings[parameter_name][level] = float(row['selected_value'])

                # Check if source_dollar_year is N/A
                year_value = str(row['source_dollar_year']).strip().upper()
                if year_value != 'N/A' and pd.notna(row['source_dollar_year']):
                    # Has valid year - enable CPI adjustment
                    self.year_lookup[row_var] = int(row['source_dollar_year'])
                    self.coefficient_lookup[row_var] = float(row['selected_value'])
                # If N/A, skip - no CPI adjustment will be done

    def _set_parameter_accessors(self):
        """Set convenience accessors for common parameters."""
        self.LoS = self.parameter_mappings.get('LoS', {})
        self.crime_weight = self.parameter_mappings.get('crime_weight', {})
        self.n_det = self.parameter_mappings.get('n_det', {})
        self.n_population = self.parameter_mappings.get('n_population', {})

    def get_coefficient(self, component_id: str) -> float:
        """
        Get coefficient value for a component from parsed values.csv.

        Args:
            component_id (str): Component identifier (e.g., 'detainee_wtp')

        Returns:
            float: Coefficient value
        """
        if component_id not in self.coefficient_lookup:
            raise KeyError(
                f"Component '{component_id}' not found in values.csv.\n"
                f"Available components: {list(self.coefficient_lookup.keys())}"
            )
        return self.coefficient_lookup[component_id]

    def get_original_year(self, component_id: str) -> int:
        """
        Get original year for a component from parsed values.csv.

        Args:
            component_id (str): Component identifier

        Returns:
            int: Original year
        """
        if component_id not in self.year_lookup:
            print(f"Warning: Year not found for {component_id}, using target year")
            return self.target_npv_year
        return self.year_lookup[component_id]

    """
    CPI conversions
    """

    def _load_cpi_data(self):
        """Load and validate CPI CSV."""
        try:
            df = pd.read_csv(self.cpi_csv)
        except FileNotFoundError:
            raise FileNotFoundError(f"CPI CSV not found: {self.cpi_csv}")

        required_cols = ['year', 'cpi_annual', 'factor_to_2025']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"CPI CSV missing required columns: {missing}")

        return df

    def _parse_cpi(self):
        """Parse CPI CSV into lookup dictionaries."""
        for _, row in self.cpi_df.iterrows():
            year = int(row['year'])
            self.cpi_annual_lookup[year] = float(row['cpi_annual'])
            self.factor_to_2025_lookup[year] = float(row['factor_to_2025'])

    def calculate_pv_conversion(self, base_value: float, original_year: int, target_year: int) -> float:
        """Convert value from original year to target year using CPI."""
        if original_year == target_year:
            return base_value

        if original_year not in self.cpi_lookup or target_year not in self.cpi_lookup:
            return base_value

        cpi_original = self.cpi_lookup[original_year]
        cpi_target = self.cpi_lookup[target_year]
        conversion_factor = cpi_target / cpi_original

        return base_value * conversion_factor

    def get_npv_adjusted_coefficient(self, component_id: str) -> float:
        """Get NPV-adjusted coefficient for a component (cached)."""
        cache_key = f"{component_id}_{self.target_npv_year}"

        if cache_key in self.npv_cache:
            return self.npv_cache[cache_key]

        original_value = self.coefficient_lookup[component_id]
        original_year = self.year_lookup[component_id]

        adjusted_value = self.calculate_pv_conversion(original_value, original_year, self.target_npv_year)

        self.npv_cache[cache_key] = adjusted_value
        return adjusted_value

    def adjust_to_target_year(self, value, source_year):
        """
        Adjust a value from source year to target NPV year using CPI.

        Args:
            value (float): Original value in source year dollars
            source_year (int): Year of the source value

        Returns:
            float: Value adjusted to target year
        """
        # Check cache
        cache_key = (value, source_year, 2025)
        if cache_key in self.npv_cache:
            return self.npv_cache[cache_key]

        # Get CPI values
        if source_year not in self.factor_to_2025_lookup:
            raise ValueError(f"No CPI data for source year {source_year}")

        factor = self.factor_to_2025_lookup[source_year]
        adjusted_value = value * factor

        self.npv_cache[cache_key] = adjusted_value
        return adjusted_value

    def adjust_to_custom_year(self, value, source_year, target_year):
        """
        Adjust a value from source year to any target year using CPI.

        Args:
            value (float): Original value in source year dollars
            source_year (int): Year of the source value
            target_year (int): Target year for adjustment

        Returns:
            float: Value adjusted to target year
        """
        # Check cache
        cache_key = (value, source_year, target_year)
        if cache_key in self.npv_cache:
            return self.npv_cache[cache_key]

        # Use cpi_annual_lookup for custom year adjustment
        if source_year not in self.cpi_annual_lookup:
            raise ValueError(f"No CPI data for source year {source_year}")
        if target_year not in self.cpi_annual_lookup:
            raise ValueError(f"No CPI data for target year {target_year}")

        # Calculate using helper function
        source_cpi = self.cpi_annual_lookup[source_year]
        target_cpi = self.cpi_annual_lookup[target_year]
        adjusted_value = helpers.adjust_value_by_cpi(value, source_cpi, target_cpi)

        # Cache and return
        self.npv_cache[cache_key] = adjusted_value
        return adjusted_value

    def get_adjusted_value(self, row_var):
        """
        Get a value adjusted to target year.

        Args:
            row_var (str): Variable name from CSV

        Returns:
            float: CPI-adjusted value
        """
        if row_var not in self.coefficient_lookup:
            raise KeyError(f"Variable '{row_var}' not found in data")

        value = self.coefficient_lookup[row_var]
        source_year = self.year_lookup[row_var]

        return self.adjust_to_target_year(value, source_year)

    def get_cpi_year_range(self):
        """Get the range of years available in CPI data."""
        return helpers.get_year_range(self.cpi_annual_lookup)

    def clear_cache(self):
        """Clear the NPV adjustment cache."""
        self.npv_cache.clear()

    """
    Component calculations
    """
    def get_component_total(self, component_name, adjust_for_baseline=True):
        """
        Calculate total for a component (detainee_values, society_values, govt_cost).

        Args:
            component_name (str): Name of component
            adjust_for_baseline (bool): Whether to apply baseline multiplier

        Returns:
            float: Total value adjusted to target year
        """
        if component_name not in self.category_groups:
            raise KeyError(f"Component '{component_name}' not found")

        total = 0
        for row_var in self.category_groups[component_name]:
            adjusted_value = self.get_adjusted_value(row_var)
            total += adjusted_value

        # Apply baseline multiplier if requested
        if adjust_for_baseline:
            total *= self.baseline_mult

        return total


    def calculate_detainee_values(self, LoS_level: str = 'standard', n_det_level: str = 'average'):
        """
        Calculates detainee-related values based on selected levels.
        NOW READS FROM CSV instead of hardcoded values.
        """
        # Get parameter values FROM MAPPING CSV (instead of hardcoded dict)
        LoS_val = self.get_parameter_value('LoS', LoS_level)
        n_det_val = self.get_parameter_value('n_det', n_det_level)

        # Get NPV-adjusted coefficients FROM VALUES CSV (instead of hardcoded 11, -295275)
        npv_wtp_base = self.get_npv_adjusted_coefficient('detainee_wtp')
        npv_rhv_base = self.get_npv_adjusted_coefficient('detainee_rhv')

        # Calculate (same logic as before)
        detainee_wtp = npv_wtp_base * LoS_val * n_det_val
        detainee_rhv = npv_rhv_base * LoS_val * n_det_val
        detainee_total_values = detainee_wtp + detainee_rhv

        return detainee_wtp, detainee_rhv, detainee_total_values

    def calculate_society_values(self, crime_weight_level: str = 'moderate', n_det_level: str = 'average'):
        """Calculate society-related values based on selected levels."""
        crime_weight_val = self.parameter_mappings['crime_weight'][crime_weight_level]
        n_det_val = self.parameter_mappings['n_det'][n_det_level]

        npv_court_base = self.get_npv_adjusted_coefficient('society_court')
        npv_crimeprev_base = self.get_npv_adjusted_coefficient('society_crimeprev')
        npv_community_base = self.get_npv_adjusted_coefficient('society_community')

        society_court = npv_court_base * crime_weight_val * n_det_val
        society_crimeprev = npv_crimeprev_base * crime_weight_val * n_det_val
        society_community = npv_community_base * crime_weight_val * n_det_val
        society_total_values = society_court + society_crimeprev + society_community

        return society_court, society_crimeprev, society_community, society_total_values

    def calculate_govt_cost(self, LoS_level: str = 'standard', n_det_level: str = 'average'):
        """Calculate government-related costs."""
        LoS_val = self.parameter_mappings['LoS'][LoS_level]
        n_det_val = self.parameter_mappings['n_det'][n_det_level]

        npv_health_base = self.get_npv_adjusted_coefficient('govt_health')
        npv_operations_base = self.get_npv_adjusted_coefficient('govt_operations')
        npv_infractions_base = self.get_npv_adjusted_coefficient('govt_infractions')

        govt_health = npv_health_base * LoS_val * n_det_val * self.baseline_mult
        govt_operations = npv_operations_base * n_det_val * self.baseline_mult
        govt_infractions = npv_infractions_base * n_det_val * self.baseline_mult
        govt_total_costs = govt_health + govt_operations + govt_infractions

        return govt_health, govt_operations, govt_infractions, govt_total_costs


    """
    Compose MVPF 
    """
    def calculate_mvpf(self, detainee_param1=None, detainee_param2=None,
                   society_param1=None, society_param2=None):
        """
        Calculate MVPF with optional parameter adjustments.

        Args:
            params (dict): Optional parameter overrides
                e.g., {'LoS': 'above', 'crime_weight': 'high'}

        Returns:
            dict: MVPF calculation results
        """
        params = {
            'detainee_param1': detainee_param1,
            'detainee_param2': detainee_param2,
            'society_param1': society_param1,
            'society_param2': society_param2
        }
        # Get base component totals
        detainee_values = self.get_component_total('detainee_values')
        society_values = self.get_component_total('society_values')
        govt_cost = self.get_component_total('govt_cost')

        # Apply parameter adjustments if provided
        if params:
            detainee_values *= self._get_param_multiplier(params, 'detainee')
            society_values *= self._get_param_multiplier(params, 'society')
            govt_cost *= self._get_param_multiplier(params, 'govt')

        # Calculate MVPF
        mvpf = (detainee_values + society_values) / govt_cost if govt_cost != 0 else float('inf')

        return {
            'mvpf': mvpf,
            'detainee_values': detainee_values,
            'society_values': society_values,
            'govt_cost': govt_cost,
            'baseline_type': self.baseline_type,
            'baseline_mult': self.baseline_mult
        }

    def get_mvpf_interpretation(self, mvpf):
        """
        Get interpretation label and color for MVPF value.

        Args:
            mvpf (float): MVPF ratio

        Returns:
            tuple: (label, color, bg_color)
        """
        if mvpf >= 2.5:
            return 'Excellent', '#16a34a', '#dcfce7'
        elif mvpf >= 1.5:
            return 'Good', '#2563eb', '#dbeafe'
        elif mvpf >= 1.0:
            return 'Fair', '#ca8a04', '#fef3c7'
        else:
            return 'Poor', '#dc2626', '#fee2e2'

    """
    Change baseline and recalculate
    """

    @property
    def baseline_mult(self):
        """
        Get baseline multiplier based on baseline type.
        Computed lazily on first access.

        Returns:
            float: Multiplier value (0.85 for 'optimal', 1.0 for 'baseline')
        """
        if self._baseline_mult is None:
            self._baseline_mult = self._calculate_baseline_multiplier()
        return self._baseline_mult

    def _calculate_baseline_multiplier(self):
        """
        Calculate baseline multiplier based on baseline type.
        Can be overridden or extended for more complex logic.

        Returns:
            float: Multiplier value
        """
        multipliers = {
            'baseline': 1.0,
            'optimal': 0.85,
            'conservative': 1.15,
            'aggressive': 0.70
        }

        baseline_lower = self.baseline_type.lower()
        if baseline_lower not in multipliers:
            raise ValueError(
                f"Unknown baseline_type '{self.baseline_type}'. "
                f"Valid options: {list(multipliers.keys())}"
            )

        return multipliers[baseline_lower]

    def _get_param_multiplier(self, params, component_type):
        """
        Get parameter multiplier for a component type.
        Override this method for custom parameter logic.

        Args:
            params (dict): Parameter settings
            component_type (str): 'detainee', 'society', or 'govt'

        Returns:
            float: Multiplier to apply
        """
        # Example implementation - customize as needed
        multiplier = 1.0

        # Add your parameter logic here based on component_type
        # This is just a placeholder

        return multiplier

    def reload_data(self):
        """Reload data from CSV files (useful for data updates)."""
        self.npv_cache.clear()
        self._baseline_mult = None  # Reset cached multiplier
        self._load_data()

    def set_baseline_type(self, baseline_type):
        """
        Change baseline type and recalculate multiplier.

        Args:
            baseline_type (str): New baseline type
        """
        self.baseline_type = baseline_type
        self._baseline_mult = None  # Force recalculation

    """
    Run calculations
    """
if __name__ == "__main__":
    calculator = MVPFCalculator()
    result = calculator.calculate_mvpf('standard', 'average', 'moderate')

        # Print results
    print(f"MVPF: {result['mvpf']:.2f}")
    print(f"Detainee Values: ${result['detainee_values']:,.2f}")
    print(f"Society Values: ${result['society_values']:,.2f}")
    print(f"Government Cost: ${result['govt_cost']:,.2f}")

        # Export
    from helpers import export_results_to_csv
    export_results_to_csv(result, '../Data/mvpf_results.csv')
    #return calculator.calculate_mvpf(detainee_param1, detainee_param2, society_param1, society_param2)



