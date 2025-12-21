"""
Utility functions for MVPF Dashboard
"""
import pandas as pd
import json
import os
from datetime import datetime

from cpi_adjuster import CPIAdjuster
from formatting import (
    format_currency,
    format_ratio,
    format_mvpf,
    get_mvpf_rating,
    format_percentage,
    format_number
)
from parameters import ParameterRegistry

"""
Data export and formatting functions
"""

def load_historical_results(filename='mvpf_results.csv'):
    """
    Load historical MVPF results from CSV.

    Args:
        filename (str): Input filename

    Returns:
        pandas.DataFrame: Historical results
    """
    try:
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return pd.DataFrame()


# ==================== RESULTS EXPORT ====================

class ResultsExporter:
    """Export MVPF results to various formats."""

    @staticmethod
    def to_csv(results, filename='mvpf_results.csv'):
        """
        Export results to CSV.

        Args:
            results (list or dict): Single result dict or list of result dicts
            filename (str): Output filename

        Returns:
            pd.DataFrame: Exported data
        """
        # Handle single result
        if isinstance(results, dict):
            results = [results]

        rows = []
        for result in results:
            row = {
                'timestamp': datetime.now().isoformat(),
                'scenario': result.get('scenario', 'unknown'),
                'mvpf': result.get('mvpf', 0),
                'detainee_total': result.get('detainee_values', 0),
                'society_total': result.get('society_values', 0),
                'govt_total': result.get('govt_cost', 0),
            }

            # Add breakdowns
            for name, value in result.get('detainee_breakdown', {}).items():
                row[f'det_{name}'] = value
            for name, value in result.get('society_breakdown', {}).items():
                row[f'soc_{name}'] = value
            for name, value in result.get('govt_breakdown', {}).items():
                row[f'gov_{name}'] = value

            # Add parameters
            for key, value in result.get('params', {}).items():
                row[f'param_{key}'] = value

            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False)
        print(f"✓ Exported {len(rows)} results to {filename}")
        return df

    @staticmethod
    def to_json(results, filename='mvpf_results.json'):
        """
        Export results to JSON.

        Args:
            results (list or dict): Single result dict or list of result dicts
            filename (str): Output filename
        """
        if isinstance(results, dict):
            results = [results]

        # Add timestamp to each result
        for result in results:
            result['timestamp'] = datetime.now().isoformat()

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"✓ Exported {len(results)} results to {filename}")

    @staticmethod
    def to_excel(results, filename='mvpf_results.xlsx'):
        """
        Export results to Excel with multiple sheets.

        Args:
            results (list or dict): Single result dict or list of result dicts
            filename (str): Output filename
        """
        if isinstance(results, dict):
            results = [results]

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = []
            for result in results:
                summary_data.append({
                    'Scenario': result.get('scenario', 'unknown'),
                    'MVPF': result.get('mvpf', 0),
                    'Detainee Values': result.get('detainee_values', 0),
                    'Society Values': result.get('society_values', 0),
                    'Government Cost': result.get('govt_cost', 0)
                })
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

            # Detailed sheet (same as CSV)
            df = ResultsExporter.to_csv(results, filename=None)  # Get dataframe without saving
            df.to_excel(writer, sheet_name='Details', index=False)

        print(f"✓ Exported {len(results)} results to {filename}")

    @staticmethod
    def to_dataframe(results):
        """
        Convert results to pandas DataFrame (no file output).

        Args:
            results (list or dict): Single result dict or list of result dicts

        Returns:
            pd.DataFrame: Results as dataframe
        """
        if isinstance(results, dict):
            results = [results]

        return pd.DataFrame(results)


# ==================== DASHBOARD HELPER FUNCTIONS ====================

# Initialize parameter registry for dashboard helpers
param_registry = ParameterRegistry()


def load_benchmarks(data_dir="Data"):
    """Load benchmark comparison data from CSV file."""
    filepath = os.path.join(data_dir, "mvpf_comparisons.csv")
    df = pd.read_csv(filepath)
    return df.to_dict("records")


def get_scenario_description(scenario):
    """Return the description for a given scenario."""
    descriptions = {
        "baseline": "Represents current operations at Cook County Jail with standard parameters. This scenario serves as the reference point for comparison.",
        "most conservative": "Uses conservative estimates for all parameters, minimizing potential benefits and maximizing costs. Provides a lower-bound estimate of MVPF.",
        "least conservative": "Uses optimistic estimates that maximize potential benefits and minimize costs. Provides an upper-bound estimate of MVPF.",
    }
    return descriptions.get(scenario, "No description available for this scenario.")


def toggle_style(n_clicks, style):
    """Helper function to toggle visibility of collapsible sections."""
    if not n_clicks:
        return style or {"display": "none"}
    if not style or style.get("display") == "none":
        return {"display": "block"}
    return {"display": "none"}


