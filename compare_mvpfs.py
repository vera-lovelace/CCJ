"""
Comparison of MVPFs across different policies and interventions

Handles analytics and mvpf selection with plotting capabilities
"""

#in progress
import matplotlib.pyplot as plt
import numpy as np

# import mvpf_calculator and mvpf_comparisons table
from mvpf_calculator import MVPFCalculator

class MVPFComparison:
    """
    Compares MVPFs across different policies and interventions.
    """

    def __init__(self, calculator=None):
        """
        Initialize comparison with an MVPFCalculator instance.

        Args:
            calculator (MVPFCalculator): Instance of MVPFCalculator
        """
        self.calculator = calculator or MVPFCalculator()

    def compare_values(self, mvpf_list, params=None):
        """
        Compare MVPFs from a list of interventions.

        Args:
            mvpf_list (list): List of policy names and values to compare
            params (dict): Optional parameters for calculation

        Returns:
            dict: Comparison results with MVPF values
        """
        results = {}
        for policy in mvpf_list:
            result = self.calculator.calculate(scenario=policy, params=params)
            results[policy] = result['mvpf']
        return results

    def analyse_differences(self, comparison_results):
        """
        Analyse differences in MVPF values.

        Args:
            comparison_results (dict): Results from compare_values method

        Returns:
            dict: Analysis of differences
        """
        analysis = {}
        base_value = comparison_results.get('ccj', None)
        if base_value is None:
            raise ValueError("Base policy 'ccj' not found in comparison results.")

        for policy, mvpf in comparison_results.items():
            difference = mvpf - base_value
            analysis[policy] = {
                'mvpf': mvpf,
                'difference_from_ccj': difference,
                'percentage_change': (difference / base_value * 100) if base_value != 0 else float('inf')
            }
        return analysis

    def plot_comparison(self, comparison_results):
        """
        Plot comparison of MVPFs.

        Args:
            comparison_results (dict): Results from compare_values method
        """
        policies = list(comparison_results.keys())
        mvpf_values = list(comparison_results.values())

        plt.figure(figsize=(10, 6))
        bars = plt.bar(policies, mvpf_values, color='skyblue')
        plt.xlabel('Scenarios')
        plt.ylabel('MVPF Values')
        plt.title('MVPF Comparison Across Scenarios')
        plt.xticks(rotation=45)

        # Add value labels on top of bars
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 2), ha='center', va='bottom')

        plt.tight_layout()
        plt.show()

# Example usage
if __name__ == '__main__':
    comparison = MVPFComparison()
    policies_to_compare = ['ccj', 'policy_a', 'policy_b']
    results = comparison.compare_values(policies_to_compare)
    comparison.plot_comparison(results)