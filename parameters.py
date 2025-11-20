"""
 Parameter Management for MVPF Calculator
 Centralizes all parameter definitions, mappings, and conversions
 """
import pandas as pd
from dataclasses import dataclass
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

    # Mapping from dashboard dropdown values to multipliers
    dropdown_map: Optional[Dict[str, float]] = None


class ParameterRegistry:
    """
    Central registry for all MVPF parameters, including definitions and conversions.
    Single source of truth for dashboard setup and parameter handling.
    """

    def __init__(self):
        self.params = self._define_parameters()

    def _define_parameters(self) -> Dict[str, ParameterDefinition]:
        """Define all available parameters."""
        return {
            'crime_rate_mult': ParameterDefinition(
                key='crime_rate_mult',
                name='Crime Rate Impact',
                description='The rate of felonies and misdemeanors across detained population',
                default_value=0.7,
                min_value=0.5,
                max_value=0.9,
                dashboard_enabled=True,
                dropdown_map={
                    'below': 0.5,  # 50% felonies rate
                    'average': 0.7,  # 70% felonies rate (baseline)
                    'significant': 0.9  # 90% felonies rate
                }
            ),

            'detainee_pop_mult': ParameterDefinition(
                key='detainee_pop_mult',
                name='Detainee Population Size',
                description='Population of CCJ detainees in a year',
                default_value=1.0,
                min_value=0.8,
                max_value=1.2,
                dashboard_enabled=True,
                dropdown_map={
                    'below': 0.8,
                    'moderate': 1.0,
                    'above': 1.2
                }
            ),

            'community_size_mult': ParameterDefinition(
                key='community_size_mult',
                name='Community Size',
                description='Size of affected community',
                default_value=1.0,
                min_value=0.9,
                max_value=1.1,
                dashboard_enabled=True,
                dropdown_map={
                    'below': 0.9,
                    'moderate': 1.0,
                    'above': 1.1
                }
            ),

            'length_of_stay_mult': ParameterDefinition(
                key='length_of_stay_mult',
                name='Length of Stay',
                description='Average detention duration',
                default_value=1.0,
                min_value=0.7,
                max_value=3,
                dashboard_enabled=True,
                dropdown_map={
                    'below': 0.7,  # 60 day stays
                    'average': 1.0,  # 70 days baseline
                    'above': 3  # Longer stays of 203 days
                }
            ),

            'crime_weight_mult': ParameterDefinition(
                key='crime_weight_mult',
                name='Crime Prevention Weighting',
                description='Weight given to crime prevention benefits',
                default_value=1.0,
                min_value=0.5,
                max_value=2.0,
                dashboard_enabled=False,  # Not exposed to dashboard yet
                dropdown_map={
                    'low': 0.5,
                    'moderate': 1.0,
                    'high': 1.5,
                    'very_high': 2.0
                }
            ),

            'recidivism_mult': ParameterDefinition(
                key='recidivism_mult',
                name='Recidivism Rate Impact',
                description='Impact of recidivism on long-term outcomes',
                default_value=1.0,
                min_value=0.6,
                max_value=1.4,
                dashboard_enabled=False,  # Not exposed to dashboard yet
                dropdown_map={
                    'low': 0.6,
                    'average': 1.0,
                    'high': 1.4
                }
            )
        }

    def convert_dashboard_input(self, **kwargs) -> Dict[str, float]:
        """
        Convert dashboard dropdown selections to parameter multipliers.

        Args:
            crime_rate: 'below' | 'average' | 'significant'
            detainee_pop: 'below' | 'moderate' | 'above'
            community_size: 'below' | 'moderate' | 'above'
            length_of_stay: 'below' | 'average' | 'above'

        Returns:
            Dict of parameter multipliers
        """
        result = {}

        # Map dashboard inputs to parameters
        input_mapping = {
            'crime_rate': 'crime_rate_mult',
            'detainee_pop': 'detainee_pop_mult',
            'community_size': 'community_size_mult',
            'length_of_stay': 'length_of_stay_mult'
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
        for key in ['crime_weight_mult', 'recidivism_mult']:
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
    """

    @staticmethod
    def get_effects_mapping() -> Dict[str, List[str]]:
        """
        Get mapping of subcomponents to their affecting parameters.

        Returns:
            Dict mapping row_var to list of parameter keys
        """
        return {
            # ==================== DETAINEE VALUES ====================
            'det_wtp_freedom': [
                'length_of_stay_mult',  # Longer detention → higher WTP to avoid
                'detainee_pop_mult',  # Scales total across population
            ],

            'det_harm_during': [
                'length_of_stay_mult',  # Longer stays → more harm accumulates
                'detainee_pop_mult',  # Scales total across population
            ],

            'det_rel_harm': [
                'length_of_stay_mult',  # Longer stays → more harm accumulates (RHV)
                'detainee_pop_mult',  # Scales total across population
            ],

            'det_post_release': [
                'length_of_stay_mult',  # Longer detention → worse post-release outcomes
                'recidivism_mult',  # Recidivism affects post-release trajectory
            ],

            # ==================== SOCIETY VALUES ====================
            'soc_court': [
                'detainee_pop_mult',  # More detainees → more court appearances
            ],

            'soc_crime_prevention': [
                'crime_weight_mult',  # Policy weight on crime prevention
                'community_size_mult',  # Larger community → more people affected
            ],

            'soc_victimization': [
                'crime_weight_mult',  # Policy weight on victim costs
                'community_size_mult',  # Larger community → more potential victims
            ],

            'soc_spillovers': [
                'community_size_mult',  # Larger community → more spillover effects
                'length_of_stay_mult',  # Longer detention → more disruption
            ],

            # ==================== GOVERNMENT COST ====================
            'gov_operations': [
                'detainee_pop_mult',  # More detainees → higher operational costs
                'length_of_stay_mult',  # Longer stays → higher costs per person
            ],

            'gov_court_admin': [
                'detainee_pop_mult',  # More detainees → more court processing
            ],

            'gov_long_term': [
                'recidivism_mult',  # Higher recidivism → more long-term costs
            ],

            'gov_health': [
                'detainee_pop_mult',  # More detainees → more health costs
                'length_of_stay_mult',  # Longer stays → more health needs
            ],
        }

    @staticmethod
    def get_justification(row_var: str, param_key: str) -> str:
        """
        Get human-readable justification for why a parameter affects a subcomponent.
        Useful for documentation and debugging.
        """
        justifications = {
            ('det_wtp_freedom', 'length_of_stay_mult'):
                'Longer detention increases WTP to avoid it',
            ('det_wtp_freedom', 'detainee_pop_mult'):
                'More detainees scales the total WTP',
            ('gov_operations', 'detainee_pop_mult'):
                'Operational costs scale with population size',
            ('gov_operations', 'length_of_stay_mult'):
                'Longer stays increase per-person operational costs',
            # ... add more
        }
        return justifications.get((row_var, param_key), 'No justification documented')


class ParameterPresets:
    """Predefined parameter configurations for common scenarios."""

    PRESETS = {
        'baseline': {
            'name': 'Baseline (Current Conditions)',
            'description': 'Default parameters reflecting current CCJ operations',
            'params': {
                'crime_rate_mult': 1.0,
                'detainee_pop_mult': 1.0,
                'community_size_mult': 1.0,
                'length_of_stay_mult': 1.0,
                'crime_weight_mult': 1.0,
                'recidivism_mult': 1.0,
            }
        },

        'high_crime': {
            'name': 'High Crime Environment',
            'description': 'Elevated crime rate scenario',
            'params': {
                'crime_rate_mult': 1.5,
                'detainee_pop_mult': 1.2,
                'community_size_mult': 1.0,
                'length_of_stay_mult': 1.1,
                'crime_weight_mult': 1.5,
                'recidivism_mult': 1.3,
            }
        },

        'reform_optimistic': {
            'name': 'Optimistic Reform Scenario',
            'description': 'Reduced detention with better outcomes',
            'params': {
                'crime_rate_mult': 0.9,
                'detainee_pop_mult': 0.8,
                'community_size_mult': 1.0,
                'length_of_stay_mult': 0.7,
                'crime_weight_mult': 1.0,
                'recidivism_mult': 0.8,
            }
        },

        'conservative': {
            'name': 'Conservative Estimates',
            'description': 'Conservative assumptions on benefits',
            'params': {
                'crime_rate_mult': 1.0,
                'detainee_pop_mult': 1.1,
                'community_size_mult': 0.9,
                'length_of_stay_mult': 1.2,
                'crime_weight_mult': 0.7,
                'recidivism_mult': 1.2,
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


class ParameterValidator:
    """Validate parameter inputs and provide warnings."""

    # Define reasonable bounds (not hard limits, but warning thresholds)
    REASONABLE_BOUNDS = {
        'crime_rate_mult': (0.3, 2.0),
        'detainee_pop_mult': (0.5, 2.0),
        'community_size_mult': (0.7, 1.5),
        'length_of_stay_mult': (0.5, 2.0),
        'crime_weight_mult': (0.2, 3.0),
        'recidivism_mult': (0.4, 2.0),
    }

    @classmethod
    def validate(cls, params: Dict[str, float], strict=False) -> Dict[str, float]:
        """
        Validate parameter dictionary.

        Args:
            params: Parameter multipliers
            strict: If True, raise error on out-of-bounds. If False, warn.

        Returns:
            Validated parameters
        """
        validated = {}
        warnings = []

        for key, value in params.items():
            if key not in cls.REASONABLE_BOUNDS:
                warnings.append(f"Unknown parameter '{key}' - ignoring")
                continue

            min_val, max_val = cls.REASONABLE_BOUNDS[key]

            if value < min_val or value > max_val:
                msg = (f"Parameter '{key}' value {value:.2f} is outside "
                       f"reasonable range [{min_val}, {max_val}]")
                if strict:
                    raise ValueError(msg)
                else:
                    warnings.append(msg)

            validated[key] = value

        # Print warnings
        if warnings:
            print("⚠️ Parameter Validation Warnings:")
            for w in warnings:
                print(f"  - {w}")

        return validated


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

#if __name__ == '__main__':
#Usage:
 #   analyzer = ParameterSensitivityAnalyzer(MVPFCalculator)
 #   sensitivity_df = analyzer.run_sensitivity(base_params)

 #   print("Parameter Sensitivity Rankings:")
 #   for _, row in sensitivity_df.iterrows():
 #       print(f"{row['parameter']:20s} | Sensitivity: {row['sensitivity']:.3f}")








