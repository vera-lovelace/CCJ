"""
MVPF Dashboard Application
Main dashboard layout and callbacks
"""

import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import global components
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd
import csv
import io

# Import local components
from content_loader import ContentManager
from mvpf_calculator import MVPFCalculator
from parameters import ParameterRegistry
from formatting import (
    Colors,
    FontSizes,
    Spacing,
    LineHeights,
    Borders,
    BorderRadius,
    CommonStyles,
    Gradients,
    format_currency,
    format_mvpf,
    get_mvpf_rating,
    FONT_SIZES,
    BODY_TEXT_STYLE,
    HEADER_2_STYLE,
)


def load_benchmarks(data_dir="Data"):
    """Load benchmark comparison data from CSV file."""
    filepath = os.path.join(data_dir, "mvpf_comparisons.csv")
    df = pd.read_csv(filepath)
    return df.to_dict("records")


# Initialize content manager
content = ContentManager()

# Initialize calculator once (singleton pattern for performance)
calculator = MVPFCalculator(data_dir="Data")

# Initialize parameter registry to get CSV-based dropdown options
param_registry = ParameterRegistry(data_dir="Data")

# Load benchmarks once at startup and cache
benchmarks = load_benchmarks()

# Get parameter definitions for dropdown generation
fel_rate_param = param_registry.params["fel_rate"]
los_days_param = param_registry.params["los_days"]
n_detainees_param = param_registry.params["n_detainees_mult"]
n_detainees_base_param = param_registry.params["n_detainees_base"]
n_society_param = param_registry.params["n_society_mult"]

# Build dropdown options from CSV weights
FEL_RATE_OPTIONS = [
    {"label": f"Below Average ({fel_rate_param.dropdown_map['below']:.0%})", "value": "below"},
    {"label": f"Average ({fel_rate_param.dropdown_map['average']:.0%})", "value": "average"},
    {"label": f"Above Average ({fel_rate_param.dropdown_map['above']:.0%})", "value": "above"},
]

LOS_DAYS_OPTIONS = [
    {"label": f"Short ({los_days_param.dropdown_map['below']:.0f} days)", "value": "below"},
    {"label": f"Average ({los_days_param.dropdown_map['average']:.0f} days)", "value": "average"},
    {"label": f"Long ({los_days_param.dropdown_map['above']:.0f} days)", "value": "above"},
]

N_DETAINEES_OPTIONS = [
    {"label": f"Below Average ({n_detainees_param.dropdown_map['below']:.0%})", "value": "below"},
    {"label": f"Average ({n_detainees_param.dropdown_map['average']:.0%})", "value": "average"},
    {"label": f"Above Average ({n_detainees_param.dropdown_map['above']:.0%})", "value": "above"},
]

N_SOCIETY_OPTIONS = [
    {"label": f"Below Average ({n_society_param.dropdown_map['below']:.0%})", "value": "below"},
    {"label": f"Average ({n_society_param.dropdown_map['average']:.0%})", "value": "average"},
    {"label": f"Above Average ({n_society_param.dropdown_map['above']:.0%})", "value": "above"},
]

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Custom CSS for styling
app.index_string = f"""
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <style>
            body {{
                font-family: system-ui, -apple-system, sans-serif;
                margin: 0;
                background: linear-gradient(to bottom right, {Colors.GRAY_100}, {Colors.GRAY_200});
            }}
            .main-container {{
                max-width: 1280px;
                margin: 0 auto;
                padding: {Spacing.XXL};
            }}
            .sidebar {{
                background: {Colors.TEAL_PRIMARY};
                border-radius: 8px;
                padding: {Spacing.XL};
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                margin-bottom: {Spacing.XXL};
            }}
            .info-tile {{
                background: {Colors.PRIMARY_BLUE_LIGHTER};
                border-left: {Borders.EXTRA_THICK} solid {Colors.PRIMARY_BLUE};
                padding: {Spacing.LG};
                border-radius: 8px;
                margin-bottom: {Spacing.XXL};
            }}
            .info-tile h3 {{
                color: {Colors.NAVY_LIGHT};
                font-weight: 600;
                margin: 0 0 {Spacing.SM} 0;
                font-size: {FontSizes.H5};
            }}
            .info-tile p, .info-tile ul {{
                color: {Colors.NAVY_LIGHTER};
                font-size: {FontSizes.BODY};
                line-height: {LineHeights.NORMAL};
                margin: {Spacing.SM} 0;
            }}
            .info-tile ul {{
                margin-left: {Spacing.SM};
                padding-left: 0;
            }}
            .info-tile li {{
                font-size: {FontSizes.LABEL};
                margin: {Spacing.XS} 0;
            }}
            .info-tile strong {{
                font-weight: 600;
            }}
            .control-section h3 {{
                font-weight: 600;
                color: {Colors.NAVY_DARK};
                margin: 0 0 {Spacing.MD} 0;
                font-size: {FontSizes.H5};
            }}
            .control-group {{
                margin-bottom: {Spacing.LG};
            }}
            .control-label {{
                display: block;
                font-size: {FontSizes.BODY};
                font-weight: 500;
                color: {Colors.GRAY_900};
                margin-bottom: {Spacing.SM};
            }}
            .label-with-info {{
                display: flex;
                align-items: center;
                gap: 6px;
                margin-bottom: {Spacing.SM};
            }}
            .info-icon {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: {Spacing.LG};
                height: {Spacing.LG};
                border-radius: 50%;
                background: {Colors.PRIMARY_BLUE};
                color: white;
                font-size: 11px;
                font-weight: 600;
                cursor: pointer;
                flex-shrink: 0;
                position: relative;
                z-index: 1;
            }}
            .info-icon:hover {{
                z-index: 10000;
            }}
            .info-icon:hover::after {{
                content: attr(data-tooltip);
                position: absolute;
                left: {Spacing.XXL};
                top: 50%;
                transform: translateY(-50%);
                background: {Colors.NAVY_DARK};
                color: white;
                padding: {Spacing.SM} {Spacing.MD};
                border-radius: 6px;
                font-size: {FontSizes.LABEL};
                font-weight: 400;
                line-height: 1.4;
                width: 220px;
                z-index: 1000;
                box-shadow: 0 4px 6px rgba(0,0,0,0.2);
                white-space: normal;
            }}
            .info-icon:hover::before {{
                content: '';
                position: absolute;
                left: {Spacing.XL};
                top: 50%;
                transform: translateY(-50%);
                width: 0;
                height: 0;
                border-top: 6px solid transparent;
                border-bottom: 6px solid transparent;
                border-right: 6px solid {Colors.NAVY_DARK};
                z-index: 10002;
            }}
            .Select-control, .dash-dropdown {{
                font-size: {FontSizes.BODY} !important;
            }}
            .baseline-switch {{
                background: white;
                border-radius: 8px;
                padding: {Spacing.LG};
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                margin-bottom: {Spacing.XXL};
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .baseline-label {{
                font-size: {FontSizes.BODY};
                font-weight: 500;
                color: {Colors.GRAY_900};
            }}
            .button-group {{
                display: flex;
                gap: {Spacing.SM};
            }}
            .baseline-button {{
                padding: {Spacing.SM} {Spacing.LG};
                border-radius: 8px;
                font-size: {FontSizes.BODY};
                font-weight: 500;
                cursor: pointer;
                border: none;
                transition: all 0.2s;
            }}
            .baseline-button-active {{
                background: {Colors.PRIMARY_BLUE_DARK};
                color: white;
            }}
            .baseline-button-inactive {{
                background: {Colors.GRAY_300};
                color: {Colors.GRAY_900};
            }}
            .baseline-button-inactive:hover {{
                background: {Colors.GRAY_400};
            }}
            .kpi-card {{
                background: {Colors.NAVY_MEDIUM};
                border-radius: 8px;
                padding: {Spacing.XXXL};
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: {Spacing.XXL};
            }}
            .kpi-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: {Spacing.LG};
            }}
            .kpi-title {{
                font-size: {FontSizes.H3};
                font-weight: 600;
                color: white;
                text-align: center;
            }}
            .kpi-badge {{
                padding: {Spacing.XS} {Spacing.MD};
                border-radius: 9999px;
                font-size: {FontSizes.BODY};
                font-weight: 600;
            }}
            .kpi-value {{
                font-size: 60px;
                font-weight: bold;
                color: white;
                line-height: 1;
                margin-bottom: {Spacing.XXL};
                text-align: center;
            }}
            .kpi-ratio {{
                font-size: {FontSizes.H3};
                color: {Colors.GRAY_600};
                margin-left: {Spacing.SM};
                textAlign: center;
            }}
            .kpi-components {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: {Spacing.LG};
                margin: {Spacing.XXL} 0;
            }}
            .kpi-component {{
                background: {Colors.GRAY_50};
                border-radius: 12px;
                padding: {Spacing.XL};
                border: {Borders.MEDIUM} solid {Colors.GRAY_300};
                transition: all 0.2s;
            }}
            .kpi-component:hover {{
                border-color: {Colors.PRIMARY_BLUE};
                box-shadow: 0 4px 6px rgba(59, 130, 246, 0.1);
            }}
            .kpi-component-link {{
                text-decoration: none;
                color: inherit;
                display: block;
            }}
            .kpi-component h4 {{
                font-size: 13px;
                color: {Colors.GRAY_600};
                margin: 0 0 {Spacing.MD} 0;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .kpi-component-link h4 {{
                color: {Colors.PRIMARY_BLUE};
                cursor: pointer;
            }}
            .kpi-component-link:hover h4 {{
                text-decoration: underline;
            }}
            .kpi-component p {{
                font-size: 28px;
                font-weight: 700;
                margin: 0 0 {Spacing.SM} 0;
                line-height: 1;
            }}
            .kpi-component span {{
                font-size: {FontSizes.LABEL};
                color: {Colors.GRAY_500};
                font-weight: 400;
            }}
            .kpi-calculation {{
                margin-top: {Spacing.XXL};
                padding-top: {Spacing.XXL};
                border-top: {Borders.THIN} solid {Colors.GRAY_300};
                font-size: 13px;
                color: {Colors.GRAY_600};
            }}
            .kpi-interpretation {{
                margin-top: {Spacing.XXL};
                padding: {Spacing.LG};
                background: {Colors.GRAY_50};
                border-radius: 8px;
            }}
            .kpi-interpretation p {{
                color: {Colors.GRAY_900};
                font-size: {FontSizes.BODY};
                margin: 0;
                line-height: {LineHeights.NORMAL};
            }}
            .chart-container {{
                background: white;
                border-radius: 8px;
                padding: {Spacing.XXL};
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                margin-bottom: {Spacing.XXL};
            }}
            .loading-text {{
                font-size: {Spacing.XXXL};
                color: {Colors.GRAY_500};
            }}
            .jumbotron {{
                background: white;
                border-radius: 12px;
                padding: {Spacing.XXL};
                box-shadow: 0 4px 6px rgba(0,0,0,0.07);
                border: {Borders.THIN} solid {Colors.GRAY_300};
                transition: all 0.2s ease;
            }}
            .jumbotron:hover {{
                box-shadow: 0 8px 12px rgba(0,0,0,0.1);
                border-color: {Colors.PRIMARY_BLUE};
            }}
            .jumbotron-icon {{
                width: 48px;
                height: 48px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: {FontSizes.H3};
                margin-bottom: {Spacing.LG};
            }}
            .jumbotron-title {{
                font-size: {FontSizes.BODY};
                font-weight: 600;
                color: {Colors.GRAY_900};
                margin: 0 0 {Spacing.XS} 0;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .jumbotron-value {{
                font-size: 28px;
                font-weight: 700;
                color: {Colors.NAVY_DARK};
                margin: 0 0 {Spacing.SM} 0;
                line-height: {LineHeights.TIGHT};
            }}
            .jumbotron-description {{
                font-size: {FontSizes.LABEL};
                color: {Colors.GRAY_600};
                margin: 0 0 {Spacing.LG} 0;
                line-height: 1.4;
            }}
            .jumbotron-grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: {Spacing.LG};
                margin-bottom: {Spacing.XXL};
            }}
            @media (max-width: 1200px) {{
                .jumbotron-grid {{
                    grid-template-columns: repeat(2, 1fr);
                }}
            }}
            @media (max-width: 768px) {{
                .jumbotron-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
            .benchmark-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: {Spacing.MD};
                margin-top: {Spacing.LG};
            }}
            @media (max-width: 900px) {{
                .benchmark-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
            .benchmark-tile {{
                background: {Colors.GRAY_50};
                border-radius: 8px;
                padding: {Spacing.LG};
                border: {Borders.THIN} solid {Colors.GRAY_300};
                transition: all 0.2s ease;
            }}
            .benchmark-tile:hover {{
                border-color: {Colors.PRIMARY_BLUE};
                box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
            }}
            .benchmark-tile-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: {Spacing.SM};
            }}
            .benchmark-tile-value {{
                font-size: {FontSizes.H3};
                font-weight: 700;
                line-height: 1;
            }}
            .benchmark-tile-value.positive {{
                color: {Colors.SUCCESS_GREEN};
            }}
            .benchmark-tile-value.negative {{
                color: {Colors.ERROR_RED};
            }}
            .benchmark-tile-comparison {{
                font-size: {FontSizes.LABEL};
                font-weight: 600;
                padding: {Spacing.XS} {Spacing.SM};
                border-radius: 9999px;
            }}
            .benchmark-tile-comparison.better {{
                background: {Colors.SUCCESS_LIGHT};
                color: {Colors.SUCCESS_GREEN};
            }}
            .benchmark-tile-comparison.worse {{
                background: {Colors.ERROR_LIGHT};
                color: {Colors.ERROR_RED};
            }}
            .benchmark-tile-name {{
                font-size: 13px;
                font-weight: 500;
                color: {Colors.GRAY_900};
                margin-bottom: {Spacing.XS};
                line-height: 1.3;
            }}
            .benchmark-tile-link {{
                font-size: 11px;
                color: {Colors.PRIMARY_BLUE};
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                gap: {Spacing.XS};
            }}
            .benchmark-tile-link:hover {{
                text-decoration: underline;
            }}
            .landing-nav-card:hover {{
                border-color: {Colors.PRIMARY_BLUE} !important;
                box-shadow: 0 8px 16px rgba(59, 130, 246, 0.2) !important;
                transform: translateY(-4px);
            }}
            /* Left Sidebar Navigation */
            .app-container {{
                display: flex;
                min-height: 100vh;
                background: linear-gradient(to bottom right, {Colors.GRAY_100}, {Colors.GRAY_200});
            }}
            .left-sidebar {{
                width: 240px;
                background: {Colors.NAVY_MEDIUM};
                box-shadow: 2px 0 8px rgba(0,0,0,0.1);
                position: fixed;
                left: 0;
                top: 0;
                height: 100vh;
                overflow-y: auto;
                z-index: 1000;
                padding: {Spacing.XXL} 0;
            }}
            .sidebar-header {{
                padding: 0 {Spacing.XL} {Spacing.XL} {Spacing.XL};
                border-bottom: {Borders.THIN} solid {Colors.GRAY_300};
                margin-bottom: {Spacing.XL};
            }}
            .sidebar-header h2 {{
                font-size: 18px;
                font-weight: 700;
                color: {Colors.NAVY_DARK};
                margin: 0 0 {Spacing.XS} 0;
            }}
            .sidebar-header p {{
                font-size: {FontSizes.LABEL};
                color: {Colors.GRAY_700};
                margin: 0;
            }}
            .nav-menu {{
                list-style: none;
                margin: 0;
                padding: 0;
            }}
            .nav-item {{
                margin: 0;
            }}
            .nav-button {{
                display: flex;
                align-items: center;
                width: 100%;
                padding: {Spacing.MD} {Spacing.XL};
                border: none;
                background: transparent;
                color: {Colors.GRAY_700};
                font-size: {FontSizes.BODY};
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                text-align: left;
                gap: {Spacing.MD};
            }}
            .nav-button:hover {{
                background: {Colors.GRAY_100};
                color: {Colors.NAVY_MEDIUM};
            }}
            .nav-button.active {{
                background: {Colors.PRIMARY_BLUE_LIGHTER};
                color: {Colors.PRIMARY_BLUE_DARK};
                border-right: 3px solid {Colors.PRIMARY_BLUE_DARK};
                font-weight: 600;
            }}
            .nav-icon {{
                font-size: 18px;
                width: {Spacing.XXL};
                text-align: center;
            }}
            .main-content {{
                margin-left: 240px;
                flex: 1;
                padding: {Spacing.XXL};
                max-width: calc(100% - 240px);
            }}
            @media (max-width: 768px) {{
                .left-sidebar {{
                    width: 200px;
                }}
                .main-content {{
                    margin-left: 200px;
                    max-width: calc(100% - 200px);
                }}
            }}
            /* Hide the horizontal tabs navigation bar */
            .custom-tabs-container .tabs__container {{
                display: none !important;
            }}
            .custom-tabs > div:first-child {{
                display: none !important;
            }}
             .custom-tabs .tab {{
                display: none !important;
            }}

        </style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
"""

