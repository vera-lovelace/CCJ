"""
Centralized formatting module for MVPF Dashboard
Contains all style constants, color definitions, and formatting functions
"""

# ============================================================================
# COLOR PALETTE
# ============================================================================

class Colors:
    """Color constants used throughout the dashboard"""

    # Primary colors
    PRIMARY_BLUE = '#3b82f6'
    PRIMARY_BLUE_DARK = '#2563eb'
    PRIMARY_BLUE_LIGHT = '#dbeafe'
    PRIMARY_BLUE_LIGHTER = '#eff6ff'

    # Navy/Dark colors
    NAVY_DARK = '#1e293b'
    NAVY_MEDIUM = '#1E3A5F'
    NAVY_LIGHT = '#1e3a8a'
    NAVY_LIGHTER = '#1e40af'

    # Teal/Accent
    TEAL_PRIMARY = '#2C5F6F'

    # Gray scale
    GRAY_50 = '#f9fafb'
    GRAY_100 = '#f8fafc'
    GRAY_200 = '#f1f5f9'
    GRAY_300 = '#e5e7eb'
    GRAY_400 = '#d1d5db'
    GRAY_500 = '#9ca3af'
    GRAY_600 = '#6b7280'
    GRAY_700 = '#64748b'
    GRAY_800 = '#4b5563'
    GRAY_900 = '#374151'
    GRAY_950 = '#334155'

    # Success colors (green)
    SUCCESS_GREEN = '#16a34a'
    SUCCESS_LIGHT = '#dcfce7'

    # Error/Warning colors (red)
    ERROR_RED = '#dc2626'
    ERROR_LIGHT = '#fee2e2'

    # Warning colors (yellow/amber)
    WARNING_YELLOW = '#ca8a04'
    WARNING_LIGHT = '#fef3c7'

    # Info colors (blue)
    INFO_BLUE = '#3b82f6'
    INFO_LIGHT = '#dbeafe'

    # Chart-specific colors
    CHART_EMERALD = '#10b981'
    CHART_SKY = '#0ea5e9'
    CHART_PURPLE = '#a855f7'
    CHART_AMBER = '#f59e0b'
    CHART_ROSE = '#f43f5e'
    CHART_INDIGO = '#6366f1'
    CHART_TEAL = '#14b8a6'
    CHART_ORANGE = '#f97316'

    # Additional grays
    GRAY_SLATE = '#64748b'

    # White
    WHITE = '#ffffff'


# ============================================================================
# FONT SIZES
# ============================================================================

class FontSizes:
    """Font size constants"""
    H1 = '32px'
    H2 = '28px'
    H2_5 = '22px'  # Intermediate size between H2 and H3
    H3 = '24px'
    H4 = '20px'
    H4_5 = '18px'  # Intermediate size between H4 and H5
    H5 = '16px'
    BODY = '14px'
    BODY_SM = '13px'  # Small body text
    LABEL = '12px'
    EXTRA_SMALL = '11px'
    SMALL = '10px'
    TINY = '8px'


# ============================================================================
# SPACING
# ============================================================================

class Spacing:
    """Spacing constants for margins and padding"""
    XXS = '3px'   # Extra extra small
    XS = '4px'
    SM = '8px'
    SM_PLUS = '10px'  # Non-standard, frequently used
    MD = '12px'
    MD_PLUS = '14px'  # Non-standard, frequently used
    LG = '16px'
    XL = '20px'
    XXL = '24px'
    XXXL = '32px'


# ============================================================================
# LINE HEIGHTS
# ============================================================================

class LineHeights:
    """Line height constants"""
    TIGHT = '1.2'
    NORMAL = '1.5'
    RELAXED = '1.6'
    LOOSE = '1.8'


# ============================================================================
# BORDER STYLES
# ============================================================================

class Borders:
    """Border width and style constants"""
    THIN = '1px'
    MEDIUM = '2px'
    THICK = '3px'
    EXTRA_THICK = '4px'
    SIDE_ACCENT = '6px'


# ============================================================================
# BORDER RADIUS
# ============================================================================

class BorderRadius:
    """Border radius constants for rounded corners"""
    NONE = '0'
    SM = '4px'
    MD = '6px'
    MD_PLUS = '8px'
    LG = '12px'
    XL = '16px'
    PILL = '9999px'  # Standardized pill shape
    CIRCLE = '50%'


