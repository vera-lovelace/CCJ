"""
MVPF Calculator Package
=======================

A comprehensive toolkit for calculating and visualizing the Marginal Value
of Public Funds (MVPF) for detention policies.

Modules:
    - mvpf_calculation: Core MVPF calculator class
    - helpers: Utility functions for CPI adjustments and data processing
    - graphs: Visualization functions for MVPF results
    - dashboard: Interactive Dash dashboard application

Example:
    # Direct import:
    >>> from mvpf_package import MVPFCalculator
    >>> calc = MVPFCalculator(baseline_type='baseline')
    >>> result = calc.calculate_mvpf()
    >>> print(result['mvpf'])

    # Namespace import
     >>>from mvpf_package import helpers
     >>>helpers.adjust_value_by_cpi(100, 250, 275)

    # Or
     >>>import mvpf_package
     >>>calc = mvpf_package.MVPFCalculator()
"""

__version__ = "0.1.0"
__author__ = "Your Name"

# Import submodules for namespace access
import helpers
import graphs
import mvpf_calculation

# Import main class for convenience
from mvpf_calculation import MVPFCalculator

# Define what gets imported with "from package import *"
__all__ = [
    'MVPFCalculator',
    'helpers',
    'graphs',
    'mvpf_calculation',
]