# Layout
app.layout = html.Div(
    className="app-container",
    children=[
        # Store component for active tab tracking
        dcc.Store(id="active-tab-store", data="tab-landing"),
        # Left Sidebar Navigation
        html.Div(
            className="left-sidebar",
            children=[
                html.Div(
                    className="sidebar-header",
                    children=[
                        html.H2(
                            content.get("header.title", "MVPF Analysis Dashboard"),
                            style={
                                "fontSize": FontSizes.H3,
                                "fontWeight": "700",
                                "color": "white",
                                "margin": f"0 0 {Spacing.SM} 0",
                            },
                        ),
                        html.P(
                            content.get(
                                "header.subtitle", "Marginal Value of Public Funds Calculation"
                            ),
                            style={
                                "fontSize": FontSizes.LABEL,
                                "color": "white",
                                "margin": f"0 0 {Spacing.LG} 0",
                                "lineHeight": "1.4",
                            },
                        ),
                    ],
                ),
                html.Nav(
                    className="nav-menu",
                    children=[
                        html.Div(
                            className="nav-item",
                            children=[
                                html.Button(
                                    content.get("navigation.home", "Home"),
                                    id="nav-home",
                                    n_clicks=0,
                                    className="nav-button active",
                                )
                            ],
                        ),
                        html.Div(
                            className="nav-item",
                            children=[
                                html.Button(
                                    content.get("tabs.overview", "Calculations"),
                                    id="nav-overview",
                                    n_clicks=0,
                                    className="nav-button",
                                )
                            ],
                        ),
                        html.Div(
                            className="nav-item",
                            children=[
                                html.Button(
                                    content.get("tabs.scenarios", "Compare Scenarios"),
                                    id="nav-scenarios",
                                    n_clicks=0,
                                    className="nav-button",
                                )
                            ],
                        ),
                        html.Div(
                            className="nav-item",
                            children=[
                                html.Button(
                                    content.get("navigation.benchmarking", "View Benchmarks"),
                                    id="nav-benchmarking",
                                    n_clicks=0,
                                    className="nav-button",
                                )
                            ],
                        ),
                        html.Div(
                            className="nav-item",
                            children=[
                                html.Button(
                                    content.get("navigation.mvpf_explained", "MVPF Explained"),
                                    id="nav-descriptions",
                                    n_clicks=0,
                                    className="nav-button",
                                )
                            ],
                        ),
                        html.Div(
                            className="nav-item",
                            children=[
                                html.Button(
                                    content.get("navigation.about", "About"),
                                    id="nav-about",
                                    n_clicks=0,
                                    className="nav-button",
                                )
                            ],
                        ),
                    ],
                ),
            ],
        ),
        # Main Content Area
        html.Div(
            className="main-content",
            children=[
                # Tabs Container (headers hidden, controlled by sidebar)
                dcc.Tabs(
                    id="main-tabs",
                    value="tab-landing",
                    parent_className="custom-tabs-container",
                    className="custom-tabs",
                    children=[
                        # Tab 0: Landing Page
                        dcc.Tab(
                            label="Home",
                            value="tab-landing",
                            style={
                                "padding": f"{Spacing.MD} {Spacing.XL}",
                                "fontWeight": "500",
                                "fontSize": FontSizes.BODY,
                            },
                            selected_style={
                                "padding": f"{Spacing.MD} {Spacing.XL}",
                                "fontWeight": "600",
                                "fontSize": FontSizes.BODY,
                                "borderTop": f"{Borders.THICK} solid {Colors.PRIMARY_BLUE}",
                                "backgroundColor": "white",
                            },
                            children=[
                                html.Div(
                                    style={
                                        "padding": f"48px {Spacing.XL}",
                                        "maxWidth": "900px",
                                        "margin": "0 auto",
                                    },
                                    children=[
                                        # Title
                                        html.H1(
                                            content.get(
                                                "landing.welcome_title",
                                                "Welcome to the MVPF Analysis Dashboard",
                                            ),
                                            style={
                                                "fontSize": "36px",
                                                "fontWeight": "bold",
                                                "color": Colors.NAVY_DARK,
                                                "marginBottom": Spacing.XL,
                                                "textAlign": "center",
                                            },
                                        ),
                                        # Purpose section
                                        html.Div(
                                            style={"marginBottom": Spacing.LG},
                                            children=[
                                                html.H3(
                                                    content.get("understanding.purpose.title", ""),
                                                    style={
                                                        "fontSize": FontSizes.H4,
                                                        "fontWeight": "600",
                                                        "color": Colors.GRAY_900,
                                                        "marginTop": "0",
                                                        "marginBottom": Spacing.MD,
                                                        "textAlign": "center",
                                                    },
                                                ),
                                                html.P(
                                                    content.get(
                                                        "understanding.purpose.description",
                                                        "This interactive dashboard provides a comprehensive analysis of the Marginal Value of Public Funds (MVPF) "
                                                        "for Cook County Jail operations. ",
                                                    ),
                                                    style={
                                                        "fontSize": FontSizes.H5,
                                                        "color": Colors.GRAY_800,
                                                        "lineHeight": LineHeights.LOOSE,
                                                        "margin": "0",
                                                        "padding": Spacing.LG,
                                                        "borderRadius": "0px",
                                                        "marginBottom": "12px",
                                                    },
                                                ),
                                                html.P(
                                                    "The MVPF measures the social welfare benefit of a policy per dollar of government spending. The below interactive MVPF calculator helps policymakers and researchers understand the tradeoffs involved in pretrial detention by quantifying both costs and benefits in a common framework. We use Cook County Jail in 2018 as our base case.",
                                                    style={
                                                        "fontSize": FontSizes.H5,
                                                        "color": Colors.GRAY_800,
                                                        "lineHeight": LineHeights.LOOSE,
                                                        "margin": "0",
                                                        "padding": Spacing.LG,
                                                        "borderRadius": "0px",
                                                        "marginBottom": "12px",
                                                    },
                                                ),
                                            ],
                                        ),
                                        # Description
                                        html.Div(
                                            style={
                                                "padding": Spacing.XXXL,
                                                "borderRadius": "0px",
                                                "marginBottom": "48px",
                                            },
                                            children=[
                                                html.P(
                                                    "Use the tabs below to explore different aspects of the analysis, from high-level overview to detailed scenario comparisons and benchmarking against other government programs.",
                                                    style={
                                                        "fontSize": FontSizes.H5,
                                                        "color": Colors.GRAY_950,
                                                        "lineHeight": LineHeights.LOOSE,
                                                        "margin": "0",
                                                    },
                                                )
                                            ],
                                        ),
                                        # Navigation Cards
                                        html.H2(
                                            content.get(
                                                "landing.explore_heading", "Explore the Dashboard"
                                            ),
                                            style={
                                                "fontSize": FontSizes.H3,
                                                "fontWeight": "600",
                                                "color": Colors.NAVY_DARK,
                                                "marginBottom": Spacing.XXL,
                                                "textAlign": "center",
                                            },
                                        ),
                                        html.Div(
                                            style={
                                                "display": "grid",
                                                "gridTemplateColumns": "1fr 1fr 1fr",
                                                "gap": Spacing.XXL,
                                            },
                                            children=[
                                                # Card 1: Overview
                                                html.A(
                                                    href="#",
                                                    id="link-to-overview",
                                                    style={"textDecoration": "none"},
                                                    children=[
                                                        html.Div(
                                                            style={
                                                                "backgroundColor": "white",
                                                                "padding": Spacing.XXXL,
                                                                "borderRadius": "12px",
                                                                "boxShadow": "0 4px 6px rgba(0,0,0,0.1)",
                                                                "border": f"{Borders.MEDIUM} solid transparent",
                                                                "transition": "all 0.2s",
                                                                "cursor": "pointer",
                                                            },
                                                            className="landing-nav-card",
                                                            children=[
                                                                html.Div(
                                                                    style={
                                                                        "width": "56px",
                                                                        "height": "56px",
                                                                        "borderRadius": "12px",
                                                                        "backgroundColor": Colors.PRIMARY_BLUE_LIGHT,
                                                                        "display": "flex",
                                                                        "alignItems": "center",
                                                                        "justifyContent": "center",
                                                                        "marginBottom": Spacing.XL,
                                                                    },
                                                                    children=[
                                                                        html.Span(
                                                                            "📊",
                                                                            style={
                                                                                "fontSize": FontSizes.H2
                                                                            },
                                                                        )
                                                                    ],
                                                                ),
                                                                html.H3(
                                                                    content.get(
                                                                        "landing.calculator_card.title",
                                                                        "Calculator",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.H4,
                                                                        "fontWeight": "600",
                                                                        "color": Colors.NAVY_DARK,
                                                                        "marginBottom": Spacing.MD,
                                                                    },
                                                                ),
                                                                html.P(
                                                                    content.get(
                                                                        "landing.calculator_card.description",
                                                                        "View the MVPF calculation, key performance indicators, and comparison charts showing detainee values, society values, and government costs.",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.BODY,
                                                                        "color": Colors.GRAY_700,
                                                                        "lineHeight": LineHeights.RELAXED,
                                                                        "margin": "0",
                                                                    },
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                                # Card 2: Scenario Analysis
                                                html.A(
                                                    href="#",
                                                    id="link-to-scenarios",
                                                    style={"textDecoration": "none"},
                                                    children=[
                                                        html.Div(
                                                            style={
                                                                "backgroundColor": "white",
                                                                "padding": Spacing.XXXL,
                                                                "borderRadius": "12px",
                                                                "boxShadow": "0 4px 6px rgba(0,0,0,0.1)",
                                                                "border": f"{Borders.MEDIUM} solid transparent",
                                                                "transition": "all 0.2s",
                                                                "cursor": "pointer",
                                                            },
                                                            className="landing-nav-card",
                                                            children=[
                                                                html.Div(
                                                                    style={
                                                                        "width": "56px",
                                                                        "height": "56px",
                                                                        "borderRadius": "12px",
                                                                        "backgroundColor": Colors.WARNING_LIGHT,
                                                                        "display": "flex",
                                                                        "alignItems": "center",
                                                                        "justifyContent": "center",
                                                                        "marginBottom": Spacing.XL,
                                                                    },
                                                                    children=[
                                                                        html.Span(
                                                                            "🔍",
                                                                            style={
                                                                                "fontSize": FontSizes.H2
                                                                            },
                                                                        )
                                                                    ],
                                                                ),
                                                                html.H3(
                                                                    content.get(
                                                                        "landing.scenario_analysis_card.title",
                                                                        "Scenario Analysis",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.H4,
                                                                        "fontWeight": "600",
                                                                        "color": Colors.NAVY_DARK,
                                                                        "marginBottom": Spacing.MD,
                                                                    },
                                                                ),
                                                                html.P(
                                                                    content.get(
                                                                        "landing.scenario_analysis_card.description",
                                                                        "Compare different policy scenarios and analyze parameter sensitivity to understand how changes in assumptions affect MVPF outcomes.",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.BODY,
                                                                        "color": Colors.GRAY_700,
                                                                        "lineHeight": LineHeights.RELAXED,
                                                                        "margin": "0",
                                                                    },
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                                # Card 3: Comparative Benchmarking
                                                html.A(
                                                    href="#",
                                                    id="link-to-benchmarking",
                                                    style={"textDecoration": "none"},
                                                    children=[
                                                        html.Div(
                                                            style={
                                                                "backgroundColor": "white",
                                                                "padding": Spacing.XXXL,
                                                                "borderRadius": "12px",
                                                                "boxShadow": "0 4px 6px rgba(0,0,0,0.1)",
                                                                "border": f"{Borders.MEDIUM} solid transparent",
                                                                "transition": "all 0.2s",
                                                                "cursor": "pointer",
                                                            },
                                                            className="landing-nav-card",
                                                            children=[
                                                                html.Div(
                                                                    style={
                                                                        "width": "56px",
                                                                        "height": "56px",
                                                                        "borderRadius": "12px",
                                                                        "backgroundColor": Colors.SUCCESS_LIGHT,
                                                                        "display": "flex",
                                                                        "alignItems": "center",
                                                                        "justifyContent": "center",
                                                                        "marginBottom": Spacing.XL,
                                                                    },
                                                                    children=[
                                                                        html.Span(
                                                                            "📈",
                                                                            style={
                                                                                "fontSize": FontSizes.H2
                                                                            },
                                                                        )
                                                                    ],
                                                                ),
                                                                html.H3(
                                                                    content.get(
                                                                        "landing.benchmarking_card.title",
                                                                        "Comparative Benchmarking",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.H4,
                                                                        "fontWeight": "600",
                                                                        "color": Colors.NAVY_DARK,
                                                                        "marginBottom": Spacing.MD,
                                                                    },
                                                                ),
                                                                html.P(
                                                                    content.get(
                                                                        "landing.benchmarking_card.description",
                                                                        "Compare Cook County Jail MVPF against other government programs and policy initiatives to contextualize the value of public spending.",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.BODY,
                                                                        "color": Colors.GRAY_700,
                                                                        "lineHeight": LineHeights.RELAXED,
                                                                        "margin": "0",
                                                                    },
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                            ],
                                        ),
                                        # Information Tile
                                        html.Div(
                                            style={
                                                "background": "white",
                                                "padding": Spacing.XL,
                                                "borderRadius": "8px",
                                                "marginBottom": Spacing.XXXL,
                                                "border": f"{Borders.THIN} solid {Colors.GRAY_300}",
                                            },
                                            children=[
                                                html.H3(
                                                    content.get("info_tile.heading", "About MVPF"),
                                                    style={
                                                        "fontSize": FontSizes.H5,
                                                        "fontWeight": "600",
                                                        "color": Colors.GRAY_900,
                                                        "marginTop": "0",
                                                        "marginBottom": Spacing.SM,
                                                    },
                                                ),
                                                dcc.Markdown(
                                                    content.get(
                                                        "info_tile.description",
                                                        "The MVPF measures the ratio of beneficiaries willingness to pay to the net cost to the government",
                                                    ),
                                                    style={
                                                        "fontSize": FontSizes.BODY,
                                                        "color": Colors.GRAY_600,
                                                        "lineHeight": LineHeights.RELAXED,
                                                        "margin": f"0 0 {Spacing.MD} 0",
                                                    },
                                                ),
                                                html.P(
                                                    [
                                                        html.Strong(
                                                            content.get(
                                                                "info_tile.formula_label",
                                                                "Formula:",
                                                            ),
                                                            style={"color": Colors.GRAY_900},
                                                        ),
                                                        html.Br(),
                                                        content.get(
                                                            "info_tile.formula",
                                                            "MVPF = (Detainee + Society) / Government Cost",
                                                        ),
                                                    ],
                                                    style={
                                                        "fontSize": FontSizes.BODY,
                                                        "color": Colors.GRAY_600,
                                                        "lineHeight": LineHeights.RELAXED,
                                                        "margin": f"0 0 {Spacing.LG} 0",
                                                    },
                                                ),
                                                # New section: application label + text
                                                dcc.Markdown(
                                                    f"**{content.get('info_tile.application_label', 'Our application of MVPF')}**\n\n{content.get('info_tile.application', 'How we apply MVPF to Cook County Jail.')}",
                                                    style={
                                                        "fontSize": FontSizes.BODY,
                                                        "color": Colors.GRAY_600,
                                                        "lineHeight": LineHeights.RELAXED,
                                                        "margin": "0",
                                                    },
                                                ),
                                            ],
                                        ),
                                    ],
                                )
                            ],
                        ),
                        # Tab 1: Overview - KPI, Main Chart, Interpretation, Benchmarks
                        dcc.Tab(
                            label=content.get("tabs.overview", "Calculator"),
                            value="tab-overview",
                            style={
                                "padding": f"{Spacing.MD} {Spacing.XXL}",
                                "fontWeight": "500",
                                "fontSize": FontSizes.BODY,
                            },
                            selected_style={
                                "padding": f"{Spacing.MD} {Spacing.XXL}",
                                "fontWeight": "600",
                                "fontSize": FontSizes.BODY,
                                "borderTop": f"{Borders.THICK} solid {Colors.PRIMARY_BLUE}",
                                "backgroundColor": "white",
                            },
                            children=[
                                html.Div(
                                    style={"padding": f"{Spacing.XXL} 0"},
                                    children=[
                                        # Overview Tab Description Placeholder
                                        html.Div(
                                            className="chart-container",
                                            style={"marginBottom": Spacing.XXL},
                                            children=[
                                                html.H3(
                                                    content.get(
                                                        "placeholders.overview_intro.title",
                                                        "Placeholder: Overview Tab Introduction",
                                                    ),
                                                    style={
                                                        "fontSize": "36px",
                                                        "fontWeight": "600",
                                                        "color": Colors.GRAY_900,
                                                        "textAlign": "center",
                                                        "marginTop": "6",
                                                        "marginBottom": Spacing.XXL,
                                                    },
                                                ),
                                                html.Div(
                                                    children=[
                                                        html.P(
                                                            content.get(
                                                                "placeholders.overview_intro.paragraph1",
                                                                "",
                                                            ),
                                                            style={
                                                                "fontSize": FontSizes.BODY,
                                                                "lineHeight": LineHeights.RELAXED,
                                                                "margin": f"0 0 {Spacing.MD} 0",
                                                                "whiteSpace": "pre-line",
                                                            },
                                                        )
                                                    ]
                                                ),
                                            ],
                                        ),
                                        # Scenario Selection Section (Centered)
                                        html.Div(
                                            style={
                                                "maxWidth": "1200px",
                                                "margin": "0 auto",
                                                "marginBottom": Spacing.XXL,
                                            },
                                            children=[
                                                html.Div(
                                                    className="jumbotron",
                                                    children=[
                                                        html.H4(
                                                            content.get(
                                                                "controls.scenario_selection.title",
                                                                "Scenario Selection",
                                                            ),
                                                            style={
                                                                "fontSize": FontSizes.H3,
                                                                "fontWeight": "600",
                                                                "color": Colors.GRAY_900,
                                                                "marginTop": "0",
                                                                "textAlign": "center",
                                                                "marginBottom": Spacing.MD,
                                                                "alignItems": "center",
                                                                "justifyContent": "center",
                                                            },
                                                        ),
                                                        # Hidden store for selected scenario
                                                        dcc.Store(
                                                            id="scenario-selector", data="baseline"
                                                        ),
                                                        # Scenerio Lead-in text
                                                        html.Div(
                                                            style={"marginBottom": Spacing.LG},
                                                            children=[
                                                                html.P(
                                                                    content.get(
                                                                        "placeholders.overview_intro.paragraph2",
                                                                        "",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.BODY,
                                                                        "color": Colors.GRAY_800,
                                                                        "lineHeight": LineHeights.RELAXED,
                                                                        "margin": "0 0 10px 0",
                                                                        "whiteSpace": "pre-line",
                                                                    },
                                                                ),
                                                                html.P(
                                                                    content.get(
                                                                        "placeholders.overview_intro.paragraph3",
                                                                        "",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.BODY,
                                                                        "color": Colors.GRAY_800,
                                                                        "lineHeight": LineHeights.RELAXED,
                                                                        "margin": "0 0 10px 0",
                                                                        "whiteSpace": "pre-line",
                                                                    },
                                                                ),
                                                                html.P(
                                                                    content.get(
                                                                        "placeholders.overview_intro.paragraph4",
                                                                        "",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.BODY,
                                                                        "color": Colors.GRAY_800,
                                                                        "lineHeight": LineHeights.RELAXED,
                                                                        "margin": "0",
                                                                        "whiteSpace": "pre-line",
                                                                    },
                                                                ),
                                                            ],
                                                        ),
                                                        # Scenario Jumbotrons Grid ( clickable)
                                                        html.Div(
                                                            className="jumbotron-grid",
                                                            style={
                                                                "marginBottom": Spacing.XXL,
                                                                "gridTemplateColumns": "repeat(3, 1fr)",
                                                            },
                                                            children=[
                                                                # Jumbotron 1: Baseline Scenario
                                                                html.Button(
                                                                    id="scenario-btn-baseline",
                                                                    n_clicks=0,
                                                                    className="jumbotron scenario-card",
                                                                    style={
                                                                        "border": f"{{Borders.THICK}} solid {Colors.PRIMARY_BLUE_DARK}",
                                                                        "cursor": "pointer",
                                                                    },
                                                                    children=[
                                                                        html.Div(
                                                                            className="jumbotron-icon",
                                                                            style={
                                                                                "background": Colors.PRIMARY_BLUE_LIGHT
                                                                            },
                                                                            children=[
                                                                                html.Span(
                                                                                    "📊",
                                                                                    style={
                                                                                        "color": Colors.PRIMARY_BLUE_DARK
                                                                                    },
                                                                                )
                                                                            ],
                                                                        ),
                                                                        html.H4(
                                                                            content.get(
                                                                                "scenarios.cards.baseline.title",
                                                                                "Baseline - Current Operations",
                                                                            ),
                                                                            className="jumbotron-title",
                                                                            style={
                                                                                "fontWeight": "700"
                                                                            },
                                                                        ),
                                                                        html.P(
                                                                            content.get(
                                                                                "scenarios.cards.baseline.value",
                                                                                "Focus on individual harm plus potential criminogenic effects",
                                                                            ),
                                                                            className="jumbotron-value",
                                                                            style={
                                                                                "fontSize": FontSizes.BODY,
                                                                                "fontWeight": "500",
                                                                                "color": Colors.PRIMARY_BLUE_DARK,
                                                                            },
                                                                        ),
                                                                        html.P(
                                                                            content.get(
                                                                                "scenarios.cards.baseline.description",
                                                                                "Choose this if you think detention may worsen public safety",
                                                                            ),
                                                                            className="jumbotron-description",
                                                                        ),
                                                                    ],
                                                                ),
                                                                # Jumbotron 2: Most Conservative Scenario
                                                                html.Button(
                                                                    id="scenario-btn-most-conservative",
                                                                    n_clicks=0,
                                                                    className="jumbotron scenario-card",
                                                                    style={
                                                                        "border": f"{{Borders.MEDIUM}} solid {Colors.GRAY_300}",
                                                                        "cursor": "pointer",
                                                                    },
                                                                    children=[
                                                                        html.Div(
                                                                            className="jumbotron-icon",
                                                                            style={
                                                                                "background": Colors.WARNING_LIGHT
                                                                            },
                                                                            children=[
                                                                                html.Span(
                                                                                    "🛡️",
                                                                                    style={
                                                                                        "color": Colors.WARNING_YELLOW
                                                                                    },
                                                                                )
                                                                            ],
                                                                        ),
                                                                        html.H4(
                                                                            content.get(
                                                                                "scenarios.cards.most_conservative.title",
                                                                                "Less Negative Detainee Value - Conservative",
                                                                            ),
                                                                            className="jumbotron-title",
                                                                            style={
                                                                                "fontWeight": "700"
                                                                            },
                                                                        ),
                                                                        html.P(
                                                                            content.get(
                                                                                "scenarios.cards.most_conservative.value",
                                                                                "Focus on conservative valuation of individual harms",
                                                                            ),
                                                                            className="jumbotron-value",
                                                                            style={
                                                                                "fontSize": FontSizes.BODY,
                                                                                "fontWeight": "500",
                                                                                "color": Colors.WARNING_YELLOW,
                                                                            },
                                                                        ),
                                                                        html.P(
                                                                            content.get(
                                                                                "scenarios.cards.most_conservative.description",
                                                                                "Choose this if you believe detainee harm should be valued using smaller, survey-based estimates",
                                                                            ),
                                                                            className="jumbotron-description",
                                                                        ),
                                                                    ],
                                                                ),
                                                                # Jumbotron 3: Least Conservative Scenario
                                                                html.Button(
                                                                    id="scenario-btn-least-conservative",
                                                                    n_clicks=0,
                                                                    className="jumbotron scenario-card",
                                                                    style={
                                                                        "border": f"{{Borders.MEDIUM}} solid {Colors.GRAY_300}",
                                                                        "cursor": "pointer",
                                                                    },
                                                                    children=[
                                                                        html.Div(
                                                                            className="jumbotron-icon",
                                                                            style={
                                                                                "background": Colors.SUCCESS_LIGHT
                                                                            },
                                                                            children=[
                                                                                html.Span(
                                                                                    "🚀",
                                                                                    style={
                                                                                        "color": Colors.SUCCESS_GREEN
                                                                                    },
                                                                                )
                                                                            ],
                                                                        ),
                                                                        html.H4(
                                                                            content.get(
                                                                                "scenarios.cards.least_conservative.title",
                                                                                "Least Conservative (lowest MVPF)",
                                                                            ),
                                                                            className="jumbotron-title",
                                                                            style={
                                                                                "fontWeight": "700"
                                                                            },
                                                                        ),
                                                                        html.P(
                                                                            content.get(
                                                                                "scenarios.cards.least_conservative.value",
                                                                                "Focus on broad social harms and criminogenic effects",
                                                                            ),
                                                                            className="jumbotron-value",
                                                                            style={
                                                                                "fontSize": FontSizes.BODY,
                                                                                "fontWeight": "500",
                                                                                "color": Colors.SUCCESS_GREEN,
                                                                            },
                                                                        ),
                                                                        html.P(
                                                                            content.get(
                                                                                "scenarios.cards.least_conservative.description",
                                                                                "Choose this if you think detention harms both individuals and communities and may increase crime",
                                                                            ),
                                                                            className="jumbotron-description",
                                                                        ),
                                                                    ],
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        ),
                                        # Parameter Lead-in text
                                        html.Div(
                                            className="jumbotron",
                                            style={"marginTop": "0", "marginBottom": Spacing.XXL},
                                            children=[
                                                html.H4(
                                                    content.get(
                                                        "placeholders.parameter_intro.title",
                                                        "Parameter Selection",
                                                    ),
                                                    style={
                                                        "fontSize": FontSizes.H3,
                                                        "fontWeight": "600",
                                                        "color": Colors.GRAY_900,
                                                        "marginTop": "0",
                                                        "marginBottom": Spacing.MD,
                                                        "textAlign": "center",
                                                    },
                                                ),
                                                html.P(
                                                    content.get(
                                                        "placeholders.parameter_intro.paragraph_1",
                                                        "",
                                                    ),
                                                    style={
                                                        "fontSize": FontSizes.BODY,
                                                        "color": Colors.GRAY_800,
                                                        "lineHeight": LineHeights.RELAXED,
                                                        "margin": "0",
                                                        "whiteSpace": "pre-line",
                                                    },
                                                ),
                                                # Parameter Jumbotrons Grid - Row 1
                                                html.Div(
                                                    className="jumbotron-grid",
                                                    style={
                                                        "marginBottom": Spacing.XXL,
                                                        "gridTemplateColumns": "repeat(3, 1fr)",
                                                    },
                                                    children=[
                                                        # Jumbotron 1: Felony Rate
                                                        html.Div(
                                                            className="jumbotron",
                                                            children=[
                                                                html.Div(
                                                                    className="jumbotron-icon",
                                                                    style={
                                                                        "background": Colors.PRIMARY_BLUE_LIGHT
                                                                    },
                                                                    children=[
                                                                        html.Span(
                                                                            "%%",
                                                                            style={
                                                                                "color": Colors.PRIMARY_BLUE_DARK
                                                                            },
                                                                        )
                                                                    ],
                                                                ),
                                                                html.H4(
                                                                    content.get(
                                                                        "controls.felony_rate.title",
                                                                        "Felony Rate",
                                                                    ),
                                                                    className="jumbotron-title",
                                                                ),
                                                                html.P(
                                                                    id="felony-rate-value",
                                                                    children=f"{fel_rate_param.default_value:.0%}",
                                                                    className="jumbotron-value",
                                                                ),
                                                                html.P(
                                                                    content.get(
                                                                        "controls.felony_rate.tooltip",
                                                                        fel_rate_param.description,
                                                                    ),
                                                                    className="jumbotron-description",
                                                                ),
                                                                dcc.Slider(
                                                                    id="detainee-param1",
                                                                    min=0.1,
                                                                    max=1.0,
                                                                    value=0.7,
                                                                    marks={
                                                                        0.1: {
                                                                            "label": "10%",
                                                                            "style": {
                                                                                "fontSize": "8px"
                                                                            },
                                                                        },
                                                                        0.2: {
                                                                            "label": "20%",
                                                                            "style": {
                                                                                "fontSize": "8px"
                                                                            },
                                                                        },
                                                                        0.3: {
                                                                            "label": "30%",
                                                                            "style": {
                                                                                "fontSize": "8px"
                                                                            },
                                                                        },
                                                                        0.4: {
                                                                            "label": "40%",
                                                                            "style": {
                                                                                "fontSize": "8px"
                                                                            },
                                                                        },
                                                                        0.5: {
                                                                            "label": "50%",
                                                                            "style": {
                                                                                "fontSize": "8px"
                                                                            },
                                                                        },
                                                                        0.6: {
                                                                            "label": "60%",
                                                                            "style": {
                                                                                "fontSize": "8px"
                                                                            },
                                                                        },
                                                                        0.7: {
                                                                            "label": "70%",
                                                                            "style": {
                                                                                "fontSize": "8px"
                                                                            },
                                                                        },
                                                                        0.8: {
                                                                            "label": "80%",
                                                                            "style": {
                                                                                "fontSize": "8px"
                                                                            },
                                                                        },
                                                                        0.9: {
                                                                            "label": "90%",
                                                                            "style": {
                                                                                "fontSize": "8px"
                                                                            },
                                                                        },
                                                                        1.0: {
                                                                            "label": "100%",
                                                                            "style": {
                                                                                "fontSize": "8px"
                                                                            },
                                                                        },
                                                                    },
                                                                    step=0.05,
                                                                    tooltip={
                                                                        "placement": "bottom",
                                                                        "always_visible": False,
                                                                    },
                                                                ),
                                                            ],
                                                        ),
                                                        # Jumbotron 2: Detainee Population
                                                        html.Div(
                                                            className="jumbotron",
                                                            children=[
                                                                html.Div(
                                                                    className="jumbotron-icon",
                                                                    style={
                                                                        "background": Colors.WARNING_LIGHT
                                                                    },
                                                                    children=[
                                                                        html.Span(
                                                                            "#",
                                                                            style={
                                                                                "color": Colors.WARNING_YELLOW,
                                                                                "fontWeight": "700",
                                                                            },
                                                                        )
                                                                    ],
                                                                ),
                                                                html.H4(
                                                                    content.get(
                                                                        "controls.detainee_population.title",
                                                                        "Detainee Population",
                                                                    ),
                                                                    className="jumbotron-title",
                                                                ),
                                                                html.P(
                                                                    id="detainee-population-value",
                                                                    children=f"{n_detainees_param.base_value:,.0f}",
                                                                    className="jumbotron-value",
                                                                ),
                                                                html.P(
                                                                    content.get(
                                                                        "controls.detainee_population.tooltip",
                                                                        n_detainees_param.description,
                                                                    ),
                                                                    className="jumbotron-description",
                                                                ),
                                                                # Baseline Population Input
                                                                html.Div(
                                                                    style={
                                                                        "marginBottom": Spacing.LG
                                                                    },
                                                                    children=[
                                                                        html.Label(
                                                                            "Baseline Population:",
                                                                            style={
                                                                                "fontSize": FontSizes.LABEL,
                                                                                "fontWeight": "500",
                                                                                "color": Colors.GRAY_900,
                                                                                "marginBottom": Spacing.XS,
                                                                                "display": "block",
                                                                            },
                                                                        ),
                                                                        dcc.Input(
                                                                            id="detainee-baseline-input",
                                                                            type="number",
                                                                            value=n_detainees_param.base_value,
                                                                            min=0,
                                                                            step=100,
                                                                            style={
                                                                                "width": "100%",
                                                                                "padding": Spacing.SM,
                                                                                "fontSize": FontSizes.BODY,
                                                                                "border": f"{Borders.THIN} solid {Colors.GRAY_400}",
                                                                                "borderRadius": "6px",
                                                                                "boxSizing": "border-box",
                                                                            },
                                                                        ),
                                                                    ],
                                                                ),
                                                                # Population Multiplier Slider
                                                                html.Div(
                                                                    style={"marginTop": Spacing.LG},
                                                                    children=[
                                                                        html.Label(
                                                                            [
                                                                                "Population Multiplier: ",
                                                                                html.Span(
                                                                                    id="detainee-multiplier-display",
                                                                                    children="100%",
                                                                                    style={
                                                                                        "fontWeight": "bold",
                                                                                        "color": Colors.PRIMARY_BLUE,
                                                                                    },
                                                                                ),
                                                                            ],
                                                                            style={
                                                                                "fontSize": FontSizes.LABEL,
                                                                                "fontWeight": "500",
                                                                                "color": Colors.GRAY_900,
                                                                                "marginBottom": Spacing.SM,
                                                                                "display": "block",
                                                                            },
                                                                        ),
                                                                        dcc.Slider(
                                                                            id="detainee-param2",
                                                                            min=0.1,
                                                                            max=2.0,
                                                                            value=1.0,
                                                                            marks={
                                                                                0.1: {
                                                                                    "label": "10%",
                                                                                    "style": {
                                                                                        "fontSize": "8px"
                                                                                    },
                                                                                },
                                                                                0.5: {
                                                                                    "label": "50%",
                                                                                    "style": {
                                                                                        "fontSize": "8px"
                                                                                    },
                                                                                },
                                                                                1.0: {
                                                                                    "label": "100%",
                                                                                    "style": {
                                                                                        "fontSize": "8px"
                                                                                    },
                                                                                },
                                                                                1.5: {
                                                                                    "label": "150%",
                                                                                    "style": {
                                                                                        "fontSize": "8px"
                                                                                    },
                                                                                },
                                                                                2.0: {
                                                                                    "label": "200%",
                                                                                    "style": {
                                                                                        "fontSize": "8px"
                                                                                    },
                                                                                },
                                                                            },
                                                                            step=0.05,
                                                                            tooltip={
                                                                                "placement": "bottom",
                                                                                "always_visible": False,
                                                                            },
                                                                        ),
                                                                    ],
                                                                ),
                                                            ],
                                                        ),
                                                        # Jumbotron 3: Length of Stay
                                                        html.Div(
                                                            className="jumbotron",
                                                            children=[
                                                                html.Div(
                                                                    className="jumbotron-icon",
                                                                    style={
                                                                        "background": Colors.ERROR_LIGHT
                                                                    },
                                                                    children=[
                                                                        html.Span(
                                                                            "D",
                                                                            style={
                                                                                "color": Colors.ERROR_RED,
                                                                                "fontWeight": "700",
                                                                            },
                                                                        )
                                                                    ],
                                                                ),
                                                                html.H4(
                                                                    content.get(
                                                                        "controls.length_of_stay.title",
                                                                        "Length of Stay",
                                                                    ),
                                                                    className="jumbotron-title",
                                                                ),
                                                                html.P(
                                                                    id="los-days-value",
                                                                    children=f"{los_days_param.default_value:.0f} days",
                                                                    className="jumbotron-value",
                                                                ),
                                                                html.P(
                                                                    content.get(
                                                                        "controls.length_of_stay.tooltip",
                                                                        los_days_param.description,
                                                                    ),
                                                                    className="jumbotron-description",
                                                                ),
                                                                dcc.Slider(
                                                                    id="society-param2",
                                                                    min=1,
                                                                    max=365,
                                                                    value=70,
                                                                    marks={
                                                                        1: {
                                                                            "label": "1",
                                                                            "style": {
                                                                                "fontSize": "8px"
                                                                            },
                                                                        },
                                                                        70: {
                                                                            "label": "70",
                                                                            "style": {
                                                                                "fontSize": "8px"
                                                                            },
                                                                        },
                                                                        203: {
                                                                            "label": "203",
                                                                            "style": {
                                                                                "fontSize": "8px"
                                                                            },
                                                                        },
                                                                        365: {
                                                                            "label": "365",
                                                                            "style": {
                                                                                "fontSize": "8px"
                                                                            },
                                                                        },
                                                                    },
                                                                    step=1,
                                                                    tooltip={
                                                                        "placement": "bottom",
                                                                        "always_visible": False,
                                                                    },
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                ),
                                                # Parameter Jumbotrons Grid - Row 2: Crime Effect
                                                html.Div(
                                                    className="jumbotron-grid",
                                                    style={
                                                        "marginBottom": Spacing.XXL,
                                                        "gridTemplateColumns": "1fr",
                                                    },
                                                    children=[
                                                        # Jumbotron: Crime Effect (Two-column layout)
                                                        html.Div(
                                                            className="jumbotron",
                                                            children=[
                                                                html.Div(
                                                                    style={
                                                                        "display": "grid",
                                                                        "gridTemplateColumns": "1fr 2fr",
                                                                        "gap": Spacing.XL,
                                                                        "alignItems": "center",
                                                                    },
                                                                    children=[
                                                                        # Left column: Explanation text
                                                                        html.Div(
                                                                            children=[
                                                                                html.P(
                                                                                    content.get(
                                                                                        "controls.crime_effect.explanation",
                                                                                        "Select the assumed impact of detention on future crime rates. The baseline is set to 0% (no effect) based on literature review. You can adjust this to explore how different crime effect assumptions change the MVPF calculation.",
                                                                                    ),
                                                                                    style={
                                                                                        "fontSize": FontSizes.BODY,
                                                                                        "color": Colors.GRAY_700,
                                                                                        "lineHeight": LineHeights.RELAXED,
                                                                                        "margin": "0",
                                                                                    },
                                                                                )
                                                                            ]
                                                                        ),
                                                                        # Right column: Original content (icon, title, value, slider)
                                                                        html.Div(
                                                                            children=[
                                                                                html.Div(
                                                                                    className="jumbotron-icon",
                                                                                    style={
                                                                                        "background": "#fef2f2"
                                                                                    },
                                                                                    children=[
                                                                                        html.Span(
                                                                                            "⚠️",
                                                                                            style={
                                                                                                "color": Colors.ERROR_RED
                                                                                            },
                                                                                        )
                                                                                    ],
                                                                                ),
                                                                                html.H4(
                                                                                    content.get(
                                                                                        "controls.crime_effect.title",
                                                                                        "Crime Effect",
                                                                                    ),
                                                                                    className="jumbotron-title",
                                                                                ),
                                                                                html.P(
                                                                                    id="crime-effect-value",
                                                                                    children="0",
                                                                                    className="jumbotron-value",
                                                                                ),
                                                                                html.P(
                                                                                    content.get(
                                                                                        "controls.crime_effect.description",
                                                                                        "Crime impact multiplier on detention outcomes",
                                                                                    ),
                                                                                    className="jumbotron-description",
                                                                                ),
                                                                                dcc.Slider(
                                                                                    id="crime-effect-slider",
                                                                                    min=-4,
                                                                                    max=14,
                                                                                    value=0,
                                                                                    marks={
                                                                                        -4: {
                                                                                            "label": "-4 (Large Decrease)",
                                                                                            "style": {
                                                                                                "fontSize": "8px"
                                                                                            },
                                                                                        },
                                                                                        0: {
                                                                                            "label": "0 (No Effect)",
                                                                                            "style": {
                                                                                                "fontSize": "8px"
                                                                                            },
                                                                                        },
                                                                                        5: {
                                                                                            "label": "5 (Moderate Increase)",
                                                                                            "style": {
                                                                                                "fontSize": "8px"
                                                                                            },
                                                                                        },
                                                                                        14: {
                                                                                            "label": "14 (Large Increase)",
                                                                                            "style": {
                                                                                                "fontSize": "8px"
                                                                                            },
                                                                                        },
                                                                                    },
                                                                                    step=None,
                                                                                    tooltip={
                                                                                        "placement": "bottom",
                                                                                        "always_visible": False,
                                                                                    },
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                )
                                                            ],
                                                        )
                                                    ],
                                                ),
                                            ],
                                        ),
                                        # Calculate Button Section
                                        html.Div(
                                            className="calculate-section",
                                            style={
                                                "display": "flex",
                                                "justifyContent": "center",
                                                "marginBottom": Spacing.XXXL,
                                            },
                                            children=[
                                                html.Button(
                                                    "Calculate MVPF",
                                                    id="btn-calculate",
                                                    n_clicks=0,
                                                    style={
                                                        "backgroundColor": Colors.NAVY_MEDIUM,
                                                        "color": "white",
                                                        "border": "none",
                                                        "borderRadius": "8px",
                                                        "padding": "14px 48px",
                                                        "fontSize": FontSizes.H5,
                                                        "fontWeight": "600",
                                                        "cursor": "pointer",
                                                        "transition": "all 0.2s",
                                                        "boxShadow": "0 4px 6px rgba(37, 99, 235, 0.25)",
                                                    },
                                                )
                                            ],
                                        ),
                                        # MVPF Score Display (Centered)
                                        html.Div(
                                            id="kpi-card",
                                            style={
                                                "marginBottom": Spacing.XXL,
                                                "display": "flex",
                                                "justifyContent": "center",
                                            },
                                        ),
                                        # MVPF Calculation Purpose Placeholder ("How to use this result")
                                        html.Div(
                                            className="chart-container",
                                            style={
                                                "background": "white",
                                                "marginBottom": Spacing.XXL,
                                            },
                                            children=[
                                                html.H3(
                                                    content.get(
                                                        "placeholders.mvpf_purpose.title",
                                                        "Placeholder: Purpose of MVPF Calculation",
                                                    ),
                                                    style={
                                                        "fontSize": FontSizes.H3,
                                                        "fontWeight": "bold",
                                                        "color": Colors.GRAY_900,
                                                        "marginTop": "0",
                                                        "marginBottom": Spacing.MD,
                                                        "textAlign": "center",
                                                    },
                                                ),
                                                html.P(
                                                    content.get(
                                                        "placeholders.mvpf_purpose.content",
                                                        "This section will explain the purpose and methodology of the MVPF calculation, providing context for interpreting the results shown above and the detailed breakdowns below.",
                                                    ),
                                                    style={
                                                        "fontSize": FontSizes.BODY,
                                                        "color": Colors.GRAY_900,
                                                        "lineHeight": LineHeights.RELAXED,
                                                        "margin": "0",
                                                    },
                                                ),
                                            ],
                                        ),
                                        # Calculation and Components Details (below "how to use this result")
                                        html.Div(
                                            id="kpi-components", style={"marginBottom": Spacing.XXL}
                                        ),
                                        # Charts Row: Numerator and Denominator Charts
                                        html.Div(
                                            style={
                                                "display": "grid",
                                                "gridTemplateColumns": "1fr 1fr",
                                                "gap": Spacing.XXL,
                                            },
                                            children=[
                                                # Numerator Chart (Detainee + Society Values)
                                                html.Div(
                                                    className="chart-container",
                                                    children=[dcc.Graph(id="numerator-chart")],
                                                ),
                                                # Denominator Chart (Government Cost vs Numerator)
                                                html.Div(
                                                    className="chart-container",
                                                    children=[dcc.Graph(id="denominator-chart")],
                                                ),
                                            ],
                                        ),
                                        # TODO: Min and Max MVPFs Card - Currently hidden for review
                                        # html.Div(className='chart-container', style={
                                        #     'background': 'white',
                                        #     'marginTop': Spacing.XXL,
                                        #     'marginBottom': Spacing.XXL,
                                        #     'padding': Spacing.XL
                                        # }, children=[
                                        #     html.P(
                                        #         "CCJ 2018 highest MVPF (within-default range): Lower-Bound Valuation + crime decreases; all other parameters at CCJ 2018 defaults.\n"
                                        #         "CCJ 2018 lowest MVPF (within-default range): Upper-Bound Valuation + maximum crime increase; all other parameters at CCJ 2018 defaults.\n"
                                        #         "Highest MVPF (global max): Lower-Bound Valuation + crime decreases + felony mix = 0% + LoS = 1 day + detainee population = minimum.\n"
                                        #         "Lowest MVPF (global min): Upper-Bound Valuation + maximum crime increase + felony mix = 100% + LoS = 365 days + detainee population = maximum.",
                                        #         style={
                                        #             'fontSize': FontSizes.BODY,
                                        #             'color': Colors.GRAY_800,
                                        #             'lineHeight': LineHeights.RELAXED,
                                        #             'margin': '0',
                                        #             'whiteSpace': 'pre-line',
                                        #             'textAlign': 'left'
                                        #         }
                                        #     )
                                        # ])
                                    ],
                                )
                            ],
                        ),
                        # Tab 2: Scenario Analysis - Scenario Selection + Subcomponents Chart
                        dcc.Tab(
                            label=content.get("tabs.scenarios", "Scenario Analysis"),
                            value="tab-scenarios",
                            style={
                                "padding": f"{Spacing.MD} {Spacing.XXL}",
                                "fontWeight": "500",
                                "fontSize": "36px",
                                "color": Colors.NAVY_DARK,
                                "textAlign": "center",
                                "marginTop": "6",
                                "marginBottom": Spacing.XXL,
                            },
                            selected_style={
                                "padding": f"{Spacing.MD} {Spacing.XXL}",
                                "fontWeight": "600",
                                "fontSize": FontSizes.BODY,
                                "borderTop": f"{{Borders.THICK}} solid {Colors.PRIMARY_BLUE}",
                                "backgroundColor": "white",
                            },
                            children=[
                                html.Div(
                                    style={"padding": "24px 0"},
                                    children=[
                                        # Main Tab Header
                                        html.H3(
                                            content.get(
                                                "placeholders.alt_scenarios.title",
                                                "Comparison of Alternative Scenarios",
                                            ),
                                            style={
                                                "fontSize": "36px",
                                                "fontWeight": "bold",
                                                "color": Colors.NAVY_DARK,
                                                "textAlign": "center",
                                                "margin": f"0 0 {Spacing.XXL} 0",
                                            },
                                        ),
                                        # Two-column layout: MVPF Comparison Chart (left) + Scenarios Paragraphs (right)
                                        html.Div(
                                            style={
                                                "display": "grid",
                                                "gridTemplateColumns": "1fr 1fr",
                                                "gap": Spacing.XXL,
                                                "marginBottom": "48px",
                                            },
                                            children=[
                                                # Left column: MVPF Comparison Chart
                                                html.Div(
                                                    className="chart-container",
                                                    children=[
                                                        dcc.Graph(id="scenario-comparison-chart")
                                                    ],
                                                ),
                                                # Right column: Scenarios 3 paragraphs
                                                html.Div(
                                                    style={
                                                        "padding": Spacing.XL,
                                                        "borderRadius": "8px",
                                                        "color": Colors.NAVY_DARK,
                                                        "display": "flex",
                                                        "flexDirection": "column",
                                                        "justifyContent": "center",
                                                    },
                                                    children=[
                                                        html.P(
                                                            content.get(
                                                                "placeholders.alt_scenarios.paragraph_1",
                                                                "",
                                                            ),
                                                            style={
                                                                "fontSize": FontSizes.BODY,
                                                                "color": Colors.NAVY_DARK,
                                                                "margin": f"0 0 {Spacing.MD} 0",
                                                                "lineHeight": LineHeights.RELAXED,
                                                            },
                                                        ),
                                                        html.P(
                                                            content.get(
                                                                "placeholders.alt_scenarios.paragraph_2",
                                                                "",
                                                            ),
                                                            style={
                                                                "fontSize": FontSizes.BODY,
                                                                "color": Colors.NAVY_DARK,
                                                                "margin": f"0 0 {Spacing.MD} 0",
                                                                "lineHeight": LineHeights.RELAXED,
                                                            },
                                                        ),
                                                        html.P(
                                                            content.get(
                                                                "placeholders.alt_scenarios.paragraph_3",
                                                                "",
                                                            ),
                                                            style={
                                                                "fontSize": FontSizes.BODY,
                                                                "color": Colors.NAVY_DARK,
                                                                "margin": f"0 0 {Spacing.XXL} 0",
                                                                "lineHeight": LineHeights.RELAXED,
                                                            },
                                                        ),
                                                        # Download Analysis Card
                                                        html.Div(
                                                            style={
                                                                "background": Colors.NAVY_MEDIUM,
                                                                "padding": Spacing.XL,
                                                                "borderRadius": "10px",
                                                                "boxShadow": "0 4px 6px rgba(37, 99, 235, 0.1)",
                                                            },
                                                            children=[
                                                                html.H4(
                                                                    content.get(
                                                                        "download.analysis_card.title",
                                                                        "Download Full Analysis",
                                                                    ),
                                                                    style={
                                                                        "fontSize": "18px",
                                                                        "fontWeight": "600",
                                                                        "color": Colors.GRAY_300,
                                                                        "marginTop": "0",
                                                                        "marginBottom": "10px",
                                                                    },
                                                                ),
                                                                html.P(
                                                                    content.get(
                                                                        "download.analysis_card.description",
                                                                        "Export detailed calculations, assumptions and sensitivity analyses in CSV format",
                                                                    ),
                                                                    style={
                                                                        "fontSize": "13px",
                                                                        "color": Colors.GRAY_300,
                                                                        "marginBottom": "14px",
                                                                        "lineHeight": LineHeights.NORMAL,
                                                                    },
                                                                ),
                                                                html.Button(
                                                                    content.get(
                                                                        "download.analysis_card.button_text",
                                                                        "Download Current Calculations",
                                                                    ),
                                                                    id="download-analysis-button",
                                                                    n_clicks=0,
                                                                    style={
                                                                        "backgroundColor": "white",
                                                                        "color": Colors.NAVY_MEDIUM,
                                                                        "border": "none",
                                                                        "padding": "10px 18px",
                                                                        "borderRadius": "6px",
                                                                        "fontSize": "13px",
                                                                        "fontWeight": "600",
                                                                        "cursor": "pointer",
                                                                        "transition": "all 0.2s",
                                                                        "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
                                                                        "width": "100%",
                                                                        "marginBottom": "10px",
                                                                    },
                                                                ),
                                                                dcc.Download(
                                                                    id="download-analysis-csv"
                                                                ),
                                                                html.Button(
                                                                    "Download Edge Cases Analysis (39 scenarios)",
                                                                    id="download-edge-cases-button",
                                                                    n_clicks=0,
                                                                    style={
                                                                        "backgroundColor": "white",
                                                                        "color": Colors.NAVY_MEDIUM,
                                                                        "border": "none",
                                                                        "padding": "10px 18px",
                                                                        "borderRadius": "6px",
                                                                        "fontSize": "13px",
                                                                        "fontWeight": "600",
                                                                        "cursor": "pointer",
                                                                        "transition": "all 0.2s",
                                                                        "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
                                                                        "width": "100%",
                                                                    },
                                                                ),
                                                                dcc.Download(
                                                                    id="download-edge-cases-csv"
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                        # Current Analysis Settings
                                        html.Div(
                                            style={
                                                "backgroundColor": Colors.GRAY_50,
                                                "padding": Spacing.XL,
                                                "borderRadius": BorderRadius.MD,
                                                "marginBottom": Spacing.XXL,
                                                "marginTop": Spacing.XXXL,
                                                "border": f"{Borders.THIN} solid {Colors.GRAY_300}",
                                            },
                                            children=[
                                                html.Div(
                                                    style={
                                                        "display": "flex",
                                                        "justifyContent": "space-between",
                                                        "alignItems": "center",
                                                        "marginBottom": Spacing.LG,
                                                    },
                                                    children=[
                                                        html.H4(
                                                            "Current Analysis Settings",
                                                            style={
                                                                "fontSize": FontSizes.H5,
                                                                "fontWeight": "600",
                                                                "color": Colors.NAVY_DARK,
                                                                "marginTop": "0",
                                                                "marginBottom": "0",
                                                            },
                                                        ),
                                                        html.Button(
                                                            [
                                                                html.Span(
                                                                    "← ",
                                                                    style={"marginRight": "4px"},
                                                                ),
                                                                "Change Parameters",
                                                            ],
                                                            id="btn-back-to-calculation",
                                                            n_clicks=0,
                                                            style={
                                                                "backgroundColor": Colors.NAVY_MEDIUM,
                                                                "color": "white",
                                                                "border": "none",
                                                                "padding": f"{Spacing.SM} {Spacing.LG}",
                                                                "borderRadius": BorderRadius.SM,
                                                                "fontSize": FontSizes.BODY_SM,
                                                                "fontWeight": "600",
                                                                "cursor": "pointer",
                                                                "transition": "all 0.2s",
                                                                "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
                                                            },
                                                        ),
                                                    ],
                                                ),
                                                html.Div(
                                                    style={
                                                        "display": "grid",
                                                        "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))",
                                                        "gap": Spacing.LG,
                                                    },
                                                    children=[
                                                        # Scenario Parameter
                                                        html.Div(
                                                            style={
                                                                "backgroundColor": "white",
                                                                "padding": Spacing.MD,
                                                                "borderRadius": BorderRadius.SM,
                                                                "border": f"{Borders.THIN} solid {Colors.GRAY_200}",
                                                            },
                                                            children=[
                                                                html.Div(
                                                                    style={
                                                                        "display": "flex",
                                                                        "alignItems": "center",
                                                                        "marginBottom": Spacing.XS,
                                                                    },
                                                                    children=[
                                                                        html.Span(
                                                                            "📊",
                                                                            style={
                                                                                "fontSize": "20px",
                                                                                "marginRight": Spacing.SM,
                                                                            },
                                                                        ),
                                                                        html.Span(
                                                                            "Scenario",
                                                                            style={
                                                                                "fontSize": FontSizes.LABEL,
                                                                                "fontWeight": "600",
                                                                                "color": Colors.GRAY_700,
                                                                            },
                                                                        ),
                                                                    ],
                                                                ),
                                                                html.Div(
                                                                    id="sensitivity-param-scenario",
                                                                    style={
                                                                        "fontSize": FontSizes.H5,
                                                                        "fontWeight": "bold",
                                                                        "color": Colors.NAVY_MEDIUM,
                                                                        "marginTop": Spacing.XS,
                                                                    },
                                                                ),
                                                            ],
                                                        ),
                                                        # Felony Rate Parameter
                                                        html.Div(
                                                            style={
                                                                "backgroundColor": "white",
                                                                "padding": Spacing.MD,
                                                                "borderRadius": BorderRadius.SM,
                                                                "border": f"{Borders.THIN} solid {Colors.GRAY_200}",
                                                            },
                                                            children=[
                                                                html.Div(
                                                                    style={
                                                                        "display": "flex",
                                                                        "alignItems": "center",
                                                                        "marginBottom": Spacing.XS,
                                                                    },
                                                                    children=[
                                                                        html.Span(
                                                                            "⚖️",
                                                                            style={
                                                                                "fontSize": "20px",
                                                                                "marginRight": Spacing.SM,
                                                                            },
                                                                        ),
                                                                        html.Span(
                                                                            "Felony Rate",
                                                                            style={
                                                                                "fontSize": FontSizes.LABEL,
                                                                                "fontWeight": "600",
                                                                                "color": Colors.GRAY_700,
                                                                            },
                                                                        ),
                                                                    ],
                                                                ),
                                                                html.Div(
                                                                    id="sensitivity-param-felony-rate",
                                                                    style={
                                                                        "fontSize": FontSizes.H5,
                                                                        "fontWeight": "bold",
                                                                        "color": Colors.NAVY_MEDIUM,
                                                                        "marginTop": Spacing.XS,
                                                                    },
                                                                ),
                                                            ],
                                                        ),
                                                        # Detainee Population Parameter
                                                        html.Div(
                                                            style={
                                                                "backgroundColor": "white",
                                                                "padding": Spacing.MD,
                                                                "borderRadius": BorderRadius.SM,
                                                                "border": f"{Borders.THIN} solid {Colors.GRAY_200}",
                                                            },
                                                            children=[
                                                                html.Div(
                                                                    style={
                                                                        "display": "flex",
                                                                        "alignItems": "center",
                                                                        "marginBottom": Spacing.XS,
                                                                    },
                                                                    children=[
                                                                        html.Span(
                                                                            "👥",
                                                                            style={
                                                                                "fontSize": "20px",
                                                                                "marginRight": Spacing.SM,
                                                                            },
                                                                        ),
                                                                        html.Span(
                                                                            "Detainee Population",
                                                                            style={
                                                                                "fontSize": FontSizes.LABEL,
                                                                                "fontWeight": "600",
                                                                                "color": Colors.GRAY_700,
                                                                            },
                                                                        ),
                                                                    ],
                                                                ),
                                                                html.Div(
                                                                    id="sensitivity-param-detainee-pop",
                                                                    style={
                                                                        "fontSize": FontSizes.H5,
                                                                        "fontWeight": "bold",
                                                                        "color": Colors.NAVY_MEDIUM,
                                                                        "marginTop": Spacing.XS,
                                                                    },
                                                                ),
                                                            ],
                                                        ),
                                                        # Length of Stay Parameter
                                                        html.Div(
                                                            style={
                                                                "backgroundColor": "white",
                                                                "padding": Spacing.MD,
                                                                "borderRadius": BorderRadius.SM,
                                                                "border": f"{Borders.THIN} solid {Colors.GRAY_200}",
                                                            },
                                                            children=[
                                                                html.Div(
                                                                    style={
                                                                        "display": "flex",
                                                                        "alignItems": "center",
                                                                        "marginBottom": Spacing.XS,
                                                                    },
                                                                    children=[
                                                                        html.Span(
                                                                            "📅",
                                                                            style={
                                                                                "fontSize": "20px",
                                                                                "marginRight": Spacing.SM,
                                                                            },
                                                                        ),
                                                                        html.Span(
                                                                            "Length of Stay",
                                                                            style={
                                                                                "fontSize": FontSizes.LABEL,
                                                                                "fontWeight": "600",
                                                                                "color": Colors.GRAY_700,
                                                                            },
                                                                        ),
                                                                    ],
                                                                ),
                                                                html.Div(
                                                                    id="sensitivity-param-los",
                                                                    style={
                                                                        "fontSize": FontSizes.H5,
                                                                        "fontWeight": "bold",
                                                                        "color": Colors.NAVY_MEDIUM,
                                                                        "marginTop": Spacing.XS,
                                                                    },
                                                                ),
                                                            ],
                                                        ),
                                                        # Crime Effect Parameter
                                                        html.Div(
                                                            style={
                                                                "backgroundColor": "white",
                                                                "padding": Spacing.MD,
                                                                "borderRadius": BorderRadius.SM,
                                                                "border": f"{Borders.THIN} solid {Colors.GRAY_200}",
                                                            },
                                                            children=[
                                                                html.Div(
                                                                    style={
                                                                        "display": "flex",
                                                                        "alignItems": "center",
                                                                        "marginBottom": Spacing.XS,
                                                                    },
                                                                    children=[
                                                                        html.Span(
                                                                            "🚨",
                                                                            style={
                                                                                "fontSize": "20px",
                                                                                "marginRight": Spacing.SM,
                                                                            },
                                                                        ),
                                                                        html.Span(
                                                                            "Crime Effect",
                                                                            style={
                                                                                "fontSize": FontSizes.LABEL,
                                                                                "fontWeight": "600",
                                                                                "color": Colors.GRAY_700,
                                                                            },
                                                                        ),
                                                                    ],
                                                                ),
                                                                html.Div(
                                                                    id="sensitivity-param-crime-effect",
                                                                    style={
                                                                        "fontSize": FontSizes.H5,
                                                                        "fontWeight": "bold",
                                                                        "color": Colors.NAVY_MEDIUM,
                                                                        "marginTop": Spacing.XS,
                                                                    },
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                        # MVPF Range Card - Hidden for now
                                        # html.Div(className='chart-container', style={
                                        #     'background': 'white',
                                        #     'marginBottom': Spacing.XXXL,
                                        #     'padding': Spacing.XL,
                                        #     'borderLeft': f'{Borders.EXTRA_THICK} solid {Colors.PRIMARY_BLUE}'
                                        # }, children=[
                                        #     html.H4('MVPF Range Under Current Settings', style={
                                        #         'fontSize': FontSizes.H5,
                                        #         'fontWeight': '600',
                                        #         'color': Colors.NAVY_DARK,
                                        #         'marginTop': '0',
                                        #         'marginBottom': Spacing.MD
                                        #     }),
                                        #     html.P(
                                        #         "The MVPF varies significantly based on parameter combinations. Below are the extreme values achievable within the dashboard's parameter ranges:",
                                        #         style={
                                        #             'fontSize': FontSizes.BODY,
                                        #             'color': Colors.GRAY_800,
                                        #             'lineHeight': LineHeights.RELAXED,
                                        #             'marginBottom': Spacing.LG
                                        #         }
                                        #     ),
                                        #     html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': Spacing.LG}, children=[
                                        #         # Highest MVPF (least negative)
                                        #         html.Div(style={
                                        #             'backgroundColor': Colors.SUCCESS_LIGHT,
                                        #             'padding': Spacing.MD,
                                        #             'borderRadius': BorderRadius.SM,
                                        #             'border': f'{Borders.THIN} solid {Colors.SUCCESS_GREEN}'
                                        #         }, children=[
                                        #             html.Div('Highest MVPF (Least Negative)', style={
                                        #                 'fontSize': FontSizes.LABEL,
                                        #                 'fontWeight': '700',
                                        #                 'color': Colors.SUCCESS_GREEN,
                                        #                 'textTransform': 'uppercase',
                                        #                 'letterSpacing': '0.04em',
                                        #                 'marginBottom': Spacing.SM
                                        #             }),
                                        #             html.P(
                                        #                 "Lower-Bound Valuation (smallest detainee harm) + crime decreases (maximum crime prevention benefit) + minimum population + shortest stay + lowest felony share",
                                        #                 style={
                                        #                     'fontSize': FontSizes.BODY_SM,
                                        #                     'color': Colors.GRAY_900,
                                        #                     'lineHeight': LineHeights.NORMAL,
                                        #                     'margin': '0'
                                        #                 }
                                        #             )
                                        #         ]),
                                        #         # Lowest MVPF (most negative)
                                        #         html.Div(style={
                                        #             'backgroundColor': Colors.ERROR_LIGHT,
                                        #             'padding': Spacing.MD,
                                        #             'borderRadius': BorderRadius.SM,
                                        #             'border': f'{Borders.THIN} solid {Colors.ERROR_RED}'
                                        #         }, children=[
                                        #             html.Div('Lowest MVPF (Most Negative)', style={
                                        #                 'fontSize': FontSizes.LABEL,
                                        #                 'fontWeight': '700',
                                        #                 'color': Colors.ERROR_RED,
                                        #                 'textTransform': 'uppercase',
                                        #                 'letterSpacing': '0.04em',
                                        #                 'marginBottom': Spacing.SM
                                        #             }),
                                        #             html.P(
                                        #                 "Upper-Bound Valuation (largest detainee harm + community spillovers) + maximum crime increase + maximum population + longest stay + highest felony share",
                                        #                 style={
                                        #                     'fontSize': FontSizes.BODY_SM,
                                        #                     'color': Colors.GRAY_900,
                                        #                     'lineHeight': LineHeights.NORMAL,
                                        #                     'margin': '0'
                                        #                 }
                                        #             )
                                        #         ])
                                        #     ]),
                                        #     html.P(
                                        #         "These extremes illustrate the sensitivity of MVPF estimates to normative choices (how harm is valued) and empirical assumptions (crime effects, detention scale). The sensitivity analysis below shows how individual parameters affect your selected scenario.",
                                        #         style={
                                        #             'fontSize': FontSizes.BODY_SM,
                                        #             'color': Colors.GRAY_600,
                                        #             'lineHeight': LineHeights.NORMAL,
                                        #             'marginTop': Spacing.MD,
                                        #             'marginBottom': '0',
                                        #             'fontStyle': 'italic'
                                        #         }
                                        #     )
                                        # ]),
                                        # Sensitivity Analysis Section Header
                                        html.H3(
                                            content.get(
                                                "sensitivity_analysis.title", "Sensitivity Analysis"
                                            ),
                                            style={
                                                "fontSize": FontSizes.H3,
                                                "fontWeight": "600",
                                                "color": Colors.NAVY_DARK,
                                                "marginTop": "0",
                                                "marginBottom": Spacing.SM,
                                            },
                                        ),
                                        html.P(
                                            content.get("sensitivity_analysis.description", ""),
                                            style={
                                                "fontSize": FontSizes.BODY,
                                                "color": Colors.GRAY_600,
                                                "marginBottom": Spacing.XXXL,
                                                "lineHeight": LineHeights.RELAXED,
                                            },
                                        ),
                                        # Sensitivity Analysis Graphs (One per row with descriptions)
                                        # Felony Rate Sensitivity
                                        html.Div(
                                            style={
                                                "display": "grid",
                                                "gridTemplateColumns": "60% 40%",
                                                "gap": Spacing.XXL,
                                                "marginBottom": Spacing.XXXL,
                                            },
                                            children=[
                                                html.Div(
                                                    className="chart-container",
                                                    children=[
                                                        dcc.Graph(id="sensitivity-felony-rate")
                                                    ],
                                                ),
                                                html.Div(
                                                    className="chart-container",
                                                    style={
                                                        "display": "flex",
                                                        "alignItems": "center",
                                                    },
                                                    children=[
                                                        html.Div(
                                                            children=[
                                                                html.H4(
                                                                    content.get(
                                                                        "sensitivity_analysis.felony_rate.title",
                                                                        "Felony Rate Sensitivity",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.H5,
                                                                        "fontWeight": "600",
                                                                        "color": Colors.NAVY_DARK,
                                                                        "marginTop": "0",
                                                                        "marginBottom": Spacing.MD,
                                                                    },
                                                                ),
                                                                html.P(
                                                                    content.get(
                                                                        "sensitivity_analysis.felony_rate.description",
                                                                        "This chart shows how MVPF changes when varying the felony rate assumption while holding all other parameters constant.",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.BODY,
                                                                        "color": Colors.GRAY_800,
                                                                        "lineHeight": LineHeights.RELAXED,
                                                                        "margin": "0",
                                                                    },
                                                                ),
                                                            ]
                                                        )
                                                    ],
                                                ),
                                            ],
                                        ),
                                        # Detainee Population Sensitivity
                                        html.Div(
                                            style={
                                                "display": "grid",
                                                "gridTemplateColumns": "60% 40%",
                                                "gap": Spacing.XXL,
                                                "marginBottom": Spacing.XXXL,
                                            },
                                            children=[
                                                html.Div(
                                                    className="chart-container",
                                                    children=[
                                                        dcc.Graph(
                                                            id="sensitivity-detainee-population"
                                                        )
                                                    ],
                                                ),
                                                html.Div(
                                                    className="chart-container",
                                                    style={
                                                        "display": "flex",
                                                        "alignItems": "center",
                                                    },
                                                    children=[
                                                        html.Div(
                                                            children=[
                                                                html.H4(
                                                                    content.get(
                                                                        "sensitivity_analysis.detainee_population.title",
                                                                        "Detainee Population Sensitivity",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.H5,
                                                                        "fontWeight": "600",
                                                                        "color": Colors.NAVY_DARK,
                                                                        "marginTop": "0",
                                                                        "marginBottom": Spacing.MD,
                                                                    },
                                                                ),
                                                                html.P(
                                                                    content.get(
                                                                        "sensitivity_analysis.detainee_population.description",
                                                                        "This chart shows how MVPF changes when varying the detainee population multiplier while holding all other parameters constant.",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.BODY,
                                                                        "color": Colors.GRAY_800,
                                                                        "lineHeight": LineHeights.RELAXED,
                                                                        "margin": "0",
                                                                    },
                                                                ),
                                                            ]
                                                        )
                                                    ],
                                                ),
                                            ],
                                        ),
                                        # Crime Effect Sensitivity
                                        html.Div(
                                            style={
                                                "display": "grid",
                                                "gridTemplateColumns": "60% 40%",
                                                "gap": Spacing.XXL,
                                                "marginBottom": Spacing.XXXL,
                                            },
                                            children=[
                                                html.Div(
                                                    className="chart-container",
                                                    children=[
                                                        dcc.Graph(id="sensitivity-crime-effect")
                                                    ],
                                                ),
                                                html.Div(
                                                    className="chart-container",
                                                    style={
                                                        "display": "flex",
                                                        "alignItems": "center",
                                                    },
                                                    children=[
                                                        html.Div(
                                                            children=[
                                                                html.H4(
                                                                    content.get(
                                                                        "sensitivity_analysis.crime_effect.title",
                                                                        "Crime Effect Sensitivity",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.H5,
                                                                        "fontWeight": "600",
                                                                        "color": Colors.NAVY_DARK,
                                                                        "marginTop": "0",
                                                                        "marginBottom": Spacing.MD,
                                                                    },
                                                                ),
                                                                html.P(
                                                                    content.get(
                                                                        "sensitivity_analysis.crime_effect.description",
                                                                        "This chart shows how MVPF changes when varying the crime effect assumption while holding all other parameters constant.",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.BODY,
                                                                        "color": Colors.GRAY_800,
                                                                        "lineHeight": LineHeights.RELAXED,
                                                                        "margin": "0",
                                                                    },
                                                                ),
                                                            ]
                                                        )
                                                    ],
                                                ),
                                            ],
                                        ),
                                        # Length of Stay Sensitivity
                                        html.Div(
                                            style={
                                                "display": "grid",
                                                "gridTemplateColumns": "60% 40%",
                                                "gap": Spacing.XXL,
                                                "marginBottom": "48px",
                                            },
                                            children=[
                                                html.Div(
                                                    className="chart-container",
                                                    children=[
                                                        dcc.Graph(id="sensitivity-length-of-stay")
                                                    ],
                                                ),
                                                html.Div(
                                                    className="chart-container",
                                                    style={
                                                        "display": "flex",
                                                        "alignItems": "center",
                                                    },
                                                    children=[
                                                        html.Div(
                                                            children=[
                                                                html.H4(
                                                                    content.get(
                                                                        "sensitivity_analysis.length_of_stay.title",
                                                                        "Length of Stay Sensitivity",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.H5,
                                                                        "fontWeight": "600",
                                                                        "color": Colors.NAVY_DARK,
                                                                        "marginTop": "0",
                                                                        "marginBottom": Spacing.MD,
                                                                    },
                                                                ),
                                                                html.P(
                                                                    content.get(
                                                                        "sensitivity_analysis.length_of_stay.description",
                                                                        "This chart shows how MVPF changes when varying the average length of stay while holding all other parameters constant.",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.BODY,
                                                                        "color": Colors.GRAY_800,
                                                                        "lineHeight": LineHeights.RELAXED,
                                                                        "margin": "0",
                                                                    },
                                                                ),
                                                            ]
                                                        )
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                )
                            ],
                        ),
                        # Tab 3: Comparative Benchmarking
                        dcc.Tab(
                            label="Comparative Benchmarking",
                            value="tab-benchmarking",
                            style={
                                "padding": f"{Spacing.MD} {Spacing.XXL}",
                                "fontWeight": "500",
                                "fontSize": FontSizes.BODY,
                            },
                            selected_style={
                                "padding": f"{Spacing.MD} {Spacing.XXL}",
                                "fontWeight": "600",
                                "fontSize": FontSizes.BODY,
                                "borderTop": f"{{Borders.THICK}} solid {Colors.PRIMARY_BLUE}",
                                "backgroundColor": "white",
                            },
                            children=[
                                html.Div(
                                    style={"padding": "24px 0"},
                                    children=[
                                        # Benchmark Card
                                        html.Div(id="benchmark-card")
                                    ],
                                )
                            ],
                        ),
                        # Tab 4: Descriptions
                        dcc.Tab(
                            label="MVPF Explained",
                            value="tab-descriptions",
                            style={
                                "padding": f"{Spacing.MD} {Spacing.XXL}",
                                "fontWeight": "500",
                                "fontSize": FontSizes.BODY,
                            },
                            selected_style={
                                "padding": f"{Spacing.MD} {Spacing.XXL}",
                                "fontWeight": "600",
                                "fontSize": FontSizes.BODY,
                                "borderTop": f"{{Borders.THICK}} solid {Colors.PRIMARY_BLUE}",
                                "backgroundColor": "white",
                            },
                            children=[
                                html.Div(
                                    style={"padding": "24px 0"},
                                    children=[
                                        # MVPF Explainer Section
                                        html.Div(
                                            className="chart-container",
                                            style={"background": Colors.GRAY_100},
                                            children=[
                                                html.H3(
                                                    content.get(
                                                        "mvpf_explainer.section_title",
                                                        "Understanding MVPF",
                                                    ),
                                                    style={
                                                        "fontSize": FontSizes.H3,
                                                        "fontWeight": "bold",
                                                        "color": Colors.NAVY_DARK,
                                                        "marginBottom": Spacing.LG,
                                                        "marginTop": "0",
                                                        "textAlign": "center",
                                                    },
                                                ),
                                                html.H4(
                                                    content.get(
                                                        "mvpf_explainer.what_is_mvpf.heading",
                                                        "What is MVPF?",
                                                    ),
                                                    style={
                                                        "fontSize": FontSizes.H5,
                                                        "fontWeight": "600",
                                                        "color": Colors.GRAY_900,
                                                        "marginTop": "0",
                                                        "marginBottom": Spacing.MD,
                                                    },
                                                ),
                                                dcc.Markdown(
                                                    content.get(
                                                        "mvpf_explainer.what_is_mvpf.description",
                                                        "The Marginal Value of Public Funds (MVPF) is a metric that measures the social welfare benefit of a policy per dollar of government spending.",
                                                    ),
                                                    style={
                                                        "color": Colors.GRAY_800,
                                                        "fontSize": FontSizes.BODY,
                                                        "lineHeight": LineHeights.RELAXED,
                                                        "margin": f"0 0 {Spacing.XXL} 0",
                                                    },
                                                ),
                                                html.H4(
                                                    content.get(
                                                        "mvpf_explainer.applying_to_detention.heading",
                                                        "Applying MVPF to detention",
                                                    ),
                                                    style={
                                                        "fontSize": FontSizes.H5,
                                                        "fontWeight": "600",
                                                        "color": Colors.GRAY_900,
                                                        "marginTop": "0",
                                                        "marginBottom": Spacing.MD,
                                                    },
                                                ),
                                                dcc.Markdown(
                                                    content.get(
                                                        "mvpf_explainer.applying_to_detention.paragraph1",
                                                        "Most MVPF work looks at policies where the person subject to the policy is also the main beneficiary.",
                                                    ),
                                                    style={
                                                        "color": Colors.GRAY_800,
                                                        "fontSize": FontSizes.BODY,
                                                        "lineHeight": LineHeights.RELAXED,
                                                        "margin": f"0 0 {Spacing.MD} 0",
                                                    },
                                                ),
                                                dcc.Markdown(
                                                    content.get(
                                                        "mvpf_explainer.applying_to_detention.paragraph2",
                                                        "Most studies on detention focus on marginal changes.",
                                                    ),
                                                    style={
                                                        "color": Colors.GRAY_800,
                                                        "fontSize": FontSizes.BODY,
                                                        "lineHeight": LineHeights.RELAXED,
                                                        "margin": f"0 0 {Spacing.MD} 0",
                                                    },
                                                ),
                                                dcc.Markdown(
                                                    content.get(
                                                        "mvpf_explainer.applying_to_detention.paragraph3"
                                                    ),
                                                    style={
                                                        "color": Colors.GRAY_900,
                                                        "fontSize": FontSizes.BODY,
                                                        "lineHeight": LineHeights.RELAXED,
                                                        "margin": f"0 0 {Spacing.XXL} 0",
                                                    },
                                                ),
                                                # Methodology section
                                                html.Div(
                                                    style={"marginBottom": Spacing.XXXL},
                                                    children=[
                                                        html.H3(
                                                            content.get(
                                                                "understanding.methodology.title",
                                                                "Methodology",
                                                            ),
                                                            style={
                                                                "fontSize": FontSizes.H4,
                                                                "fontWeight": "600",
                                                                "color": Colors.GRAY_900,
                                                                "marginTop": "0",
                                                                "marginBottom": Spacing.MD,
                                                            },
                                                        ),
                                                        html.P(
                                                            content.get(
                                                                "understanding.methodology.description",
                                                                "This dashboard computes the Marginal Value of Public Funds (MVPF) as:",
                                                            ),
                                                            style={
                                                                "fontSize": "15px",
                                                                "color": Colors.GRAY_800,
                                                                "lineHeight": LineHeights.RELAXED,
                                                                "marginBottom": Spacing.MD,
                                                            },
                                                        ),
                                                        # MVPF = (Total Value) / (Total Government Cost)
                                                        html.Div(
                                                            style={
                                                                "display": "grid",
                                                                "gridTemplateColumns": "1fr auto 1fr",
                                                                "alignItems": "start",  # top-justify columns
                                                                "gap": Spacing.MD,
                                                                "background": "white",
                                                                "border": f"{Borders.THIN} solid {Colors.GRAY_300}",
                                                                "borderRadius": "10px",
                                                                "padding": Spacing.LG,
                                                                "marginBottom": Spacing.LG,
                                                            },
                                                            children=[
                                                                # Left: Numerator
                                                                html.Div(
                                                                    style={
                                                                        "display": "flex",
                                                                        "flexDirection": "column",
                                                                        "gap": "10px",
                                                                    },
                                                                    children=[
                                                                        html.Div(
                                                                            style={
                                                                                "border": f"{Borders.THIN} solid #cbd5e1",
                                                                                "borderRadius": "10px",
                                                                                "padding": "10px 12px",
                                                                                "background": Colors.GRAY_100,
                                                                            },
                                                                            children=[
                                                                                html.Div(
                                                                                    "Total Value",
                                                                                    style={
                                                                                        "fontSize": FontSizes.LABEL,
                                                                                        "fontWeight": "700",
                                                                                        "color": Colors.GRAY_950,
                                                                                        "textTransform": "uppercase",
                                                                                        "letterSpacing": "0.04em",
                                                                                    },
                                                                                ),
                                                                                html.Div(
                                                                                    "to Detainees and Society",
                                                                                    style={
                                                                                        "fontSize": FontSizes.BODY,
                                                                                        "fontWeight": "600",
                                                                                        "color": "#0f172a",
                                                                                        "marginTop": "2px",
                                                                                    },
                                                                                ),
                                                                            ],
                                                                        ),
                                                                        # Components within Total Value
                                                                        html.Div(
                                                                            style={
                                                                                "display": "grid",
                                                                                "gridTemplateColumns": "1fr",
                                                                                "gap": Spacing.SM,
                                                                            },
                                                                            children=[
                                                                                html.Div(
                                                                                    style={
                                                                                        "borderLeft": f"{{Borders.EXTRA_THICK}} solid {Colors.PRIMARY_BLUE}",
                                                                                        "border": f"{Borders.THIN} solid {Colors.GRAY_300}",
                                                                                        "borderRadius": "10px",
                                                                                        "padding": "10px 12px",
                                                                                        "background": "white",
                                                                                    },
                                                                                    children=[
                                                                                        html.A(
                                                                                            "Detainee Harm",
                                                                                            href="#components-breakdown",
                                                                                            style={
                                                                                                "fontSize": "13px",
                                                                                                "fontWeight": "700",
                                                                                                "color": "#111827",
                                                                                                "textDecoration": "none",
                                                                                                "cursor": "pointer",
                                                                                            },
                                                                                        ),
                                                                                        html.Div(
                                                                                            "Harm from time in custody",
                                                                                            style={
                                                                                                "fontSize": FontSizes.LABEL,
                                                                                                "color": Colors.GRAY_600,
                                                                                                "marginTop": "2px",
                                                                                            },
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                                html.Div(
                                                                                    style={
                                                                                        "borderLeft": f"{Borders.EXTRA_THICK} solid #10b981",
                                                                                        "border": f"{Borders.THIN} solid {Colors.GRAY_300}",
                                                                                        "borderRadius": "10px",
                                                                                        "padding": "10px 12px",
                                                                                        "background": "white",
                                                                                    },
                                                                                    children=[
                                                                                        html.A(
                                                                                            "Court Appearance",
                                                                                            href="#components-breakdown",
                                                                                            style={
                                                                                                "fontSize": "13px",
                                                                                                "fontWeight": "700",
                                                                                                "color": "#111827",
                                                                                                "textDecoration": "none",
                                                                                                "cursor": "pointer",
                                                                                            },
                                                                                        ),
                                                                                        html.Div(
                                                                                            "Benefits from improved appearance",
                                                                                            style={
                                                                                                "fontSize": FontSizes.LABEL,
                                                                                                "color": Colors.GRAY_600,
                                                                                                "marginTop": "2px",
                                                                                            },
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                                html.Div(
                                                                                    style={
                                                                                        "borderLeft": f"{Borders.EXTRA_THICK} solid #ef4444",
                                                                                        "border": f"{Borders.THIN} solid {Colors.GRAY_300}",
                                                                                        "borderRadius": "10px",
                                                                                        "padding": "10px 12px",
                                                                                        "background": "white",
                                                                                    },
                                                                                    children=[
                                                                                        html.A(
                                                                                            "Crime Effects",
                                                                                            href="#components-breakdown",
                                                                                            style={
                                                                                                "fontSize": "13px",
                                                                                                "fontWeight": "700",
                                                                                                "color": "#111827",
                                                                                                "textDecoration": "none",
                                                                                                "cursor": "pointer",
                                                                                            },
                                                                                        ),
                                                                                        html.Div(
                                                                                            "Set to 0 in baseline; adjustable",
                                                                                            style={
                                                                                                "fontSize": FontSizes.LABEL,
                                                                                                "color": Colors.GRAY_600,
                                                                                                "marginTop": "2px",
                                                                                            },
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                                html.Div(
                                                                                    style={
                                                                                        "borderLeft": f"{Borders.EXTRA_THICK} solid #8b5cf6",
                                                                                        "border": f"{Borders.THIN} solid {Colors.GRAY_300}",
                                                                                        "borderRadius": "10px",
                                                                                        "padding": "10px 12px",
                                                                                        "background": "white",
                                                                                    },
                                                                                    children=[
                                                                                        html.A(
                                                                                            "Community Spillovers",
                                                                                            href="#components-breakdown",
                                                                                            style={
                                                                                                "fontSize": "13px",
                                                                                                "fontWeight": "700",
                                                                                                "color": "#111827",
                                                                                                "textDecoration": "none",
                                                                                                "cursor": "pointer",
                                                                                            },
                                                                                        ),
                                                                                        html.Div(
                                                                                            "Optional; depends on scenario",
                                                                                            style={
                                                                                                "fontSize": FontSizes.LABEL,
                                                                                                "color": Colors.GRAY_600,
                                                                                                "marginTop": "2px",
                                                                                            },
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ],
                                                                        ),
                                                                    ],
                                                                ),
                                                                # Center: Division / equals
                                                                html.Div(
                                                                    style={
                                                                        "display": "flex",
                                                                        "flexDirection": "column",
                                                                        "alignItems": "center",
                                                                        "justifyContent": "flex-start",
                                                                        "gap": Spacing.SM,
                                                                        "paddingTop": "44px",  # tweak (36-52px) to align with stacks
                                                                    },
                                                                    children=[
                                                                        html.Div(
                                                                            "÷",
                                                                            style={
                                                                                "fontSize": "22px",
                                                                                "fontWeight": "800",
                                                                                "color": "#111827",
                                                                                "lineHeight": "1",
                                                                            },
                                                                        ),
                                                                        html.Div(
                                                                            "MVPF",
                                                                            style={
                                                                                "fontSize": FontSizes.LABEL,
                                                                                "fontWeight": "800",
                                                                                "color": Colors.GRAY_900,
                                                                                "letterSpacing": "0.06em",
                                                                            },
                                                                        ),
                                                                    ],
                                                                ),
                                                                # Right: Denominator
                                                                html.Div(
                                                                    style={
                                                                        "display": "flex",
                                                                        "flexDirection": "column",
                                                                        "gap": "10px",
                                                                    },
                                                                    children=[
                                                                        html.Div(
                                                                            style={
                                                                                "border": f"{Borders.THIN} solid #cbd5e1",
                                                                                "borderRadius": "10px",
                                                                                "padding": "10px 12px",
                                                                                "background": Colors.GRAY_100,
                                                                            },
                                                                            children=[
                                                                                html.Div(
                                                                                    "Total Government Cost",
                                                                                    style={
                                                                                        "fontSize": FontSizes.LABEL,
                                                                                        "fontWeight": "700",
                                                                                        "color": Colors.GRAY_950,
                                                                                        "textTransform": "uppercase",
                                                                                        "letterSpacing": "0.04em",
                                                                                    },
                                                                                ),
                                                                            ],
                                                                        ),
                                                                        html.Div(
                                                                            style={
                                                                                "display": "grid",
                                                                                "gridTemplateColumns": "1fr",
                                                                                "gap": Spacing.SM,
                                                                            },
                                                                            children=[
                                                                                html.Div(
                                                                                    style={
                                                                                        "borderLeft": f"{Borders.EXTRA_THICK} solid #0ea5e9",
                                                                                        "border": f"{Borders.THIN} solid {Colors.GRAY_300}",
                                                                                        "borderRadius": "10px",
                                                                                        "padding": "10px 12px",
                                                                                        "background": "white",
                                                                                    },
                                                                                    children=[
                                                                                        html.A(
                                                                                            "CCJ Operating Costs",
                                                                                            href="#components-breakdown",
                                                                                            style={
                                                                                                "fontSize": "13px",
                                                                                                "fontWeight": "700",
                                                                                                "color": "#111827",
                                                                                                "textDecoration": "none",
                                                                                                "cursor": "pointer",
                                                                                            },
                                                                                        ),
                                                                                        html.Div(
                                                                                            "Fixed baseline denominator",
                                                                                            style={
                                                                                                "fontSize": FontSizes.LABEL,
                                                                                                "color": Colors.GRAY_600,
                                                                                                "marginTop": "2px",
                                                                                            },
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                                html.Div(
                                                                                    style={
                                                                                        "borderLeft": f"{Borders.EXTRA_THICK} solid #ef4444",
                                                                                        "border": f"{Borders.THIN} solid {Colors.GRAY_300}",
                                                                                        "borderRadius": "10px",
                                                                                        "padding": "10px 12px",
                                                                                        "background": "white",
                                                                                    },
                                                                                    children=[
                                                                                        html.A(
                                                                                            "Crime Effect-Related Costs/Savings",
                                                                                            href="#components-breakdown",
                                                                                            style={
                                                                                                "fontSize": "13px",
                                                                                                "fontWeight": "700",
                                                                                                "color": "#111827",
                                                                                                "textDecoration": "none",
                                                                                                "cursor": "pointer",
                                                                                            },
                                                                                        ),
                                                                                        html.Div(
                                                                                            "Only non-zero when Crime Effect is non-zero",
                                                                                            style={
                                                                                                "fontSize": FontSizes.LABEL,
                                                                                                "color": Colors.GRAY_600,
                                                                                                "marginTop": "2px",
                                                                                            },
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ],
                                                                        ),
                                                                    ],
                                                                ),
                                                            ],
                                                        ),
                                                        # Parameter-to-component legend
                                                        html.Div(
                                                            style={
                                                                "background": "white",
                                                                "border": f"{Borders.THIN} solid {Colors.GRAY_300}",
                                                                "borderRadius": "10px",
                                                                "padding": "14px 16px",
                                                            },
                                                            children=[
                                                                html.Div(
                                                                    "How parameters map to MVPF components",
                                                                    style={
                                                                        "fontSize": "13px",
                                                                        "fontWeight": "700",
                                                                        "color": "#111827",
                                                                        "marginBottom": Spacing.MD,
                                                                    },
                                                                ),
                                                                html.Div(
                                                                    style={
                                                                        "display": "grid",
                                                                        "gridTemplateColumns": "1fr 1fr",
                                                                        "gap": "14px",
                                                                    },
                                                                    children=[
                                                                        # Detainee Population
                                                                        html.Div(
                                                                            children=[
                                                                                html.Div(
                                                                                    "Detainee Population",
                                                                                    style={
                                                                                        "fontSize": FontSizes.LABEL,
                                                                                        "fontWeight": "700",
                                                                                        "color": "#111827",
                                                                                        "marginBottom": "6px",
                                                                                    },
                                                                                ),
                                                                                html.Div(
                                                                                    style={
                                                                                        "display": "flex",
                                                                                        "flexWrap": "wrap",
                                                                                        "gap": "6px",
                                                                                    },
                                                                                    children=[
                                                                                        html.Div(
                                                                                            "Detainee Harm",
                                                                                            style={
                                                                                                "fontSize": "11px",
                                                                                                "padding": "3px 8px",
                                                                                                "borderRadius": "999px",
                                                                                                "background": Colors.PRIMARY_BLUE_LIGHT,
                                                                                                "color": "#1e40af",
                                                                                            },
                                                                                        ),
                                                                                        html.Div(
                                                                                            "Court Appearance",
                                                                                            style={
                                                                                                "fontSize": "11px",
                                                                                                "padding": "3px 8px",
                                                                                                "borderRadius": "999px",
                                                                                                "background": Colors.SUCCESS_LIGHT,
                                                                                                "color": "#166534",
                                                                                            },
                                                                                        ),
                                                                                        html.Div(
                                                                                            "Crime Effect",
                                                                                            style={
                                                                                                "fontSize": "11px",
                                                                                                "padding": "3px 8px",
                                                                                                "borderRadius": "999px",
                                                                                                "background": Colors.SUCCESS_LIGHT,
                                                                                                "color": "#166534",
                                                                                            },
                                                                                        ),
                                                                                        html.Div(
                                                                                            "Community Spillovers",
                                                                                            style={
                                                                                                "fontSize": "11px",
                                                                                                "padding": "3px 8px",
                                                                                                "borderRadius": "999px",
                                                                                                "background": Colors.SUCCESS_LIGHT,
                                                                                                "color": "#166534",
                                                                                            },
                                                                                        ),
                                                                                        html.Div(
                                                                                            "Crime Cost",
                                                                                            style={
                                                                                                "fontSize": "11px",
                                                                                                "padding": "3px 8px",
                                                                                                "borderRadius": "999px",
                                                                                                "background": "#fecaca",
                                                                                                "color": "#7f1d1d",
                                                                                            },
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        # Length of Stay
                                                                        html.Div(
                                                                            children=[
                                                                                html.Div(
                                                                                    "Length of Stay",
                                                                                    style={
                                                                                        "fontSize": FontSizes.LABEL,
                                                                                        "fontWeight": "700",
                                                                                        "color": "#111827",
                                                                                        "marginBottom": "6px",
                                                                                    },
                                                                                ),
                                                                                html.Div(
                                                                                    style={
                                                                                        "display": "flex",
                                                                                        "flexWrap": "wrap",
                                                                                        "gap": "6px",
                                                                                    },
                                                                                    children=[
                                                                                        html.Div(
                                                                                            "Detainee Harm",
                                                                                            style={
                                                                                                "fontSize": "11px",
                                                                                                "padding": "3px 8px",
                                                                                                "borderRadius": "999px",
                                                                                                "background": Colors.PRIMARY_BLUE_LIGHT,
                                                                                                "color": "#1e40af",
                                                                                            },
                                                                                        ),
                                                                                        html.Div(
                                                                                            "Community Spillovers",
                                                                                            style={
                                                                                                "fontSize": "11px",
                                                                                                "padding": "3px 8px",
                                                                                                "borderRadius": "999px",
                                                                                                "background": Colors.SUCCESS_LIGHT,
                                                                                                "color": "#166534",
                                                                                            },
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        # Crime Effect
                                                                        html.Div(
                                                                            children=[
                                                                                html.Div(
                                                                                    "Crime Effect Assumption",
                                                                                    style={
                                                                                        "fontSize": FontSizes.LABEL,
                                                                                        "fontWeight": "700",
                                                                                        "color": "#111827",
                                                                                        "marginBottom": "6px",
                                                                                    },
                                                                                ),
                                                                                html.Div(
                                                                                    style={
                                                                                        "display": "flex",
                                                                                        "flexWrap": "wrap",
                                                                                        "gap": "6px",
                                                                                    },
                                                                                    children=[
                                                                                        html.Div(
                                                                                            "Crime Effect",
                                                                                            style={
                                                                                                "fontSize": "11px",
                                                                                                "padding": "3px 8px",
                                                                                                "borderRadius": "999px",
                                                                                                "background": Colors.SUCCESS_LIGHT,
                                                                                                "color": "#166534",
                                                                                            },
                                                                                        ),
                                                                                        html.Div(
                                                                                            "Crime Cost",
                                                                                            style={
                                                                                                "fontSize": "11px",
                                                                                                "padding": "3px 8px",
                                                                                                "borderRadius": "999px",
                                                                                                "background": "#fecaca",
                                                                                                "color": "#7f1d1d",
                                                                                            },
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        # Felony Share
                                                                        html.Div(
                                                                            children=[
                                                                                html.Div(
                                                                                    "Felony Share",
                                                                                    style={
                                                                                        "fontSize": FontSizes.LABEL,
                                                                                        "fontWeight": "700",
                                                                                        "color": "#111827",
                                                                                        "marginBottom": "6px",
                                                                                    },
                                                                                ),
                                                                                html.Div(
                                                                                    style={
                                                                                        "display": "flex",
                                                                                        "flexWrap": "wrap",
                                                                                        "gap": "6px",
                                                                                    },
                                                                                    children=[
                                                                                        html.Div(
                                                                                            "Crime Effect",
                                                                                            style={
                                                                                                "fontSize": "11px",
                                                                                                "padding": "3px 8px",
                                                                                                "borderRadius": "999px",
                                                                                                "background": Colors.SUCCESS_LIGHT,
                                                                                                "color": "#166534",
                                                                                            },
                                                                                        ),
                                                                                        html.Div(
                                                                                            "Crime Cost",
                                                                                            style={
                                                                                                "fontSize": "11px",
                                                                                                "padding": "3px 8px",
                                                                                                "borderRadius": "999px",
                                                                                                "background": "#fecaca",
                                                                                                "color": "#7f1d1d",
                                                                                            },
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ],
                                                        ),
                                                        # Components breakdown
                                                        html.Div(
                                                            id="components-breakdown",
                                                            style={
                                                                "marginTop": Spacing.XXL,
                                                                "paddingTop": Spacing.XXL,
                                                                "borderTop": f"{{Borders.THIN}} solid {Colors.GRAY_300}",
                                                            },
                                                            children=[
                                                                html.H4(
                                                                    content.get(
                                                                        "components_breakdown.title",
                                                                        "Components",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.H5,
                                                                        "fontWeight": "600",
                                                                        "color": Colors.GRAY_900,
                                                                        "marginTop": "0",
                                                                        "marginBottom": Spacing.LG,
                                                                    },
                                                                ),
                                                                html.Div(
                                                                    style={
                                                                        "display": "grid",
                                                                        "gridTemplateColumns": "1fr 1fr 1fr",
                                                                        "gap": Spacing.LG,
                                                                    },
                                                                    children=[
                                                                        # Detainee Values
                                                                        html.Div(
                                                                            id="detainee-values-section",
                                                                            style={
                                                                                "background": "white",
                                                                                "padding": Spacing.XL,
                                                                                "borderRadius": "8px",
                                                                                "borderLeft": f"{{Borders.EXTRA_THICK}} solid {Colors.PRIMARY_BLUE_DARK}",
                                                                            },
                                                                            children=[
                                                                                html.H5(
                                                                                    content.get(
                                                                                        "components_breakdown.detainee_values.title",
                                                                                        "Detainee Values",
                                                                                    ),
                                                                                    style={
                                                                                        "fontSize": "15px",
                                                                                        "fontWeight": "600",
                                                                                        "color": Colors.PRIMARY_BLUE_DARK,
                                                                                        "margin": f"0 0 {Spacing.MD} 0",
                                                                                    },
                                                                                ),
                                                                                html.P(
                                                                                    content.get(
                                                                                        "components_breakdown.detainee_values.description",
                                                                                        "Detainee Values capture the total harm detention imposes on people who are jailed. "
                                                                                        "We measure this using a willingness-to-pay lens, estimating how much a person would trade "
                                                                                        "to avoid being detained. This reflects short-term harms, disruptions to work and family life, "
                                                                                        "and long-term effects on health, income, and stability.",
                                                                                    ),
                                                                                    style={
                                                                                        "fontSize": FontSizes.BODY,
                                                                                        "color": Colors.GRAY_900,
                                                                                        "margin": f"0 0 {Spacing.MD} 0",
                                                                                        "lineHeight": LineHeights.RELAXED,
                                                                                    },
                                                                                ),
                                                                                # Subcomponents header
                                                                                html.Div(
                                                                                    className="label-with-info",
                                                                                    children=[
                                                                                        html.Span(
                                                                                            content.get(
                                                                                                "components_breakdown.detainee_values.subcomponents_label",
                                                                                                "Subcomponents",
                                                                                            ),
                                                                                            style={
                                                                                                "fontWeight": "500",
                                                                                                "fontSize": FontSizes.BODY,
                                                                                            },
                                                                                        )
                                                                                    ],
                                                                                ),
                                                                                html.Div(
                                                                                    children=[
                                                                                        # RHV
                                                                                        html.Div(
                                                                                            [
                                                                                                html.Button(
                                                                                                    content.get(
                                                                                                        "components_breakdown.detainee_values.subcomponents.harm_valuation.button_text",
                                                                                                        "Detainee Harm: Willingness to Pay derived from Relative Harm Valuation",
                                                                                                    ),
                                                                                                    id="detainee-harm-btn",
                                                                                                    n_clicks=0,
                                                                                                    className="collapse-toggle",
                                                                                                    style={
                                                                                                        "backgroundColor": Colors.NAVY_MEDIUM,
                                                                                                        "color": Colors.GRAY_300,
                                                                                                    },
                                                                                                ),
                                                                                                html.Div(
                                                                                                    id="detainee-harm",
                                                                                                    style={
                                                                                                        "display": "none"
                                                                                                    },
                                                                                                    children=[
                                                                                                        dcc.Markdown(
                                                                                                            content.get(
                                                                                                                "components_breakdown.detainee_values.subcomponents.harm_valuation.explanation",
                                                                                                                "",
                                                                                                            ),
                                                                                                            style={
                                                                                                                "fontSize": "13px",
                                                                                                                "color": Colors.GRAY_600,
                                                                                                                "margin": "6px 0",
                                                                                                            },
                                                                                                        )
                                                                                                    ],
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        # Willingness to Pay for Freedom
                                                                                        html.Div(
                                                                                            [
                                                                                                html.Button(
                                                                                                    content.get(
                                                                                                        "components_breakdown.detainee_values.subcomponents.wtp_freedom.button_text",
                                                                                                        "Detainee Harm: Willingness to Pay for Freedom",
                                                                                                    ),
                                                                                                    id="detainee-wtp-btn",
                                                                                                    n_clicks=0,
                                                                                                    className="collapse-toggle",
                                                                                                    style={
                                                                                                        "backgroundColor": Colors.NAVY_MEDIUM,
                                                                                                        "color": Colors.GRAY_300,
                                                                                                    },
                                                                                                ),
                                                                                                html.Div(
                                                                                                    id="detainee-wtp",
                                                                                                    style={
                                                                                                        "display": "none"
                                                                                                    },
                                                                                                    children=[
                                                                                                        dcc.Markdown(
                                                                                                            content.get(
                                                                                                                "components_breakdown.detainee_values.subcomponents.wtp_freedom.explanation",
                                                                                                                "",
                                                                                                            ),
                                                                                                            style={
                                                                                                                "fontSize": "13px",
                                                                                                                "color": Colors.GRAY_600,
                                                                                                                "margin": "6px 0",
                                                                                                            },
                                                                                                        )
                                                                                                    ],
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ]
                                                                                ),
                                                                            ],
                                                                        ),
                                                                        # Society Values
                                                                        html.Div(
                                                                            id="society-values-section",
                                                                            style={
                                                                                "background": "white",
                                                                                "padding": Spacing.XL,
                                                                                "borderRadius": "8px",
                                                                                "borderLeft": f"{{Borders.EXTRA_THICK}} solid {Colors.SUCCESS_GREEN}",
                                                                            },
                                                                            children=[
                                                                                html.H5(
                                                                                    content.get(
                                                                                        "components_breakdown.society_values.title",
                                                                                        "Society Values",
                                                                                    ),
                                                                                    style={
                                                                                        "fontSize": "15px",
                                                                                        "fontWeight": "600",
                                                                                        "color": Colors.SUCCESS_GREEN,
                                                                                        "margin": f"0 0 {Spacing.MD} 0",
                                                                                    },
                                                                                ),
                                                                                html.P(
                                                                                    content.get(
                                                                                        "components_breakdown.society_values.description",
                                                                                        "Society Values measure how detention affects external factors like public safety, victimization risk, and community wellbeing. "
                                                                                        "These values summarize the effects felt by people outside the jail and convert those effects into a "
                                                                                        "common dollar scale for comparison.",
                                                                                    ),
                                                                                    style={
                                                                                        "fontSize": FontSizes.BODY,
                                                                                        "color": Colors.GRAY_900,
                                                                                        "margin": f"0 0 {Spacing.MD} 0",
                                                                                        "lineHeight": LineHeights.RELAXED,
                                                                                    },
                                                                                ),
                                                                                html.Div(
                                                                                    className="label-with-info",
                                                                                    children=[
                                                                                        html.Span(
                                                                                            content.get(
                                                                                                "components_breakdown.society_values.subcomponents_label",
                                                                                                "Subcomponents",
                                                                                            ),
                                                                                            style={
                                                                                                "fontWeight": "500",
                                                                                                "fontSize": FontSizes.BODY,
                                                                                            },
                                                                                        )
                                                                                    ],
                                                                                ),
                                                                                html.Div(
                                                                                    children=[
                                                                                        # 1. Crime Prevention
                                                                                        html.Div(
                                                                                            [
                                                                                                html.Button(
                                                                                                    content.get(
                                                                                                        "components_breakdown.society_values.subcomponents.crime_prevention.button_text",
                                                                                                        "Crime Prevention",
                                                                                                    ),
                                                                                                    id="society-crime-btn",
                                                                                                    n_clicks=0,
                                                                                                    className="collapse-toggle",
                                                                                                    style={
                                                                                                        "backgroundColor": Colors.NAVY_MEDIUM,
                                                                                                        "color": Colors.GRAY_300,
                                                                                                    },
                                                                                                ),
                                                                                                html.Div(
                                                                                                    id="society-crime",
                                                                                                    style={
                                                                                                        "display": "none"
                                                                                                    },
                                                                                                    children=[
                                                                                                        html.P(
                                                                                                            content.get(
                                                                                                                "components_breakdown.society_values.subcomponents.crime_prevention.explanation",
                                                                                                                "",
                                                                                                            ),
                                                                                                            style={
                                                                                                                "fontSize": "13px",
                                                                                                                "color": Colors.GRAY_600,
                                                                                                            },
                                                                                                        )
                                                                                                    ],
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        # 2. Court Appearance Effects
                                                                                        html.Div(
                                                                                            [
                                                                                                html.Button(
                                                                                                    content.get(
                                                                                                        "components_breakdown.society_values.subcomponents.court_appearance.button_text",
                                                                                                        "Court Appearance Effects",
                                                                                                    ),
                                                                                                    id="society-court-btn",
                                                                                                    n_clicks=0,
                                                                                                    className="collapse-toggle",
                                                                                                    style={
                                                                                                        "backgroundColor": Colors.NAVY_MEDIUM,
                                                                                                        "color": Colors.GRAY_300,
                                                                                                    },
                                                                                                ),
                                                                                                html.Div(
                                                                                                    id="society-court",
                                                                                                    style={
                                                                                                        "display": "none"
                                                                                                    },
                                                                                                    children=[
                                                                                                        dcc.Markdown(
                                                                                                            content.get(
                                                                                                                "components_breakdown.society_values.subcomponents.court_appearance.explanation",
                                                                                                                "",
                                                                                                            ),
                                                                                                            style={
                                                                                                                "fontSize": "13px",
                                                                                                                "color": Colors.GRAY_600,
                                                                                                            },
                                                                                                        )
                                                                                                    ],
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        # 3. Community Spillovers
                                                                                        html.Div(
                                                                                            [
                                                                                                html.Button(
                                                                                                    content.get(
                                                                                                        "components_breakdown.society_values.subcomponents.community_spillovers.button_text",
                                                                                                        "Community and Economic Spillovers",
                                                                                                    ),
                                                                                                    id="society-spill-btn",
                                                                                                    n_clicks=0,
                                                                                                    className="collapse-toggle",
                                                                                                    style={
                                                                                                        "backgroundColor": Colors.NAVY_MEDIUM,
                                                                                                        "color": Colors.GRAY_300,
                                                                                                    },
                                                                                                ),
                                                                                                html.Div(
                                                                                                    id="society-spill",
                                                                                                    style={
                                                                                                        "display": "none"
                                                                                                    },
                                                                                                    children=[
                                                                                                        html.P(
                                                                                                            content.get(
                                                                                                                "components_breakdown.society_values.subcomponents.community_spillovers.explanation",
                                                                                                                "",
                                                                                                            ),
                                                                                                            style={
                                                                                                                "fontSize": "13px",
                                                                                                                "color": Colors.GRAY_600,
                                                                                                            },
                                                                                                        )
                                                                                                    ],
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ]
                                                                                ),
                                                                            ],
                                                                        ),
                                                                        # Government Cost
                                                                        html.Div(
                                                                            id="government-cost-section",
                                                                            style={
                                                                                "background": "white",
                                                                                "padding": Spacing.XL,
                                                                                "borderRadius": "8px",
                                                                                "borderLeft": f"{{Borders.EXTRA_THICK}} solid {Colors.ERROR_RED}",
                                                                            },
                                                                            children=[
                                                                                html.H5(
                                                                                    content.get(
                                                                                        "components_breakdown.government_cost.title",
                                                                                        "Government Cost",
                                                                                    ),
                                                                                    style={
                                                                                        "fontSize": "15px",
                                                                                        "fontWeight": "600",
                                                                                        "color": Colors.ERROR_RED,
                                                                                        "margin": f"0 0 {Spacing.MD} 0",
                                                                                    },
                                                                                ),
                                                                                html.P(
                                                                                    content.get(
                                                                                        "components_breakdown.government_cost.description",
                                                                                        "Government Cost reflects all public spending required to run the detention system. This includes daily "
                                                                                        "operations, staffing, healthcare, facilities, court processing, and administrative overhead. It represents "
                                                                                        "the fiscal cost taxpayers bear to support the current level of detention.",
                                                                                    ),
                                                                                    style={
                                                                                        "fontSize": FontSizes.BODY,
                                                                                        "color": Colors.GRAY_900,
                                                                                        "margin": f"0 0 {Spacing.MD} 0",
                                                                                        "lineHeight": LineHeights.RELAXED,
                                                                                    },
                                                                                ),
                                                                                html.Div(
                                                                                    className="label-with-info",
                                                                                    children=[
                                                                                        html.Span(
                                                                                            content.get(
                                                                                                "components_breakdown.government_cost.subcomponents_label",
                                                                                                "Subcomponents",
                                                                                            ),
                                                                                            style={
                                                                                                "fontWeight": "500",
                                                                                                "fontSize": FontSizes.BODY,
                                                                                            },
                                                                                        )
                                                                                    ],
                                                                                ),
                                                                                html.Div(
                                                                                    children=[
                                                                                        # Operational Cost
                                                                                        html.Div(
                                                                                            [
                                                                                                html.Button(
                                                                                                    content.get(
                                                                                                        "components_breakdown.government_cost.subcomponents.operational.button_text",
                                                                                                        "Operational Costs",
                                                                                                    ),
                                                                                                    id="gov-op-btn",
                                                                                                    n_clicks=0,
                                                                                                    className="collapse-toggle",
                                                                                                    style={
                                                                                                        "backgroundColor": Colors.NAVY_MEDIUM,
                                                                                                        "color": Colors.GRAY_300,
                                                                                                    },
                                                                                                ),
                                                                                                html.Div(
                                                                                                    id="gov-op",
                                                                                                    style={
                                                                                                        "display": "none"
                                                                                                    },
                                                                                                    children=[
                                                                                                        dcc.Markdown(
                                                                                                            content.get(
                                                                                                                "components_breakdown.government_cost.subcomponents.operational.explanation",
                                                                                                                "",
                                                                                                            ),
                                                                                                            style={
                                                                                                                "fontSize": "13px",
                                                                                                                "color": Colors.GRAY_600,
                                                                                                            },
                                                                                                        )
                                                                                                    ],
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        # Crime Effect Costs
                                                                                        html.Div(
                                                                                            [
                                                                                                html.Button(
                                                                                                    content.get(
                                                                                                        "components_breakdown.government_cost.subcomponents.crime_decrease.button_text",
                                                                                                        "Costs associated with Crime Effect: Decrease",
                                                                                                    ),
                                                                                                    id="gov-crime-decrease-btn",
                                                                                                    n_clicks=0,
                                                                                                    className="collapse-toggle",
                                                                                                    style={
                                                                                                        "backgroundColor": Colors.NAVY_MEDIUM,
                                                                                                        "color": Colors.GRAY_300,
                                                                                                    },
                                                                                                ),
                                                                                                html.Div(
                                                                                                    id="gov-crime-decrease",
                                                                                                    style={
                                                                                                        "display": "none"
                                                                                                    },
                                                                                                    children=[
                                                                                                        dcc.Markdown(
                                                                                                            content.get(
                                                                                                                "components_breakdown.government_cost.subcomponents.crime_decrease.explanation",
                                                                                                                "",
                                                                                                            ),
                                                                                                            style={
                                                                                                                "fontSize": "13px",
                                                                                                                "color": Colors.GRAY_600,
                                                                                                            },
                                                                                                        )
                                                                                                    ],
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ]
                                                                                ),
                                                                            ],
                                                                        ),
                                                                    ],
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                        # Scenarios section
                                        html.Div(
                                            className="chart-container",
                                            style={
                                                "background": Colors.GRAY_100,
                                                "marginTop": Spacing.XXXL,
                                            },
                                            children=[
                                                html.H3(
                                                    content.get(
                                                        "mvpf_explainer.scenarios_heading",
                                                        "Scenarios",
                                                    ),
                                                    style={
                                                        "fontSize": FontSizes.H4,
                                                        "fontWeight": "600",
                                                        "color": Colors.NAVY_DARK,
                                                        "marginBottom": Spacing.LG,
                                                        "marginTop": "0",
                                                    },
                                                ),
                                                html.P(
                                                    content.get("alt_scenarios.paragraph_1", ""),
                                                    style={
                                                        "fontSize": "15px",
                                                        "color": Colors.GRAY_800,
                                                        "marginBottom": Spacing.MD,
                                                    },
                                                ),
                                                html.P(
                                                    content.get("alt_scenarios.paragraph_2", ""),
                                                    style={
                                                        "fontSize": "15px",
                                                        "color": Colors.GRAY_800,
                                                        "marginBottom": Spacing.MD,
                                                    },
                                                ),
                                                html.P(
                                                    content.get("alt_scenarios.paragraph_3", ""),
                                                    style={
                                                        "fontSize": "15px",
                                                        "color": Colors.GRAY_800,
                                                        "marginBottom": Spacing.XL,
                                                    },
                                                ),
                                                html.Div(
                                                    style={
                                                        "display": "grid",
                                                        "gridTemplateColumns": "1fr 1fr 1fr",
                                                        "gap": Spacing.LG,
                                                    },
                                                    children=[
                                                        # Baseline Scenario
                                                        html.Div(
                                                            id="scenario-baseline",
                                                            className="jumbotron",
                                                            style={
                                                                "background": "white",
                                                                "padding": Spacing.XL,
                                                                "borderRadius": "8px",
                                                                "borderLeft": f"{{Borders.EXTRA_THICK}} solid {Colors.PRIMARY_BLUE_DARK}",
                                                            },
                                                            children=[
                                                                html.H4(
                                                                    content.get(
                                                                        "scenarios_explained.baseline.title",
                                                                        "Baseline Scenario",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.H5,
                                                                        "fontWeight": "600",
                                                                        "color": Colors.PRIMARY_BLUE_DARK,
                                                                        "margin": f"0 0 {Spacing.MD} 0",
                                                                    },
                                                                ),
                                                                html.P(
                                                                    content.get(
                                                                        "scenarios_explained.baseline.description",
                                                                        "Focuses on individual harm to detainees plus potential criminogenic effects of detention.",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.BODY,
                                                                        "color": Colors.GRAY_900,
                                                                        "lineHeight": LineHeights.RELAXED,
                                                                        "margin": "0",
                                                                    },
                                                                ),
                                                            ],
                                                        ),
                                                        # Most Conservative Scenario
                                                        html.Div(
                                                            id="scenario-most-conservative",
                                                            className="jumbotron",
                                                            style={
                                                                "background": "white",
                                                                "padding": Spacing.XL,
                                                                "borderRadius": "8px",
                                                                "borderLeft": f"{Borders.EXTRA_THICK} solid Colors.WARNING_YELLOW",
                                                            },
                                                            children=[
                                                                html.H4(
                                                                    content.get(
                                                                        "scenarios_explained.most_conservative.title",
                                                                        "Conservative Scenario",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.H5,
                                                                        "fontWeight": "600",
                                                                        "color": Colors.WARNING_YELLOW,
                                                                        "margin": f"0 0 {Spacing.MD} 0",
                                                                    },
                                                                ),
                                                                html.P(
                                                                    content.get(
                                                                        "scenarios_explained.most_conservative.description",
                                                                        "Uses smaller survey-based estimates to value detainee harm, producing less negative MVPF values.",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.BODY,
                                                                        "color": Colors.GRAY_900,
                                                                        "lineHeight": LineHeights.RELAXED,
                                                                        "margin": "0",
                                                                    },
                                                                ),
                                                            ],
                                                        ),
                                                        # Least Conservative Scenario
                                                        html.Div(
                                                            id="scenario-least-conservative",
                                                            className="jumbotron",
                                                            style={
                                                                "background": "white",
                                                                "padding": Spacing.XL,
                                                                "borderRadius": "8px",
                                                                "borderLeft": f"{{Borders.EXTRA_THICK}} solid {Colors.SUCCESS_GREEN}",
                                                            },
                                                            children=[
                                                                html.H4(
                                                                    content.get(
                                                                        "scenarios_explained.least_conservative.title",
                                                                        "Least Conservative Scenario",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.H5,
                                                                        "fontWeight": "600",
                                                                        "color": Colors.SUCCESS_GREEN,
                                                                        "margin": f"0 0 {Spacing.MD} 0",
                                                                    },
                                                                ),
                                                                html.P(
                                                                    content.get(
                                                                        "scenarios_explained.least_conservative.description",
                                                                        "Includes broad social harms to communities and families, plus criminogenic effects of detention.",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.BODY,
                                                                        "color": Colors.GRAY_900,
                                                                        "lineHeight": LineHeights.RELAXED,
                                                                        "margin": "0",
                                                                    },
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                        # Parameters section
                                        html.Div(
                                            className="chart-container",
                                            style={
                                                "background": Colors.GRAY_100,
                                                "marginTop": Spacing.XXXL,
                                            },
                                            children=[
                                                html.H3(
                                                    content.get(
                                                        "mvpf_explainer.analysis_parameters.heading",
                                                        "Analysis Parameters",
                                                    ),
                                                    style={
                                                        "fontSize": FontSizes.H4,
                                                        "fontWeight": "600",
                                                        "color": Colors.NAVY_DARK,
                                                        "marginBottom": Spacing.LG,
                                                        "marginTop": "0",
                                                    },
                                                ),
                                                html.P(
                                                    content.get(
                                                        "mvpf_explainer.analysis_parameters.description",
                                                        "You can adjust several parameters that act as multipliers to the components in the MVPF set-up. These inputs scale the numerator and denominator components of the MVPF and let you test how sensitive the results are to policy or system changes. The defaults for each parameter capture the picture of Cook County Jail in 2018. The other options available are outer bounds for sensitivity analysis, and some alternatives based on our broad review of the literature.",
                                                    ),
                                                    style={
                                                        "fontSize": "15px",
                                                        "color": Colors.GRAY_800,
                                                        "marginBottom": Spacing.XL,
                                                    },
                                                ),
                                                html.Div(
                                                    style={
                                                        "display": "grid",
                                                        "gridTemplateColumns": "1fr 1fr",
                                                        "gap": Spacing.LG,
                                                    },
                                                    children=[
                                                        # Felony Rate
                                                        html.Div(
                                                            id="parameter-felony-rate",
                                                            className="jumbotron",
                                                            style={
                                                                "background": "white",
                                                                "padding": Spacing.XL,
                                                                "borderRadius": "8px",
                                                                "borderLeft": f"{{Borders.EXTRA_THICK}} solid {Colors.PRIMARY_BLUE}",
                                                            },
                                                            children=[
                                                                html.H4(
                                                                    content.get(
                                                                        "parameters.felony_rate.title",
                                                                        "Felony Rate",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.H5,
                                                                        "fontWeight": "600",
                                                                        "color": Colors.PRIMARY_BLUE,
                                                                        "margin": f"0 0 {Spacing.MD} 0",
                                                                    },
                                                                ),
                                                                html.Div(
                                                                    children=[
                                                                        html.Div(
                                                                            style={
                                                                                "marginBottom": "10px"
                                                                            },
                                                                            children=[
                                                                                html.Div(
                                                                                    sec.get(
                                                                                        "label", ""
                                                                                    ),
                                                                                    style={
                                                                                        "fontSize": FontSizes.LABEL,
                                                                                        "fontWeight": "700",
                                                                                        "color": Colors.GRAY_900,
                                                                                        "textTransform": "uppercase",
                                                                                        "letterSpacing": "0.04em",
                                                                                        "marginBottom": Spacing.XS,
                                                                                    },
                                                                                ),
                                                                                dcc.Markdown(
                                                                                    sec.get(
                                                                                        "text", ""
                                                                                    ),
                                                                                    style={
                                                                                        "fontSize": "13px",
                                                                                        "color": Colors.GRAY_900,
                                                                                        "lineHeight": LineHeights.NORMAL,
                                                                                        "margin": "0",
                                                                                    },
                                                                                ),
                                                                            ],
                                                                        )
                                                                        for sec in content.get(
                                                                            "parameters.felony_rate.sections",
                                                                            [],
                                                                        )
                                                                        if sec.get("text")
                                                                    ]
                                                                ),
                                                            ],
                                                        ),
                                                        # Detainee Population
                                                        html.Div(
                                                            id="parameter-detainee-population",
                                                            className="jumbotron",
                                                            style={
                                                                "background": "white",
                                                                "padding": Spacing.XL,
                                                                "borderRadius": "8px",
                                                                "borderLeft": f"{Borders.EXTRA_THICK} solid #10b981",
                                                            },
                                                            children=[
                                                                html.H4(
                                                                    content.get(
                                                                        "parameters.detainee_population.title",
                                                                        "Detainee Population",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.H5,
                                                                        "fontWeight": "600",
                                                                        "color": "#10b981",
                                                                        "margin": f"0 0 {Spacing.MD} 0",
                                                                    },
                                                                ),
                                                                html.Div(
                                                                    children=[
                                                                        html.Div(
                                                                            style={
                                                                                "marginBottom": "10px"
                                                                            },
                                                                            children=[
                                                                                html.Div(
                                                                                    sec.get(
                                                                                        "label", ""
                                                                                    ),
                                                                                    style={
                                                                                        "fontSize": FontSizes.LABEL,
                                                                                        "fontWeight": "700",
                                                                                        "color": Colors.GRAY_900,
                                                                                        "textTransform": "uppercase",
                                                                                        "letterSpacing": "0.04em",
                                                                                        "marginBottom": Spacing.XS,
                                                                                    },
                                                                                ),
                                                                                dcc.Markdown(
                                                                                    sec.get(
                                                                                        "text", ""
                                                                                    ),
                                                                                    style={
                                                                                        "fontSize": "13px",
                                                                                        "color": Colors.GRAY_900,
                                                                                        "lineHeight": LineHeights.NORMAL,
                                                                                        "margin": "0",
                                                                                    },
                                                                                ),
                                                                            ],
                                                                        )
                                                                        for sec in content.get(
                                                                            "parameters.detainee_population.sections",
                                                                            [],
                                                                        )
                                                                        if sec.get("text")
                                                                    ]
                                                                ),
                                                            ],
                                                        ),
                                                        # Length of Stay
                                                        html.Div(
                                                            id="parameter-length-of-stay",
                                                            className="jumbotron",
                                                            style={
                                                                "background": "white",
                                                                "padding": Spacing.XL,
                                                                "borderRadius": "8px",
                                                                "borderLeft": f"{Borders.EXTRA_THICK} solid #f59e0b",
                                                            },
                                                            children=[
                                                                html.H4(
                                                                    content.get(
                                                                        "parameters.length_of_stay.title",
                                                                        "Length of Stay",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.H5,
                                                                        "fontWeight": "600",
                                                                        "color": "#f59e0b",
                                                                        "margin": f"0 0 {Spacing.MD} 0",
                                                                    },
                                                                ),
                                                                html.Div(
                                                                    children=[
                                                                        html.Div(
                                                                            style={
                                                                                "marginBottom": "10px"
                                                                            },
                                                                            children=[
                                                                                html.Div(
                                                                                    sec.get(
                                                                                        "label", ""
                                                                                    ),
                                                                                    style={
                                                                                        "fontSize": FontSizes.LABEL,
                                                                                        "fontWeight": "700",
                                                                                        "color": Colors.GRAY_900,
                                                                                        "textTransform": "uppercase",
                                                                                        "letterSpacing": "0.04em",
                                                                                        "marginBottom": Spacing.XS,
                                                                                    },
                                                                                ),
                                                                                dcc.Markdown(
                                                                                    sec.get(
                                                                                        "text", ""
                                                                                    ),
                                                                                    style={
                                                                                        "fontSize": "13px",
                                                                                        "color": Colors.GRAY_900,
                                                                                        "lineHeight": LineHeights.NORMAL,
                                                                                        "margin": "0",
                                                                                    },
                                                                                ),
                                                                            ],
                                                                        )
                                                                        for sec in content.get(
                                                                            "parameters.length_of_stay.sections",
                                                                            [],
                                                                        )
                                                                        if sec.get("text")
                                                                    ]
                                                                ),
                                                            ],
                                                        ),
                                                        # Crime Effect
                                                        html.Div(
                                                            id="parameter-crime-effect",
                                                            className="jumbotron",
                                                            style={
                                                                "background": "white",
                                                                "padding": Spacing.XL,
                                                                "borderRadius": "8px",
                                                                "borderLeft": f"{Borders.EXTRA_THICK} solid #ef4444",
                                                            },
                                                            children=[
                                                                html.H4(
                                                                    content.get(
                                                                        "parameters.crime_effect.title",
                                                                        "Crime Effect",
                                                                    ),
                                                                    style={
                                                                        "fontSize": FontSizes.H5,
                                                                        "fontWeight": "600",
                                                                        "color": "#ef4444",
                                                                        "margin": f"0 0 {Spacing.MD} 0",
                                                                    },
                                                                ),
                                                                html.Div(
                                                                    children=[
                                                                        html.Div(
                                                                            style={
                                                                                "marginBottom": "10px"
                                                                            },
                                                                            children=[
                                                                                html.Div(
                                                                                    sec.get(
                                                                                        "label", ""
                                                                                    ),
                                                                                    style={
                                                                                        "fontSize": FontSizes.LABEL,
                                                                                        "fontWeight": "700",
                                                                                        "color": Colors.GRAY_900,
                                                                                        "textTransform": "uppercase",
                                                                                        "letterSpacing": "0.04em",
                                                                                        "marginBottom": Spacing.XS,
                                                                                    },
                                                                                ),
                                                                                dcc.Markdown(
                                                                                    sec.get(
                                                                                        "text", ""
                                                                                    ),
                                                                                    style={
                                                                                        "fontSize": "13px",
                                                                                        "color": Colors.GRAY_900,
                                                                                        "lineHeight": LineHeights.NORMAL,
                                                                                        "margin": "0",
                                                                                    },
                                                                                ),
                                                                            ],
                                                                        )
                                                                        for sec in content.get(
                                                                            "parameters.crime_effect.sections",
                                                                            [],
                                                                        )
                                                                        if sec.get("text")
                                                                    ]
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                        # Limitations section
                                        html.Div(
                                            style={"marginBottom": "0"},
                                            children=[
                                                html.H3(
                                                    content.get(
                                                        "mvpf_explainer.limitations.heading",
                                                        "Limitations and Considerations",
                                                    ),
                                                    style={
                                                        "fontSize": "18px",
                                                        "fontWeight": "600",
                                                        "color": Colors.GRAY_900,
                                                        "marginTop": "0",
                                                        "marginBottom": Spacing.MD,
                                                    },
                                                ),
                                                html.P(
                                                    content.get(
                                                        "mvpf_explainer.limitations.intro",
                                                        'This dashboard is a structured way to translate assumptions into an MVPF for pretrial detention. It is not a definitive estimate of detention\'s "true" social value.',
                                                    ),
                                                    style={
                                                        "fontSize": FontSizes.LABEL,
                                                        "color": Colors.GRAY_800,
                                                        "lineHeight": LineHeights.LOOSE,
                                                        "marginBottom": Spacing.MD,
                                                    },
                                                ),
                                                html.Ul(
                                                    style={
                                                        "fontSize": "15px",
                                                        "color": Colors.GRAY_800,
                                                        "lineHeight": LineHeights.LOOSE,
                                                        "marginBottom": Spacing.LG,
                                                    },
                                                    children=[
                                                        html.Li(item)
                                                        for item in content.get(
                                                            "mvpf_explainer.limitations.items",
                                                            [
                                                                "Normative choices drive results: the largest source of variation is how detainee harm is monetized (RHV vs WTP) and whether additional community spillovers are added.",
                                                                "Crime impacts are uncertain and context-dependent; in this dashboard, crime effects can affect both the numerator (social harms/benefits) and the denominator (public costs or savings).",
                                                                "Local transferability is limited: baseline costs and operating conditions are anchored to Cook County Jail in 2018 and may not generalize to other years or jurisdictions.",
                                                                "Component coverage is incomplete: the MVPF includes only impacts with usable estimates, so some downstream, distributional, or hard-to-monetize effects may be missing.",
                                                                'Interpret outputs as sensitivity analysis ("what the MVPF would be if these assumptions held"), not as a prediction of what will happen under a policy change.',
                                                            ],
                                                        )
                                                    ],
                                                ),
                                                html.P(
                                                    "This tool is designed to inform policy discussions and should be used alongside other evidence, "
                                                    "stakeholder input, and contextual knowledge about Cook County Jail operations.",
                                                    style={
                                                        "fontSize": FontSizes.LABEL,
                                                        "color": Colors.GRAY_800,
                                                        "lineHeight": LineHeights.LOOSE,
                                                        "margin": "0",
                                                        "fontStyle": "italic",
                                                    },
                                                ),
                                            ],
                                        ),
                                    ],
                                )
                            ],
                        ),
                        # Tab 5: About this Data Tool
                        dcc.Tab(
                            label="About",
                            value="tab-about",
                            style={
                                "padding": f"{Spacing.MD} {Spacing.XXL}",
                                "fontWeight": "500",
                                "fontSize": FontSizes.BODY,
                            },
                            selected_style={
                                "padding": f"{Spacing.MD} {Spacing.XXL}",
                                "fontWeight": "600",
                                "fontSize": FontSizes.BODY,
                                "borderTop": f"{{Borders.THICK}} solid {Colors.PRIMARY_BLUE}",
                                "backgroundColor": "white",
                            },
                            children=[
                                html.Div(
                                    style={
                                        "padding": "24px 0",
                                        "maxWidth": "900px",
                                        "margin": "0 auto",
                                    },
                                    children=[
                                        # Contact Section
                                        html.H2(
                                            content.get("about.contact.title", "Contact"),
                                            style={
                                                "fontSize": "18px",
                                                "fontWeight": "bold",
                                                "color": Colors.NAVY_DARK,
                                                "marginTop": "0",
                                                "marginBottom": Spacing.LG,
                                            },
                                        ),
                                        html.P(
                                            content.get("about.contact.content", ""),
                                            style={
                                                "fontSize": FontSizes.LABEL,
                                                "color": Colors.GRAY_800,
                                                "lineHeight": LineHeights.LOOSE,
                                                "marginBottom": Spacing.XXXL,
                                            },
                                        ),
                                        # About Cook County Jail Section
                                        html.H2(
                                            content.get(
                                                "about.about_ccj.title", "About Cook County Jail"
                                            ),
                                            style={
                                                "fontSize": "18px",
                                                "fontWeight": "bold",
                                                "color": Colors.NAVY_DARK,
                                                "marginTop": "0",
                                                "marginBottom": Spacing.LG,
                                            },
                                        ),
                                        html.P(
                                            content.get("about.about_ccj.content", ""),
                                            style={
                                                "fontSize": FontSizes.LABEL,
                                                "color": Colors.GRAY_800,
                                                "lineHeight": LineHeights.LOOSE,
                                                "marginBottom": Spacing.XXXL,
                                            },
                                        ),
                                        # Data Sources Section
                                        html.H2(
                                            content.get("about.data_sources.title", "Data Sources"),
                                            style={
                                                "fontSize": "18px",
                                                "fontWeight": "bold",
                                                "color": Colors.NAVY_DARK,
                                                "marginTop": "0",
                                                "marginBottom": Spacing.LG,
                                            },
                                        ),
                                        dcc.Markdown(
                                            content.get("about.data_sources.content", ""),
                                            style={
                                                "fontSize": FontSizes.LABEL,
                                                "color": Colors.GRAY_800,
                                                "lineHeight": LineHeights.LOOSE,
                                                "marginBottom": Spacing.XXXL,
                                            },
                                        ),
                                        # Acknowledgements Section
                                        html.H2(
                                            content.get(
                                                "about.acknowledgements.title", "Acknowledgements"
                                            ),
                                            style={
                                                "fontSize": "18px",
                                                "fontWeight": "bold",
                                                "color": Colors.NAVY_DARK,
                                                "marginTop": "0",
                                                "marginBottom": Spacing.LG,
                                            },
                                        ),
                                        html.P(
                                            content.get("about.acknowledgements.development", ""),
                                            style={
                                                "fontSize": FontSizes.LABEL,
                                                "color": Colors.GRAY_800,
                                                "lineHeight": LineHeights.LOOSE,
                                                "marginBottom": Spacing.LG,
                                            },
                                        ),
                                        html.P(
                                            content.get("about.acknowledgements.framework", ""),
                                            style={
                                                "fontSize": FontSizes.LABEL,
                                                "color": Colors.GRAY_800,
                                                "lineHeight": LineHeights.LOOSE,
                                                "marginBottom": Spacing.LG,
                                            },
                                        ),
                                        html.P(
                                            content.get("about.acknowledgements.data_access", ""),
                                            style={
                                                "fontSize": FontSizes.LABEL,
                                                "color": Colors.GRAY_800,
                                                "lineHeight": LineHeights.LOOSE,
                                                "marginBottom": "48px",
                                            },
                                        ),
                                    ],
                                )
                            ],
                        ),
                    ],
                ),
                # Standalone Disclaimer Section (outside of tabs)
                html.Div(
                    style={
                        "maxWidth": "900px",
                        "margin": f"{Spacing.LG} auto {Spacing.XXL} auto",
                        "padding": Spacing.MD,
                        "backgroundColor": Colors.GRAY_200,
                        "borderLeft": f"{Borders.EXTRA_THICK} solid {Colors.TEAL_PRIMARY}",
                        "borderRadius": BorderRadius.SM,
                    },
                    children=[
                        html.H2(
                            content.get("about.disclaimer.title", "Disclaimer"),
                            style={
                                "fontSize": FontSizes.EXTRA_SMALL,
                                "fontWeight": "600",
                                "color": Colors.NAVY_DARK,
                                "marginTop": "0",
                                "marginBottom": Spacing.SM,
                                "textTransform": "uppercase",
                                "letterSpacing": "0.5px",
                            },
                        ),
                        html.P(
                            content.get("about.disclaimer.content", ""),
                            style={
                                "fontSize": FontSizes.TINY,
                                "color": Colors.GRAY_800,
                                "lineHeight": LineHeights.TIGHT,
                                "margin": "0",
                            },
                        ),
                    ],
                ),
            ],
        ),
    ],
)

# =============================================================================
# CALLBACKS MODULE
# All dashboard callbacks are registered via register_callbacks()
# =============================================================================


def _get_scenario_description(scenario):
    """Return the description for a given scenario."""
    descriptions = {
        "baseline": "Represents current operations at Cook County Jail with standard parameters. This scenario serves as the reference point for comparison.",
        "most conservative": "Uses conservative estimates for all parameters, minimizing potential benefits and maximizing costs. Provides a lower-bound estimate of MVPF.",
        "least conservative": "Uses optimistic estimates that maximize potential benefits and minimize costs. Provides an upper-bound estimate of MVPF.",
    }
    return descriptions.get(scenario, "No description available for this scenario.")


def _toggle_style(n_clicks, style):
    """Helper function to toggle visibility of collapsible sections."""
    if not n_clicks:
        return style or {"display": "none"}
    if not style or style.get("display") == "none":
        return {"display": "block"}
    return {"display": "none"}


def _convert_dropdown_to_params(
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


def _calculate_mvpf(
    scenario,
    detainee_param1,
    detainee_param2,
    society_param1,
    society_param2,
    detainee_baseline=None,
    crime_effect=0,
):
    """
    Calculate MVPF using the modular MVPFCalculator class.

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

    Returns:
    --------
    dict : MVPF results with all breakdowns
    """
    params = _convert_dropdown_to_params(
        fel_rate_sel=detainee_param1,
        n_detainees_sel=detainee_param2,
        n_society_sel=society_param1,
        los_days_sel=society_param2,
        n_detainees_base=detainee_baseline,
        crime_effect=crime_effect,
    )

    result = calculator.calculate(scenario, params)

    # Extract breakdown values for backwards compatibility
    detainee_breakdown = list(result["detainee_breakdown"].values())
    society_breakdown = list(result["society_breakdown"].values())
    govt_breakdown = list(result["govt_breakdown"].values())

    def safe_get(lst, index, default=0):
        try:
            return lst[index]
        except IndexError:
            return default

    result["detainee_sub1"] = safe_get(detainee_breakdown, 0)
    result["detainee_sub2"] = safe_get(detainee_breakdown, 1)
    result["society_sub1"] = safe_get(society_breakdown, 0)
    result["society_sub2"] = safe_get(society_breakdown, 1)
    result["society_sub3"] = safe_get(society_breakdown, 2)
    result["govt_sub1"] = safe_get(govt_breakdown, 0)
    result["govt_sub2"] = safe_get(govt_breakdown, 1)
    result["govt_sub3"] = safe_get(govt_breakdown, 2)

    return result


def _build_kpi_card(result, mvpf, badge_color, badge_text_color, label, params):
    """Build the KPI card component with subcomponent details and parameters."""

    # Build subcomponent lists for each main component
    detainee_subs = []
    for name, value in result.get("detainee_breakdown", {}).items():
        detainee_subs.append(
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "fontSize": FontSizes.LABEL,
                    "color": Colors.GRAY_600,
                    "marginTop": Spacing.XS,
                },
                children=[
                    html.Span(name, style={"maxWidth": "60%"}),
                    html.Span(
                        f"${int(value):,}",
                        style={"fontWeight": "500", "color": Colors.PRIMARY_BLUE_DARK},
                    ),
                ],
            )
        )

    society_subs = []
    for name, value in result.get("society_breakdown", {}).items():
        society_subs.append(
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "fontSize": FontSizes.LABEL,
                    "color": Colors.GRAY_600,
                    "marginTop": Spacing.XS,
                },
                children=[
                    html.Span(name, style={"maxWidth": "60%"}),
                    html.Span(
                        f"${int(value):,}",
                        style={"fontWeight": "500", "color": Colors.SUCCESS_GREEN},
                    ),
                ],
            )
        )

    govt_subs = []
    for name, value in result.get("govt_breakdown", {}).items():
        govt_subs.append(
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "fontSize": FontSizes.LABEL,
                    "color": Colors.GRAY_600,
                    "marginTop": Spacing.XS,
                },
                children=[
                    html.Span(name, style={"maxWidth": "60%"}),
                    html.Span(
                        f"${int(value):,}", style={"fontWeight": "500", "color": Colors.ERROR_RED}
                    ),
                ],
            )
        )

    return html.Div(
        className="kpi-card",
        children=[
            html.Div(
                className="kpi-header",
                style={"textAlign": "center"},
                children=[
                    html.H2(content.get("kpi_card.title", "MVPF Score"), className="kpi-title")
                ],
            ),
            html.Div(
                style={"textAlign": "center"},
                children=[
                    html.Span(f"{mvpf:.4f}", className="kpi-value"),
                    html.Span(content.get("kpi_card.ratio_label", "ratio"), className="kpi-ratio"),
                ],
            ),
            html.Div(
                className="kpi-interpretation",
                style={
                    "marginTop": Spacing.XXL,
                    "padding": Spacing.XL,
                    "background": "#f0f9ff",
                    "borderRadius": "8px",
                    "border": f"{Borders.THIN} solid #bfdbfe",
                },
                children=[
                    html.Div(
                        style={"marginBottom": Spacing.MD},
                        children=[
                            html.Span(
                                label,
                                className="kpi-badge",
                                style={
                                    "backgroundColor": badge_color,
                                    "color": badge_text_color,
                                    "display": "inline-block",
                                    "padding": "6px 14px",
                                    "borderRadius": "9999px",
                                    "fontSize": FontSizes.BODY,
                                    "fontWeight": "600",
                                },
                            )
                        ],
                    ),
                    html.P(
                        (
                            content.get(
                                "kpi_card.interpretation_positive",
                                "This indicates the program delivers more value than its cost.",
                            )
                            if mvpf > 1
                            else content.get(
                                "kpi_card.interpretation_negative",
                                "Consider reviewing program efficiency.",
                            )
                        ),
                        style={
                            "marginTop": "0",
                            "marginBottom": Spacing.LG,
                            "color": "#1e3a8a",
                            "fontSize": FontSizes.BODY,
                            "lineHeight": LineHeights.RELAXED,
                            "fontWeight": "500",
                        },
                    ),
                    html.Div(
                        style={
                            "marginTop": Spacing.LG,
                            "paddingTop": Spacing.LG,
                            "borderTop": f"{Borders.THIN} solid #bfdbfe",
                        },
                        children=[
                            html.H4(
                                content.get("interpretation_card.title", "How to Interpret"),
                                style={
                                    "fontSize": FontSizes.BODY,
                                    "fontWeight": "600",
                                    "color": "#1e3a8a",
                                    "marginTop": "0",
                                    "marginBottom": Spacing.MD,
                                },
                            ),
                            html.Ul(
                                style={
                                    "margin": "0",
                                    "paddingLeft": Spacing.XL,
                                    "color": "#1e40af",
                                    "fontSize": "13px",
                                    "lineHeight": LineHeights.LOOSE,
                                },
                                children=[
                                    html.Li(
                                        [
                                            html.Strong(
                                                content.get(
                                                    "interpretation_card.levels.very_high.threshold",
                                                    "MVPF ≥ 2.5:",
                                                )
                                            ),
                                            " "
                                            + content.get(
                                                "interpretation_card.levels.very_high.description",
                                                "Very high social return on investment",
                                            ),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong(
                                                content.get(
                                                    "interpretation_card.levels.positive.threshold",
                                                    "MVPF > 1:",
                                                )
                                            ),
                                            " "
                                            + content.get(
                                                "interpretation_card.levels.positive.description",
                                                "Program delivers more value than it costs",
                                            ),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong(
                                                content.get(
                                                    "interpretation_card.levels.neutral.threshold",
                                                    "MVPF = 1:",
                                                )
                                            ),
                                            " "
                                            + content.get(
                                                "interpretation_card.levels.neutral.description",
                                                "Program value equals its cost",
                                            ),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong(
                                                content.get(
                                                    "interpretation_card.levels.negative.threshold",
                                                    "MVPF < 1:",
                                                )
                                            ),
                                            " "
                                            + content.get(
                                                "interpretation_card.levels.negative.description",
                                                "Program costs more than the value it provides",
                                            ),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong(
                                                content.get(
                                                    "interpretation_card.levels.harmful.threshold",
                                                    "MVPF < 0:",
                                                )
                                            ),
                                            " "
                                            + content.get(
                                                "interpretation_card.levels.harmful.description",
                                                "Indicates program delivers net harm",
                                            ),
                                        ]
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # Calculation row -  above components
            html.Div(
                className="kpi-calculation",
                style={
                    "marginTop": Spacing.MD,
                    "marginBottom": Spacing.XXL,
                    "paddingTop": "0",
                    "borderTop": "none",
                },
                children=[
                    html.P(
                        [
                            html.Strong(content.get("kpi_card.calculation_label", "Calculation: ")),
                            f"MVPF = (${int(result['detainee_values']):,} + ${int(result['society_values']):,}) / ${int(result['govt_cost']):,} = {mvpf:.4f}",
                        ],
                        style={
                            "margin": "0",
                            "fontSize": FontSizes.H4,
                        },
                    )
                ],
            ),
            # Component sections in 3-column grid
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr", "gap": Spacing.LG},
                children=[
                    # Detainee Values Component
                    html.Div(
                        className="kpi-component",
                        children=[
                            html.Div(
                                style={
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "alignItems": "flex-start",
                                },
                                children=[
                                    html.Div(
                                        children=[
                                            html.A(
                                                href="#detainee-values-section",
                                                className="kpi-component-link",
                                                children=[
                                                    html.H4(
                                                        content.get(
                                                            "kpi_card.components.detainee.title",
                                                            "Values for Detainees",
                                                        )
                                                    )
                                                ],
                                            ),
                                            html.P(
                                                f"${int(result['detainee_values']):,}",
                                                style={
                                                    "color": Colors.PRIMARY_BLUE_DARK,
                                                    "margin": "0",
                                                },
                                            ),
                                        ]
                                    ),
                                    # Parameters on the right
                                    html.Div(
                                        style={
                                            "textAlign": "right",
                                            "fontSize": "11px",
                                            "color": Colors.GRAY_600,
                                        },
                                        children=[
                                            html.Div(
                                                [
                                                    html.Span(
                                                        content.get(
                                                            "kpi_card.parameter_labels.felony_rate",
                                                            "Felony Rate: ",
                                                        ),
                                                        style={"fontWeight": "500"},
                                                    ),
                                                    f"{params['fel_rate']:.1%}",
                                                ]
                                            ),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        content.get(
                                                            "kpi_card.parameter_labels.population_mult",
                                                            "Population Mult: ",
                                                        ),
                                                        style={"fontWeight": "500"},
                                                    ),
                                                    f"{params['n_detainees_mult']:.0%}",
                                                ]
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            # Subcomponents list
                            html.Div(
                                style={
                                    "marginTop": Spacing.MD,
                                    "paddingTop": Spacing.SM,
                                    "borderTop": f"{{Borders.THIN}} solid {Colors.GRAY_300}",
                                },
                                children=[
                                    html.Span(
                                        content.get(
                                            "kpi_card.subcomponents_label", "Subcomponents:"
                                        ),
                                        style={
                                            "fontSize": "11px",
                                            "fontWeight": "600",
                                            "color": Colors.GRAY_900,
                                            "textTransform": "uppercase",
                                        },
                                    ),
                                    html.Div(children=detainee_subs),
                                ],
                            ),
                        ],
                    ),
                    # Society Values Component
                    html.Div(
                        className="kpi-component",
                        children=[
                            html.Div(
                                style={
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "alignItems": "flex-start",
                                },
                                children=[
                                    html.Div(
                                        children=[
                                            html.A(
                                                href="#society-values-section",
                                                className="kpi-component-link",
                                                children=[
                                                    html.H4(
                                                        content.get(
                                                            "kpi_card.components.society.title",
                                                            "Value for Society",
                                                        )
                                                    )
                                                ],
                                            ),
                                            html.P(
                                                f"${int(result['society_values']):,}",
                                                style={
                                                    "color": Colors.SUCCESS_GREEN,
                                                    "margin": "0",
                                                },
                                            ),
                                        ]
                                    ),
                                    # Parameters on the right
                                    html.Div(
                                        style={
                                            "textAlign": "right",
                                            "fontSize": "11px",
                                            "color": Colors.GRAY_600,
                                        },
                                        children=[
                                            html.Div(
                                                [
                                                    html.Span(
                                                        content.get(
                                                            "kpi_card.parameter_labels.community_mult",
                                                            "Community Mult: ",
                                                        ),
                                                        style={"fontWeight": "500"},
                                                    ),
                                                    f"{params['n_society_mult']:.0%}",
                                                ]
                                            ),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        content.get(
                                                            "kpi_card.parameter_labels.length_of_stay",
                                                            "Length of Stay: ",
                                                        ),
                                                        style={"fontWeight": "500"},
                                                    ),
                                                    f"{params['los_days']:.0f} days",
                                                ]
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            # Subcomponents list
                            html.Div(
                                style={
                                    "marginTop": Spacing.MD,
                                    "paddingTop": Spacing.SM,
                                    "borderTop": f"{{Borders.THIN}} solid {Colors.GRAY_300}",
                                },
                                children=[
                                    html.Span(
                                        content.get(
                                            "kpi_card.subcomponents_label", "Subcomponents:"
                                        ),
                                        style={
                                            "fontSize": "11px",
                                            "fontWeight": "600",
                                            "color": Colors.GRAY_900,
                                            "textTransform": "uppercase",
                                        },
                                    ),
                                    html.Div(children=society_subs),
                                ],
                            ),
                        ],
                    ),
                    # Government Costs Component
                    html.Div(
                        className="kpi-component",
                        children=[
                            html.Div(
                                style={
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "alignItems": "flex-start",
                                },
                                children=[
                                    html.Div(
                                        children=[
                                            html.A(
                                                href="#government-cost-section",
                                                className="kpi-component-link",
                                                children=[
                                                    html.H4(
                                                        content.get(
                                                            "kpi_card.components.government.title",
                                                            "Government Costs",
                                                        )
                                                    )
                                                ],
                                            ),
                                            html.P(
                                                f"${int(result['govt_cost']):,}",
                                                style={"color": Colors.ERROR_RED, "margin": "0"},
                                            ),
                                        ]
                                    ),
                                    # Parameters on the right
                                    html.Div(
                                        style={
                                            "textAlign": "right",
                                            "fontSize": "11px",
                                            "color": Colors.GRAY_600,
                                        },
                                        children=[
                                            html.Div(
                                                [
                                                    html.Span(
                                                        content.get(
                                                            "kpi_card.parameter_labels.population_mult",
                                                            "Population Mult: ",
                                                        ),
                                                        style={"fontWeight": "500"},
                                                    ),
                                                    f"{params['n_detainees_mult']:.0%}",
                                                ]
                                            ),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        content.get(
                                                            "kpi_card.parameter_labels.length_of_stay",
                                                            "Length of Stay: ",
                                                        ),
                                                        style={"fontWeight": "500"},
                                                    ),
                                                    f"{params['los_days']:.0f} days",
                                                ]
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            # Subcomponents list
                            html.Div(
                                style={
                                    "marginTop": Spacing.MD,
                                    "paddingTop": Spacing.SM,
                                    "borderTop": f"{{Borders.THIN}} solid {Colors.GRAY_300}",
                                },
                                children=[
                                    html.Span(
                                        content.get(
                                            "kpi_card.subcomponents_label", "Subcomponents:"
                                        ),
                                        style={
                                            "fontSize": "11px",
                                            "fontWeight": "600",
                                            "color": Colors.GRAY_900,
                                            "textTransform": "uppercase",
                                        },
                                    ),
                                    html.Div(children=govt_subs),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def _build_kpi_card_split(result, mvpf, badge_color, badge_text_color, label, params, scenario):
    """Build the KPI card split into two components: score display and detailed components."""

    # Build subcomponent lists for each main component
    detainee_subs = []
    for name, value in result.get("detainee_breakdown", {}).items():
        detainee_subs.append(
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "fontSize": FontSizes.LABEL,
                    "color": Colors.GRAY_600,
                    "marginTop": Spacing.XS,
                },
                children=[
                    html.Span(name, style={"maxWidth": "60%"}),
                    html.Span(
                        f"${int(value):,}",
                        style={"fontWeight": "500", "color": Colors.PRIMARY_BLUE_DARK},
                    ),
                ],
            )
        )

    society_subs = []
    for name, value in result.get("society_breakdown", {}).items():
        society_subs.append(
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "fontSize": FontSizes.LABEL,
                    "color": Colors.GRAY_600,
                    "marginTop": Spacing.XS,
                },
                children=[
                    html.Span(name, style={"maxWidth": "60%"}),
                    html.Span(
                        f"${int(value):,}",
                        style={"fontWeight": "500", "color": Colors.SUCCESS_GREEN},
                    ),
                ],
            )
        )

    govt_subs = []
    for name, value in result.get("govt_breakdown", {}).items():
        govt_subs.append(
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "fontSize": FontSizes.LABEL,
                    "color": Colors.GRAY_600,
                    "marginTop": Spacing.XS,
                },
                children=[
                    html.Span(name, style={"maxWidth": "60%"}),
                    html.Span(
                        f"${int(value):,}", style={"fontWeight": "500", "color": Colors.ERROR_RED}
                    ),
                ],
            )
        )

    # First component: Score display (to be centered)
    kpi_score = html.Div(
        className="kpi-card",
        style={"maxWidth": "800px", "margin": "0 auto"},
        children=[
            html.Div(
                className="kpi-header",
                style={"textAlign": "center"},
                children=[
                    html.H2(content.get("kpi_card.title", "MVPF Score"), className="kpi-title")
                ],
            ),
            html.Div(
                style={"textAlign": "center"},
                children=[
                    html.Span(f"{mvpf:.4f}", className="kpi-value"),
                    html.Span(content.get("kpi_card.ratio_label", "ratio"), className="kpi-ratio"),
                ],
            ),
            # Two-column layout: Explanation (left) and Interpretation (right)
            html.Div(
                style={
                    "marginTop": Spacing.XXL,
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr",
                    "gap": Spacing.XL,
                },
                children=[
                    # Left column: Dynamic explanation
                    html.Div(
                        style={
                            "padding": Spacing.XL,
                            "background": "#f0f9ff",
                            "borderRadius": "8px",
                            "border": f"{Borders.THIN} solid #bfdbfe",
                        },
                        children=[
                            html.H4(
                                "What This Means",
                                style={
                                    "fontSize": FontSizes.H5,
                                    "fontWeight": "600",
                                    "color": "#1e3a8a",
                                    "marginTop": "0",
                                    "marginBottom": Spacing.MD,
                                },
                            ),
                            html.P(
                                f"For each dollar spent operating CCJ, ${abs(mvpf):.2f} of {'net value is generated' if mvpf > 0 else 'net harm is caused'} for detainees and society combined.",
                                style={
                                    "margin": f"0 0 {Spacing.MD} 0",
                                    "color": "#1e3a8a",
                                    "fontSize": FontSizes.BODY,
                                    "lineHeight": LineHeights.RELAXED,
                                    "fontWeight": "500",
                                },
                            ),
                            html.P(
                                [
                                    f"This calculation uses the '{scenario}' scenario, which ",
                                    content.get(
                                        f'scenario_descriptions.{scenario.replace(" ", "_")}',
                                        "represents a specific set of assumptions about detainee harm and societal impacts",
                                    ),
                                    ".",
                                ],
                                style={
                                    "margin": "0",
                                    "color": "#1e40af",
                                    "fontSize": "13px",
                                    "lineHeight": LineHeights.RELAXED,
                                },
                            ),
                        ],
                    ),
                    # Right column: Interpretation guide
                    html.Div(
                        style={
                            "padding": Spacing.XL,
                            "background": "#f0f9ff",
                            "borderRadius": "8px",
                            "border": f"{Borders.THIN} solid #bfdbfe",
                        },
                        children=[
                            html.H4(
                                content.get("interpretation_card.title", "How to Interpret"),
                                style={
                                    "fontSize": FontSizes.H5,
                                    "fontWeight": "600",
                                    "color": "#1e3a8a",
                                    "marginTop": "0",
                                    "marginBottom": Spacing.MD,
                                },
                            ),
                            html.Ul(
                                style={
                                    "margin": "0",
                                    "paddingLeft": Spacing.XL,
                                    "color": "#1e40af",
                                    "fontSize": "13px",
                                    "lineHeight": LineHeights.LOOSE,
                                },
                                children=[
                                    html.Li(
                                        [
                                            html.Strong(
                                                content.get(
                                                    "interpretation_card.levels.very_high.threshold",
                                                    "MVPF ≥ 2.5:",
                                                )
                                            ),
                                            " "
                                            + content.get(
                                                "interpretation_card.levels.very_high.description",
                                                "Very high social return",
                                            ),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong(
                                                content.get(
                                                    "interpretation_card.levels.positive.threshold",
                                                    "MVPF > 1:",
                                                )
                                            ),
                                            " "
                                            + content.get(
                                                "interpretation_card.levels.positive.description",
                                                "More value than cost",
                                            ),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong(
                                                content.get(
                                                    "interpretation_card.levels.neutral.threshold",
                                                    "MVPF = 1:",
                                                )
                                            ),
                                            " "
                                            + content.get(
                                                "interpretation_card.levels.neutral.description",
                                                "Value equals cost",
                                            ),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong(
                                                content.get(
                                                    "interpretation_card.levels.negative.threshold",
                                                    "MVPF < 1:",
                                                )
                                            ),
                                            " "
                                            + content.get(
                                                "interpretation_card.levels.negative.description",
                                                "Costs exceed value",
                                            ),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong(
                                                content.get(
                                                    "interpretation_card.levels.harmful.threshold",
                                                    "MVPF < 0:",
                                                )
                                            ),
                                            " "
                                            + content.get(
                                                "interpretation_card.levels.harmful.description",
                                                "Net harm delivered",
                                            ),
                                        ]
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    # Second component: Calculation and component details
    kpi_components = html.Div(
        className="kpi-card",
        style={"background": "transparent"},
        children=[
            # Calculation row
            html.Div(
                className="kpi-calculation",
                style={
                    "marginBottom": Spacing.XXL,
                    "padding": Spacing.XL,
                    "background": "#f8f9fa",
                    "borderRadius": "8px",
                },
                children=[
                    html.Div(
                        children=[
                            html.H4(
                                content.get("kpi_card.calculation_label", "Calculation"),
                                style={
                                    "fontSize": "18px",
                                    "fontWeight": "600",
                                    "color": Colors.GRAY_900,
                                    "marginTop": "0",
                                    "marginBottom": Spacing.LG,
                                },
                            ),
                            html.Div(
                                style={
                                    "fontSize": FontSizes.H5,
                                    "lineHeight": LineHeights.LOOSE,
                                    "color": "#1f2937",
                                },
                                children=[
                                    html.Div(
                                        [
                                            html.Span("MVPF = (", style={"fontWeight": "500"}),
                                            html.Span(
                                                "Detainee Values",
                                                style={
                                                    "color": Colors.PRIMARY_BLUE_DARK,
                                                    "fontWeight": "600",
                                                },
                                            ),
                                            html.Span(" + ", style={"fontWeight": "500"}),
                                            html.Span(
                                                "Society Values",
                                                style={
                                                    "color": Colors.SUCCESS_GREEN,
                                                    "fontWeight": "600",
                                                },
                                            ),
                                            html.Span(") / ", style={"fontWeight": "500"}),
                                            html.Span(
                                                "Government Costs",
                                                style={
                                                    "color": Colors.ERROR_RED,
                                                    "fontWeight": "600",
                                                },
                                            ),
                                        ],
                                        style={"marginBottom": Spacing.SM},
                                    ),
                                    html.Div(
                                        [
                                            html.Span("MVPF = (", style={"fontWeight": "500"}),
                                            html.Span(
                                                f"${int(result['detainee_values']):,}",
                                                style={
                                                    "color": Colors.PRIMARY_BLUE_DARK,
                                                    "fontWeight": "600",
                                                },
                                            ),
                                            html.Span(" + ", style={"fontWeight": "500"}),
                                            html.Span(
                                                f"${int(result['society_values']):,}",
                                                style={
                                                    "color": Colors.SUCCESS_GREEN,
                                                    "fontWeight": "600",
                                                },
                                            ),
                                            html.Span(") / ", style={"fontWeight": "500"}),
                                            html.Span(
                                                f"${int(result['govt_cost']):,}",
                                                style={
                                                    "color": Colors.ERROR_RED,
                                                    "fontWeight": "600",
                                                },
                                            ),
                                        ],
                                        style={"marginBottom": Spacing.SM},
                                    ),
                                    html.Div(
                                        [
                                            html.Span("MVPF = ", style={"fontWeight": "500"}),
                                            html.Span(
                                                f"{mvpf:.4f}",
                                                style={
                                                    "fontSize": FontSizes.H4,
                                                    "fontWeight": "700",
                                                    "color": "#1f2937",
                                                },
                                            ),
                                        ]
                                    ),
                                ],
                            ),
                        ]
                    )
                ],
            ),
            # Component sections in 3-column grid
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr", "gap": Spacing.LG},
                children=[
                    # Detainee Values Component
                    html.Div(
                        className="kpi-component",
                        children=[
                            html.Div(
                                style={
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "alignItems": "flex-start",
                                },
                                children=[
                                    html.Div(
                                        children=[
                                            html.A(
                                                href="#detainee-values-section",
                                                className="kpi-component-link",
                                                children=[
                                                    html.H4(
                                                        content.get(
                                                            "kpi_card.components.detainee.title",
                                                            "Values for Detainees",
                                                        )
                                                    )
                                                ],
                                            ),
                                            html.P(
                                                f"${int(result['detainee_values']):,}",
                                                style={
                                                    "color": Colors.PRIMARY_BLUE_DARK,
                                                    "margin": "0",
                                                },
                                            ),
                                        ]
                                    ),
                                    # Parameters on the right
                                    html.Div(
                                        style={
                                            "textAlign": "right",
                                            "fontSize": "11px",
                                            "color": Colors.GRAY_600,
                                        },
                                        children=[
                                            html.Div(
                                                [
                                                    html.Span(
                                                        content.get(
                                                            "kpi_card.parameter_labels.felony_rate",
                                                            "Felony Rate: ",
                                                        ),
                                                        style={"fontWeight": "500"},
                                                    ),
                                                    f"{params['fel_rate']:.1%}",
                                                ]
                                            ),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        content.get(
                                                            "kpi_card.parameter_labels.population_mult",
                                                            "Population Mult: ",
                                                        ),
                                                        style={"fontWeight": "500"},
                                                    ),
                                                    f"{params['n_detainees_mult']:.0%}",
                                                ]
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            # Subcomponents list
                            html.Div(
                                style={
                                    "marginTop": Spacing.MD,
                                    "paddingTop": Spacing.SM,
                                    "borderTop": f"{{Borders.THIN}} solid {Colors.GRAY_300}",
                                },
                                children=[
                                    html.Span(
                                        content.get(
                                            "kpi_card.subcomponents_label", "Subcomponents:"
                                        ),
                                        style={
                                            "fontSize": "11px",
                                            "fontWeight": "600",
                                            "color": Colors.GRAY_900,
                                            "textTransform": "uppercase",
                                        },
                                    ),
                                    html.Div(children=detainee_subs),
                                ],
                            ),
                        ],
                    ),
                    # Society Values Component
                    html.Div(
                        className="kpi-component",
                        children=[
                            html.Div(
                                style={
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "alignItems": "flex-start",
                                },
                                children=[
                                    html.Div(
                                        children=[
                                            html.A(
                                                href="#society-values-section",
                                                className="kpi-component-link",
                                                children=[
                                                    html.H4(
                                                        content.get(
                                                            "kpi_card.components.society.title",
                                                            "Value for Society",
                                                        )
                                                    )
                                                ],
                                            ),
                                            html.P(
                                                f"${int(result['society_values']):,}",
                                                style={
                                                    "color": Colors.SUCCESS_GREEN,
                                                    "margin": "0",
                                                },
                                            ),
                                        ]
                                    ),
                                    # Parameters on the right
                                    html.Div(
                                        style={
                                            "textAlign": "right",
                                            "fontSize": "11px",
                                            "color": Colors.GRAY_600,
                                        },
                                        children=[
                                            html.Div(
                                                [
                                                    html.Span(
                                                        content.get(
                                                            "kpi_card.parameter_labels.community_mult",
                                                            "Community Mult: ",
                                                        ),
                                                        style={"fontWeight": "500"},
                                                    ),
                                                    f"{params['n_society_mult']:.0%}",
                                                ]
                                            ),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        content.get(
                                                            "kpi_card.parameter_labels.length_of_stay",
                                                            "Length of Stay: ",
                                                        ),
                                                        style={"fontWeight": "500"},
                                                    ),
                                                    f"{params['los_days']:.0f} days",
                                                ]
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            # Subcomponents list
                            html.Div(
                                style={
                                    "marginTop": Spacing.MD,
                                    "paddingTop": Spacing.SM,
                                    "borderTop": f"{{Borders.THIN}} solid {Colors.GRAY_300}",
                                },
                                children=[
                                    html.Span(
                                        content.get(
                                            "kpi_card.subcomponents_label", "Subcomponents:"
                                        ),
                                        style={
                                            "fontSize": "11px",
                                            "fontWeight": "600",
                                            "color": Colors.GRAY_900,
                                            "textTransform": "uppercase",
                                        },
                                    ),
                                    html.Div(children=society_subs),
                                ],
                            ),
                        ],
                    ),
                    # Government Costs Component
                    html.Div(
                        className="kpi-component",
                        children=[
                            html.Div(
                                style={
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "alignItems": "flex-start",
                                },
                                children=[
                                    html.Div(
                                        children=[
                                            html.A(
                                                href="#government-cost-section",
                                                className="kpi-component-link",
                                                children=[
                                                    html.H4(
                                                        content.get(
                                                            "kpi_card.components.government.title",
                                                            "Government Costs",
                                                        )
                                                    )
                                                ],
                                            ),
                                            html.P(
                                                f"${int(result['govt_cost']):,}",
                                                style={"color": Colors.ERROR_RED, "margin": "0"},
                                            ),
                                        ]
                                    ),
                                    # Parameters on the right
                                    html.Div(
                                        style={
                                            "textAlign": "right",
                                            "fontSize": "11px",
                                            "color": Colors.GRAY_600,
                                        },
                                        children=[
                                            html.Div(
                                                [
                                                    html.Span(
                                                        content.get(
                                                            "kpi_card.parameter_labels.population_mult",
                                                            "Population Mult: ",
                                                        ),
                                                        style={"fontWeight": "500"},
                                                    ),
                                                    f"{params['n_detainees_mult']:.0%}",
                                                ]
                                            ),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        content.get(
                                                            "kpi_card.parameter_labels.length_of_stay",
                                                            "Length of Stay: ",
                                                        ),
                                                        style={"fontWeight": "500"},
                                                    ),
                                                    f"{params['los_days']:.0f} days",
                                                ]
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            # Subcomponents list
                            html.Div(
                                style={
                                    "marginTop": Spacing.MD,
                                    "paddingTop": Spacing.SM,
                                    "borderTop": f"{{Borders.THIN}} solid {Colors.GRAY_300}",
                                },
                                children=[
                                    html.Span(
                                        content.get(
                                            "kpi_card.subcomponents_label", "Subcomponents:"
                                        ),
                                        style={
                                            "fontSize": "11px",
                                            "fontWeight": "600",
                                            "color": Colors.GRAY_900,
                                            "textTransform": "uppercase",
                                        },
                                    ),
                                    html.Div(children=govt_subs),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # Download button at the bottom of KPI components
            html.Div(
                style={"marginTop": Spacing.XXL, "display": "flex", "justifyContent": "center"},
                children=[
                    html.Button(
                        content.get("download.button_text", "Download Current Calculations"),
                        id="btn-download-csv",
                        n_clicks=0,
                        className="download-button",
                        style={
                            "backgroundColor": Colors.NAVY_MEDIUM,
                            "color": "white",
                            "border": "none",
                            "borderRadius": "6px",
                            "padding": f"{Spacing.MD} {Spacing.XXL}",
                            "fontSize": FontSizes.BODY,
                            "fontWeight": "600",
                            "cursor": "pointer",
                            "transition": "all 0.2s",
                            "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
                        },
                    ),
                    dcc.Download(id="download-dataframe-csv"),
                ],
            ),
        ],
    )

    return kpi_score, kpi_components


def _build_interpretation_card():
    """Build the interpretation guide card component."""
    return html.Div(
        className="kpi-card",
        children=[
            html.H4(
                content.get("interpretation_card.title", "How to Interpret"),
                style={
                    "fontSize": FontSizes.H5,
                    "fontWeight": "600",
                    "color": Colors.GRAY_900,
                    "marginTop": "0",
                    "marginBottom": Spacing.MD,
                },
            ),
            html.Ul(
                style={
                    "margin": "0",
                    "paddingLeft": Spacing.XL,
                    "color": Colors.GRAY_800,
                    "fontSize": FontSizes.BODY,
                    "lineHeight": LineHeights.LOOSE,
                },
                children=[
                    html.Li(
                        [
                            html.Strong(
                                content.get(
                                    "interpretation_card.levels.very_high.threshold", "MVPF ≥ 2.5:"
                                )
                            ),
                            " "
                            + content.get(
                                "interpretation_card.levels.very_high.description",
                                "Very high social return on investment",
                            ),
                        ]
                    ),
                    html.Li(
                        [
                            html.Strong(
                                content.get(
                                    "interpretation_card.levels.positive.threshold", "MVPF > 1:"
                                )
                            ),
                            " "
                            + content.get(
                                "interpretation_card.levels.positive.description",
                                "Program delivers more value than it costs",
                            ),
                        ]
                    ),
                    html.Li(
                        [
                            html.Strong(
                                content.get(
                                    "interpretation_card.levels.neutral.threshold", "MVPF = 1:"
                                )
                            ),
                            " "
                            + content.get(
                                "interpretation_card.levels.neutral.description",
                                "Program value equals its cost",
                            ),
                        ]
                    ),
                    html.Li(
                        [
                            html.Strong(
                                content.get(
                                    "interpretation_card.levels.negative.threshold", "MVPF < 1:"
                                )
                            ),
                            " "
                            + content.get(
                                "interpretation_card.levels.negative.description",
                                "Program costs more than the value it provides",
                            ),
                        ]
                    ),
                    html.Li(
                        [
                            html.Strong(
                                content.get(
                                    "interpretation_card.levels.harmful.threshold", "MVPF < 0:"
                                )
                            ),
                            " "
                            + content.get(
                                "interpretation_card.levels.harmful.description",
                                "Indicates program delivers net harm",
                            ),
                        ]
                    ),
                ],
            ),
        ],
    )


def _build_benchmark_chart(current_mvpf, benchmarks):
    """Build the benchmark comparison bar chart (vertical orientation)."""
    # Prepare data: current MVPF first, then benchmarks
    names = ["Current MVPF for CCJ"]
    values = [current_mvpf]
    colors = [Colors.NAVY_MEDIUM]  # Blue for current

    for benchmark in benchmarks:
        bench_mvpf = float(benchmark["mvpf_value"])
        description = benchmark["Description"]
        # Shorten long names for chart labels
        short_name = description if len(description) <= 40 else description[:37] + "..."
        names.append(short_name)
        values.append(bench_mvpf)
        # Color based on positive/negative
        colors.append(Colors.SUCCESS_GREEN if bench_mvpf >= 0 else Colors.ERROR_RED)

    # Create horizontal bar chart (vertical orientation)
    fig = go.Figure(
        data=[
            go.Bar(
                y=names,
                x=values,
                orientation="h",
                marker_color=colors,
                text=[f"{v:.2f}" for v in values],
                textposition="outside",
                textfont=dict(size=11, color=Colors.GRAY_900),
                cliponaxis=False,  # Prevent text from being clipped
            )
        ]
    )

    # Calculate x-axis range with extra padding for text labels
    min_val = min(values)
    max_val = max(values)
    padding = max(abs(max_val), abs(min_val)) * 0.3  # Increased padding for text visibility
    x_range = [min(0, min_val - padding), max(0, max_val + padding)]

    fig.update_layout(
        title=None,
        xaxis_title="MVPF",
        yaxis_title="",
        xaxis_range=x_range,
        paper_bgcolor="white",
        plot_bgcolor="#f9fafb",
        font=dict(family="system-ui", size=11),
        margin=dict(t=20, b=40, l=250, r=100),  # Increased right margin for text labels
        showlegend=False,
        height=max(450, len(names) * 50),  # Increased height for better spacing
        yaxis=dict(autorange="reversed"),  # Put Current MVPF at top
    )

    # Add vertical line at x=0
    fig.add_vline(x=0, line_dash="solid", line_color=Colors.GRAY_500, line_width=1)

    # Add vertical line at x=1 (break-even point)
    fig.add_vline(
        x=1,
        line_dash="dash",
        line_color="#f59e0b",
        line_width=1,
        annotation_text="Break-even",
        annotation_position="top",
    )

    return fig


def _build_benchmark_card(current_mvpf, scenario="baseline", params=None):
    """Build the benchmark comparison card component with dynamic tiles and chart."""
    # Use cached benchmarks instead of reloading CSV

    # Build comparison chart
    benchmark_chart = _build_benchmark_chart(current_mvpf, benchmarks)

    benchmark_tiles = []
    for benchmark in benchmarks:
        bench_mvpf = float(benchmark["mvpf_value"])
        description = benchmark["Description"]
        source_link = benchmark["source_link"]
        benchmark_id = benchmark["Id"]

        # Calculate comparison
        if current_mvpf != 0:
            if bench_mvpf >= 0 and current_mvpf >= 0:
                # Both positive: compare directly
                pct_diff = (abs(bench_mvpf) / (current_mvpf)) if bench_mvpf != 0 else 0
            elif bench_mvpf < 0 and current_mvpf >= 0:
                # Benchmark negative, current positive: CCJ is better
                pct_diff = abs(bench_mvpf) / abs(current_mvpf)
            elif bench_mvpf >= 0 and current_mvpf < 0:
                # Benchmark positive, current negative: CCJ is worse
                pct_diff = -abs(bench_mvpf) / abs(current_mvpf)
            else:
                # Both negative: less negative is better
                pct_diff = abs(bench_mvpf) / (current_mvpf)
        else:
            pct_diff = 0

        # Determine if CCJ is better or worse
        is_better = current_mvpf > bench_mvpf

        # Value styling
        value_class = "positive" if bench_mvpf >= 0 else "negative"
        comparison_class = "better" if is_better else "worse"

        # Format comparison text
        if is_better:
            comparison_text = f"-{abs(pct_diff):.2f}X" if pct_diff != 0 else "Same"
        else:
            comparison_text = f"+{abs(pct_diff):.2f}X" if pct_diff != 0 else "Same"

        # Get first source link if multiple
        first_link = source_link.split(",")[0].strip()

        # Get description from content.json
        bench_description = content.get(f"benchmark_descriptions.{benchmark_id}", "")

        tile = html.Div(
            className="benchmark-tile",
            style={
                "marginBottom": Spacing.LG,
                "padding": Spacing.LG,
                "background": "white",
                "borderRadius": "8px",
                "border": f"{Borders.THIN} solid {Colors.GRAY_300}",
            },
            children=[
                html.Div(
                    className="benchmark-tile-header",
                    children=[
                        html.Span(
                            f"{bench_mvpf:.2f}", className=f"benchmark-tile-value {value_class}"
                        ),
                        html.Span(
                            comparison_text,
                            className=f"benchmark-tile-comparison {comparison_class}",
                        ),
                    ],
                ),
                html.Div(className="benchmark-tile-name", children=description),
                html.P(
                    bench_description,
                    style={
                        "fontSize": "13px",
                        "color": Colors.GRAY_600,
                        "marginTop": Spacing.SM,
                        "marginBottom": Spacing.MD,
                        "lineHeight": LineHeights.NORMAL,
                    },
                ),
                html.A(
                    "View Source", href=first_link, target="_blank", className="benchmark-tile-link"
                ),
            ],
        )
        benchmark_tiles.append(tile)

    return html.Div(
        className="kpi-card",
        children=[
            # Header section
            html.Div(
                children=[
                    html.H3(
                        content.get("benchmark_card.title", "Comparative Benchmarking"),
                        style={
                            "fontSize": FontSizes.H3,
                            "fontWeight": "600",
                            "color": "white",
                            "marginBottom": Spacing.SM,
                            "marginTop": "0",
                            "textAlign": "center",
                        },
                    ),
                    html.P(
                        "This section compares the MVPF values of selected government programs, interventions, and policy initiatives across different domains. Each comparison shows how one dollar spent on Cook County Jail detention compares to spending on other policy initiatives, helping contextualize the relative social value of pretrial detention against other uses of public funds.",
                        style={
                            "fontSize": FontSizes.BODY,
                            "color": "white",
                            "marginBottom": Spacing.LG,
                            "fontWeight": "400",
                            "lineHeight": LineHeights.RELAXED,
                        },
                    ),
                    # Current Settings Display
                    html.Div(
                        style={
                            "backgroundColor": "rgba(255, 255, 255, 0.15)",
                            "padding": Spacing.MD,
                            "borderRadius": BorderRadius.SM,
                            "marginBottom": Spacing.XXL,
                            "border": f"{Borders.THIN} solid rgba(255, 255, 255, 0.2)",
                        },
                        children=[
                            html.Div(
                                style={
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "alignItems": "center",
                                    "marginBottom": Spacing.XS,
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "fontSize": FontSizes.LABEL,
                                            "color": "rgba(255, 255, 255, 0.9)",
                                            "fontWeight": "600",
                                            "textTransform": "uppercase",
                                            "letterSpacing": "0.5px",
                                        },
                                        children="Current Analysis Settings",
                                    ),
                                    html.Button(
                                        [html.Span("← ", style={"marginRight": "4px"}), "Change"],
                                        id="btn-back-to-calc-benchmark",
                                        n_clicks=0,
                                        style={
                                            "backgroundColor": "rgba(255, 255, 255, 0.25)",
                                            "color": "white",
                                            "border": f"{Borders.THIN} solid rgba(255, 255, 255, 0.4)",
                                            "padding": f"{Spacing.XS} {Spacing.MD}",
                                            "borderRadius": BorderRadius.SM,
                                            "fontSize": FontSizes.LABEL,
                                            "fontWeight": "600",
                                            "cursor": "pointer",
                                            "transition": "all 0.2s",
                                        },
                                    ),
                                ],
                            ),
                            html.Div(
                                style={
                                    "display": "flex",
                                    "flexWrap": "wrap",
                                    "gap": Spacing.LG,
                                    "fontSize": FontSizes.BODY_SM,
                                    "color": "white",
                                },
                                children=[
                                    html.Div(
                                        children=[
                                            html.Span("Scenario: ", style={"opacity": "0.8"}),
                                            html.Span(
                                                scenario.replace("_", " ").title(),
                                                style={"fontWeight": "600"},
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        children=[
                                            html.Span("Felony Rate: ", style={"opacity": "0.8"}),
                                            html.Span(
                                                (
                                                    f"{params.get('fel_rate', 0.7):.0%}"
                                                    if params
                                                    else "70%"
                                                ),
                                                style={"fontWeight": "600"},
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        children=[
                                            html.Span(
                                                "Detainee Population: ", style={"opacity": "0.8"}
                                            ),
                                            html.Span(
                                                (
                                                    f"{params.get('n_detainees_base', 33945) * params.get('n_detainees_mult', 1.0):,.0f}"
                                                    if params
                                                    else "33,945"
                                                ),
                                                style={"fontWeight": "600"},
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        children=[
                                            html.Span("Length of Stay: ", style={"opacity": "0.8"}),
                                            html.Span(
                                                (
                                                    f"{params.get('los_days', 70):.0f} days"
                                                    if params
                                                    else "70 days"
                                                ),
                                                style={"fontWeight": "600"},
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        children=[
                                            html.Span("Crime Effect: ", style={"opacity": "0.8"}),
                                            html.Span(
                                                (
                                                    f"{params.get('crime_effect', 0):+.0f}%"
                                                    if params and params.get("crime_effect", 0) != 0
                                                    else "0% (No Effect)"
                                                ),
                                                style={"fontWeight": "600"},
                                            ),
                                        ]
                                    ),
                                ],
                            ),
                        ],
                    ),
                ]
            ),
            # Two-column layout: Chart on left (65%), Single column of tiles on right (35%)
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "65% 35%", "gap": Spacing.XXL},
                children=[
                    # Left: Benchmark comparison chart
                    html.Div(
                        style={"background": "white", "borderRadius": "8px", "padding": Spacing.LG},
                        children=[
                            dcc.Graph(figure=benchmark_chart, config={"displayModeBar": False})
                        ],
                    ),
                    # Right: Benchmark tiles in single column
                    html.Div(
                        style={"overflowY": "auto", "maxHeight": "700px"}, children=benchmark_tiles
                    ),
                ],
            ),
        ],
    )


def _build_numerator_chart(result):
    """Build the numerator chart showing Detainee Values and Society Values."""
    det_val = result["detainee_values"]
    soc_val = result["society_values"]

    fig = go.Figure(
        data=[
            go.Bar(
                x=[
                    content.get("charts.numerator_chart.labels.detainee_values", "Detainee Values"),
                    content.get("charts.numerator_chart.labels.society_values", "Society Values"),
                ],
                y=[det_val, soc_val],
                marker_color=[Colors.PRIMARY_BLUE, "#10b981"],
                text=[f"${int(det_val):,}", f"${int(soc_val):,}"],
                textposition="outside",
            )
        ]
    )

    fig.update_layout(
        title=content.get(
            "charts.numerator_chart.title", "Willingness to Pay (MVPF numerator value)"
        ),
        xaxis_title="",
        yaxis_title=content.get("charts.numerator_chart.y_axis", "Value ($)"),
        paper_bgcolor=Colors.GRAY_100,
        plot_bgcolor="#ffffff",
        font=dict(family="system-ui", size=12),
        margin=dict(t=50, b=80, l=80, r=40),
        showlegend=False,
    )

    return fig


def _build_denominator_chart(result):
    """Build the denominator chart showing Government Cost vs Numerator (Detainee + Society)."""
    gov_val = result["govt_cost"]
    det_val = result["detainee_values"]
    soc_val = result["society_values"]
    numerator = det_val + soc_val

    # Determine colors based on values (negative = red, positive = green/blue)
    numerator_color = "#10b981" if numerator >= 0 else "#ef4444"

    fig = go.Figure(
        data=[
            go.Bar(
                x=[
                    content.get(
                        "charts.denominator_chart.labels.aggregated_value", "Aggregated Value"
                    ),
                    content.get(
                        "charts.denominator_chart.labels.government_cost", "Government Cost"
                    ),
                ],
                y=[numerator, gov_val],
                marker_color=[numerator_color, "#ef4444"],
                text=[f"${int(numerator):,}", f"${int(gov_val):,}"],
                textposition="outside",
            )
        ]
    )

    fig.update_layout(
        title=content.get(
            "charts.denominator_chart.title", "Marginal Value to Government Costs Comparison"
        ),
        xaxis_title="",
        yaxis_title=content.get("charts.denominator_chart.y_axis", "Value ($)"),
        paper_bgcolor=Colors.GRAY_100,
        plot_bgcolor="#ffffff",
        font=dict(family="system-ui", size=12),
        margin=dict(t=50, b=100, l=80, r=40),
        showlegend=False,
    )

    return fig


def _build_parameter_comparison_chart(
    scenario,
    base_det_p1,
    base_det_p2,
    base_soc_p1,
    base_soc_p2,
    detainee_baseline=None,
    crime_effect=0,
):
    """Build the parameter comparison chart showing MVPF sensitivity to parameter changes."""
    # Calculate MVPFs for each parameter variation
    param_variations = {
        "Felony Rate": [],
        "Detainee Population": [],
        "Community Size": [],
        "Length of Stay": [],
    }

    # Define parameter value mappings
    fel_rate_values = {
        "below": fel_rate_param.dropdown_map["below"],
        "average": fel_rate_param.dropdown_map["average"],
        "above": fel_rate_param.dropdown_map["above"],
    }
    n_detainees_values = {
        "below": n_detainees_param.dropdown_map["below"],
        "average": n_detainees_param.dropdown_map["average"],
        "above": n_detainees_param.dropdown_map["above"],
    }
    n_society_values = {
        "below": n_society_param.dropdown_map["below"],
        "average": n_society_param.dropdown_map["average"],
        "above": n_society_param.dropdown_map["above"],
    }
    los_days_values = {
        "below": los_days_param.dropdown_map["below"],
        "average": los_days_param.dropdown_map["average"],
        "above": los_days_param.dropdown_map["above"],
    }

    # Vary Felony Rate (detainee_param1)
    for variation in ["below", "average", "above"]:
        result = _calculate_mvpf(
            scenario,
            fel_rate_values[variation],
            base_det_p2,
            base_soc_p1,
            base_soc_p2,
            detainee_baseline=detainee_baseline,
            crime_effect=crime_effect,
        )
        param_variations["Felony Rate"].append(result["mvpf"])

    # Vary Detainee Population (detainee_param2)
    for variation in ["below", "average", "above"]:
        result = _calculate_mvpf(
            scenario,
            base_det_p1,
            n_detainees_values[variation],
            base_soc_p1,
            base_soc_p2,
            detainee_baseline=detainee_baseline,
            crime_effect=crime_effect,
        )
        param_variations["Detainee Population"].append(result["mvpf"])

    # Vary Community Size (society_param1)
    for variation in ["below", "average", "above"]:
        result = _calculate_mvpf(
            scenario,
            base_det_p1,
            base_det_p2,
            n_society_values[variation],
            base_soc_p2,
            detainee_baseline=detainee_baseline,
            crime_effect=crime_effect,
        )
        param_variations["Community Size"].append(result["mvpf"])

    # Vary Length of Stay (society_param2)
    for variation in ["below", "average", "above"]:
        result = _calculate_mvpf(
            scenario,
            base_det_p1,
            base_det_p2,
            base_soc_p1,
            los_days_values[variation],
            detainee_baseline=detainee_baseline,
            crime_effect=crime_effect,
        )
        param_variations["Length of Stay"].append(result["mvpf"])

    # Create grouped bar chart
    fig = go.Figure()

    colors = [
        "#93c5fd",
        Colors.PRIMARY_BLUE,
        "#1e40af",
    ]  # Light to dark blue for below, average, above
    labels = ["Lower Bound", "Baseline", "Upper Bound"]

    for i, label in enumerate(labels):
        values = [param_variations[param][i] for param in param_variations.keys()]
        fig.add_trace(
            go.Bar(
                name=label,
                x=list(param_variations.keys()),
                y=values,
                marker_color=colors[i],
                text=[f"{v:.2f}" for v in values],
                textposition="outside",
                textfont=dict(size=10),
            )
        )

    fig.update_layout(
        title="MVPF Sensitivity to Parameter Changes",
        xaxis_title="Parameter",
        yaxis_title="MVPF",
        barmode="group",
        paper_bgcolor=Colors.GRAY_100,
        plot_bgcolor="#ffffff",
        font=dict(family="system-ui", size=11),
        margin=dict(t=50, b=100, l=60, r=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
    )

    # Add horizontal line at y=1 (break-even)
    fig.add_hline(
        y=1,
        line_dash="dash",
        line_color="#f59e0b",
        line_width=1,
        annotation_text="Break-even",
        annotation_position="right",
    )

    return fig


def _build_scenario_comparison_chart(
    det_p1, det_p2, soc_p1, soc_p2, detainee_baseline=None, crime_effect=0
):
    """Build the scenario comparison chart showing MVPF for all scenarios on y-axis."""
    scenarios = ["baseline", "most conservative", "least conservative"]

    scenario_labels = {
        "baseline": "Baseline",
        "most conservative": "Lower bound",
        "least conservative": "Upper bound",
    }

    # Calculate MVPF for each scenario
    mvpf_values = []
    for scenario in scenarios:
        result = _calculate_mvpf(
            scenario,
            det_p1,
            det_p2,
            soc_p1,
            soc_p2,
            detainee_baseline=detainee_baseline,
            crime_effect=crime_effect,
        )
        mvpf_values.append(result["mvpf"])

    # Color bars based on MVPF value (green for good, yellow for fair, red for poor)
    colors = []
    for mvpf in mvpf_values:
        if mvpf >= 2.5:
            colors.append(Colors.SUCCESS_GREEN)  # Green - Excellent
        elif mvpf >= 1.5:
            colors.append(Colors.NAVY_MEDIUM)  # Blue - Good
        elif mvpf >= 1.0:
            colors.append("#f59e0b")  # Yellow - Fair
        else:
            colors.append(Colors.ERROR_RED)  # Red - Poor

    # Create horizontal bar chart with scenarios on y-axis
    labels = [scenario_labels[s] for s in scenarios]

    fig = go.Figure(
        data=[
            go.Bar(
                y=labels,
                x=mvpf_values,
                marker_color=colors,
                text=[f"{v:.2f}" for v in mvpf_values],
                textposition="outside",
                textfont=dict(size=11),
                orientation="h",
            )
        ]
    )

    # Calculate x-axis range
    min_val = min(mvpf_values)
    max_val = max(mvpf_values)
    padding = max(abs(max_val), abs(min_val)) * 0.15
    x_range = [min(0, min_val - padding), max(0, max_val + padding)]

    fig.update_layout(
        title="MVPF Comparison Across Scenarios",
        xaxis_title="MVPF",
        yaxis_title="",
        xaxis_range=x_range,
        paper_bgcolor=Colors.GRAY_100,
        plot_bgcolor="#ffffff",
        font=dict(family="system-ui", size=11),
        margin=dict(t=50, b=60, l=180, r=100),
        showlegend=False,
        bargap=0.3,
        height=max(400, len(scenarios) * 50),
    )

    # Add vertical line at x=0
    fig.add_vline(x=0, line_dash="solid", line_color=Colors.GRAY_500, line_width=1)

    # Add vertical line at x=1 (break-even)
    fig.add_vline(
        x=1,
        line_dash="dash",
        line_color="#f59e0b",
        line_width=1,
        annotation_text="Break-even",
        annotation_position="top",
    )

    return fig


def _build_sensitivity_analysis_chart(
    parameter_name, param_values, base_det_p1, base_det_p2, base_soc_p1, base_soc_p2, crime_effect=0
):
    """
    Build a sensitivity analysis chart showing how one parameter affects MVPF for baseline,
    least conservative, and most conservative scenarios.

    Parameters:
    -----------
    parameter_name : str
        Name of the parameter being varied ('Felony Rate', 'Detainee Population', 'Community Size', 'Length of Stay')
    param_values : list
        Array of parameter values to test (e.g., [0.1, 0.2, ..., 1.0])
    base_det_p1, base_det_p2, base_soc_p1, base_soc_p2 : float
        Base parameter values to use when not varying the parameter
    crime_effect : float, optional
        Crime effect multiplier (-4 to 14). Defaults to 0 (no effect).

    Returns:
    --------
    plotly.graph_objs.Figure
    """
    scenarios = ["baseline", "most conservative", "least conservative"]
    scenario_labels = {
        "baseline": "Baseline",
        "most conservative": "Lower Bound",
        "least conservative": "Upper bound",
    }
    scenario_colors = {
        "baseline": Colors.NAVY_MEDIUM,  # Blue
        "most conservative": Colors.WARNING_YELLOW,  # Orange
        "least conservative": Colors.SUCCESS_GREEN,  # Green
    }

    # Create descriptive x-axis labels with actual parameter values
    x_labels = []
    for value in param_values:
        if parameter_name == "Felony Rate":
            x_labels.append(f"{value:.0%}")
        elif parameter_name == "Detainee Population":
            x_labels.append(f"{value:.0%}")
        elif parameter_name == "Length of Stay":
            x_labels.append(f"{value:.0f} days")
        elif parameter_name == "Crime Effect":
            x_labels.append(f"{value:+.0f}%")
        else:
            x_labels.append(f"{value:.1f}")

    fig = go.Figure()

    for scenario in scenarios:
        mvpf_values = []

        for value in param_values:
            # Determine which parameter to vary based on parameter_name
            if parameter_name == "Felony Rate":
                result = _calculate_mvpf(
                    scenario,
                    value,
                    base_det_p2,
                    base_soc_p1,
                    base_soc_p2,
                    crime_effect=crime_effect,
                )
            elif parameter_name == "Detainee Population":
                result = _calculate_mvpf(
                    scenario,
                    base_det_p1,
                    value,
                    base_soc_p1,
                    base_soc_p2,
                    crime_effect=crime_effect,
                )
            elif parameter_name == "Community Size":
                result = _calculate_mvpf(
                    scenario,
                    base_det_p1,
                    base_det_p2,
                    value,
                    base_soc_p2,
                    crime_effect=crime_effect,
                )
            elif parameter_name == "Length of Stay":
                result = _calculate_mvpf(
                    scenario,
                    base_det_p1,
                    base_det_p2,
                    base_soc_p1,
                    value,
                    crime_effect=crime_effect,
                )
            elif parameter_name == "Crime Effect":
                result = _calculate_mvpf(
                    scenario, base_det_p1, base_det_p2, base_soc_p1, base_soc_p2, crime_effect=value
                )
            else:
                result = {"mvpf": 0}

            mvpf_values.append(result["mvpf"])

        fig.add_trace(
            go.Scatter(
                x=x_labels,
                y=mvpf_values,
                mode="lines+markers",
                name=scenario_labels[scenario],
                line=dict(color=scenario_colors[scenario], width=3),
                marker=dict(size=8, color=scenario_colors[scenario]),
                text=[f"{v:.2f}" for v in mvpf_values],
                textposition="top center",
                textfont=dict(size=10),
            )
        )

    fig.update_layout(
        title=f"Sensitivity to {parameter_name}",
        xaxis_title=parameter_name,
        yaxis_title="MVPF",
        paper_bgcolor="white",
        plot_bgcolor="#f9fafb",
        font=dict(family="system-ui", size=11),
        margin=dict(t=50, b=60, l=60, r=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.8)",
        ),
        height=300,
        hovermode="x unified",
    )

    # Add horizontal line at y=1 (break-even)
    fig.add_hline(
        y=1,
        line_dash="dash",
        line_color="#f59e0b",
        line_width=1,
        annotation_text="Break-even",
        annotation_position="right",
    )

    return fig


def _build_subcomponents_chart(result):
    """Build the subcomponents horizontal bar chart with variable names on y-axis."""
    # Collect all subcomponents with their variable names and values
    subcomponents = []
    colors = []

    # Detainee subcomponents (blue)
    for var_name, value in result.get("detainee_breakdown", {}).items():
        subcomponents.append({"name": var_name, "value": value, "category": "Detainee"})
        colors.append(Colors.NAVY_MEDIUM)

    # Society subcomponents (green)
    for var_name, value in result.get("society_breakdown", {}).items():
        subcomponents.append({"name": var_name, "value": value, "category": "Society"})
        colors.append("#10b981")

    # Government subcomponents (red)
    for var_name, value in result.get("govt_breakdown", {}).items():
        subcomponents.append({"name": var_name, "value": value, "category": "Govt"})
        colors.append("#ef4444")

    # Extract data for the chart
    names = [s["name"] for s in subcomponents]
    values = [s["value"] for s in subcomponents]
    text_labels = [f"${int(v):,}" for v in values]

    # Calculate x-axis range to ensure all bars are visible
    if values:
        min_val = min(values)
        max_val = max(values)
        # Add padding (20%) to ensure text labels are visible
        padding = max(abs(max_val), abs(min_val)) * 0.2
        x_range = [min(0, min_val - padding), max(0, max_val + padding)]
    else:
        x_range = None

    fig = go.Figure(
        data=[
            go.Bar(
                y=names,  # Names on y-axis for horizontal bars
                x=values,  # Values on x-axis for horizontal bars
                marker_color=colors,
                text=text_labels,
                textposition="outside",
                textfont=dict(size=10),
                orientation="h",  # Horizontal orientation
            )
        ]
    )

    fig.update_layout(
        title="Subcomponent Breakdown",
        xaxis_title="Value ($)",
        yaxis_title="",
        xaxis_range=x_range,
        paper_bgcolor=Colors.GRAY_100,
        plot_bgcolor="#ffffff",
        font=dict(family="system-ui", size=11),
        margin=dict(t=50, b=60, l=250, r=100),  # Increased left margin for labels
        showlegend=False,
        bargap=0.3,
        height=max(400, len(names) * 40),  # Dynamic height based on number of items
    )

    # Add a vertical line at x=0 for reference (vertical line for horizontal bars)
    fig.add_vline(x=0, line_dash="solid", line_color="Colors.GRAY_500", line_width=1)

    return fig


def register_callbacks(app):
    """
    Register all dashboard callbacks.

    This function encapsulates all callback definitions for cleaner code organization.
    Call this function after defining the app layout.

    Parameters:
    -----------
    app : dash.Dash
        The Dash application instance
    """

    # -------------------------------------------------------------------------
    # Toggle Callbacks for Collapsible Sections
    # -------------------------------------------------------------------------

    @app.callback(
        Output("detainee-wtp", "style"),
        Input("detainee-wtp-btn", "n_clicks"),
        State("detainee-wtp", "style"),
    )
    def toggle_detainee_wtp(n_clicks, style):
        return _toggle_style(n_clicks, style)

    @app.callback(
        Output("detainee-harm", "style"),
        Input("detainee-harm-btn", "n_clicks"),
        State("detainee-harm", "style"),
    )
    def toggle_detainee_harm(n_clicks, style):
        return _toggle_style(n_clicks, style)

    @app.callback(
        Output("society-crime", "style"),
        Input("society-crime-btn", "n_clicks"),
        State("society-crime", "style"),
    )
    def toggle_society_crime(n_clicks, style):
        return _toggle_style(n_clicks, style)

    @app.callback(
        Output("society-court", "style"),
        Input("society-court-btn", "n_clicks"),
        State("society-court", "style"),
    )
    def toggle_society_court(n_clicks, style):
        return _toggle_style(n_clicks, style)

    @app.callback(
        Output("society-spill", "style"),
        Input("society-spill-btn", "n_clicks"),
        State("society-spill", "style"),
    )
    def toggle_society_spill(n_clicks, style):
        return _toggle_style(n_clicks, style)

    @app.callback(
        Output("gov-op", "style"), Input("gov-op-btn", "n_clicks"), State("gov-op", "style")
    )
    def toggle_gov_op(n_clicks, style):
        return _toggle_style(n_clicks, style)

    @app.callback(
        Output("gov-crime-increase", "style"),
        Input("gov-crime-increase-btn", "n_clicks"),
        State("gov-crime-increase", "style"),
    )
    def toggle_gov_crime_increase(n_clicks, style):
        return _toggle_style(n_clicks, style)

    @app.callback(
        Output("gov-crime-decrease", "style"),
        Input("gov-crime-decrease-btn", "n_clicks"),
        State("gov-crime-decrease", "style"),
    )
    def toggle_gov_crime_decrease(n_clicks, style):
        return _toggle_style(n_clicks, style)

    # -------------------------------------------------------------------------
    # Scenario Selection Callback (Jumbotron Buttons)
    # -------------------------------------------------------------------------

    @app.callback(
        [
            Output("scenario-selector", "data"),
            Output("scenario-btn-baseline", "style"),
            Output("scenario-btn-most-conservative", "style"),
            Output("scenario-btn-least-conservative", "style"),
        ],
        [
            Input("scenario-btn-baseline", "n_clicks"),
            Input("scenario-btn-most-conservative", "n_clicks"),
            Input("scenario-btn-least-conservative", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def update_scenario_selection(baseline_clicks, conservative_clicks, least_clicks):
        """Handle scenario button clicks and update styling."""
        ctx = dash.callback_context

        if not ctx.triggered:
            return dash.no_update

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Determine selected scenario based on button clicked
        scenario_map = {
            "scenario-btn-baseline": "baseline",
            "scenario-btn-most-conservative": "most conservative",
            "scenario-btn-least-conservative": "least conservative",
        }
        selected_scenario = scenario_map.get(button_id, "baseline")

        # Define styles for selected and unselected states
        baseline_style = (
            {"border": f"{{Borders.THICK}} solid {Colors.PRIMARY_BLUE_DARK}", "cursor": "pointer"}
            if button_id == "scenario-btn-baseline"
            else {"border": f"{{Borders.MEDIUM}} solid {Colors.GRAY_300}", "cursor": "pointer"}
        )
        conservative_style = (
            {"border": f"{Borders.THICK} solid Colors.WARNING_YELLOW", "cursor": "pointer"}
            if button_id == "scenario-btn-most-conservative"
            else {"border": f"{{Borders.MEDIUM}} solid {Colors.GRAY_300}", "cursor": "pointer"}
        )
        least_style = (
            {"border": f"{{Borders.THICK}} solid {Colors.SUCCESS_GREEN}", "cursor": "pointer"}
            if button_id == "scenario-btn-least-conservative"
            else {"border": f"{{Borders.MEDIUM}} solid {Colors.GRAY_300}", "cursor": "pointer"}
        )

        return selected_scenario, baseline_style, conservative_style, least_style

    # -------------------------------------------------------------------------
    # Slider Value Display Update Callbacks
    # -------------------------------------------------------------------------

    @app.callback(Output("felony-rate-value", "children"), Input("detainee-param1", "value"))
    def update_felony_rate_display(value):
        """Update displayed felony rate based on slider value."""
        return f"{value:.0%}"

    @app.callback(
        Output("detainee-population-value", "children"),
        [Input("detainee-baseline-input", "value"), Input("detainee-param2", "value")],
    )
    def update_detainee_display(baseline, multiplier):
        """Update displayed detainee population based on baseline value and multiplier."""
        baseline_value = baseline if baseline is not None else n_detainees_param.base_value
        mult_value = multiplier if multiplier is not None else 1.0
        total = baseline_value * mult_value
        return f"{total:,.0f}"

    @app.callback(
        Output("detainee-multiplier-display", "children"), Input("detainee-param2", "value")
    )
    def update_detainee_multiplier_display(value):
        """Update displayed multiplier percentage."""
        if value is None:
            value = 1.0
        return f"{value:.0%}"

    @app.callback(Output("los-days-value", "children"), Input("society-param2", "value"))
    def update_los_days_display(value):
        """Update displayed length of stay based on slider value."""
        return f"{value:.0f} days"

    @app.callback(Output("crime-effect-value", "children"), Input("crime-effect-slider", "value"))
    def update_crime_effect_display(value):
        """Update displayed crime effect based on slider value."""
        if value is None:
            value = 0
        return f"{value}"

    # -------------------------------------------------------------------------
    # Main Dashboard Update Callback
    # -------------------------------------------------------------------------

    @app.callback(
        [
            Output("kpi-card", "children"),
            Output("kpi-components", "children"),
            Output("benchmark-card", "children"),
            Output("numerator-chart", "figure"),
            Output("denominator-chart", "figure"),
            Output("scenario-comparison-chart", "figure"),
        ],
        [Input("btn-calculate", "n_clicks")],
        [
            State("scenario-selector", "data"),
            State("detainee-param1", "value"),
            State("detainee-param2", "value"),
            State("detainee-baseline-input", "value"),
            State("society-param2", "value"),
            State("crime-effect-slider", "value"),
        ],
    )
    def update_dashboard(n_clicks, scenario, det_p1, det_p2, det_baseline, soc_p2, crime_effect):
        """Main callback to update all dashboard components."""
        # Convert string parameters from State to floats
        det_p1 = float(det_p1) if det_p1 is not None else 0.7
        det_p2 = float(det_p2) if det_p2 is not None else 1.0
        det_baseline = (
            float(det_baseline)
            if det_baseline is not None
            else n_detainees_base_param.default_value
        )
        soc_p2 = float(soc_p2) if soc_p2 is not None else 70
        crime_effect = float(crime_effect) if crime_effect is not None else 0

        # Use default value for community size multiplier
        soc_p1 = 1.0

        # Get params for display in KPI card
        params = _convert_dropdown_to_params(
            fel_rate_sel=det_p1,
            n_detainees_sel=det_p2,
            n_society_sel=soc_p1,
            los_days_sel=soc_p2,
            n_detainees_base=det_baseline,
            crime_effect=crime_effect,
        )

        result = _calculate_mvpf(
            scenario,
            det_p1,
            det_p2,
            soc_p1,
            soc_p2,
            detainee_baseline=det_baseline,
            crime_effect=crime_effect,
        )
        mvpf = result["mvpf"]

        # Determine badge color and label
        if mvpf >= 2.5:
            badge_color, badge_text_color, label = (
                Colors.SUCCESS_LIGHT,
                Colors.SUCCESS_GREEN,
                "Excellent",
            )
        elif mvpf >= 1.5:
            badge_color, badge_text_color, label = (
                Colors.PRIMARY_BLUE_LIGHT,
                Colors.PRIMARY_BLUE_DARK,
                "Good",
            )
        elif mvpf >= 1.0:
            badge_color, badge_text_color, label = (
                Colors.WARNING_LIGHT,
                Colors.WARNING_YELLOW,
                "Fair",
            )
        else:
            badge_color, badge_text_color, label = Colors.ERROR_LIGHT, Colors.ERROR_RED, "Poor"

        # Build components
        kpi_score, kpi_components = _build_kpi_card_split(
            result, mvpf, badge_color, badge_text_color, label, params, scenario
        )
        benchmark_card = _build_benchmark_card(mvpf, scenario, params)
        numerator_fig = _build_numerator_chart(result)
        denominator_fig = _build_denominator_chart(result)
        scenario_comparison_fig = _build_scenario_comparison_chart(
            det_p1, det_p2, soc_p1, soc_p2, det_baseline, crime_effect
        )

        return (
            kpi_score,
            kpi_components,
            benchmark_card,
            numerator_fig,
            denominator_fig,
            scenario_comparison_fig,
        )

    # -------------------------------------------------------------------------
    # Sensitivity Analysis Callback for Tab 3
    # -------------------------------------------------------------------------

    @app.callback(
        [
            Output("sensitivity-felony-rate", "figure"),
            Output("sensitivity-detainee-population", "figure"),
            Output("sensitivity-crime-effect", "figure"),
            Output("sensitivity-length-of-stay", "figure"),
            Output("sensitivity-param-scenario", "children"),
            Output("sensitivity-param-felony-rate", "children"),
            Output("sensitivity-param-detainee-pop", "children"),
            Output("sensitivity-param-los", "children"),
            Output("sensitivity-param-crime-effect", "children"),
        ],
        [Input("btn-calculate", "n_clicks")],
        [
            State("scenario-selector", "data"),
            State("detainee-param1", "value"),
            State("detainee-param2", "value"),
            State("society-param2", "value"),
            State("crime-effect-slider", "value"),
            State("detainee-baseline-input", "value"),
        ],
    )
    def update_sensitivity_analysis(
        n_clicks, scenario, det_p1, det_p2, soc_p2, crime_effect, det_baseline
    ):
        """Update sensitivity analysis graphs for baseline, most conservative, and least conservative scenarios."""
        # Convert string parameters from State to floats
        det_p1 = float(det_p1) if det_p1 is not None else 0.7
        det_p2 = float(det_p2) if det_p2 is not None else 1.0
        soc_p2 = float(soc_p2) if soc_p2 is not None else 70
        crime_effect = float(crime_effect) if crime_effect is not None else 0

        # Use default value for community size multiplier
        soc_p1 = 1.0

        # Define parameter value arrays using all slider marks (full ranges)
        # Felony Rate: All 10 marks from slider (10% to 100%)
        fel_rate_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

        # Detainee Population: All 5 marks from slider (10% to 200%)
        n_detainees_values = [0.1, 0.5, 1.0, 1.5, 2.0]

        # Crime Effect: All 4 marks from slider (-4 to +14)
        crime_effect_values = [-4, 0, 5, 14]

        # Length of Stay: All 4 marks from slider (1 to 365 days)
        los_days_values = [1, 70, 203, 365]

        # Build all 4 sensitivity analysis charts
        # For non-crime-effect charts, use the current crime_effect slider value
        felony_rate_fig = _build_sensitivity_analysis_chart(
            "Felony Rate",
            fel_rate_values,
            det_p1,
            det_p2,
            soc_p1,
            soc_p2,
            crime_effect=crime_effect,
        )

        detainee_pop_fig = _build_sensitivity_analysis_chart(
            "Detainee Population",
            n_detainees_values,
            det_p1,
            det_p2,
            soc_p1,
            soc_p2,
            crime_effect=crime_effect,
        )

        # For crime effect sensitivity, we vary crime_effect itself, so pass 0 as default
        crime_effect_fig = _build_sensitivity_analysis_chart(
            "Crime Effect", crime_effect_values, det_p1, det_p2, soc_p1, soc_p2, crime_effect=0
        )

        length_of_stay_fig = _build_sensitivity_analysis_chart(
            "Length of Stay",
            los_days_values,
            det_p1,
            det_p2,
            soc_p1,
            soc_p2,
            crime_effect=crime_effect,
        )

        # Format parameter displays
        scenario_display = (scenario or "baseline").replace("_", " ").title()
        felony_rate_display = f"{det_p1:.0%}"

        # Calculate total detainee population
        baseline_value = det_baseline if det_baseline is not None else n_detainees_param.base_value
        total_detainees = baseline_value * det_p2
        detainee_pop_display = f"{total_detainees:,.0f} ({det_p2:.0%})"

        los_display = f"{soc_p2:.0f} days"

        if crime_effect > 0:
            crime_effect_display = f"+{crime_effect:.0f}%"
        elif crime_effect < 0:
            crime_effect_display = f"{crime_effect:.0f}%"
        else:
            crime_effect_display = "0% (No Effect)"

        return (
            felony_rate_fig,
            detainee_pop_fig,
            crime_effect_fig,
            length_of_stay_fig,
            scenario_display,
            felony_rate_display,
            detainee_pop_display,
            los_display,
            crime_effect_display,
        )

    # -------------------------------------------------------------------------
    # Tab Navigation Callbacks (Combined landing page cards + sidebar)
    # -------------------------------------------------------------------------

    @app.callback(
        [
            Output("main-tabs", "value"),
            Output("nav-home", "className"),
            Output("nav-overview", "className"),
            Output("nav-scenarios", "className"),
            Output("nav-benchmarking", "className"),
            Output("nav-descriptions", "className"),
            Output("nav-about", "className"),
        ],
        [
            Input("nav-home", "n_clicks"),
            Input("nav-overview", "n_clicks"),
            Input("nav-scenarios", "n_clicks"),
            Input("nav-benchmarking", "n_clicks"),
            Input("nav-descriptions", "n_clicks"),
            Input("nav-about", "n_clicks"),
            Input("link-to-overview", "n_clicks"),
            Input("link-to-scenarios", "n_clicks"),
            Input("link-to-benchmarking", "n_clicks"),
            Input("btn-back-to-calculation", "n_clicks"),
            Input("btn-back-to-calc-benchmark", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def sidebar_navigation(
        home_clicks,
        overview_clicks,
        scenarios_clicks,
        benchmarking_clicks,
        descriptions_clicks,
        about_clicks,
        overview_card_clicks,
        scenarios_card_clicks,
        benchmarking_card_clicks,
        back_to_calc_clicks,
        back_to_calc_benchmark_clicks,
    ):
        """Handle navigation from left sidebar buttons and landing page cards."""
        ctx = dash.callback_context

        if not ctx.triggered:
            return dash.no_update

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Map button IDs to tab values (sidebar + landing page cards)
        button_to_tab = {
            "nav-home": "tab-landing",
            "nav-overview": "tab-overview",
            "nav-scenarios": "tab-scenarios",
            "nav-benchmarking": "tab-benchmarking",
            "nav-descriptions": "tab-descriptions",
            "nav-about": "tab-about",
            "link-to-overview": "tab-overview",
            "link-to-scenarios": "tab-scenarios",
            "link-to-benchmarking": "tab-benchmarking",
            "btn-back-to-calculation": "tab-overview",
            "btn-back-to-calc-benchmark": "tab-overview",
        }

        # Get the tab value for the clicked button
        tab_value = button_to_tab.get(button_id, "tab-landing")

        # Update button class names - add 'active' to the clicked button (only for sidebar)
        nav_classes = [
            "nav-button active" if button_id == "nav-home" else "nav-button",
            (
                "nav-button active"
                if (button_id == "nav-overview" or button_id == "link-to-overview")
                else "nav-button"
            ),
            (
                "nav-button active"
                if (button_id == "nav-scenarios" or button_id == "link-to-scenarios")
                else "nav-button"
            ),
            (
                "nav-button active"
                if (button_id == "nav-benchmarking" or button_id == "link-to-benchmarking")
                else "nav-button"
            ),
            "nav-button active" if button_id == "nav-descriptions" else "nav-button",
            "nav-button active" if button_id == "nav-about" else "nav-button",
        ]

        return tab_value, *nav_classes

    # -------------------------------------------------------------------------
    # Download CSV Callback
    # -------------------------------------------------------------------------

    @app.callback(
        Output("download-dataframe-csv", "data"),
        Input("btn-download-csv", "n_clicks"),
        [
            State("scenario-selector", "data"),
            State("detainee-param1", "value"),
            State("detainee-param2", "value"),
            State("society-param2", "value"),
        ],
        prevent_initial_call=True,
    )
    def download_csv(n_clicks, scenario, det_p1, det_p2, soc_p2):
        """Generate and download CSV file with current MVPF results."""
        if n_clicks is None or n_clicks == 0:
            return None

        # Convert string parameters from State to floats
        det_p1 = float(det_p1) if det_p1 is not None else 0.7
        det_p2 = float(det_p2) if det_p2 is not None else 1.0
        soc_p2 = float(soc_p2) if soc_p2 is not None else 70

        # Use default value for community size multiplier
        soc_p1 = 1.0

        params = _convert_dropdown_to_params(
            fel_rate_sel=det_p1, n_detainees_sel=det_p2, n_society_sel=soc_p1, los_days_sel=soc_p2
        )

        result = calculator.calculate(scenario, params)
        csv_string = calculator.export_to_string(result, include_metadata=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mvpf_results_{scenario}_{timestamp}.csv"

        return dict(content=csv_string, filename=filename)

    # -------------------------------------------------------------------------
    # Download Full Analysis Callback
    # -------------------------------------------------------------------------

    @app.callback(
        Output("download-analysis-csv", "data"),
        Input("download-analysis-button", "n_clicks"),
        [
            State("scenario-selector", "data"),
            State("detainee-param1", "value"),
            State("detainee-param2", "value"),
            State("society-param2", "value"),
        ],
        prevent_initial_call=True,
    )
    def download_full_analysis(n_clicks, scenario, det_p1, det_p2, soc_p2):
        """Generate and download comprehensive CSV with calculations and sensitivity analyses."""
        if n_clicks is None or n_clicks == 0:
            return None

        # Convert string parameters from State to floats
        det_p1 = float(det_p1) if det_p1 is not None else 0.7
        det_p2 = float(det_p2) if det_p2 is not None else 1.0
        soc_p2 = float(soc_p2) if soc_p2 is not None else 70
        soc_p1 = 1.0  # Default value for community size multiplier

        # Calculate main result
        params = _convert_dropdown_to_params(
            fel_rate_sel=det_p1, n_detainees_sel=det_p2, n_society_sel=soc_p1, los_days_sel=soc_p2
        )
        result = calculator.calculate(scenario, params)

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Section 1: Current Calculations
        writer.writerow(["CURRENT MVPF CALCULATION"])
        writer.writerow(["Scenario", scenario])
        writer.writerow(["Timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow([])

        writer.writerow(["PARAMETERS"])
        writer.writerow(["Parameter", "Value"])
        writer.writerow(["Felony Rate", f"{params['fel_rate']:.1%}"])
        writer.writerow(["Detainee Population Multiplier", f"{params['n_detainees_mult']:.0%}"])
        writer.writerow(["Community Size Multiplier", f"{params['n_society_mult']:.0%}"])
        writer.writerow(["Length of Stay (days)", f"{params['los_days']:.0f}"])
        writer.writerow(["Crime Effect", f"{params.get('crime_effect', 0):+.0f}%"])
        writer.writerow([])

        writer.writerow(["MAIN RESULTS"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["MVPF", f"{result['mvpf']:.4f}"])
        writer.writerow(["Detainee Values", f"${result['detainee_values']:,.2f}"])
        writer.writerow(["Society Values", f"${result['society_values']:,.2f}"])
        writer.writerow(["Government Costs", f"${result['govt_cost']:,.2f}"])
        writer.writerow([])

        writer.writerow(["DETAINEE BREAKDOWN"])
        writer.writerow(["Component", "Value"])
        for name, value in result.get("detainee_breakdown", {}).items():
            writer.writerow([name, f"${value:,.2f}"])
        writer.writerow([])

        writer.writerow(["SOCIETY BREAKDOWN"])
        writer.writerow(["Component", "Value"])
        for name, value in result.get("society_breakdown", {}).items():
            writer.writerow([name, f"${value:,.2f}"])
        writer.writerow([])

        writer.writerow(["GOVERNMENT BREAKDOWN"])
        writer.writerow(["Component", "Value"])
        for name, value in result.get("govt_breakdown", {}).items():
            writer.writerow([name, f"${value:,.2f}"])
        writer.writerow([])
        writer.writerow([])

        # Section 2: Sensitivity Analyses
        writer.writerow(["SENSITIVITY ANALYSES"])
        writer.writerow([])

        # Felony Rate Sensitivity
        writer.writerow(["FELONY RATE SENSITIVITY"])
        writer.writerow(["Variation", "Value", "MVPF"])
        for variation in ["below", "average", "above"]:
            test_params = params.copy()
            test_params["fel_rate"] = fel_rate_param.dropdown_map[variation]
            test_result = calculator.calculate(scenario, test_params)
            writer.writerow(
                [
                    variation.capitalize(),
                    f"{test_params['fel_rate']:.0%}",
                    f"{test_result['mvpf']:.4f}",
                ]
            )
        writer.writerow([])

        # Detainee Population Sensitivity
        writer.writerow(["DETAINEE POPULATION SENSITIVITY"])
        writer.writerow(["Variation", "Value", "MVPF"])
        for variation in ["below", "average", "above"]:
            test_params = params.copy()
            test_params["n_detainees_mult"] = n_detainees_param.dropdown_map[variation]
            test_result = calculator.calculate(scenario, test_params)
            writer.writerow(
                [
                    variation.capitalize(),
                    f"{test_params['n_detainees_mult']:.0%}",
                    f"{test_result['mvpf']:.4f}",
                ]
            )
        writer.writerow([])

        # Length of Stay Sensitivity
        writer.writerow(["LENGTH OF STAY SENSITIVITY"])
        writer.writerow(["Variation", "Value (days)", "MVPF"])
        for variation in ["below", "average", "above"]:
            test_params = params.copy()
            test_params["los_days"] = los_days_param.dropdown_map[variation]
            test_result = calculator.calculate(scenario, test_params)
            writer.writerow(
                [
                    variation.capitalize(),
                    f"{test_params['los_days']:.0f}",
                    f"{test_result['mvpf']:.4f}",
                ]
            )
        writer.writerow([])

        # Crime Effect Sensitivity
        writer.writerow(["CRIME EFFECT SENSITIVITY"])
        writer.writerow(["Variation", "Value (%)", "MVPF"])
        crime_effects = {"below": -4, "average": 0, "above": 14}
        for variation in ["below", "average", "above"]:
            test_params = params.copy()
            test_result = _calculate_mvpf(
                scenario, det_p1, det_p2, soc_p1, soc_p2, crime_effect=crime_effects[variation]
            )
            writer.writerow(
                [
                    variation.capitalize(),
                    f"{crime_effects[variation]:+.0f}",
                    f"{test_result['mvpf']:.4f}",
                ]
            )
        writer.writerow([])
        writer.writerow([])

        # Section 3: Scenario Comparisons
        writer.writerow(["SCENARIO COMPARISONS"])
        writer.writerow(["Scenario", "MVPF"])
        for test_scenario in ["baseline", "most conservative", "least conservative"]:
            test_result = calculator.calculate(test_scenario, params)
            writer.writerow([test_scenario.title(), f"{test_result['mvpf']:.4f}"])

        csv_string = output.getvalue()
        output.close()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'mvpf_full_analysis_{scenario.replace(" ", "_")}_{timestamp}.csv'

        return dict(content=csv_string, filename=filename)

    # -------------------------------------------------------------------------
    # Download Edge Cases CSV Callback
    # -------------------------------------------------------------------------

    @app.callback(
        Output("download-edge-cases-csv", "data"),
        Input("download-edge-cases-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_edge_cases(n_clicks):
        """Download the pre-generated edge cases CSV file."""
        if n_clicks is None or n_clicks == 0:
            return None

        # Read the static CSV file
        edge_cases_path = "Data/mvpf_edge_cases.csv"

        try:
            with open(edge_cases_path, "r") as f:
                csv_content = f.read()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mvpf_edge_cases_{timestamp}.csv"

            return dict(content=csv_content, filename=filename)
        except FileNotFoundError:
            print(f"Edge cases file not found at {edge_cases_path}")
            return None


# Register all callbacks
register_callbacks(app)


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=True)
