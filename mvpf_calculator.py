"""
MVPF Calculator Module
Contains all calculation logic for Marginal Value of Public Funds
"""

import pandas as pd
import numpy as np

class MVPFCalculator:

    def __init__(self, baseline_type: str = 'baseline',
                 values_csv: str = 'CCJ_quantified_values.csv',
                 mapping_csv: str = 'mvpf_mappingtable.csv'):
        """
        Initialize calculator with baseline type and data files.

        Args:
            baseline_type (str): 'baseline' or 'optimal'
            values_csv (str): Path to values configuration CSV
            mapping_csv (str): Path to MVPF mapping table CSV
        """
        self.baseline_type = baseline_type

        # Load configuration data
        try:
            self.values_df = pd.read_csv(values_csv)
            self.mapping_df = pd.read_csv(mapping_csv)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Required CSV file not found: {e}")

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

    def multipliers(self, file):
        file=read.csv(file)
        baseline_mult = 1.0 if baseline_type == 'historical' else 1.0

        LoS = {'basic': 60, 'standard': 70, 'enhanced': 203}[detainee_param1]
        crime_weight = {'minimal': 0.3, 'moderate': 0.7, 'significant': 0.9}[detainee_param2]
        n_det = {'below': 2500, 'average': 3000, 'above': 5000}[society_param1]
        n_population={'below': 5000000, 'average': 5171000, 'above': 5200000}[society_param2]


    def calculate_detainee_values():
        detainee_wtp = 11 * LoS * n_det
        detainee_rhv = -295275 * LoS * n_det
        detainee_values = detainee_wtp + detainee_rhv

    def calculate_values(self):
        society_court = 13 * crime_weight* n_det
        society_crimeprev = 0
        society_community = -294728 * crime_weight* n_det
        society_values = society_sub1 + society_sub2 + society_sub3

    def govt_cost(self):
        govt_health= 50 * baseline_mult
        govt_operations = 13200 * baseline_mult
        govt_refractions = 8000 * baseline_mult
        govt_costs = govt_health+ govt_operations + govt_refractions


    def calculate_mvpf(baseline_type, detainee_values, society_values, govt_cost):
        """
         MVPF calculation based on the weighted average of each component module
        Example: from mvpf_calculator import MVPFCalculator
                 calculator = MVPFCalculator(baseline_type)
                 return calculator.calculate_mvpf({...})
        """
        # Calculate all components
        det_sub1, det_sub2, det_total = self.calculate_detainee_values(
            detainee_wtp, detainee_rhv
        )

        soc_sub1, soc_sub2, soc_sub3, soc_total = self.calculate_society_values(
            society_court, society_crime, societ_community
        )

        gov_sub1, gov_sub2, gov_sub3, gov_total = self.calculate_govt_cost(
            detainee_param1, society_param1
        )

        # Calculate MVPF
        mvpf = (detainee_values + society_values) / govt_cost if govt_cost > 0 else 0

        return {
            'mvpf': mvpf,
            'detainee_values': detainee_values,
            'society_values': society_values,
            'govt_cost': govt_cost,
            'detainee_sub1': detainee_sub1,
            'detainee_sub2': detainee_sub2,
            'society_sub1': society_sub1,
            'society_sub2': society_sub2,
            'society_sub3': society_sub3,
            'govt_sub1': govt_sub1,
            'govt_sub2': govt_sub2,
            'govt_sub3': govt_sub3
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

