"""
MVPF Calculator Package
=======================

A comprehensive toolkit for calculating and visualizing the Marginal Value
of Public Funds (MVPF) for detention policies.

Modules:
    - mvpf_calculation: Core MVPF calculator class
    - helpers: Utility functions for CPI adjustments and data processing
    - content_loader: Content management for dashboard text
    - graphs: Visualization functions for MVPF results
    - dashboard: Interactive Dash dashboard application


    # Direct import:
    >>> import MVPFCalculator
    >>> calc = MVPFCalculator(baseline_type='baseline')
    >>> result = calc.calculate_mvpf()
    >>> print(result['mvpf'])

    # Content management:
    >>> import ContentManager
    >>> content = ContentManager()
    >>> print(content.get('header.title'))

    # Namespace import:
    >>> import helpers
    >>> helpers.adjust_value_by_cpi(100, 250, 275)

    # Benchmark creation:
    >>> from mvpf_benchmarks import create_mvpf_benchmarks
    >>> benchmarks_component = create_mvpf_benchmarks()


"""

__version__ = "0.2.0"
__author__ = "Adrienn J. Sinapis"

# Import submodules for namespace access (use relative imports)


# Main calculator (primary interface)
from mvpf_calculator import MVPFCalculator

# Constants
from constants import COMPONENT_TYPES, DETAINEE_VALUES, SOCIETY_VALUES, GOVT_COST

# Helper utilities
from helpers import (
    ResultsExporter,
    format_currency,
    format_mvpf,
    get_mvpf_rating
)

# Scenario management
from scenarios import ScenarioManager

# Content management
from content_loader import ContentManager
import graphs

__all__ = [
    # Main class
    'MVPFCalculator',

    # Constants
    'COMPONENT_TYPES',
    'DETAINEE_VALUES',
    'SOCIETY_VALUES',
    'GOVT_COST',

    # Helpers
    'ResultsExporter',
    'format_currency',
    'format_mvpf',
    'get_mvpf_rating',

    # Advanced
    'ScenarioManager',
    'ContentManager',
    'create_mvpf_benchmarks',
]