# ============================================================================
# BOX SHADOWS
# ============================================================================

class BoxShadows:
    """Box shadow definitions for cards and elevated elements"""
    NONE = 'none'
    SM = '0 1px 2px rgba(0,0,0,0.05)'
    DEFAULT = '0 1px 3px rgba(0,0,0,0.1)'
    MD = '0 4px 6px rgba(0,0,0,0.1)'
    LG = '0 10px 15px rgba(0,0,0,0.1)'
    XL = '0 20px 25px rgba(0,0,0,0.1)'
    TOOLTIP = '0 4px 6px rgba(0,0,0,0.2)'
    INNER = 'inset 0 2px 4px rgba(0,0,0,0.06)'


# ============================================================================
# TRANSITIONS
# ============================================================================

class Transitions:
    """Transition definitions for animations"""
    FAST = '150ms ease-in-out'
    DEFAULT = '200ms ease-in-out'
    SLOW = '300ms ease-in-out'
    COLOR = 'color 200ms ease-in-out'
    BACKGROUND = 'background 200ms ease-in-out'
    ALL = 'all 200ms ease-in-out'


# ============================================================================
# MVPF RATING THRESHOLDS
# ============================================================================

class MVPFThresholds:
    """MVPF rating threshold values"""
    EXCELLENT = 2.5
    GOOD = 1.5
    FAIR = 1.0


# ============================================================================
# COMMON STYLE DICTIONARIES
# ============================================================================

