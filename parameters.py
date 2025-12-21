"""
Parameter Management for MVPF Calculator

Centralizes all parameter definitions, mappings, and conversions.

PARAMETER NAMING CONVENTIONS:
==============================

Three types of parameters are used throughout the system:

1. BASE Parameters (e.g., n_detainees_base)
   - Type: Absolute count/value
   - Example: 33,945 (detainee population count)
   - Usage: Provides the baseline value for calculations
   - In calculations: Used as the starting point before multipliers

2. MULT Parameters (e.g., n_detainees_mult)
   - Type: Multiplier (typically 0.8 to 1.2)
   - Applied WITH base: base × multiplier
   - Example: 33,945 × 1.2 = 40,734
   - Usage: Scales the baseline population up or down
   - In calculations: base_value × n_detainees_mult

3. SCALE_ONLY Parameters (e.g., n_detainees_scale_only)
   - Type: Multiplier (typically 0.8 to 1.2)
   - Applied WITHOUT base: just the multiplier
   - Example: 1.2 (percentage adjustment only)
   - Usage: Percentage adjustment where base population isn't needed
   - In calculations: value × n_detainees_mult (no base applied)

EXAMPLES:
=========
- det_wtp_freedom uses 'n_detainees_mult': $value × (33,945 × 1.2)
- soc_spillover uses 'n_detainees_scale_only': $value × 1.2 (no base)

The distinction ensures proper scaling:
- MULT: When the subcomponent value is per-detainee and needs population scaling
- SCALE_ONLY: When the subcomponent already includes population or needs only % adjustment
"""
import pandas as pd
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ParameterDefinition:
    """Define a parameter's properties."""
    key: str
    name: str
    description: str
    default_value: float
    min_value: float
    max_value: float
    dashboard_enabled: bool = True
    is_multiplier: bool = True  # True = multiplier, False = direct value from CSV

    # Mapping from dashboard dropdown values to multipliers or direct values
    dropdown_map: Optional[Dict[str, float]] = None

    # Base value from CSV (for multiplier params)
    base_value: Optional[float] = None


