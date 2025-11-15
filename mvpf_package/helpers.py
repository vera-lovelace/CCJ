"""
Utility functions for MVPF Dashboard
"""
import pandas as pd
import json
from datetime import datetime

"""
CPI adjustment utilities for converting values across years.
"""
def adjust_value_by_factor(value, factor):
    """
    Adjust a value by a pre-calculated inflation factor.

    Args:
        value (float): Original value
        factor (float): Multiplication factor (e.g., factor_to_2025)

    Returns:
        float: Adjusted value
    """
    return value * factor


def adjust_value_by_cpi(value, source_cpi, target_cpi):
    """
    Adjust a value from source year to target year using CPI values.

    Args:
        value (float): Original value in source year dollars
        source_cpi (float): CPI for source year
        target_cpi (float): CPI for target year

    Returns:
        float: Value adjusted to target year
    """
    if source_cpi <= 0:
        raise ValueError("Source CPI must be positive")
    return value * (target_cpi / source_cpi)


def calculate_inflation_factor(source_cpi, target_cpi):
    """
    Calculate the inflation factor between two years.

    Args:
        source_cpi (float): CPI for source year
        target_cpi (float): CPI for target year

    Returns:
        float: Inflation factor
    """
    if source_cpi <= 0:
        raise ValueError("Source CPI must be positive")
    return target_cpi / source_cpi


def validate_year_in_data(year, available_years):
    """
    Validate that a year exists in the dataset.

    Args:
        year (int): Year to validate
        available_years (list): List of available years

    Raises:
        ValueError: If year not in available years
    """
    if year not in available_years:
        raise ValueError(
            f"No CPI data for year {year}. "
            f"Available years: {min(available_years)}-{max(available_years)}"
        )


def get_year_range(cpi_lookup):
    """
    Get the range of years available in CPI data.

    Args:
        cpi_lookup (dict): Dictionary mapping years to CPI values

    Returns:
        tuple: (min_year, max_year)
    """
    years = sorted(cpi_lookup.keys())
    return (years[0], years[-1]) if years else (None, None)

"""
Data export and formatting functions
"""

def export_results_to_csv(result, filename='mvpf_results.csv'):
    """
    Export MVPF calculation results to CSV.

    Args:
        result (dict): MVPF calculation results
        filename (str): Output filename
    """
    df = pd.DataFrame([result])
    df['timestamp'] = datetime.now().isoformat()
    df.to_csv(filename, index=False)
    print(f"Results exported to {filename}")


def export_results_to_json(result, filename='mvpf_results.json'):
    """
    Export MVPF calculation results to JSON.

    Args:
        result (dict): MVPF calculation results
        filename (str): Output filename
    """
    result_with_timestamp = {
        **result,
        'timestamp': datetime.now().isoformat()
    }

    with open(filename, 'w') as f:
        json.dump(result_with_timestamp, f, indent=2)

    print(f"Results exported to {filename}")


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


def calculate_summary_statistics(results_df):
    """
    Calculate summary statistics from multiple MVPF calculations.

    Args:
        results_df (pandas.DataFrame): DataFrame with MVPF results

    Returns:
        dict: Summary statistics
    """
    if results_df.empty:
        return {}

    return {
        'mean_mvpf': results_df['mvpf'].mean(),
        'median_mvpf': results_df['mvpf'].median(),
        'min_mvpf': results_df['mvpf'].min(),
        'max_mvpf': results_df['mvpf'].max(),
        'std_mvpf': results_df['mvpf'].std()
    }


def format_currency(value):
    """
    Format value as currency string.

    Args:
        value (float): Numeric value

    Returns:
        str: Formatted currency string
    """
    return f"${int(value):,}"


def format_ratio(value, decimals=2):
    """
    Format value as ratio string.

    Args:
        value (float): Numeric value
        decimals (int): Number of decimal places

    Returns:
        str: Formatted ratio string
    """
    return f"{value:.{decimals}f}"