class CommonStyles:
    """Reusable style dictionaries"""

    BODY_TEXT = {
        'fontSize': FontSizes.BODY,
        'color': Colors.GRAY_800,
        'lineHeight': LineHeights.LOOSE
    }

    HEADER_1 = {
        'fontSize': FontSizes.H1,
        'fontWeight': 'bold',
        'color': Colors.NAVY_DARK,
        'marginBottom': Spacing.LG
    }

    HEADER_2 = {
        'fontSize': FontSizes.H2,
        'fontWeight': 'bold',
        'color': Colors.NAVY_DARK,
        'marginBottom': Spacing.LG
    }

    HEADER_3 = {
        'fontSize': FontSizes.H3,
        'fontWeight': '600',
        'color': Colors.NAVY_DARK,
        'marginBottom': Spacing.MD
    }

    HEADER_4 = {
        'fontSize': FontSizes.H4,
        'fontWeight': '600',
        'color': Colors.GRAY_900,
        'marginBottom': Spacing.SM
    }

    HEADER_5 = {
        'fontSize': FontSizes.H5,
        'fontWeight': '600',
        'color': Colors.GRAY_900,
        'marginBottom': Spacing.SM
    }

    SMALL_TEXT = {
        'fontSize': FontSizes.SMALL,
        'color': Colors.GRAY_600,
        'lineHeight': LineHeights.NORMAL
    }

    LABEL_TEXT = {
        'fontSize': FontSizes.LABEL,
        'color': Colors.GRAY_600,
        'fontWeight': '500'
    }

    CARD_CONTAINER = {
        'background': Colors.WHITE,
        'padding': Spacing.XL,
        'borderRadius': '8px',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
        'marginBottom': Spacing.XXL
    }

    BUTTON_PRIMARY = {
        'background': Colors.PRIMARY_BLUE,
        'color': Colors.WHITE,
        'padding': f'{Spacing.SM} {Spacing.LG}',
        'border': 'none',
        'borderRadius': '4px',
        'cursor': 'pointer'
    }

    INPUT_FIELD = {
        'border': f'{Borders.THIN} solid {Colors.GRAY_300}',
        'borderRadius': '4px',
        'padding': Spacing.SM
    }

    INPUT_FIELD_FOCUSED = {
        'border': f'{Borders.MEDIUM} solid {Colors.PRIMARY_BLUE}',
        'outline': 'none'
    }

    # Badge/Pill styles
    BADGE_PRIMARY = {
        'display': 'inline-block',
        'padding': f'{Spacing.XS} {Spacing.MD}',
        'borderRadius': BorderRadius.PILL,
        'fontSize': FontSizes.LABEL,
        'fontWeight': '600',
        'backgroundColor': Colors.PRIMARY_BLUE,
        'color': Colors.WHITE
    }

    BADGE_SUCCESS = {
        'display': 'inline-block',
        'padding': f'{Spacing.XS} {Spacing.MD}',
        'borderRadius': BorderRadius.PILL,
        'fontSize': FontSizes.LABEL,
        'fontWeight': '600',
        'backgroundColor': Colors.SUCCESS_GREEN,
        'color': Colors.WHITE
    }

    BADGE_WARNING = {
        'display': 'inline-block',
        'padding': f'{Spacing.XS} {Spacing.MD}',
        'borderRadius': BorderRadius.PILL,
        'fontSize': FontSizes.LABEL,
        'fontWeight': '600',
        'backgroundColor': Colors.WARNING_YELLOW,
        'color': Colors.WHITE
    }

    BADGE_ERROR = {
        'display': 'inline-block',
        'padding': f'{Spacing.XS} {Spacing.MD}',
        'borderRadius': BorderRadius.PILL,
        'fontSize': FontSizes.LABEL,
        'fontWeight': '600',
        'backgroundColor': Colors.ERROR_RED,
        'color': Colors.WHITE
    }

    # Tooltip style
    TOOLTIP = {
        'position': 'absolute',
        'backgroundColor': Colors.GRAY_900,
        'color': Colors.WHITE,
        'padding': Spacing.SM,
        'borderRadius': BorderRadius.MD,
        'fontSize': FontSizes.BODY_SM,
        'boxShadow': BoxShadows.TOOLTIP,
        'zIndex': '10000'
    }

    # Info tile
    INFO_TILE = {
        'backgroundColor': Colors.WHITE,
        'padding': Spacing.LG,
        'borderRadius': BorderRadius.MD_PLUS,
        'boxShadow': BoxShadows.DEFAULT,
        'marginBottom': Spacing.LG
    }

    # Control section
    CONTROL_SECTION = {
        'backgroundColor': Colors.WHITE,
        'padding': Spacing.XL,
        'borderRadius': BorderRadius.MD_PLUS,
        'marginBottom': Spacing.XL
    }

    # Chart container
    CHART_CONTAINER = {
        'backgroundColor': Colors.WHITE,
        'borderRadius': BorderRadius.MD_PLUS,
        'padding': Spacing.XL,
        'boxShadow': BoxShadows.DEFAULT
    }

    # Flex row
    FLEX_ROW = {
        'display': 'flex',
        'flexDirection': 'row',
        'alignItems': 'center'
    }

    # Flex column
    FLEX_COLUMN = {
        'display': 'flex',
        'flexDirection': 'column'
    }

    # Flex space between
    FLEX_SPACE_BETWEEN = {
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center'
    }

    # Full width
    FULL_WIDTH = {
        'width': '100%'
    }

    # Text center
    TEXT_CENTER = {
        'textAlign': 'center'
    }

    # Text right
    TEXT_RIGHT = {
        'textAlign': 'right'
    }


# ============================================================================
# FORMATTING FUNCTIONS
# ============================================================================

def format_currency(value):
    """
    Format value as currency string.

    Args:
        value: Numeric value to format

    Returns:
        str: Formatted currency string (e.g., "$1,234,567")
    """
    return f"${int(value):,}"


def format_ratio(value, decimals=2):
    """
    Format value as ratio string.

    Args:
        value (float): Numeric value
        decimals (int): Number of decimal places (default: 2)

    Returns:
        str: Formatted ratio string
    """
    return f"{value:.{decimals}f}"


def format_mvpf(value):
    """
    Format MVPF score with proper handling of infinity.

    Args:
        value: MVPF numeric value

    Returns:
        str: Formatted MVPF string (returns ∞ for infinity)
    """
    if value == float('inf'):
        return "∞"
    return f"{value:.2f}"


def get_mvpf_rating(mvpf):
    """
    Get rating and color for MVPF score based on threshold values.

    Args:
        mvpf (float): MVPF score value

    Returns:
        tuple: (rating_string, color_hex)
            - rating_string: One of 'Excellent', 'Good', 'Fair', 'Poor'
            - color_hex: Corresponding color code
    """
    if mvpf >= MVPFThresholds.EXCELLENT:
        return 'Excellent', Colors.SUCCESS_GREEN
    elif mvpf >= MVPFThresholds.GOOD:
        return 'Good', Colors.PRIMARY_BLUE_DARK
    elif mvpf >= MVPFThresholds.FAIR:
        return 'Fair', Colors.WARNING_YELLOW
    else:
        return 'Poor', Colors.ERROR_RED


