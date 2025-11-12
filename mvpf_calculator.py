"""
MVPF Calculator Module
Contains all calculation logic for Marginal Value of Public Funds
"""

import pandas as pd
import numpy as np

class MVPFCalculator:

    def __init__(self, baseline_type: str = 'baseline',
                 values_csv: str = 'subcomponent_values.csv',
                 mapping_csv: str = 'mvpf_component_mapping.csv'):
        """
        Initialize calculator with baseline scenario and data files.

        Args:
            baseline_type (str): 'baseline'
            values_csv (str): Path to values configuration CSV
            mapping_csv (str): Path to MVPF mapping table CSV
        """
        # Load configuration data
        try:
            self.values_df = pd.read_csv(values_csv)
            self.mapping_df = pd.read_csv(mapping_csv)
            self.cpi_df = pd.read_csv(cpi_csv)
        except FileNotFoundError as e:
            print(f"Warning: Required CSV file not found: {e}. Using dummy dataframes.")
            self.values_df = pd.DataFrame()  # Placeholder for values if file not found
            self.mapping_df = pd.DataFrame()  # Placeholder for mapping if file not found
            self.cpi_df = pd.DataFrame()  # Placeholder for CPI if file not found
            # In a production environment, you might re-raise the error or handle it differently

        # Initialize component selection tracking
        self.selected_components = {
            'detainee': [],  # e.g., ['wtp', 'rhv']
            'society': [],  # e.g., ['court', 'crimeprev', 'community']
            'government': []  # e.g., ['health', 'operations', 'refractions']
        }

        # Initialize weights
        self.component_weights = {
            'detainee': {},
            'society': {},
            'government': {}
        }

        # Initialize multipliers and parameters based on baseline_type and potentially values_df
        self.baseline_mult = 1.0 if self.baseline_type == 'historical' else 1.0

        # These would ideally be loaded from values_df or another config source, for now hardcoded as per original intent
        self.LoS = {'basic': 60, 'standard': 70, 'enhanced': 203}
        self.crime_weight = {'minimal': 0.5, 'moderate': 0.7, 'significant': 0.9}
        self.n_det = {'below': 2500, 'average': 3000, 'above': 5000}
        self.n_population = {'below': 5000000, 'average': 5171000, 'above': 5200000}

        # Define target NPV year
        self.target_npv_year = 2025

        # Initialize dictionaries for NPV calculation
        self.original_base_values = {}
        self.original_years = {}

        # Parse 'Original Base Value' and 'Original Year' from values_df
        if not self.values_df.empty and all(
                col in self.values_df.columns for col in ['Component', 'Original Base Value', 'Original Year']):
            for index, row in self.values_df.iterrows():
                component_name = row['Component']
                # Handle missing 'Original Base Value' or 'Original Year'
                original_base_value = row['Original Base Value'] if pd.notna(row['Original Base Value']) else None
                original_year = int(row['Original Year']) if pd.notna(row['Original Year']) else None

                self.original_base_values[component_name] = original_base_value
                self.original_years[component_name] = original_year
        else:
            print(
                "Warning: 'Component', 'Original Base Value', or 'Original Year' columns not found in values_df or values_df is empty. NPV calculations may be affected.")

    def calculate_detainee_values(self, LoS_level: str = 'standard', n_det_level: str = 'average'):
        """
        Calculates detainee-related values based on selected levels.
        """
        LoS_val = self.LoS.get(LoS_level, self.LoS['standard'])
        n_det_val = self.n_det.get(n_det_level, self.n_det['average'])

        # Retrieve original base values and years for NPV adjustment
        original_wtp_value = self.original_base_values.get('detainee_wtp', 11) # Default to 11 if not found
        original_wtp_year = self.original_years.get('detainee_wtp')

        original_rhv_value = self.original_base_values.get('detainee_rhv', -295275) # Default to -295275 if not found
        original_rhv_year = self.original_years.get('detainee_rhv')

        # Calculate NPV-adjusted WTP
        if original_wtp_value is not None and original_wtp_year is not None:
            npv_wtp_base = calculate_pv_conversion(
                original_wtp_value, original_wtp_year, self.target_npv_year, self.cpi_df
            )
        else:
            npv_wtp_base = 11 # Fallback to hardcoded default

        # Calculate NPV-adjusted RHV
        if original_rhv_value is not None and original_rhv_year is not None:
            npv_rhv_base = calculate_pv_conversion(
                original_rhv_value, original_rhv_year, self.target_npv_year, self.cpi_df
            )
        else:
            npv_rhv_base = -295275 # Fallback to hardcoded default

        detainee_wtp = npv_wtp_base * LoS_val * n_det_val
        detainee_rhv = npv_rhv_base * LoS_val * n_det_val
        detainee_total_values = detainee_wtp + detainee_rhv
        return detainee_wtp, detainee_rhv, detainee_total_values

    def calculate_society_values(self, crime_weight_level: str = 'moderate', n_det_level: str = 'average'):
        """
        Calculates society-related values based on selected levels.
        """
        crime_weight_val = self.crime_weight.get(crime_weight_level, self.crime_weight['moderate'])
        n_det_val = self.n_det.get(n_det_level, self.n_det['average'])

        # Retrieve original base values and years for NPV adjustment
        original_court_value = self.original_base_values.get('society_court', 13)
        original_court_year = self.original_years.get('society_court')

        original_crimeprev_value = self.original_base_values.get('society_crimeprev', 0)
        original_crimeprev_year = self.original_years.get('society_crimeprev')

        original_community_value = self.original_base_values.get('society_community', -294728)
        original_community_year = self.original_years.get('society_community')

        # Calculate NPV-adjusted base amounts
        if original_court_value is not None and original_court_year is not None:
            npv_court_base = calculate_pv_conversion(
                original_court_value, original_court_year, self.target_npv_year, self.cpi_df
            )
        else:
            npv_court_base = 13  # Fallback to hardcoded default

        if original_crimeprev_value is not None and original_crimeprev_year is not None:
            npv_crimeprev_base = calculate_pv_conversion(
                original_crimeprev_value, original_crimeprev_year, self.target_npv_year, self.cpi_df
            )
        else:
            npv_crimeprev_base = 0  # Fallback to hardcoded default

        if original_community_value is not None and original_community_year is not None:
            npv_community_base = calculate_pv_conversion(
                original_community_value, original_community_year, self.target_npv_year, self.cpi_df
            )
        else:
            npv_community_base = -294728  # Fallback to hardcoded default

        society_court = npv_court_base * crime_weight_val * n_det_val
        society_crimeprev = npv_crimeprev_base * crime_weight_val * n_det_val  # Assuming crimeprev also scales, adjust if not.
        society_community = npv_community_base * crime_weight_val * n_det_val
        society_total_values = society_court + society_crimeprev + society_community
        return society_court, society_crimeprev, society_community, society_total_values

    def calculate_govt_cost(self):
        """
        Calculates government-related costs.
        """
        govt_health = 50 * self.baseline_mult
        govt_operations = 13200 * self.baseline_mult
        govt_refractions = 8000 * self.baseline_mult
        govt_total_costs = govt_health + govt_operations + govt_refractions
        return govt_health, govt_operations, govt_refractions, govt_total_costs


    def calculate_mvpf(self, LoS_level: str = 'standard', n_det_level: str = 'average', crime_weight_level: str = 'moderate'):
        """
        MVPF calculation based on the weighted average of each component module
        """
        # Calculate all components
        det_wtp, det_rhv, detainee_total_values = self.calculate_detainee_values(LoS_level, n_det_level)
        soc_court, soc_crimeprev, soc_community, society_total_values = self.calculate_society_values(crime_weight_level, n_det_level)
        gov_health, gov_operations, gov_refractions, govt_total_costs = self.calculate_govt_cost()

        # Calculate MVPF
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
            'govt_sub3': gov_refractions
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


# Convenience functions for direct use
def calculate_mvpf_quick(baseline_type, detainee_param1, detainee_param2,
                         society_param1, society_param2):
    """
    Quick MVPF calculation without instantiating class.

    Returns:
        dict: MVPF results
    """
    calculator = MVPFCalculator(baseline_type)
    return calculator.calculate_mvpf(
        detainee_param1, detainee_param2,
        society_param1, society_param2
    )