class ParameterRegistry:
    """
    Central registry for all MVPF parameters, including definitions and conversions.
    Single source of truth for dashboard setup and parameter handling.
    Loads weight values from subcomponent_values.csv.
    """

    def __init__(self, data_dir='Data'):
        self.weights = self._load_weights(data_dir)
        self.params = self._define_parameters()

    def _load_weights(self, data_dir: str) -> Dict[str, Dict]:
        """Load weight values from CSV."""
        csv_path = os.path.join(data_dir, 'subcomponent_values.csv')
        try:
            df = pd.read_csv(csv_path)
            df.columns = df.columns.str.strip()
            weight_rows = df[df['component'].str.lower() == 'weight']

            weights = {}
            for _, row in weight_rows.iterrows():
                weights[row['row_var']] = {
                    'value': float(row['selected_value']),
                    'min': float(row['min']) if pd.notna(row['min']) else None,
                    'max': float(row['max']) if pd.notna(row['max']) else None,
                    'name': row['name'],
                    'unit': row['unit']
                }
            return weights
        except Exception as e:
            print(f"⚠️ Could not load weights from CSV: {e}")
            return {}

    def _define_parameters(self) -> Dict[str, ParameterDefinition]:
        """Define all available parameters using CSV weights where available."""

        # Get weight values with defaults
        fel_rate = self.weights.get('fel_rate', {'value': 0.7, 'min': 0.5, 'max': 1.0})
        los_days = self.weights.get('los_days', {'value': 70, 'min': 60, 'max': 203})
        n_detainees = self.weights.get('n_detainees', {'value': 33945})
        n_society = self.weights.get('n_society', {'value': 5171000})

        return {
            # === DIRECT VALUE PARAMS (use CSV min/selected/max as dropdown options) ===

            'fel_rate': ParameterDefinition(
                key='fel_rate',
                name='Felony Rate',
                description='Proportion of felonies vs. misdemeanors in detained population',
                default_value=fel_rate['value'],
                min_value=fel_rate['min'] or 0.5,
                max_value=fel_rate['max'] or 1.0,
                dashboard_enabled=True,
                is_multiplier=False,  # Direct value
                dropdown_map={
                    'below': fel_rate['min'] or 0.5,
                    'average': fel_rate['value'],
                    'above': fel_rate['max'] or 1.0
                }
            ),

            'los_days': ParameterDefinition(
                key='los_days',
                name='Length of Stay',
                description='Average detention duration in days',
                default_value=los_days['value'],
                min_value=los_days['min'] or 60,
                max_value=los_days['max'] or 203,
                dashboard_enabled=True,
                is_multiplier=False,  # Direct value
                dropdown_map={
                    'below': los_days['min'] or 60,
                    'average': los_days['value'],
                    'above': los_days['max'] or 203
                }
            ),

            # === MULTIPLIER PARAMS (base value × multiplier) ===

            'n_detainees_mult': ParameterDefinition(
                key='n_detainees_mult',
                name='Detainee Population',
                description=f"Multiplier for detainee population (base: {n_detainees['value']:,.0f})",
                default_value=1.0,
                min_value=0.8,
                max_value=1.2,
                dashboard_enabled=True,
                is_multiplier=True,
                base_value=n_detainees['value'],
                dropdown_map={
                    'below': 0.8,
                    'average': 1.0,
                    'above': 1.2
                }
            ),

            'n_society_mult': ParameterDefinition(
                key='n_society_mult',
                name='Community Size',
                description=f"Multiplier for community size (base: {n_society['value']:,.0f})",
                default_value=1.0,
                min_value=0.8,
                max_value=1.2,
                dashboard_enabled=True,
                is_multiplier=True,
                base_value=n_society['value'],
                dropdown_map={
                    'below': 0.8,
                    'average': 1.0,
                    'above': 1.2
                }
            ),

            'crime_weight_mult': ParameterDefinition(
                key='crime_weight_mult',
                name='Crime Prevention Weighting',
                description='Weight given to crime prevention benefits',
                default_value=1.0,
                min_value=0.5,
                max_value=2.0,
                dashboard_enabled=False,
                is_multiplier=True,
                dropdown_map={
                    'low': 0.5,
                    'moderate': 1.0,
                    'high': 1.5,
                    'very_high': 2.0
                }
            ),

            'crime_effect': ParameterDefinition(
                key='crime_effect',
                name='Crime Effect',
                description='Crime impact multiplier on detention outcomes',
                default_value=0,
                min_value=-1.04,
                max_value=1.14,
                dashboard_enabled=True,
                is_multiplier=True,
                dropdown_map={
                    'large_decrease': 0.96,
                    'no_effect': 0,
                    'moderate_increase': 1.05,
                    'large_increase': 1.14
                }
            ),

            'n_detainees_base': ParameterDefinition(
                key='n_detainees_base',
                name='Number of Detainees (Base)',
                description='Actual base number of detainees',
                default_value=n_detainees['value'],
                min_value=n_detainees['value'],
                max_value=n_detainees['value'],
                dashboard_enabled=False,
                is_multiplier=False
            )
        }

    def convert_dashboard_input(self, **kwargs) -> Dict[str, float]:
        """
        Convert dashboard dropdown selections to parameter values.

        Returns:
            Dict of parameter values (direct values and multipliers)
        """
        result = {}

        # Map dashboard inputs to parameters (new names)
        input_mapping = {
            'fel_rate': 'fel_rate',
            'n_detainees': 'n_detainees_mult',
            'crime_effect': 'crime_effect',
            'los_days': 'los_days',

        }

        # Convert each input
        for input_key, param_key in input_mapping.items():
            if input_key in kwargs and kwargs[input_key] is not None:
                param_def = self.params[param_key]
                dropdown_value = kwargs[input_key]
                result[param_key] = param_def.dropdown_map.get(
                    dropdown_value,
                    param_def.default_value
                )

        # Add defaults for non-dashboard parameters
        for key in ['crime_weight_mult', 'crime_effect', 'n_detainees_base']:
            if key not in result:
                result[key] = self.params[key].default_value

        return result

    def validate_params(self, params: Dict[str, float]) -> Dict[str, float]:
        """
        Validate and clamp parameter values to allowed ranges.

        Args:
            params: Dictionary of parameter multipliers

        Returns:
            Validated parameters (clamped to valid ranges)
        """
        validated = {}
        for key, value in params.items():
            if key in self.params:
                param_def = self.params[key]
                # Clamp to min/max
                clamped = max(param_def.min_value,
                              min(param_def.max_value, value))
                if clamped != value:
                    print(f"⚠️ Warning: {key} value {value} clamped to {clamped}")
                validated[key] = clamped
            else:
                print(f"⚠️ Warning: Unknown parameter '{key}' ignored")

        return validated

    def get_defaults(self) -> Dict[str, float]:
        """Get default values for all parameters."""
        return {key: param.default_value for key, param in self.params.items()}

    def get_dashboard_enabled(self) -> List[str]:
        """Get list of parameters exposed to dashboard."""
        return [key for key, param in self.params.items() if param.dashboard_enabled]  #


