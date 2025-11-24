"""
Subcomponent Registry and Calculations
Handles individual subcomponent data and parameter-based calculations
"""

import pandas as pd
import numpy as np

from cpi_adjuster import CPIAdjuster
from parameters import ParameterRegistry, ParameterEffectsRegistry

class SubcomponentRegistry:
    """
    Registry for all MVPF subcomponents.

    Responsibilities:
    - Store subcomponent metadata (name, component, sign, year)
    - Pre-calculate CPI-adjusted base values
    - Define parameter effects on each subcomponent
    - Calculate subcomponent values with parameter multipliers
    """

    def __init__(self, values_df, cpi_adjuster):
        """
        Initialize subcomponent registry.

        Args:
            values_df (pd.DataFrame): Subcomponent values data
            cpi_adjuster (CPIAdjuster): CPI adjustment utility
        """
        self.data = {}
        self.cpi = cpi_adjuster

        # Build registry from dataframe
        self._build_registry(values_df)

        # Define parameter effects
        self._define_parameter_effects()

        print(f"✓ Loaded {len(self.data)} subcomponents")

    def _build_registry(self, values_df):
        """
        Build subcomponent lookup from values dataframe.

        Pre-calculates CPI-adjusted base values for performance.
        """
        for _, row in values_df.iterrows():
            # Skip parameters (only process subcomponents)
            if pd.notna(row.get('parameter')):
                continue

            row_var = row['row_var']

            # Extract data
            raw_value = float(row['selected_value'])
            sign_str = str(row['sign']).strip().lower()
            sign = 1 if sign_str == 'positive' else -1
            year = int(row['source_dollar_year']) if pd.notna(row['source_dollar_year']) else None

            # Calculate base value with sign applied
            base_value = abs(raw_value) * sign

            # Apply CPI adjustment to base value (pre-computation for speed)
            if year:
                base_value = self.cpi.adjust_to_year(base_value, year, 2025)

            # Store in registry
            self.data[row_var] = {
                'name': row['name'],
                'component': row['component'],
                'base_value': base_value,  # Pre-computed CPI-adjusted value
                'raw_value': raw_value,  # Original value from CSV
                'sign': sign,  # 1 or -1
                'year': year  # Source year or None
            }

    def _define_parameter_effects(self):
        """
        Define which parameters affect which subcomponents.

        This mapping controls how dashboard parameters multiply subcomponent values.
        Each subcomponent lists the parameter keys that should multiply its value.

        Parameter names (matching CSV and ParameterEffectsRegistry):
        - los_days: Length of stay in days (direct value)
        - n_detainees_mult: Detainee population multiplier
        - n_society_mult: Community size multiplier
        - fel_rate: Felony rate (direct value)
        - crime_weight_mult: Crime prevention weighting
        - recidivism_mult: Recidivism rate impact
        """
        self.param_effects = {
            # ==================== DETAINEE VALUES ====================
            'det_wtp_freedom': [
                'los_days',  # Longer stays → more harm during detention
                'n_detainees_mult'  # More detainees → scales total WTP
            ],

            'det_rel_harm': [
                'los_days',  # Longer stays → more harm during detention
                # Note: RHV value ($295,275/day) is already a daily aggregate total,
                # NOT per-detainee. Don't multiply by n_detainees.
            ],

            # ==================== SOCIETY VALUES ====================
            'soc_court': [
                'n_detainees_mult'  # Per detainee value × detainee population
            ],

            'soc_crime_prevention': [
                # Unit: "dollars per detainee" - value is $0 currently
                'n_detainees_mult',  # Per detainee value × detainee population
                'fel_rate'  # Felony rate affects crime prevention value
            ],

            'soc_victimization': [
                # Unit: "dollar per victim" - $875,000 per victim
                # This is a per-victim cost, not per-detainee or per-society
                # Don't multiply by population - it's already a unit cost
                'fel_rate'  # Felony rate affects victimization likelihood
            ],

            'soc_spillover': [
                # Unit: "dollars per detainee" - $294,728 per detainee
                'n_detainees_mult',  # Per detainee value × detainee population (base × mult)
                'n_society_adj'  # Society weight adjustment only (0.8/1.0/1.2), no base
            ],

            # ==================== GOVERNMENT COST ====================
            'gov_operations': [
                # Fixed cost - not scaled by parameters
            ],

            'gov_health': [
                'los_days',  # Longer stays → more health needs
                'n_detainees_mult'  # More detainees → scales total health costs
            ]
        }

    def calculate(self, row_var, params=None):
        """
        Calculate a subcomponent value with parameter effects.

        Args:
            row_var (str): Subcomponent identifier (e.g., 'det_wtp_freedom')
            params (dict): Parameter multipliers

        Returns:
            float: Calculated value (CPI-adjusted, sign-applied, parameter-multiplied)

        Raises:
            KeyError: If row_var not found in registry
        """
        if row_var not in self.data:
            raise KeyError(f"Subcomponent '{row_var}' not found in registry")

        # Get pre-computed base value (already CPI-adjusted and sign-applied)
        value = self.data[row_var]['base_value']

        # Apply parameter multipliers
        if params:
            multiplier = self._get_combined_multiplier(row_var, params)
            value *= multiplier

        return value

    def _get_combined_multiplier(self, row_var, params):
        """
        Calculate combined multiplier for a subcomponent.

        Multiplies together all relevant parameter effects.

        Args:
            row_var (str): Subcomponent identifier
            params (dict): Parameter multipliers

        Returns:
            float: Combined multiplier (product of all relevant parameters)
        """
        # Start with neutral multiplier
        multiplier = 1.0

        # Check if this subcomponent has defined parameter effects
        if row_var not in self.param_effects:
            return multiplier

        # Multiply all relevant parameters
        for param_key in self.param_effects[row_var]:
            multiplier *= params.get(param_key, 1.0)

        return multiplier

    def get_name(self, row_var):
        """
        Get display name for a subcomponent.

        Args:
            row_var (str): Subcomponent identifier

        Returns:
            str: Display name or row_var if not found
        """
        return self.data.get(row_var, {}).get('name', row_var)

    def get_type(self, row_var):
        """
        Get component type for a subcomponent.

        Args:
            row_var (str): Subcomponent identifier

        Returns:
            str: Component type ('detainee_values', 'society_values', 'govt_cost')
        """
        return self.data.get(row_var, {}).get('component', None)

    def get_base_value(self, row_var):
        """
        Get pre-computed base value (CPI-adjusted, sign-applied).

        Args:
            row_var (str): Subcomponent identifier

        Returns:
            float: Base value
        """
        return self.data.get(row_var, {}).get('base_value', 0)

    def get_metadata(self, row_var):
        """
        Get all metadata for a subcomponent.

        Args:
            row_var (str): Subcomponent identifier

        Returns:
            dict: Complete metadata
        """
        return self.data.get(row_var, {})

    def list_subcomponents(self, component=None):
        """
        List all subcomponents, optionally filtered by component type.

        Args:
            component (str, optional): Filter by component type

        Returns:
            list: Subcomponent row_var identifiers
        """
        if component is None:
            return list(self.data.keys())

        return [
            row_var for row_var, data in self.data.items()
            if data['component'] == component
        ]

    def get_parameter_effects_for(self, row_var):
        """
        Get list of parameters that affect a subcomponent.

        Args:
            row_var (str): Subcomponent identifier

        Returns:
            list: Parameter keys that affect this subcomponent
        """
        return self.param_effects.get(row_var, [])

    def add_subcomponent(self, row_var, name, component, value, sign, year=None, param_effects=None):
        """
        Programmatically add a subcomponent (for testing or extensions).

        Args:
            row_var (str): Unique identifier
            name (str): Display name
            component (str): Component type
            value (float): Raw value
            sign (int): 1 for positive, -1 for negative
            year (int, optional): Source year for CPI adjustment
            param_effects (list, optional): List of parameter keys that affect this
        """
        base_value = abs(value) * sign
        if year:
            base_value = self.cpi.adjust(base_value, year)

        self.data[row_var] = {
            'name': name,
            'component': component,
            'base_value': base_value,
            'raw_value': value,
            'sign': sign,
            'year': year
        }

        if param_effects:
            self.param_effects[row_var] = param_effects

        print(f"✓ Added subcomponent: {row_var}")

    def get_summary_stats(self):
        """
        Get summary statistics about the registry.

        Returns:
            dict: Summary information
        """
        components = {}
        for row_var, data in self.data.items():
            comp = data['component']
            if comp not in components:
                components[comp] = {'count': 0, 'total_base_value': 0}
            components[comp]['count'] += 1
            components[comp]['total_base_value'] += data['base_value']

        return {
            'total_subcomponents': len(self.data),
            'by_component': components,
            'parameters_defined': len(self.param_effects)
        }