def convert_dropdown_to_params(
    fel_rate_sel,
    n_detainees_sel,
    n_society_sel,
    los_days_sel,
    n_detainees_base=None,
    crime_effect=0,
):
    """
    Convert dashboard slider values to parameter values.

    Parameters:
    -----------
    fel_rate_sel : float
        Felony rate value (0.5 to 1.0)
    n_detainees_sel : float
        Detainee population multiplier (0.8 to 1.2)
    n_society_sel : float
        Community size multiplier (0.8 to 1.2)
    los_days_sel : float
        Length of stay in days (60 to 203)
    n_detainees_base : float, optional
        Baseline detainee population. If None, uses default value.
    crime_effect : float, optional
        Crime effect multiplier (-4 to 14). Defaults to 0 (no effect).

    Returns:
    --------
    dict : Parameter values for calculator
    """
    # Get default value from parameter registry
    from parameters import ParameterRegistry
    n_detainees_base_param = ParameterRegistry().params["n_detainees_base"]

    # Use provided baseline or fall back to default
    baseline = (
        n_detainees_base if n_detainees_base is not None else n_detainees_base_param.default_value
    )

    # Sliders now return numeric values directly
    return {
        "fel_rate": fel_rate_sel,
        "los_days": los_days_sel,
        "n_detainees_mult": n_detainees_sel,
        "n_detainees_base": baseline,
        "n_society_mult": n_society_sel,
        "crime_weight_mult": 1.0,
        "crime_effect": crime_effect,
    }


def dashboard_params(fel_rate='average', n_detainees_mult='average', n_society_mult='average', los_days='average', crime_weight_mult=None):
    """Convert dashboard dropdowns to parameter dict.

    Uses ParameterRegistry to get correct values
    """
    # Use the ParameterRegistry for correct value mapping
    result = param_registry.convert_dashboard_input(
        fel_rate=fel_rate,
        n_detainees=n_detainees_mult,
        n_society=n_society_mult,
        los_days=los_days
    )

    if crime_weight_mult is not None:
        mult_maps = {'low': 0.5, 'moderate': 1.0, 'average': 1.0, 'high': 1.5}
        result['crime_weight_mult'] = mult_maps.get(crime_weight_mult, 1.0)

    return result


def safe_get(lst, index, default=0):
    """Safely get item from list by index, returning default if index out of range."""
    try:
        return lst[index]
    except IndexError:
        return default


def calculate_mvpf_for_dashboard(
    scenario,
    detainee_param1,
    detainee_param2,
    society_param1,
    society_param2,
    detainee_baseline=None,
    crime_effect=0,
    calculator=None
):
    """
    Calculate MVPF using the modular MVPFCalculator class.
    Wrapper function for dashboard callbacks.

    Parameters:
    -----------
    scenario : str
        Scenario name (e.g., 'baseline', 'most conservative', etc.)
    detainee_param1 : float
        Felony rate value (0.5 to 1.0)
    detainee_param2 : float
        Detainee population multiplier (0.8 to 1.2)
    society_param1 : float
        Community size multiplier (0.8 to 1.2)
    society_param2 : float
        Length of stay in days (60 to 203)
    detainee_baseline : float, optional
        Baseline detainee population. If None, uses default value.
    crime_effect : float, optional
        Crime effect multiplier (-4 to 14). Defaults to 0 (no effect).
    calculator : MVPFCalculator, optional
        Calculator instance to use. If None, creates a new one.

    Returns:
    --------
    dict : MVPF results with all breakdowns
    """
    params = convert_dropdown_to_params(
        fel_rate_sel=detainee_param1,
        n_detainees_sel=detainee_param2,
        n_society_sel=society_param1,
        los_days_sel=society_param2,
        n_detainees_base=detainee_baseline,
        crime_effect=crime_effect,
    )

    # Use provided calculator or import and create one
    if calculator is None:
        from mvpf_calculator import MVPFCalculator
        calculator = MVPFCalculator(data_dir="Data")

    result = calculator.calculate(scenario, params)

    # Extract breakdown values for backwards compatibility
    detainee_breakdown = list(result["detainee_breakdown"].values())
    society_breakdown = list(result["society_breakdown"].values())
    govt_breakdown = list(result["govt_breakdown"].values())

    result["detainee_sub1"] = safe_get(detainee_breakdown, 0)
    result["detainee_sub2"] = safe_get(detainee_breakdown, 1)
    result["society_sub1"] = safe_get(society_breakdown, 0)
    result["society_sub2"] = safe_get(society_breakdown, 1)
    result["society_sub3"] = safe_get(society_breakdown, 2)
    result["govt_sub1"] = safe_get(govt_breakdown, 0)
    result["govt_sub2"] = safe_get(govt_breakdown, 1)
    result["govt_sub3"] = safe_get(govt_breakdown, 2)

    return result