class ParameterEffectsRegistry:
    """
    Defines which parameters affect which subcomponents.
    Single source of truth for parameter-subcomponent relationships.

    Parameters use new naming convention:
    - los_days: Length of stay in days (direct value from CSV)
    - n_detainees_mult: Detainee population multiplier (base from CSV)
    - n_society_mult: Community size multiplier (base from CSV)
    - fel_rate: Felony rate (direct value from CSV)
    """

    @staticmethod
    def get_effects_mapping() -> Dict[str, List[str]]:
        """
        Get mapping of subcomponents to their affecting parameters.

        row_var names must match subcomponent_values.csv exactly:
        - det_wtp_freedom, det_rel_harm (detainee_values)
        - soc_court, soc_crime_prevention, soc_spillover, soc_victimization (society_values)
        - gov_operations, gov_health (govt_cost)

        Returns:
            Dict mapping row_var to list of parameter keys
        """
        return {
            # ==================== DETAINEE VALUES ====================
            'det_wtp_freedom': [
                'los_days',  # Longer detention → higher WTP to avoid
                'n_detainees_mult',  # Scales total across population
            ],

            'det_rel_harm': [
                'los_days',  # Longer stays → more harm accumulates (RHV)
                'n_detainees_mult',  # Scales total across population
                # RHV value ($295,275/day) is per-day per-detainee, scaled by population
            ],

            # ==================== SOCIETY VALUES ====================
            'soc_court': [
                'n_detainees_mult',  # Per detainee value × detainee population
            ],

            'soc_crime_prevention': [
                # Unit: "dollars per detainee" - value is $0 currently
                # Special calculation: uses min/max weighted by fel_rate when crime_effect != 0
                # fel_rate and crime_effect are handled specially in _calc_one, not as multipliers
                'n_detainees_mult',  # Per detainee value × detainee population
            ],

            'soc_victimization': [
                # Unit: "dollar per victim" - $875,000 per victim
                # This is a per-victim cost, not per-detainee or per-society
                # Don't multiply by population - it's already a unit cost
                'fel_rate',  # Felony rate affects victimization likelihood
            ],

            'soc_spillover': [  # Note: no 's' - matches CSV
                # Unit: "dollars per detainee" - $294,728 per detainee
                'n_detainees_mult',  # Per detainee value × detainee population (base × mult)
                'n_society_scale_only',  # Society weight adjustment only (0.8/1.0/1.2), no base
            ],

            # ==================== GOVERNMENT COST ====================
            'gov_operations': [],  # Fixed cost - not scaled by parameters

            'gov_health': [
                'n_detainees_mult',  # More detainees → more health costs
                'los_days',  # Longer stays → more health needs
            ],

            'gov_crime_prevention': [
                'fel_rate',  # Felony vs misdemeanor rate affects cost
                'n_detainees_mult',  # Scales with detainee population
            ],
        }

    @staticmethod
    def get_justification(row_var: str, param_key: str) -> str:
        """
        Get human-readable justification for why a parameter affects a subcomponent.
        Useful for documentation and debugging.
        """
        justifications = {
            # Detainee effects
            ('det_wtp_freedom', 'los_days'):
                'Longer detention increases WTP to avoid it',
            ('det_wtp_freedom', 'n_detainees_mult'):
                'More detainees scales the total WTP',
            ('det_harm_during', 'los_days'):
                'Longer stays accumulate more harm',
            ('det_harm_during', 'n_detainees_mult'):
                'More detainees scales total harm',
            ('det_rel_harm', 'los_days'):
                'Relative harm valuation scales with detention length',
            ('det_post_release', 'los_days'):
                'Longer detention worsens post-release outcomes',

            # Society effects
            ('soc_crime_prevention', 'fel_rate'):
                'Higher felony rate increases crime prevention value',
            ('soc_crime_prevention', 'n_society_mult'):
                'Larger community benefits more from crime prevention',
            ('soc_victimization', 'fel_rate'):
                'Higher felony rate affects victimization costs',
            ('soc_spillovers', 'los_days'):
                'Longer detention increases family/community disruption',

            # Government effects
            ('gov_operations', 'n_detainees_mult'):
                'Operational costs scale with population size',
            ('gov_health', 'los_days'):
                'Longer stays increase per-person health costs',
        }
        return justifications.get((row_var, param_key), 'No justification documented')


