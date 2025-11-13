"""
MVPF Calculator Module
Contains all calculation logic for Marginal Value of Public Funds
"""

import pandas as pd
import numpy as np
import os
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from helpers import export_results_to_csv

class MVPFCalculator:

    def __init__(self,
                 baseline_type: str = 'baseline',
                 values_csv: str = os.path.join('Data', 'subcomponent_values.csv'),
                 mapping_csv: str = os.path.join('Data', 'mvpf_component_mapping.csv'),
                 cpi_csv: str = os.path.join('Data', 'cpi.csv')):
        """
        Initialize calculator with baseline scenario and data files.

        Args:
            baseline_type (str): 'baseline' or 'optimal'
            values_csv (str): Path to values configuration CSV
            mapping_csv (str): Path to MVPF component mapping table CSV
            cpi_csv (str): Path to CPI data CSV for NPV adjustments
        """
        self.baseline_type = baseline_type
        self.target_npv_year = 2025

        # Load CSV files
        try:
            self.values_df = pd.read_csv(values_csv)
            self.mapping_df = pd.read_csv(mapping_csv)
            self.cpi_df = pd.read_csv(cpi_csv)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"CSV file not found: {e}")

        # Validate required columns
        required_values_cols = ['component', 'name', 'unit', 'sign', 'source_dollar_year', 'selected_value']
        #required_mapping_cols = ['parameter', 'level', 'numeric_value']
        required_cpi_cols = ['year', 'factor_to_2025']

        if not all(col in self.values_df.columns for col in required_values_cols):
            raise ValueError(f"values.csv missing required columns")
        #if not all(col in self.mapping_df.columns for col in required_mapping_cols):
         #   raise ValueError(f"mapping.csv missing required columns")
        if not all(col in self.cpi_df.columns for col in required_cpi_cols):
            raise ValueError(f"cpi.csv missing required columns")

        # Parse values.csv
        self.coefficient_lookup = {}
        self.year_lookup = {}
        self.unit_lookup = {}
        self.category_groups = defaultdict(list)

        for index, row in self.values_df.iterrows():
            component_id = str(row['Component']).strip()
            category = str(row['Category']).strip()

            self.coefficient_lookup[component_id] = float(row['Original Base Value'])
            self.year_lookup[component_id] = int(row['Original Year'])
            self.unit_lookup[component_id] = str(row['Unit'])
            self.category_groups[category].append(component_id)

        # Parse mapping.csv
        self.parameter_mappings = defaultdict(dict)

        for index, row in self.mapping_df.iterrows():
            parameter = str(row['parameter']).strip()
            level = str(row['level']).strip()
            numeric_value = float(row['numeric_value'])
            self.parameter_mappings[parameter][level] = numeric_value

        # Convenience accessors
        self.LoS = self.parameter_mappings.get('LoS', {})
        self.crime_weight = self.parameter_mappings.get('crime_weight', {})
        self.n_det = self.parameter_mappings.get('n_det', {})
        self.n_population = self.parameter_mappings.get('n_population', {})

        # Parse cpi.csv
        self.cpi_lookup = {}
        for index, row in self.cpi_df.iterrows():
            year = int(row['year'])
            cpi_value = float(row['cpi'])
            self.cpi_lookup[year] = cpi_value

        # Set baseline multiplier
        self.baseline_mult = 0.85 if self.baseline_type.lower() == 'optimal' else 1.0

        # NPV cache
        self.npv_cache = {}

    def get_coefficient(self, component_id: str) -> float:
        """
        Get coefficient value for a component from parsed values.csv.

        Args:
            component_id (str): Component identifier (e.g., 'detainee_wtp')

        Returns:
            float: Coefficient value

        Raises:
            KeyError: If component_id not found
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

    def get_parameter_value(self, parameter: str, level: str) -> float:
        """
        Get numeric value for a parameter level from parsed mapping.csv.

        Args:
            parameter (str): Parameter name (e.g., 'LoS', 'crime_weight')
            level (str): Level name (e.g., 'basic', 'moderate')

        Returns:
            float: Numeric value

        Raises:
            KeyError: If parameter or level not found
        """
        if parameter not in self.parameter_mappings:
            raise KeyError(
                f"Parameter '{parameter}' not found in mapping.csv.\n"
                f"Available parameters: {list(self.parameter_mappings.keys())}"
            )

        if level not in self.parameter_mappings[parameter]:
            raise KeyError(
                f"Level '{level}' not found for parameter '{parameter}'.\n"
                f"Available levels: {list(self.parameter_mappings[parameter].keys())}"
            )

        return self.parameter_mappings[parameter][level]

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

    def calculate_mvpf(self, LoS_level: str = 'standard', n_det_level: str = 'average',
                       crime_weight_level: str = 'moderate'):
        """MVPF calculation based on all components."""
        det_wtp, det_rhv, detainee_total_values = self.calculate_detainee_values(LoS_level, n_det_level)
        soc_court, soc_crimeprev, soc_community, society_total_values = self.calculate_society_values(
            crime_weight_level, n_det_level)
        gov_health, gov_operations, gov_infractions, govt_total_costs = self.calculate_govt_cost(LoS_level, n_det_level)

        mvpf = (detainee_total_values + society_total_values) / govt_total_costs if govt_total_costs != 0 else 0

        return {
            'mvpf': mvpf,
            'detainee_values': detainee_total_values,
            'society_values': society_total_values,
            'govt_cost': govt_total_costs,
            'detainee_sub1': det_wtp,
            'detainee_sub2': det_rhv,
            'society_sub1': soc_court,
            'society_sub2': soc_crimeprev,
            'society_sub3': soc_community,
            'govt_sub1': gov_health,
            'govt_sub2': gov_operations,
            'govt_sub3': gov_infractions
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




calculator = MVPFCalculator()

    # Run calculation
result = calculator.calculate_mvpf('standard', 'average', 'moderate')

    # Print results
print(f"MVPF: {result['mvpf']:.2f}")
print(f"Detainee Values: ${result['detainee_values']:,.2f}")
print(f"Society Values: ${result['society_values']:,.2f}")
print(f"Government Cost: ${result['govt_cost']:,.2f}")

    # Export
from helpers import export_results_to_csv
export_results_to_csv(result, 'Data/mvpf_results.csv')

    #return calculator.calculate_mvpf(detainee_param1, detainee_param2, society_param1, society_param2)



