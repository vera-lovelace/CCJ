"""
Constants for MVPF Calculator

This module contains shared constants used throughout the codebase.
"""

# ============================================================================
# COMPONENT TYPE CONSTANTS
# ============================================================================

COMPONENT_TYPES = ["detainee_values", "society_values", "govt_cost"]
DETAINEE_VALUES = "detainee_values"
SOCIETY_VALUES = "society_values"
GOVT_COST = "govt_cost"


# ============================================================================
# SCENARIO CONSTANTS
# ============================================================================

SCENARIO_BASELINE = "baseline"
SCENARIO_MOST_CONSERVATIVE = "most conservative"
SCENARIO_LEAST_CONSERVATIVE = "least conservative"


# ============================================================================
# MVPF CALCULATION CONSTANTS
# ============================================================================

INFINITE_MVPF = float('inf')  # Used when government cost is zero

# MVPF rating thresholds
MVPF_THRESHOLD_EXCELLENT = 2.5
MVPF_THRESHOLD_GOOD = 1.5
MVPF_THRESHOLD_FAIR = 1.0

# Neutral multiplier (no effect)
NEUTRAL_MULTIPLIER = 1.0

# Sign values
SIGN_POSITIVE = 1
SIGN_NEGATIVE = -1


# ============================================================================
# PARAMETER DEFAULTS
# ============================================================================

# Default parameter values (from parameters.py)
DEFAULT_LOS_DAYS = 70  # Average length of stay in days
DEFAULT_FEL_RATE = 0.7  # Default felony rate (70%)


# ============================================================================
# STRING/TEXT CONSTANTS
# ============================================================================

# String truncation lengths
MAX_DESCRIPTION_LENGTH = 40
TRUNCATED_SUFFIX_LENGTH = 3  # Length of "..." suffix
MAX_DESCRIPTION_DISPLAY = MAX_DESCRIPTION_LENGTH - TRUNCATED_SUFFIX_LENGTH  # 37


# ============================================================================
# NUMERICAL CONSTANTS
# ============================================================================

ZERO = 0  # Used for comparisons to avoid magic number 0

# Port numbers
DEFAULT_PORT = 8050


# ============================================================================
# UI/LAYOUT CONSTANTS
# ============================================================================

# Maximum width for main container
MAX_CONTAINER_WIDTH = 1280  # pixels

# Z-index values
Z_INDEX_TOOLTIP = 10000
Z_INDEX_MODAL = 1000
Z_INDEX_DROPDOWN = 100
Z_INDEX_BASE = 1


# ============================================================================
# STYLE PROPERTY CONSTANTS
# ============================================================================

# Common property values
FONT_WEIGHT_NORMAL = '400'
FONT_WEIGHT_MEDIUM = '500'
FONT_WEIGHT_SEMIBOLD = '600'
FONT_WEIGHT_BOLD = 'bold'

# Flexbox constants
FLEX_SHRINK_NONE = 0
FLEX_GROW_NONE = 0
FLEX_GROW_FULL = 1
