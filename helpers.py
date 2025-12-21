"""
Utility functions for MVPF Dashboard
"""
import pandas as pd
import json
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


# ==================== FORMATTING HELPERS ====================

# Formatting functions are now imported from formatting.py module
# This ensures consistent formatting across the entire application