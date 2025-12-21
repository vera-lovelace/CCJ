"""
Constants for MVPF Calculator

This module contains shared constants used throughout the codebase.
"""

# Component type constants
COMPONENT_TYPES = ["detainee_values", "society_values", "govt_cost"]
DETAINEE_VALUES = "detainee_values"
SOCIETY_VALUES = "society_values"
GOVT_COST = "govt_cost"

# Scenario constants
SCENARIO_BASELINE = "baseline"
SCENARIO_MOST_CONSERVATIVE = "most conservative"
SCENARIO_LEAST_CONSERVATIVE = "least conservative"

# MVPF calculation constants
INFINITE_MVPF = float('inf')  # Used when government cost is zero