class ParameterPresets:
    """Predefined parameter configurations for common scenarios.

    Uses new naming convention:
    - fel_rate: Felony rate (direct value, e.g., 0.7 = 70%)
    - los_days: Length of stay in days (direct value)
    - n_detainees_mult: Detainee population multiplier
    - n_society_mult: Community size multiplier
    """

    # Base values from CSV (defaults if CSV not available)
    BASE_LOS_DAYS = 70
    BASE_FEL_RATE = 0.7

    PRESETS = {
        'baseline': {
            'name': 'Baseline (Current Conditions)',
            'description': 'Default parameters reflecting current CCJ operations',
            'params': {
                'fel_rate': 0.7,  # 70% felony rate
                'los_days': 70,  # 70 days average stay
                'n_detainees_mult': 1.0,
                'n_society_mult': 1.0,
                'crime_weight_mult': 1.0,
                'crime_effect': 0,  # No crime effect
            }
        },

        'high_crime': {
            'name': 'High Crime Environment',
            'description': 'Elevated crime rate scenario',
            'params': {
                'fel_rate': 0.9,  # 90% felony rate
                'los_days': 77,  # 77 days (10% longer)
                'n_detainees_mult': 1.2,
                'n_society_mult': 1.0,
                'crime_weight_mult': 1.5,
                'crime_effect': 14,  # Large increase in crime
            }
        },

        'reform_optimistic': {
            'name': 'Optimistic Reform Scenario',
            'description': 'Reduced detention with better outcomes',
            'params': {
                'fel_rate': 0.63,  # 63% felony rate (10% lower)
                'los_days': 49,  # 49 days (30% shorter)
                'n_detainees_mult': 0.8,
                'n_society_mult': 1.0,
                'crime_weight_mult': 1.0,
                'crime_effect': -4,  # Large decrease in crime
            }
        },

        'conservative': {
            'name': 'Conservative Estimates',
            'description': 'Conservative assumptions on benefits',
            'params': {
                'fel_rate': 0.7,  # 70% felony rate (baseline)
                'los_days': 84,  # 84 days (20% longer)
                'n_detainees_mult': 1.1,
                'n_society_mult': 0.9,
                'crime_weight_mult': 0.7,
                'crime_effect': 5,  # Moderate increase in crime
            }
        }
    }

    @classmethod
    def get_preset(cls, preset_name: str) -> Dict[str, float]:
        """Get parameter values for a preset."""
        if preset_name not in cls.PRESETS:
            raise ValueError(f"Unknown preset '{preset_name}'. "
                             f"Available: {list(cls.PRESETS.keys())}")
        return cls.PRESETS[preset_name]['params'].copy()

    @classmethod
    def list_presets(cls) -> List[Dict]:
        """List all available presets with descriptions."""
        return [
            {
                'key': key,
                'name': preset['name'],
                'description': preset['description']
            }
            for key, preset in cls.PRESETS.items()
        ]

 #Usage in Dashboard:
  # Add preset dropdown
  #dcc.Dropdown(
  #    id='preset-selector',
  #    options=[
  #        {'label': p['name'], 'value': p['key']}
  #        for p in ParameterPresets.list_presets()
  #    ],
   #   value='baseline'
  #)

  # Load preset parameters
  #params = ParameterPresets.get_preset('high_crime')
  #result = calculator.calculate('baseline', params)


class ParameterSensitivityAnalyzer:
    """Analyze sensitivity of MVPF to parameter changes."""

    def __init__(self, calculator):
        self.calculator = calculator

    def run_sensitivity(self, base_params, scenario='baseline',
                        param_range=0.2):
        """
        Run sensitivity analysis by varying each parameter.

        Args:
            base_params: Base parameter values
            scenario: Scenario to test
            param_range: How much to vary each parameter (+/-)

        Returns:
            DataFrame with sensitivity results
        """
        results = []

        # Baseline calculation
        base_result = self.calculator.calculate(scenario, base_params)
        base_mvpf = base_result['mvpf']

        # Test each parameter
        for param_key in base_params.keys():
            base_val = base_params[param_key]

            # Test lower bound
            test_params_low = base_params.copy()
            test_params_low[param_key] = base_val * (1 - param_range)
            result_low = self.calculator.calculate(scenario, test_params_low)

            # Test upper bound
            test_params_high = base_params.copy()
            test_params_high[param_key] = base_val * (1 + param_range)
            result_high = self.calculator.calculate(scenario, test_params_high)

            # Calculate sensitivity
            mvpf_change = result_high['mvpf'] - result_low['mvpf']
            param_change = test_params_high[param_key] - test_params_low[param_key]
            sensitivity = mvpf_change / param_change if param_change != 0 else 0

            results.append({
                'parameter': param_key,
                'base_value': base_val,
                'mvpf_at_low': result_low['mvpf'],
                'mvpf_at_high': result_high['mvpf'],
                'mvpf_change': mvpf_change,
                'sensitivity': abs(sensitivity),
                'direction': 'positive' if sensitivity > 0 else 'negative'
            })

        # Sort by sensitivity (highest impact first)
        df = pd.DataFrame(results)
        df = df.sort_values('sensitivity', ascending=False)

        return df







