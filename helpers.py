"""
Utility functions for MVPF Dashboard
"""
import pandas as pd
import json
from datetime import datetime

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