def format_percentage(value, decimals=1):
    """
    Format value as percentage string.

    Args:
        value (float): Numeric value (0.0 to 1.0)
        decimals (int): Number of decimal places (default: 1)

    Returns:
        str: Formatted percentage string (e.g., "45.2%")
    """
    return f"{value * 100:.{decimals}f}%"


def format_number(value, decimals=0):
    """
    Format number with comma separators.

    Args:
        value: Numeric value
        decimals (int): Number of decimal places (default: 0)

    Returns:
        str: Formatted number string with commas
    """
    if decimals == 0:
        return f"{int(value):,}"
    return f"{value:,.{decimals}f}"


# ============================================================================
# GRADIENT HELPERS
# ============================================================================

class Gradients:
    """Gradient background definitions"""

    LIGHT_GRAY = f'linear-gradient(to bottom right, {Colors.GRAY_100}, {Colors.GRAY_200})'

    @staticmethod
    def custom(color1, color2, direction='to bottom right'):
        """Create a custom gradient"""
        return f'linear-gradient({direction}, {color1}, {color2})'


# ============================================================================
# CHART COLOR PALETTES
# ============================================================================

class ChartColors:
    """Component-specific color palettes for charts and visualizations"""

    # Primary chart palette (for main data series)
    PRIMARY_PALETTE = [
        Colors.CHART_SKY,      # Blue
        Colors.CHART_EMERALD,  # Green
        Colors.CHART_PURPLE,   # Purple
        Colors.CHART_AMBER,    # Amber/Orange
        Colors.CHART_ROSE,     # Rose/Pink
        Colors.CHART_INDIGO,   # Indigo
        Colors.CHART_TEAL,     # Teal
        Colors.CHART_ORANGE    # Orange
    ]

    # Sequential palette (for gradients/heatmaps)
    SEQUENTIAL_BLUE = [
        '#eff6ff',  # Lightest
        '#dbeafe',
        '#bfdbfe',
        '#93c5fd',
        '#60a5fa',
        '#3b82f6',
        '#2563eb',
        '#1d4ed8',
        '#1e40af'   # Darkest
    ]

    # Diverging palette (for positive/negative comparisons)
    DIVERGING_PALETTE = [
        Colors.ERROR_RED,      # Negative
        '#f87171',
        '#fca5a5',
        Colors.GRAY_300,       # Neutral
        '#93c5fd',
        '#60a5fa',
        Colors.PRIMARY_BLUE    # Positive
    ]

    # MVPF-specific colors
    MVPF_EXCELLENT = Colors.SUCCESS_GREEN
    MVPF_GOOD = Colors.CHART_EMERALD
    MVPF_FAIR = Colors.WARNING_YELLOW
    MVPF_POOR = Colors.ERROR_RED

    # Component breakdown colors
    NUMERATOR_COLOR = Colors.CHART_EMERALD
    DENOMINATOR_COLOR = Colors.CHART_AMBER
    DETAINEE_VALUE = Colors.CHART_SKY
    SOCIETY_VALUE = Colors.CHART_PURPLE
    GOVERNMENT_COST = Colors.CHART_ROSE

    # Sensitivity analysis colors
    SENSITIVITY_BASE = Colors.GRAY_500
    SENSITIVITY_VARIATION = Colors.CHART_SKY
    SENSITIVITY_HIGHLIGHT = Colors.PRIMARY_BLUE_DARK


# ============================================================================
# QUICK ACCESS DICTIONARIES (for backward compatibility)
# ============================================================================

# Legacy font sizes dict for easy migration
FONT_SIZES = {
    'h1': FontSizes.H1,
    'h2': FontSizes.H2,
    'h3': FontSizes.H3,
    'h4': FontSizes.H4,
    'body': FontSizes.BODY,
    'small': FontSizes.SMALL,
    'label': FontSizes.LABEL
}

# Legacy style dicts for easy migration
BODY_TEXT_STYLE = CommonStyles.BODY_TEXT
HEADER_2_STYLE = CommonStyles.HEADER_2