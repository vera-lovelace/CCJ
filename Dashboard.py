"""
MVPF Dashboard Application
Main dashboard layout and callbacks
"""

# Import global components
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd
import os

from content_loader import ContentManager
from mvpf_calculator import MVPFCalculator
from parameters import ParameterRegistry


def load_benchmarks(data_dir='Data'):
    """Load benchmark comparison data from CSV file."""
    filepath = os.path.join(data_dir, 'mvpf_comparisons.csv')
    df = pd.read_csv(filepath)
    return df.to_dict('records')


# Initialize content manager
content = ContentManager()

# Initialize calculator once (singleton pattern for performance)
calculator = MVPFCalculator(data_dir='Data')

# Initialize parameter registry to get CSV-based dropdown options
param_registry = ParameterRegistry(data_dir='Data')

# Get parameter definitions for dropdown generation
fel_rate_param = param_registry.params['fel_rate']
los_days_param = param_registry.params['los_days']
n_detainees_param = param_registry.params['n_detainees_mult']
n_detainees_base_param = param_registry.params['n_detainees_base']
n_society_param = param_registry.params['n_society_mult']

# Build dropdown options from CSV weights
FEL_RATE_OPTIONS = [
    {'label': f"Below Average ({fel_rate_param.dropdown_map['below']:.0%})", 'value': 'below'},
    {'label': f"Average ({fel_rate_param.dropdown_map['average']:.0%})", 'value': 'average'},
    {'label': f"Above Average ({fel_rate_param.dropdown_map['above']:.0%})", 'value': 'above'}
]

LOS_DAYS_OPTIONS = [
    {'label': f"Short ({los_days_param.dropdown_map['below']:.0f} days)", 'value': 'below'},
    {'label': f"Average ({los_days_param.dropdown_map['average']:.0f} days)", 'value': 'average'},
    {'label': f"Long ({los_days_param.dropdown_map['above']:.0f} days)", 'value': 'above'}
]

N_DETAINEES_OPTIONS = [
    {'label': f"Below Average ({n_detainees_param.dropdown_map['below']:.0%})", 'value': 'below'},
    {'label': f"Average ({n_detainees_param.dropdown_map['average']:.0%})", 'value': 'average'},
    {'label': f"Above Average ({n_detainees_param.dropdown_map['above']:.0%})", 'value': 'above'}
]

N_SOCIETY_OPTIONS = [
    {'label': f"Below Average ({n_society_param.dropdown_map['below']:.0%})", 'value': 'below'},
    {'label': f"Average ({n_society_param.dropdown_map['average']:.0%})", 'value': 'average'},
    {'label': f"Above Average ({n_society_param.dropdown_map['above']:.0%})", 'value': 'above'}
]

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Custom CSS for styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: system-ui, -apple-system, sans-serif;
                margin: 0;
                background: linear-gradient(to bottom right, #f8fafc, #f1f5f9);
            }
            .main-container {
                max-width: 1280px;
                margin: 0 auto;
                padding: 24px;
            }
            .sidebar {
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                margin-bottom: 24px;
            }
            .info-tile {
                background: #eff6ff;
                border-left: 4px solid #3b82f6;
                padding: 16px;
                border-radius: 8px;
                margin-bottom: 24px;
            }
            .info-tile h3 {
                color: #1e3a8a;
                font-weight: 600;
                margin: 0 0 8px 0;
                font-size: 16px;
            }
            .info-tile p, .info-tile ul {
                color: #1e40af;
                font-size: 14px;
                line-height: 1.5;
                margin: 8px 0;
            }
            .info-tile ul {
                margin-left: 8px;
                padding-left: 0;
            }
            .info-tile li {
                font-size: 12px;
                margin: 4px 0;
            }
            .info-tile strong {
                font-weight: 600;
            }
            .control-section h3 {
                font-weight: 600;
                color: #1e293b;
                margin: 0 0 12px 0;
                font-size: 16px;
            }
            .control-group {
                margin-bottom: 16px;
            }
            .control-label {
                display: block;
                font-size: 14px;
                font-weight: 500;
                color: #374151;
                margin-bottom: 8px;
            }
            .label-with-info {
                display: flex;
                align-items: center;
                gap: 6px;
                margin-bottom: 8px;
            }
            .info-icon {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 16px;
                height: 16px;
                border-radius: 50%;
                background: #3b82f6;
                color: white;
                font-size: 11px;
                font-weight: 600;
                cursor: pointer;
                flex-shrink: 0;
                position: relative;
                z-index: 1;
            }
            .info-icon:hover {
                z-index: 10000;
            }
            .info-icon:hover::after {
                content: attr(data-tooltip);
                position: absolute;
                left: 24px;
                top: 50%;
                transform: translateY(-50%);
                background: #1e293b;
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 400;
                line-height: 1.4;
                width: 220px;
                z-index: 1000;
                box-shadow: 0 4px 6px rgba(0,0,0,0.2);
                white-space: normal;
            }
            .info-icon:hover::before {
                content: '';
                position: absolute;
                left: 20px;
                top: 50%;
                transform: translateY(-50%);
                width: 0;
                height: 0;
                border-top: 6px solid transparent;
                border-bottom: 6px solid transparent;
                border-right: 6px solid #1e293b;
                z-index: 10002;
            }
            .Select-control, .dash-dropdown {
                font-size: 14px !important;
            }
            .baseline-switch {
                background: white;
                border-radius: 8px;
                padding: 16px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                margin-bottom: 24px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .baseline-label {
                font-size: 14px;
                font-weight: 500;
                color: #374151;
            }
            .button-group {
                display: flex;
                gap: 8px;
            }
            .baseline-button {
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                border: none;
                transition: all 0.2s;
            }
            .baseline-button-active {
                background: #2563eb;
                color: white;
            }
            .baseline-button-inactive {
                background: #e5e7eb;
                color: #374151;
            }
            .baseline-button-inactive:hover {
                background: #d1d5db;
            }
            .kpi-card {
                background: white;
                border-radius: 8px;
                padding: 32px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 24px;
            }
            .kpi-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
            }
            .kpi-title {
                font-size: 20px;
                font-weight: 600;
                color: #1e293b;
            }
            .kpi-badge {
                padding: 4px 12px;
                border-radius: 9999px;
                font-size: 14px;
                font-weight: 600;
            }
            .kpi-value {
                font-size: 60px;
                font-weight: bold;
                color: #111827;
                line-height: 1;
                margin-bottom: 24px;
            }
            .kpi-ratio {
                font-size: 24px;
                color: #6b7280;
                margin-left: 8px;
            }
            .kpi-components {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 16px;
                margin: 24px 0;
            }
            .kpi-component {
                background: #f9fafb;
                border-radius: 12px;
                padding: 20px;
                border: 2px solid #e5e7eb;
                transition: all 0.2s;
            }
            .kpi-component:hover {
                border-color: #3b82f6;
                box-shadow: 0 4px 6px rgba(59, 130, 246, 0.1);
            }
            .kpi-component-link {
                text-decoration: none;
                color: inherit;
                display: block;
            }
            .kpi-component h4 {
                font-size: 13px;
                color: #6b7280;
                margin: 0 0 12px 0;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .kpi-component-link h4 {
                color: #3b82f6;
                cursor: pointer;
            }
            .kpi-component-link:hover h4 {
                text-decoration: underline;
            }
            .kpi-component p {
                font-size: 28px;
                font-weight: 700;
                margin: 0 0 8px 0;
                line-height: 1;
            }
            .kpi-component span {
                font-size: 12px;
                color: #9ca3af;
                font-weight: 400;
            }
            .kpi-calculation {
                margin-top: 24px;
                padding-top: 24px;
                border-top: 1px solid #e5e7eb;
                font-size: 13px;
                color: #6b7280;
            }
            .kpi-interpretation {
                margin-top: 24px;
                padding: 16px;
                background: #f9fafb;
                border-radius: 8px;
            }
            .kpi-interpretation p {
                color: #374151;
                font-size: 14px;
                margin: 0;
                line-height: 1.5;
            }
            .chart-container {
                background: white;
                border-radius: 8px;
                padding: 24px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                margin-bottom: 24px;
            }
            .loading-text {
                font-size: 32px;
                color: #9ca3af;
            }
            .jumbotron {
                background: white;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.07);
                border: 1px solid #e5e7eb;
                transition: all 0.2s ease;
            }
            .jumbotron:hover {
                box-shadow: 0 8px 12px rgba(0,0,0,0.1);
                border-color: #3b82f6;
            }
            .jumbotron-icon {
                width: 48px;
                height: 48px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                margin-bottom: 16px;
            }
            .jumbotron-title {
                font-size: 14px;
                font-weight: 600;
                color: #374151;
                margin: 0 0 4px 0;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .jumbotron-value {
                font-size: 28px;
                font-weight: 700;
                color: #1e293b;
                margin: 0 0 8px 0;
                line-height: 1.2;
            }
            .jumbotron-description {
                font-size: 12px;
                color: #6b7280;
                margin: 0 0 16px 0;
                line-height: 1.4;
            }
            .jumbotron-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 16px;
                margin-bottom: 24px;
            }
            @media (max-width: 1200px) {
                .jumbotron-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
            @media (max-width: 768px) {
                .jumbotron-grid {
                    grid-template-columns: 1fr;
                }
            }
            .benchmark-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 12px;
                margin-top: 16px;
            }
            @media (max-width: 900px) {
                .benchmark-grid {
                    grid-template-columns: 1fr;
                }
            }
            .benchmark-tile {
                background: #f9fafb;
                border-radius: 8px;
                padding: 16px;
                border: 1px solid #e5e7eb;
                transition: all 0.2s ease;
            }
            .benchmark-tile:hover {
                border-color: #3b82f6;
                box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
            }
            .benchmark-tile-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 8px;
            }
            .benchmark-tile-value {
                font-size: 24px;
                font-weight: 700;
                line-height: 1;
            }
            .benchmark-tile-value.positive {
                color: #16a34a;
            }
            .benchmark-tile-value.negative {
                color: #dc2626;
            }
            .benchmark-tile-comparison {
                font-size: 12px;
                font-weight: 600;
                padding: 4px 8px;
                border-radius: 9999px;
            }
            .benchmark-tile-comparison.better {
                background: #dcfce7;
                color: #16a34a;
            }
            .benchmark-tile-comparison.worse {
                background: #fee2e2;
                color: #dc2626;
            }
            .benchmark-tile-name {
                font-size: 13px;
                font-weight: 500;
                color: #374151;
                margin-bottom: 4px;
                line-height: 1.3;
            }
            .benchmark-tile-link {
                font-size: 11px;
                color: #3b82f6;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                gap: 4px;
            }
            .benchmark-tile-link:hover {
                text-decoration: underline;
            }
            .landing-nav-card:hover {
                border-color: #3b82f6 !important;
                box-shadow: 0 8px 16px rgba(59, 130, 246, 0.2) !important;
                transform: translateY(-4px);
            }
            /* Left Sidebar Navigation */
            .app-container {
                display: flex;
                min-height: 100vh;
                background: linear-gradient(to bottom right, #f8fafc, #f1f5f9);
            }
            .left-sidebar {
                width: 240px;
                background: white;
                box-shadow: 2px 0 8px rgba(0,0,0,0.1);
                position: fixed;
                left: 0;
                top: 0;
                height: 100vh;
                overflow-y: auto;
                z-index: 1000;
                padding: 24px 0;
            }
            .sidebar-header {
                padding: 0 20px 20px 20px;
                border-bottom: 1px solid #e5e7eb;
                margin-bottom: 20px;
            }
            .sidebar-header h2 {
                font-size: 18px;
                font-weight: 700;
                color: #1e293b;
                margin: 0 0 4px 0;
            }
            .sidebar-header p {
                font-size: 12px;
                color: #64748b;
                margin: 0;
            }
            .nav-menu {
                list-style: none;
                margin: 0;
                padding: 0;
            }
            .nav-item {
                margin: 0;
            }
            .nav-button {
                display: flex;
                align-items: center;
                width: 100%;
                padding: 12px 20px;
                border: none;
                background: transparent;
                color: #64748b;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                text-align: left;
                gap: 12px;
            }
            .nav-button:hover {
                background: #f8fafc;
                color: #2563eb;
            }
            .nav-button.active {
                background: #eff6ff;
                color: #2563eb;
                border-right: 3px solid #2563eb;
                font-weight: 600;
            }
            .nav-icon {
                font-size: 18px;
                width: 24px;
                text-align: center;
            }
            .main-content {
                margin-left: 240px;
                flex: 1;
                padding: 24px;
                max-width: calc(100% - 240px);
            }
            @media (max-width: 768px) {
                .left-sidebar {
                    width: 200px;
                }
                .main-content {
                    margin-left: 200px;
                    max-width: calc(100% - 200px);
                }
            }
            /* Hide the horizontal tabs navigation bar */
            .custom-tabs-container .tabs__container {
                display: none !important;
            }
            .custom-tabs > div:first-child {
                display: none !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Layout
app.layout = html.Div(className='app-container', children=[
    # Store component for active tab tracking
    dcc.Store(id='active-tab-store', data='tab-landing'),

    # Left Sidebar Navigation
    html.Div(className='left-sidebar', children=[
        html.Div(className='sidebar-header', children=[
            html.H2(content.get('header.title', 'MVPF Analysis Dashboard'), style={
                'fontSize': '18px',
                'fontWeight': '700',
                'color': '#1e293b',
                'margin': '0 0 8px 0'
            }),
            html.P(content.get('header.subtitle', 'Marginal Value of Public Funds Calculation'), style={
                'fontSize': '12px',
                'color': '#64748b',
                'margin': '0 0 16px 0',
                'lineHeight': '1.4'
            })
        ]),
        html.Nav(className='nav-menu', children=[
            html.Div(className='nav-item', children=[
                html.Button('Home', id='nav-home', n_clicks=0, className='nav-button active')
            ]),
            html.Div(className='nav-item', children=[
                html.Button(content.get('tabs.overview', 'Overview'), id='nav-overview', n_clicks=0, className='nav-button')
            ]),
            html.Div(className='nav-item', children=[
                html.Button(content.get('tabs.scenarios', 'Scenario Analysis'), id='nav-scenarios', n_clicks=0, className='nav-button')
            ]),
            html.Div(className='nav-item', children=[
                html.Button('Comparative Benchmarking', id='nav-benchmarking', n_clicks=0, className='nav-button')
            ]),
            html.Div(className='nav-item', children=[
                html.Button('MVPF Explained', id='nav-descriptions', n_clicks=0, className='nav-button')
            ]),
            html.Div(className='nav-item', children=[
                html.Button('About', id='nav-about', n_clicks=0, className='nav-button')
            ])
        ])
    ]),

    # Main Content Area
    html.Div(className='main-content', children=[
                # Download section
                html.Div(className='download-section', style={
                    'display': 'flex',
                    'justifyContent': 'flex-end',
                    'marginBottom': '16px'
                }, children=[
                    html.Button(
                        content.get('download.button_text', 'Download Results (CSV)'),
                        id='btn-download-csv',
                        n_clicks=0,
                        className='download-button',
                        style={
                            'backgroundColor': '#0ea5e9',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '6px',
                            'padding': '10px 20px',
                            'fontSize': '14px',
                            'fontWeight': '600',
                            'cursor': 'pointer',
                            'transition': 'all 0.2s'
                        }
                    ),
                    dcc.Download(id='download-dataframe-csv')
                ]),

                # Tabs Container (headers hidden, controlled by sidebar)
                dcc.Tabs(id='main-tabs', value='tab-landing', parent_className='custom-tabs-container', className='custom-tabs', children=[
                    # Tab 0: Landing Page
                    dcc.Tab(label='Home', value='tab-landing', style={
                        'padding': '12px 24px',
                        'fontWeight': '500',
                        'fontSize': '14px'
                    }, selected_style={
                        'padding': '12px 24px',
                        'fontWeight': '600',
                        'fontSize': '14px',
                        'borderTop': '3px solid #3b82f6',
                        'backgroundColor': 'white'
                    }, children=[
                        html.Div(style={'padding': '48px 24px', 'maxWidth': '900px', 'margin': '0 auto'}, children=[
                            # Title
                            html.H1(content.get('landing.welcome_title', 'Welcome to the MVPF Analysis Dashboard'), style={
                                'fontSize': '36px',
                                'fontWeight': 'bold',
                                'color': '#1e293b',
                                'marginBottom': '24px',
                                'textAlign': 'center'
                            }),

                            # Purpose section
                            html.Div(style={'marginBottom': '32px'}, children=[
                                html.H3(content.get('understanding.purpose.title', 'Purpose'), style={
                                    'fontSize': '20px',
                                    'fontWeight': '600',
                                    'color': '#374151',
                                    'marginTop': '0',
                                    'marginBottom': '12px'
                                }),
                                html.P(
                                    content.get('understanding.purpose.description',
                                                'This interactive dashboard provides a comprehensive analysis of the Marginal Value of Public Funds (MVPF) '
                                                'for Cook County Jail operations. It enables policymakers, researchers, and stakeholders to evaluate the '
                                                'social welfare impacts of detention policies through a systematic, data-driven framework.'),
                                    style={
                                        'fontSize': '15px',
                                        'color': '#4b5563',
                                        'lineHeight': '1.8',
                                        'margin': '0'
                                    }
                                )
                            ]),

                            # Information Tile
                            html.Div(
                                style={
                                    'background': 'white',
                                    'padding': '20px',
                                    'borderRadius': '8px',
                                    'marginBottom': '32px',
                                    'border': '1px solid #e5e7eb'
                                },
                                children=[
                                    html.H3(
                                        content.get('info_tile.heading', 'About MVPF'),
                                        style={
                                            'fontSize': '16px',
                                            'fontWeight': '600',
                                            'color': '#374151',
                                            'marginTop': '0',
                                            'marginBottom': '8px'
                                        }
                                    ),

                                    html.P(
                                        content.get(
                                            'info_tile.description',
                                            'The MVPF measures the ratio of beneficiaries willingness to pay to the net cost to the government'
                                        ),
                                        style={
                                            'fontSize': '14px',
                                            'color': '#6b7280',
                                            'lineHeight': '1.6',
                                            'margin': '0 0 12px 0'
                                        }
                                    ),

                                    html.P(
                                        [
                                            html.Strong(
                                                content.get('info_tile.formula_label', 'Formula:'),
                                                style={'color': '#374151'}
                                            ),
                                            html.Br(),
                                            content.get(
                                                'info_tile.formula',
                                                'MVPF = (Detainee + Society) / Government Cost'
                                            )
                                        ],
                                        style={
                                            'fontSize': '14px',
                                            'color': '#6b7280',
                                            'lineHeight': '1.6',
                                            'margin': '0 0 16px 0'
                                        }
                                    ),

                                    # New section: application label + text
                                    html.P(
                                        [
                                            html.Strong(
                                                content.get('info_tile.application_label', 'Our application of MVPF'),
                                                style={'color': '#374151'}
                                            ),
                                            html.Br(),
                                            content.get(
                                                'info_tile.application',
                                                'How we apply MVPF to Cook County Jail.'
                                            )
                                        ],
                                        style={
                                            'fontSize': '14px',
                                            'color': '#6b7280',
                                            'lineHeight': '1.6',
                                            'margin': '0'
                                        }
                                    ),
                                ]
                            ),

                            # Description
                            html.Div(style={
                                'backgroundColor': '#f0f9ff',
                                'padding': '32px',
                                'borderRadius': '12px',
                                'marginBottom': '48px',
                                'borderLeft': '6px solid #3b82f6'
                            }, children=[
                                html.P([
                                    'This interactive dashboard helps you analyze the ',
                                    html.Strong('Marginal Value of Public Funds (MVPF)'),
                                    ' for Cook County Jail operations. The MVPF measures the social welfare benefit of a policy per dollar of government spending.'
                                ], style={
                                    'fontSize': '16px',
                                    'color': '#334155',
                                    'lineHeight': '1.8',
                                    'marginBottom': '16px'
                                }),
                                html.P(
                                    'Use the tabs below to explore different aspects of the analysis, from high-level overview to detailed scenario comparisons and benchmarking against other government programs.',
                                    style={
                                        'fontSize': '16px',
                                        'color': '#334155',
                                        'lineHeight': '1.8',
                                        'margin': '0'
                                    }
                                )
                            ]),

                            # Navigation Cards
                            html.H2('Explore the Dashboard', style={
                                'fontSize': '24px',
                                'fontWeight': '600',
                                'color': '#1e293b',
                                'marginBottom': '24px',
                                'textAlign': 'center'
                            }),

                            html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr 1fr', 'gap': '24px'}, children=[
                                # Card 1: Overview
                                html.A(href='#', id='link-to-overview', style={'textDecoration': 'none'}, children=[
                                    html.Div(style={
                                        'backgroundColor': 'white',
                                        'padding': '32px',
                                        'borderRadius': '12px',
                                        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                                        'border': '2px solid transparent',
                                        'transition': 'all 0.2s',
                                        'cursor': 'pointer'
                                    }, className='landing-nav-card', children=[
                                        html.Div(style={
                                            'width': '56px',
                                            'height': '56px',
                                            'borderRadius': '12px',
                                            'backgroundColor': '#dbeafe',
                                            'display': 'flex',
                                            'alignItems': 'center',
                                            'justifyContent': 'center',
                                            'marginBottom': '20px'
                                        }, children=[
                                            html.Span('📊', style={'fontSize': '28px'})
                                        ]),
                                        html.H3('Overview', style={
                                            'fontSize': '20px',
                                            'fontWeight': '600',
                                            'color': '#1e293b',
                                            'marginBottom': '12px'
                                        }),
                                        html.P(
                                            'View the MVPF calculation, key performance indicators, and comparison charts showing detainee values, society values, and government costs.',
                                            style={
                                                'fontSize': '14px',
                                                'color': '#64748b',
                                                'lineHeight': '1.6',
                                                'margin': '0'
                                            }
                                        )
                                    ])
                                ]),

                                # Card 2: Scenario Analysis
                                html.A(href='#', id='link-to-scenarios', style={'textDecoration': 'none'}, children=[
                                    html.Div(style={
                                        'backgroundColor': 'white',
                                        'padding': '32px',
                                        'borderRadius': '12px',
                                        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                                        'border': '2px solid transparent',
                                        'transition': 'all 0.2s',
                                        'cursor': 'pointer'
                                    }, className='landing-nav-card', children=[
                                        html.Div(style={
                                            'width': '56px',
                                            'height': '56px',
                                            'borderRadius': '12px',
                                            'backgroundColor': '#fef3c7',
                                            'display': 'flex',
                                            'alignItems': 'center',
                                            'justifyContent': 'center',
                                            'marginBottom': '20px'
                                        }, children=[
                                            html.Span('🔍', style={'fontSize': '28px'})
                                        ]),
                                        html.H3('Scenario Analysis', style={
                                            'fontSize': '20px',
                                            'fontWeight': '600',
                                            'color': '#1e293b',
                                            'marginBottom': '12px'
                                        }),
                                        html.P(
                                            'Compare different policy scenarios and analyze parameter sensitivity to understand how changes in assumptions affect MVPF outcomes.',
                                            style={
                                                'fontSize': '14px',
                                                'color': '#64748b',
                                                'lineHeight': '1.6',
                                                'margin': '0'
                                            }
                                        )
                                    ])
                                ]),

                                # Card 3: Comparative Benchmarking
                                html.A(href='#', id='link-to-benchmarking', style={'textDecoration': 'none'}, children=[
                                    html.Div(style={
                                        'backgroundColor': 'white',
                                        'padding': '32px',
                                        'borderRadius': '12px',
                                        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                                        'border': '2px solid transparent',
                                        'transition': 'all 0.2s',
                                        'cursor': 'pointer'
                                    }, className='landing-nav-card', children=[
                                        html.Div(style={
                                            'width': '56px',
                                            'height': '56px',
                                            'borderRadius': '12px',
                                            'backgroundColor': '#dcfce7',
                                            'display': 'flex',
                                            'alignItems': 'center',
                                            'justifyContent': 'center',
                                            'marginBottom': '20px'
                                        }, children=[
                                            html.Span('📈', style={'fontSize': '28px'})
                                        ]),
                                        html.H3('Comparative Benchmarking', style={
                                            'fontSize': '20px',
                                            'fontWeight': '600',
                                            'color': '#1e293b',
                                            'marginBottom': '12px'
                                        }),
                                        html.P(
                                            'Compare Cook County Jail MVPF against other government programs and policy initiatives to contextualize the value of public spending.',
                                            style={
                                                'fontSize': '14px',
                                                'color': '#64748b',
                                                'lineHeight': '1.6',
                                                'margin': '0'
                                            }
                                        )
                                    ])
                                ])
                            ])
                        ])
                    ]),

                    # Tab 1: Overview - KPI, Main Chart, Interpretation, Benchmarks
                    dcc.Tab(label=content.get('tabs.overview', 'Overview'), value='tab-overview', style={
                        'padding': '12px 24px',
                        'fontWeight': '500',
                        'fontSize': '14px'
                    }, selected_style={
                        'padding': '12px 24px',
                        'fontWeight': '600',
                        'fontSize': '14px',
                        'borderTop': '3px solid #3b82f6',
                        'backgroundColor': 'white'
                    }, children=[
                        html.Div(style={'padding': '24px 0'}, children=[
                            # Overview Tab Description Placeholder
                            html.Div(className='chart-container', style={
                                'background': '#fef3c7',
                                'borderLeft': '4px solid #f59e0b',
                                'marginBottom': '24px'
                            }, children=[
                                html.H3(
                                    content.get('placeholders.overview_intro.title',
                                                'Placeholder: Overview Tab Introduction'),
                                    style={
                                        'fontSize': '18px',
                                        'fontWeight': '600',
                                        'color': '#92400e',
                                        'marginTop': '0',
                                        'marginBottom': '12px'
                                    }
                                ),
                                html.Div(children=[
                                    html.P(
                                        content.get('placeholders.overview_intro.paragraph1', ''),
                                        style={
                                            'fontSize': '14px',
                                            'color': '#92400e',
                                            'lineHeight': '1.6',
                                            'margin': '0 0 12px 0',
                                            'whiteSpace': 'pre-line'
                                        }
                                    )
                                ])
                            ]),

                            # Parameter Jumbotrons Grid
                            html.Div(className='jumbotron-grid', style={'marginBottom': '24px'}, children=[
                                # Jumbotron 1: Felony Rate
                                html.Div(className='jumbotron', children=[
                                    html.Div(className='jumbotron-icon', style={'background': '#dbeafe'}, children=[
                                        html.Span('%%', style={'color': '#2563eb'})
                                    ]),
                                    html.H4(content.get('controls.felony_rate.title', 'Felony Rate'), className='jumbotron-title'),
                                    html.P(id='felony-rate-value', children=f"{fel_rate_param.default_value:.0%}", className='jumbotron-value'),
                                    html.P(content.get('controls.felony_rate.tooltip', fel_rate_param.description), className='jumbotron-description'),
                                    dcc.Slider(
                                        id='detainee-param1',
                                        min=0.5,
                                        max=1.0,
                                        value=0.7,
                                        marks={
                                            0.5: {'label': '50%', 'style': {'fontSize': '11px'}},
                                            0.7: {'label': '70%', 'style': {'fontSize': '11px'}},
                                            1.0: {'label': '100%', 'style': {'fontSize': '11px'}}
                                        },
                                        step=0.01,
                                        tooltip={'placement': 'bottom', 'always_visible': False}
                                    )
                                ]),

                                # Jumbotron 2: Detainee Population
                                html.Div(className='jumbotron', children=[
                                    html.Div(className='jumbotron-icon', style={'background': '#fef3c7'}, children=[
                                        html.Span('#', style={'color': '#d97706', 'fontWeight': '700'})
                                    ]),
                                    html.H4(content.get('controls.detainee_population.title', 'Detainee Population'), className='jumbotron-title'),
                                    html.P(id='detainee-population-value', children=f"{n_detainees_param.base_value:,.0f}", className='jumbotron-value'),
                                    html.P(content.get('controls.detainee_population.tooltip', n_detainees_param.description), className='jumbotron-description'),

                                    # Baseline Population Input
                                    html.Div(style={'marginBottom': '16px'}, children=[
                                        html.Label('Baseline Population:', style={
                                            'fontSize': '12px',
                                            'fontWeight': '500',
                                            'color': '#374151',
                                            'marginBottom': '4px',
                                            'display': 'block'
                                        }),
                                        dcc.Input(
                                            id='detainee-baseline-input',
                                            type='number',
                                            value=n_detainees_param.base_value,
                                            min=0,
                                            step=100,
                                            style={
                                                'width': '100%',
                                                'padding': '8px',
                                                'fontSize': '14px',
                                                'border': '1px solid #d1d5db',
                                                'borderRadius': '6px',
                                                'boxSizing': 'border-box'
                                            }
                                        )
                                    ]),

                                    # Population Multiplier Slider
                                    html.Label('Population Multiplier:', style={
                                        'fontSize': '12px',
                                        'fontWeight': '500',
                                        'color': '#374151',
                                        'marginBottom': '8px',
                                        'display': 'block'
                                    }),
                                    dcc.Slider(
                                        id='detainee-param2',
                                        min=0.8,
                                        max=1.2,
                                        value=1.0,
                                        marks={
                                            0.8: {'label': '80%', 'style': {'fontSize': '11px'}},
                                            1.0: {'label': '100%', 'style': {'fontSize': '11px'}},
                                            1.2: {'label': '120%', 'style': {'fontSize': '11px'}}
                                        },
                                        step=0.01,
                                        tooltip={'placement': 'bottom', 'always_visible': False}
                                    )
                                ]),

                                # Jumbotron 3: Crime Effect
                                html.Div(className='jumbotron', children=[
                                    html.Div(className='jumbotron-icon', style={'background': '#fef2f2'}, children=[
                                        html.Span('⚠️', style={'color': '#dc2626'})
                                    ]),
                                    html.H4(content.get('controls.crime_effect.title', 'Crime Effect'), className='jumbotron-title'),
                                    html.P(id='crime-effect-value', children='0', className='jumbotron-value'),
                                    html.P(content.get('controls.crime_effect.description', 'Crime impact multiplier on detention outcomes'), className='jumbotron-description'),
                                    dcc.Slider(
                                        id='crime-effect-slider',
                                        min=-4,
                                        max=14,
                                        value=0,
                                        marks={
                                            -4: {'label': '-4 (Large Decrease)', 'style': {'fontSize': '8px'}},
                                            0: {'label': '0 (No Effect)', 'style': {'fontSize': '8px'}},
                                            5: {'label': '5 (Moderate Increase)', 'style': {'fontSize': '8px'}},
                                            14: {'label': '14 (Large Increase)', 'style': {'fontSize': '8px'}}
                                        },
                                        step=None,
                                        tooltip={'placement': 'bottom', 'always_visible': False}
                                    )
                                ]),

                                # Jumbotron 4: Length of Stay
                                html.Div(className='jumbotron', children=[
                                    html.Div(className='jumbotron-icon', style={'background': '#fee2e2'}, children=[
                                        html.Span('D', style={'color': '#dc2626', 'fontWeight': '700'})
                                    ]),
                                    html.H4(content.get('controls.length_of_stay.title', 'Length of Stay'), className='jumbotron-title'),
                                    html.P(id='los-days-value', children=f"{los_days_param.default_value:.0f} days", className='jumbotron-value'),
                                    html.P(content.get('controls.length_of_stay.tooltip', los_days_param.description), className='jumbotron-description'),
                                    dcc.Slider(
                                        id='society-param2',
                                        min=60,
                                        max=203,
                                        value=70,
                                        marks={
                                            60: {'label': '60', 'style': {'fontSize': '11px'}},
                                            70: {'label': '70', 'style': {'fontSize': '11px'}},
                                            203: {'label': '203', 'style': {'fontSize': '11px'}}
                                        },
                                        step=1,
                                        tooltip={'placement': 'bottom', 'always_visible': False}
                                    )
                                ])
                            ]),

                            # Scenario Selection Section
                            html.Div(className='jumbotron', style={'marginTop': '0', 'marginBottom': '24px'}, children=[
                                html.H4(content.get('controls.scenario_selection.title', 'Scenario Selection'), style={
                                    'fontSize': '18px',
                                    'fontWeight': '600',
                                    'color': '#374151',
                                    'marginTop': '0',
                                    'marginBottom': '12px'
                                }),

                                # Hidden store for selected scenario
                                dcc.Store(id='scenario-selector', data='baseline'),
                                # Scenerio Lead-in text
                                html.Div(style={'marginBottom': '16px'}, children=[
                                    html.P(
                                        content.get('placeholders.overview_intro.paragraph2', ''),
                                        style={
                                            'fontSize': '14px',
                                            'color': '#4b5563',
                                            'lineHeight': '1.6',
                                            'margin': '0 0 10px 0',
                                            'whiteSpace': 'pre-line'
                                        }
                                    ),
                                    html.P(
                                        content.get('placeholders.overview_intro.paragraph3', ''),
                                        style={
                                            'fontSize': '14px',
                                            'color': '#4b5563',
                                            'lineHeight': '1.6',
                                            'margin': '0 0 10px 0',
                                            'whiteSpace': 'pre-line'
                                        }
                                    ),
                                    html.P(
                                        content.get('placeholders.overview_intro.paragraph4', ''),
                                        style={
                                            'fontSize': '14px',
                                            'color': '#4b5563',
                                            'lineHeight': '1.6',
                                            'margin': '0',
                                            'whiteSpace': 'pre-line'
                                        }
                                    )
                                ]),

                                # Scenario Jumbotrons Grid (now clickable)
                                html.Div(className='jumbotron-grid', style={'marginBottom': '24px'}, children=[
                                    # Jumbotron 1: Baseline Scenario
                                    html.Button(
                                        id='scenario-btn-baseline',
                                        n_clicks=0,
                                        className='jumbotron scenario-card',
                                        style={'border': '3px solid #2563eb', 'cursor': 'pointer'},
                                        children=[
                                            html.Div(className='jumbotron-icon', style={'background': '#dbeafe'}, children=[
                                                html.Span('📊', style={'color': '#2563eb'})
                                            ]),
                                            html.H4(content.get('scenarios.cards.baseline.title', 'Baseline - Current Operations'), className='jumbotron-title', style={'fontWeight': '700'}),
                                            html.P(content.get('scenarios.cards.baseline.value', 'Focus on individual harm plus potential criminogenic effects'), className='jumbotron-value', style={'fontSize': '14px', 'fontWeight': '500', 'color': '#2563eb'}),
                                            html.P(content.get('scenarios.cards.baseline.description', 'Choose this if you think detention may worsen public safety'), className='jumbotron-description')
                                        ]
                                    ),

                                    # Jumbotron 2: Most Conservative Scenario
                                    html.Button(
                                        id='scenario-btn-most-conservative',
                                        n_clicks=0,
                                        className='jumbotron scenario-card',
                                        style={'border': '2px solid #e5e7eb', 'cursor': 'pointer'},
                                        children=[
                                            html.Div(className='jumbotron-icon', style={'background': '#fef3c7'}, children=[
                                                html.Span('🛡️', style={'color': '#d97706'})
                                            ]),
                                            html.H4(content.get('scenarios.cards.most_conservative.title', 'Less Negative Detainee Value - Conservative'), className='jumbotron-title', style={'fontWeight': '700'}),
                                            html.P(content.get('scenarios.cards.most_conservative.value', 'Focus on conservative valuation of individual harms'), className='jumbotron-value', style={'fontSize': '14px', 'fontWeight': '500', 'color': '#d97706'}),
                                            html.P(content.get('scenarios.cards.most_conservative.description', 'Choose this if you believe detainee harm should be valued using smaller, survey-based estimates'), className='jumbotron-description')
                                        ]
                                    ),

                                    # Jumbotron 3: Least Conservative Scenario
                                    html.Button(
                                        id='scenario-btn-least-conservative',
                                        n_clicks=0,
                                        className='jumbotron scenario-card',
                                        style={'border': '2px solid #e5e7eb', 'cursor': 'pointer'},
                                        children=[
                                            html.Div(className='jumbotron-icon', style={'background': '#dcfce7'}, children=[
                                                html.Span('🚀', style={'color': '#16a34a'})
                                            ]),
                                            html.H4(content.get('scenarios.cards.least_conservative.title', 'Least Conservative (lowest MVPF)'), className='jumbotron-title', style={'fontWeight': '700'}),
                                            html.P(content.get('scenarios.cards.least_conservative.value', 'Focus on broad social harms and criminogenic effects'), className='jumbotron-value', style={'fontSize': '14px', 'fontWeight': '500', 'color': '#16a34a'}),
                                            html.P(content.get('scenarios.cards.least_conservative.description', 'Choose this if you think detention harms both individuals and communities and may increase crime'), className='jumbotron-description')
                                        ]
                                    )
                                ])
                            ]),

                            # Calculate Button Section
                            html.Div(className='calculate-section', style={
                                'display': 'flex',
                                'justifyContent': 'center',
                                'marginBottom': '32px'
                            }, children=[
                                html.Button(
                                    'Calculate MVPF',
                                    id='btn-calculate',
                                    n_clicks=0,
                                    style={
                                        'backgroundColor': '#2563eb',
                                        'color': 'white',
                                        'border': 'none',
                                        'borderRadius': '8px',
                                        'padding': '14px 48px',
                                        'fontSize': '16px',
                                        'fontWeight': '600',
                                        'cursor': 'pointer',
                                        'transition': 'all 0.2s',
                                        'boxShadow': '0 4px 6px rgba(37, 99, 235, 0.25)'
                                    }
                                )
                            ]),

                            # KPI Card (Full Width with embedded interpretation)
                            html.Div(id='kpi-card', style={'marginBottom': '24px'}),

                            # MVPF Calculation Purpose Placeholder
                            html.Div(className='chart-container', style={
                                'background': '#f0f9ff',
                                'borderLeft': '4px solid #3b82f6',
                                'marginBottom': '24px'
                            }, children=[
                                html.H3(content.get('placeholders.mvpf_purpose.title', 'Placeholder: Purpose of MVPF Calculation'), style={
                                    'fontSize': '18px',
                                    'fontWeight': '600',
                                    'color': '#1e3a8a',
                                    'marginTop': '0',
                                    'marginBottom': '12px'
                                }),
                                html.P(
                                    content.get('placeholders.mvpf_purpose.content', 'This section will explain the purpose and methodology of the MVPF calculation, providing context for interpreting the results shown above and the detailed breakdowns below.'),
                                    style={
                                        'fontSize': '14px',
                                        'color': '#1e40af',
                                        'lineHeight': '1.6',
                                        'margin': '0'
                                    }
                                )
                            ]),

                            # Charts Row: Numerator and Denominator Charts
                            html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '24px'}, children=[
                                # Numerator Chart (Detainee + Society Values)
                                html.Div(className='chart-container', children=[
                                    dcc.Graph(id='numerator-chart')
                                ]),

                                # Denominator Chart (Government Cost vs Numerator)
                                html.Div(className='chart-container', children=[
                                    dcc.Graph(id='denominator-chart')
                                ])
                            ])
                        ])
                    ]),

                    # Tab 2: Scenario Analysis - Scenario Selection + Subcomponents Chart
                    dcc.Tab(label=content.get('tabs.scenarios', 'Scenario Analysis'), value='tab-scenarios', style={
                        'padding': '12px 24px',
                        'fontWeight': '500',
                        'fontSize': '14px'
                    }, selected_style={
                        'padding': '12px 24px',
                        'fontWeight': '600',
                        'fontSize': '14px',
                        'borderTop': '3px solid #3b82f6',
                        'backgroundColor': 'white'
                    }, children=[
                        html.Div(style={'padding': '24px 0'}, children=[
                            # Tab 2 Description Placeholder
                            html.Div(style={
                                'backgroundColor': '#f9fafb',
                                'padding': '20px',
                                'borderRadius': '8px',
                                'marginBottom': '24px',
                                'borderLeft': '4px solid #3b82f6'
                            }, children=[
                                html.H3(content.get('placeholders.scenarios_intro.title', 'Placeholder for Tab 2 Description'), style={
                                    'fontSize': '18px',
                                    'fontWeight': '600',
                                    'color': '#374151',
                                    'margin': '0 0 8px 0'
                                }),
                                html.P(content.get('placeholders.scenarios_intro.content', 'Placeholder for: Overview of the Scenario Analysis tab, explaining what users can explore and learn from the visualizations below.'), style={
                                    'fontSize': '14px',
                                    'color': '#6b7280',
                                    'margin': '0',
                                    'lineHeight': '1.6'
                                })
                            ]),

                            # Alternative Scenarios Description
                            html.Div(
                                style={
                                    'backgroundColor': '#fffbeb',
                                    'padding': '20px',
                                    'borderRadius': '8px',
                                    'marginBottom': '24px',
                                    'borderLeft': '4px solid #f59e0b'
                                },
                                children=[
                                    html.H3(
                                        content.get(
                                            'placeholders.alt_scenarios.title',
                                            'Alternative Scenarios Description'
                                        ),
                                        style={
                                            'fontSize': '18px',
                                            'fontWeight': '600',
                                            'color': '#374151',
                                            'margin': '0 0 12px 0'
                                        }
                                    ),
                                    html.P(
                                        content.get('placeholders.alt_scenarios.paragraph_1', ''),
                                        style={
                                            'fontSize': '14px',
                                            'color': '#92400e',
                                            'margin': '0 0 8px 0',
                                            'lineHeight': '1.6'
                                        }
                                    ),
                                    html.P(
                                        content.get('placeholders.alt_scenarios.paragraph_2', ''),
                                        style={
                                            'fontSize': '14px',
                                            'color': '#92400e',
                                            'margin': '0 0 8px 0',
                                            'lineHeight': '1.6'
                                        }
                                    ),
                                    html.P(
                                        content.get('placeholders.alt_scenarios.paragraph_3', ''),
                                        style={
                                            'fontSize': '14px',
                                            'color': '#92400e',
                                            'margin': '0',
                                            'lineHeight': '1.6'
                                        }
                                    )
                                ]
                            ),

                            # Sensitivity Analysis Section Header
                            html.H3('Sensitivity Analysis', style={
                                'fontSize': '24px',
                                'fontWeight': '600',
                                'color': '#1e293b',
                                'marginTop': '0',
                                'marginBottom': '8px'
                            }),
                            html.P('Examine how each parameter affects MVPF values across baseline, most conservative, and least conservative scenarios.', style={
                                'fontSize': '14px',
                                'color': '#6b7280',
                                'marginBottom': '24px'
                            }),

                            # Sensitivity Analysis Graphs (2x2 Grid)
                            html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '24px', 'marginBottom': '48px'}, children=[
                                # Row 1
                                html.Div(className='chart-container', children=[
                                    dcc.Graph(id='sensitivity-felony-rate')
                                ]),
                                html.Div(className='chart-container', children=[
                                    dcc.Graph(id='sensitivity-detainee-population')
                                ]),
                                # Row 2
                                html.Div(className='chart-container', children=[
                                    dcc.Graph(id='sensitivity-crime-effect')
                                ]),
                                html.Div(className='chart-container', children=[
                                    dcc.Graph(id='sensitivity-length-of-stay')
                                ])
                            ]),

                            # Side-by-side charts: Scenario Comparison and Parameter Sensitivity
                            html.Div(style={
                                'display': 'flex',
                                'gap': '24px',
                                'marginBottom': '24px'
                            }, children=[
                                html.Div(className='chart-container', style={'flex': '1'}, children=[
                                    dcc.Graph(id='scenario-comparison-chart')
                                ]),
                                html.Div(className='chart-container', style={'flex': '1'}, children=[
                                    dcc.Graph(id='parameter-comparison-chart')
                                ])
                            ])
                        ])
                    ]),

                    # Tab 3: Comparative Benchmarking
                    dcc.Tab(label='Comparative Benchmarking', value='tab-benchmarking', style={
                        'padding': '12px 24px',
                        'fontWeight': '500',
                        'fontSize': '14px'
                    }, selected_style={
                        'padding': '12px 24px',
                        'fontWeight': '600',
                        'fontSize': '14px',
                        'borderTop': '3px solid #3b82f6',
                        'backgroundColor': 'white'
                    }, children=[
                        html.Div(style={'padding': '24px 0'}, children=[
                            # Benchmark Card
                            html.Div(id='benchmark-card')
                        ])
                    ]),

                    # Tab 4: Descriptions
                    dcc.Tab(label='MVPF Explained', value='tab-descriptions', style={
                        'padding': '12px 24px',
                        'fontWeight': '500',
                        'fontSize': '14px'
                    }, selected_style={
                        'padding': '12px 24px',
                        'fontWeight': '600',
                        'fontSize': '14px',
                        'borderTop': '3px solid #3b82f6',
                        'backgroundColor': 'white'
                    }, children=[
                        html.Div(style={'padding': '24px 0'}, children=[
                            # MVPF Explainer Section
                            html.Div(className='chart-container', style={'background': '#f8fafc'}, children=[
                                html.H3(content.get('mvpf_explainer.section_title', 'Understanding MVPF'), style={
                                    'fontSize': '20px',
                                    'fontWeight': '600',
                                    'color': '#1e293b',
                                    'marginBottom': '16px',
                                    'marginTop': '0'
                                }),

                                html.Div(
                                    style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '24px'},
                                    children=[
                                        # Left column
                                        html.Div(children=[
                                            html.H4(
                                                content.get('mvpf_explainer.what_is_mvpf.heading', 'What is MVPF?'),
                                                style={
                                                    'fontSize': '16px',
                                                    'fontWeight': '600',
                                                    'color': '#374151',
                                                    'marginTop': '0',
                                                    'marginBottom': '12px'
                                                }
                                            ),
                                            html.P(
                                                content.get('mvpf_explainer.what_is_mvpf.description', 'The Marginal Value of Public Funds (MVPF) is a metric that measures the social welfare benefit of a policy per dollar of government spending.'),
                                                style={
                                                    'color': '#4b5563',
                                                    'fontSize': '14px',
                                                    'lineHeight': '1.6',
                                                    'margin': '0'
                                                }
                                            ),
                                            html.Div(children=[
                                                html.H4(
                                                    content.get('mvpf_explainer.applying_to_detention.heading', 'Applying MVPF to detention'),
                                                    style={
                                                        'fontSize': '16px',
                                                        'fontWeight': '600',
                                                        'color': '#374151',
                                                        'marginTop': '1',
                                                        'marginBottom': '12px'
                                                    }
                                                ),
                                                html.P(
                                                    content.get('mvpf_explainer.applying_to_detention.paragraph1', 'Most MVPF work looks at policies where the person subject to the policy is also the main beneficiary.'),
                                                    style={
                                                        'color': '#4b5563',
                                                        'fontSize': '14px',
                                                        'lineHeight': '1.6',
                                                        'margin': '0',
                                                    }
                                                ),
                                                html.P(
                                                    content.get('mvpf_explainer.applying_to_detention.paragraph2', 'Most studies on detention focus on marginal changes.'),
                                                    style={
                                                        'color': '#4b5563',
                                                        'fontSize': '14px',
                                                        'lineHeight': '1.6',
                                                        'marginTop': '1',
                                                        'marginBottom': '12px'
                                                    }
                                                ),
                                                html.P(
                                                    content.get('mvpf_explainer.applying_to_detention.paragraph3'),
                                                    style={
                                                        'color': '#4b5563',
                                                        'fontSize': '14px',
                                                        'lineHeight': '1.6',
                                                        'marginTop': '1',
                                                        'marginBottom': '12px'
                                                    }
                                                )
                                            ])
                                        ])
                                    ]
                                ),

                                # Methodology section (visual equation + top-justified + in-page links)
                                html.Div(style={'marginBottom': '32px'}, children=[
                                    html.H3(
                                        content.get('understanding.methodology.title', 'Methodology'),
                                        style={
                                            'fontSize': '20px',
                                            'fontWeight': '600',
                                            'color': '#374151',
                                            'marginTop': '0',
                                            'marginBottom': '12px'
                                        }
                                    ),

                                    html.P(
                                        content.get(
                                            'understanding.methodology.description',
                                            'This dashboard computes the Marginal Value of Public Funds (MVPF) as:'
                                        ),
                                        style={
                                            'fontSize': '15px',
                                            'color': '#4b5563',
                                            'lineHeight': '1.6',
                                            'marginBottom': '12px'
                                        }
                                    ),

                                    # MVPF = (Total Value) / (Total Government Cost)
                                    html.Div(style={
                                        'display': 'grid',
                                        'gridTemplateColumns': '1fr auto 1fr',
                                        'alignItems': 'start',   # top-justify columns
                                        'gap': '12px',
                                        'background': 'white',
                                        'border': '1px solid #e5e7eb',
                                        'borderRadius': '10px',
                                        'padding': '16px',
                                        'marginBottom': '16px'
                                    }, children=[
                                        # Left: Numerator
                                        html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '10px'}, children=[
                                            html.Div(style={
                                                'border': '1px solid #cbd5e1',
                                                'borderRadius': '10px',
                                                'padding': '10px 12px',
                                                'background': '#f8fafc'
                                            }, children=[
                                                html.Div('Total Value', style={'fontSize': '12px', 'fontWeight': '700', 'color': '#334155', 'textTransform': 'uppercase', 'letterSpacing': '0.04em'}),
                                                html.Div('to Detainees and Society', style={'fontSize': '14px', 'fontWeight': '600', 'color': '#0f172a', 'marginTop': '2px'})
                                            ]),

                                            # Components within Total Value
                                            html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr', 'gap': '8px'}, children=[
                                                html.Div(style={'borderLeft': '4px solid #3b82f6', 'border': '1px solid #e5e7eb', 'borderRadius': '10px', 'padding': '10px 12px', 'background': 'white'}, children=[
                                                    html.A('Detainee Harm', href='#components-breakdown', style={'fontSize': '13px', 'fontWeight': '700', 'color': '#111827', 'textDecoration': 'none', 'cursor': 'pointer'}),
                                                    html.Div('Harm from time in custody', style={'fontSize': '12px', 'color': '#6b7280', 'marginTop': '2px'})
                                                ]),
                                                html.Div(style={'borderLeft': '4px solid #10b981', 'border': '1px solid #e5e7eb', 'borderRadius': '10px', 'padding': '10px 12px', 'background': 'white'}, children=[
                                                    html.A('Court Appearance', href='#components-breakdown', style={'fontSize': '13px', 'fontWeight': '700', 'color': '#111827', 'textDecoration': 'none', 'cursor': 'pointer'}),
                                                    html.Div('Benefits from improved appearance', style={'fontSize': '12px', 'color': '#6b7280', 'marginTop': '2px'})
                                                ]),
                                                html.Div(style={'borderLeft': '4px solid #ef4444', 'border': '1px solid #e5e7eb', 'borderRadius': '10px', 'padding': '10px 12px', 'background': 'white'}, children=[
                                                    html.A('Crime Effects', href='#components-breakdown', style={'fontSize': '13px', 'fontWeight': '700', 'color': '#111827', 'textDecoration': 'none', 'cursor': 'pointer'}),
                                                    html.Div('Set to 0 in baseline; adjustable', style={'fontSize': '12px', 'color': '#6b7280', 'marginTop': '2px'})
                                                ]),
                                                html.Div(style={'borderLeft': '4px solid #8b5cf6', 'border': '1px solid #e5e7eb', 'borderRadius': '10px', 'padding': '10px 12px', 'background': 'white'}, children=[
                                                    html.A('Community Spillovers', href='#components-breakdown', style={'fontSize': '13px', 'fontWeight': '700', 'color': '#111827', 'textDecoration': 'none', 'cursor': 'pointer'}),
                                                    html.Div('Optional; depends on scenario', style={'fontSize': '12px', 'color': '#6b7280', 'marginTop': '2px'})
                                                ])
                                            ])
                                        ]),

                                        # Center: Division / equals
                                        html.Div(style={
                                            'display': 'flex',
                                            'flexDirection': 'column',
                                            'alignItems': 'center',
                                            'justifyContent': 'flex-start',
                                            'gap': '8px',
                                            'paddingTop': '44px'  # tweak (36-52px) to align with stacks
                                        }, children=[
                                            html.Div('÷', style={'fontSize': '22px', 'fontWeight': '800', 'color': '#111827', 'lineHeight': '1'}),
                                            html.Div('MVPF', style={'fontSize': '12px', 'fontWeight': '800', 'color': '#374151', 'letterSpacing': '0.06em'})
                                        ]),

                                        # Right: Denominator
                                        html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '10px'}, children=[
                                            html.Div(style={
                                                'border': '1px solid #cbd5e1',
                                                'borderRadius': '10px',
                                                'padding': '10px 12px',
                                                'background': '#f8fafc'
                                            }, children=[
                                                html.Div('Total Government Cost', style={'fontSize': '12px', 'fontWeight': '700', 'color': '#334155', 'textTransform': 'uppercase', 'letterSpacing': '0.04em'}),
                                            ]),

                                            html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr', 'gap': '8px'}, children=[
                                                html.Div(style={'borderLeft': '4px solid #0ea5e9', 'border': '1px solid #e5e7eb', 'borderRadius': '10px', 'padding': '10px 12px', 'background': 'white'}, children=[
                                                    html.A('CCJ Operating Costs', href='#components-breakdown', style={'fontSize': '13px', 'fontWeight': '700', 'color': '#111827', 'textDecoration': 'none', 'cursor': 'pointer'}),
                                                    html.Div('Fixed baseline denominator', style={'fontSize': '12px', 'color': '#6b7280', 'marginTop': '2px'})
                                                ]),
                                                html.Div(style={'borderLeft': '4px solid #ef4444', 'border': '1px solid #e5e7eb', 'borderRadius': '10px', 'padding': '10px 12px', 'background': 'white'}, children=[
                                                    html.A('Crime Effect-Related Costs/Savings', href='#components-breakdown', style={'fontSize': '13px', 'fontWeight': '700', 'color': '#111827', 'textDecoration': 'none', 'cursor': 'pointer'}),
                                                    html.Div('Only non-zero when Crime Effect is non-zero', style={'fontSize': '12px', 'color': '#6b7280', 'marginTop': '2px'})
                                                ])
                                            ])
                                        ])
                                    ]),

                                # Parameter-to-component legend
                                html.Div(style={
                                    'background': 'white',
                                    'border': '1px solid #e5e7eb',
                                    'borderRadius': '10px',
                                    'padding': '14px 16px'
                                }, children=[
                                    html.Div('How parameters map to MVPF components', style={
                                        'fontSize': '13px',
                                        'fontWeight': '700',
                                        'color': '#111827',
                                        'marginBottom': '12px'
                                    }),

                                    html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '14px'}, children=[

                                        # Detainee Population
                                        html.Div(children=[
                                            html.Div('Detainee Population', style={
                                                'fontSize': '12px',
                                                'fontWeight': '700',
                                                'color': '#111827',
                                                'marginBottom': '6px'
                                            }),
                                            html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '6px'}, children=[
                                                html.Div('Detainee Harm', style={
                                                    'fontSize': '11px', 'padding': '3px 8px', 'borderRadius': '999px',
                                                    'background': '#dbeafe', 'color': '#1e40af'
                                                }),
                                                html.Div('Court Appearance', style={
                                                    'fontSize': '11px', 'padding': '3px 8px', 'borderRadius': '999px',
                                                    'background': '#dcfce7', 'color': '#166534'
                                                }),
                                                html.Div('Crime Effect', style={
                                                    'fontSize': '11px', 'padding': '3px 8px', 'borderRadius': '999px',
                                                    'background': '#dcfce7', 'color': '#166534'
                                                }),
                                                html.Div('Community Spillovers', style={
                                                    'fontSize': '11px', 'padding': '3px 8px', 'borderRadius': '999px',
                                                    'background': '#dcfce7', 'color': '#166534'
                                                }),
                                                html.Div('Crime Cost', style={
                                                    'fontSize': '11px', 'padding': '3px 8px', 'borderRadius': '999px',
                                                    'background': '#fecaca', 'color': '#7f1d1d'
                                                })
                                            ])
                                        ]),

                                        # Length of Stay
                                        html.Div(children=[
                                            html.Div('Length of Stay', style={
                                                'fontSize': '12px',
                                                'fontWeight': '700',
                                                'color': '#111827',
                                                'marginBottom': '6px'
                                            }),
                                            html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '6px'}, children=[
                                                html.Div('Detainee Harm', style={
                                                    'fontSize': '11px', 'padding': '3px 8px', 'borderRadius': '999px',
                                                    'background': '#dbeafe', 'color': '#1e40af'
                                                }),
                                                html.Div('Community Spillovers', style={
                                                    'fontSize': '11px', 'padding': '3px 8px', 'borderRadius': '999px',
                                                    'background': '#dcfce7', 'color': '#166534'
                                                })
                                            ])
                                        ]),

                                        # Crime Effect
                                        html.Div(children=[
                                            html.Div('Crime Effect Assumption', style={
                                                'fontSize': '12px',
                                                'fontWeight': '700',
                                                'color': '#111827',
                                                'marginBottom': '6px'
                                            }),
                                            html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '6px'}, children=[
                                                html.Div('Crime Effect', style={
                                                    'fontSize': '11px', 'padding': '3px 8px', 'borderRadius': '999px',
                                                    'background': '#dcfce7', 'color': '#166534'
                                                }),
                                                html.Div('Crime Cost', style={
                                                    'fontSize': '11px', 'padding': '3px 8px', 'borderRadius': '999px',
                                                    'background': '#fecaca', 'color': '#7f1d1d'
                                                })
                                            ])
                                        ]),

                                        # Felony Share
                                        html.Div(children=[
                                            html.Div('Felony Share', style={
                                                'fontSize': '12px',
                                                'fontWeight': '700',
                                                'color': '#111827',
                                                'marginBottom': '6px'
                                            }),
                                            html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '6px'}, children=[
                                                html.Div('Crime Effect', style={
                                                    'fontSize': '11px', 'padding': '3px 8px', 'borderRadius': '999px',
                                                    'background': '#dcfce7', 'color': '#166534'
                                                }),
                                                html.Div('Crime Cost', style={
                                                    'fontSize': '11px', 'padding': '3px 8px', 'borderRadius': '999px',
                                                    'background': '#fecaca', 'color': '#7f1d1d'
                                                })
                                            ])
                                        ])
                                    ])
                                ]),

                                # Components breakdown
                                html.Div(
                                         id='components-breakdown',
                                         style={'marginTop': '24px', 'paddingTop': '24px', 'borderTop': '1px solid #e5e7eb'},
                                         children=[
                                             html.H4(content.get('components_breakdown.title', 'Components'), style={
                                                 'fontSize': '16px',
                                                 'fontWeight': '600',
                                                 'color': '#374151',
                                                 'marginTop': '0',
                                                 'marginBottom': '16px'
                                             }),
                                             html.Div(
                                                 style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr 1fr', 'gap': '16px'},
                                                 children=[
                                                     # Detainee Values
                                                     html.Div(
                                                         id='detainee-values-section',
                                                         style={
                                                             'background': 'white',
                                                             'padding': '20px',
                                                             'borderRadius': '8px',
                                                             'borderLeft': '4px solid #2563eb'
                                                         },
                                                         children=[
                                                             html.H5(content.get('components_breakdown.detainee_values.title', 'Detainee Values'), style={
                                                                 'fontSize': '15px',
                                                                 'fontWeight': '600',
                                                                 'color': '#2563eb',
                                                                 'margin': '0 0 12px 0'
                                                             }),

                                                             html.P(
                                                                 content.get('components_breakdown.detainee_values.description',
                                                                 'Detainee Values capture the total harm detention imposes on people who are jailed. '
                                                                 'We measure this using a willingness-to-pay lens, estimating how much a person would trade '
                                                                 'to avoid being detained. This reflects short-term harms, disruptions to work and family life, '
                                                                 'and long-term effects on health, income, and stability.'),
                                                                 style={
                                                                     'fontSize': '14px',
                                                                     'color': '#374151',
                                                                     'margin': '0 0 12px 0',
                                                                     'lineHeight': '1.6'
                                                                 }
                                                             ),

                                                             # Subcomponents header
                                                             html.Div(className='label-with-info', children=[
                                                                 html.Span(content.get('components_breakdown.detainee_values.subcomponents_label', 'Subcomponents'), style={
                                                                     'fontWeight': '500',
                                                                     'fontSize': '14px'
                                                                    })

                                                                ]),
                                                             html.Div(children=[
                                                                # RHV
                                                                 html.Div([
                                                                     html.Button(
                                                                         content.get('components_breakdown.detainee_values.subcomponents.harm_valuation.button_text', 'Detainee Harm: Willingness to Pay derived from Relative Harm Valuation'),
                                                                         id='detainee-harm-btn',
                                                                         n_clicks=0,
                                                                         className='collapse-toggle'
                                                                     ),
                                                                     html.Div(
                                                                         id='detainee-harm',
                                                                         style={'display': 'none'},
                                                                         children=[
                                                                             html.P(
                                                                                 content.get('components_breakdown.detainee_values.subcomponents.harm_valuation.explanation', ''),
                                                                                 style={
                                                                                     'fontSize': '13px',
                                                                                     'color': '#6b7280',
                                                                                     'margin': '6px 0'
                                                                                 }
                                                                             )
                                                                         ]
                                                                     )
                                                                 ]),
                                                                 # Willingness to Pay for Freedom
                                                                 html.Div([
                                                                     html.Button(
                                                                         content.get('components_breakdown.detainee_values.subcomponents.wtp_freedom.button_text', 'Detainee Harm: Willingness to Pay for Freedom'),
                                                                         id='detainee-wtp-btn',
                                                                         n_clicks=0,
                                                                         className='collapse-toggle'
                                                                     ),
                                                                     html.Div(
                                                                         id='detainee-wtp',
                                                                         style={'display': 'none'},
                                                                         children=[
                                                                             html.P(
                                                                                 content.get('components_breakdown.detainee_values.subcomponents.wtp_freedom.explanation', ''),
                                                                                 style={
                                                                                     'fontSize': '13px',
                                                                                     'color': '#6b7280',
                                                                                     'margin': '6px 0'
                                                                                 }
                                                                             )
                                                                         ]
                                                                     )
                                                                 ]),
                                                             ])
                                                         ]
                                                     ),

                                                     # Society Values
                                                     html.Div(
                                                         id='society-values-section',
                                                         style={
                                                             'background': 'white',
                                                             'padding': '20px',
                                                             'borderRadius': '8px',
                                                             'borderLeft': '4px solid #16a34a'
                                                         },
                                                         children=[
                                                             html.H5(content.get('components_breakdown.society_values.title', 'Society Values'), style={
                                                                 'fontSize': '15px',
                                                                 'fontWeight': '600',
                                                                 'color': '#16a34a',
                                                                 'margin': '0 0 12px 0'
                                                             }),

                                                             html.P(
                                                                 content.get('components_breakdown.society_values.description',
                                                                 'Society Values measure how detention affects external factors like public safety, victimization risk, and community wellbeing. '
                                                                 'These values summarize the effects felt by people outside the jail and convert those effects into a '
                                                                 'common dollar scale for comparison.'),
                                                                 style={
                                                                     'fontSize': '14px',
                                                                     'color': '#374151',
                                                                     'margin': '0 0 12px 0',
                                                                     'lineHeight': '1.6'
                                                                 }
                                                             ),

                                                             html.Div(className='label-with-info', children=[
                                                                 html.Span(content.get('components_breakdown.society_values.subcomponents_label', 'Subcomponents'), style={
                                                                     'fontWeight': '500',
                                                                     'fontSize': '14px'
                                                                 }
                                                                )
                                                             ]
                                                             ),
                                                             html.Div(children=[
                                                                 # 1. Crime Prevention
                                                                 html.Div([
                                                                     html.Button(
                                                                         content.get('components_breakdown.society_values.subcomponents.crime_prevention.button_text', 'Crime Prevention'),
                                                                         id='society-crime-btn',
                                                                         n_clicks=0,
                                                                         className='collapse-toggle'
                                                                     ),
                                                                     html.Div(
                                                                         id='society-crime',
                                                                         style={'display': 'none'},
                                                                         children=[
                                                                             html.P(
                                                                                 content.get('components_breakdown.society_values.subcomponents.crime_prevention.explanation', ''),
                                                                                 style={
                                                                                     'fontSize': '13px',
                                                                                     'color': '#6b7280'
                                                                                 }
                                                                             )
                                                                         ]
                                                                     )
                                                                 ]),
                                                                 # 2. Court Appearance Effects
                                                                 html.Div([
                                                                     html.Button(
                                                                         content.get('components_breakdown.society_values.subcomponents.court_appearance.button_text', 'Court Appearance Effects'),
                                                                         id='society-court-btn',
                                                                         n_clicks=0,
                                                                         className='collapse-toggle'
                                                                     ),
                                                                     html.Div(
                                                                         id='society-court',
                                                                         style={'display': 'none'},
                                                                         children=[
                                                                             html.P(
                                                                                 content.get('components_breakdown.society_values.subcomponents.court_appearance.explanation', ''),
                                                                                 style={
                                                                                     'fontSize': '13px',
                                                                                     'color': '#6b7280'
                                                                                 }
                                                                             )
                                                                         ]
                                                                     )
                                                                 ]),

                                                                 # 3. Community Spillovers
                                                                 html.Div([
                                                                     html.Button(
                                                                         content.get('components_breakdown.society_values.subcomponents.community_spillovers.button_text', 'Community and Economic Spillovers'),
                                                                         id='society-spill-btn',
                                                                         n_clicks=0,
                                                                         className='collapse-toggle'
                                                                     ),
                                                                     html.Div(
                                                                         id='society-spill',
                                                                         style={'display': 'none'},
                                                                         children=[
                                                                             html.P(
                                                                                 content.get('components_breakdown.society_values.subcomponents.community_spillovers.explanation', ''),
                                                                                 style={
                                                                                     'fontSize': '13px',
                                                                                     'color': '#6b7280'
                                                                                 }
                                                                             )
                                                                         ]
                                                                     )
                                                                 ])
                                                             ])
                                                         ]
                                                     ),

                                                     # Government Cost
                                                     html.Div(
                                                         id='government-cost-section',
                                                         style={
                                                             'background': 'white',
                                                             'padding': '20px',
                                                             'borderRadius': '8px',
                                                             'borderLeft': '4px solid #dc2626'
                                                         },
                                                         children=[
                                                             html.H5(content.get('components_breakdown.government_cost.title', 'Government Cost'), style={
                                                                 'fontSize': '15px',
                                                                 'fontWeight': '600',
                                                                 'color': '#dc2626',
                                                                 'margin': '0 0 12px 0'
                                                             }),

                                                             html.P(
                                                                 content.get('components_breakdown.government_cost.description',
                                                                 'Government Cost reflects all public spending required to run the detention system. This includes daily '
                                                                 'operations, staffing, healthcare, facilities, court processing, and administrative overhead. It represents '
                                                                 'the fiscal cost taxpayers bear to support the current level of detention.'),
                                                                 style={
                                                                     'fontSize': '14px',
                                                                     'color': '#374151',
                                                                     'margin': '0 0 12px 0',
                                                                     'lineHeight': '1.6'
                                                                 }
                                                             ),

                                                             html.Div(className='label-with-info', children=[
                                                                 html.Span(content.get('components_breakdown.government_cost.subcomponents_label', 'Subcomponents'), style={
                                                                     'fontWeight': '500',
                                                                     'fontSize': '14px'
                                                                 }
                                                                 )
                                                             ]
                                                            ),

                                                             html.Div(children=[
                                                                 # Operational Cost
                                                                 html.Div([
                                                                     html.Button(
                                                                         content.get('components_breakdown.government_cost.subcomponents.operational.button_text', 'Operational Costs'),
                                                                         id='gov-op-btn',
                                                                         n_clicks=0,
                                                                         className='collapse-toggle'
                                                                     ),
                                                                     html.Div(
                                                                         id='gov-op',
                                                                         style={'display': 'none'},
                                                                         children=[
                                                                             html.P(
                                                                                 content.get('components_breakdown.government_cost.subcomponents.operational.explanation', ''),
                                                                                 style={
                                                                                     'fontSize': '13px',
                                                                                     'color': '#6b7280'
                                                                                 }
                                                                             )
                                                                         ]
                                                                     )
                                                                 ]),

                                                                 # Crime Effect Costs
                                                                 html.Div([
                                                                     html.Button(
                                                                         content.get('components_breakdown.government_cost.subcomponents.crime_decrease.button_text', 'Costs associated with Crime Effect: Decrease'),
                                                                         id='gov-crime-decrease-btn',
                                                                         n_clicks=0,
                                                                         className='collapse-toggle'
                                                                     ),
                                                                     html.Div(
                                                                         id='gov-crime-decrease',
                                                                         style={'display': 'none'},
                                                                         children=[
                                                                             html.P(
                                                                                 content.get('components_breakdown.government_cost.subcomponents.crime_decrease.explanation', ''),
                                                                                 style={
                                                                                     'fontSize': '13px',
                                                                                     'color': '#6b7280'
                                                                                 }
                                                                             )
                                                                         ]
                                                                     )
                                                                 ]),
                                                             ])
                                                         ],

                                                     ),

                                                 ]
                                             )
                                         ])
                                    ]),


                                ]),

                            # Scenarios section
                            html.Div(className='chart-container', style={'background': '#f8fafc', 'marginTop': '32px'}, children=[
                                html.H3('Scenarios', style={
                                    'fontSize': '20px',
                                    'fontWeight': '600',
                                    'color': '#1e293b',
                                    'marginBottom': '16px',
                                    'marginTop': '0'
                                }),
                                html.P('Three normative scenarios offer different perspectives on how to value detention impacts:', style={
                                    'fontSize': '15px',
                                    'color': '#4b5563',
                                    'marginBottom': '20px'
                                }),
                                html.Div(
                                    style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr 1fr', 'gap': '16px'},
                                    children=[
                                        # Baseline Scenario
                                        html.Div(
                                            id='scenario-baseline',
                                            className='jumbotron',
                                            style={
                                                'background': 'white',
                                                'padding': '20px',
                                                'borderRadius': '8px',
                                                'borderLeft': '4px solid #2563eb'
                                            },
                                            children=[
                                                html.H4(content.get('scenarios_explained.baseline.title', 'Baseline Scenario'), style={
                                                    'fontSize': '16px',
                                                    'fontWeight': '600',
                                                    'color': '#2563eb',
                                                    'margin': '0 0 12px 0'
                                                }),
                                                html.P(
                                                    content.get('scenarios_explained.baseline.description', 'Focuses on individual harm to detainees plus potential criminogenic effects of detention.'),
                                                    style={
                                                        'fontSize': '14px',
                                                        'color': '#374151',
                                                        'lineHeight': '1.6',
                                                        'margin': '0'
                                                    }
                                                )
                                            ]
                                        ),

                                        # Most Conservative Scenario
                                        html.Div(
                                            id='scenario-most-conservative',
                                            className='jumbotron',
                                            style={
                                                'background': 'white',
                                                'padding': '20px',
                                                'borderRadius': '8px',
                                                'borderLeft': '4px solid #d97706'
                                            },
                                            children=[
                                                html.H4(content.get('scenarios_explained.most_conservative.title', 'Conservative Scenario'), style={
                                                    'fontSize': '16px',
                                                    'fontWeight': '600',
                                                    'color': '#d97706',
                                                    'margin': '0 0 12px 0'
                                                }),
                                                html.P(
                                                    content.get('scenarios_explained.most_conservative.description', 'Uses smaller survey-based estimates to value detainee harm, producing less negative MVPF values.'),
                                                    style={
                                                        'fontSize': '14px',
                                                        'color': '#374151',
                                                        'lineHeight': '1.6',
                                                        'margin': '0'
                                                    }
                                                )
                                            ]
                                        ),

                                        # Least Conservative Scenario
                                        html.Div(
                                            id='scenario-least-conservative',
                                            className='jumbotron',
                                            style={
                                                'background': 'white',
                                                'padding': '20px',
                                                'borderRadius': '8px',
                                                'borderLeft': '4px solid #16a34a'
                                            },
                                            children=[
                                                html.H4(content.get('scenarios_explained.least_conservative.title', 'Least Conservative Scenario'), style={
                                                    'fontSize': '16px',
                                                    'fontWeight': '600',
                                                    'color': '#16a34a',
                                                    'margin': '0 0 12px 0'
                                                }),
                                                html.P(
                                                    content.get('scenarios_explained.least_conservative.description', 'Includes broad social harms to communities and families, plus criminogenic effects of detention.'),
                                                    style={
                                                        'fontSize': '14px',
                                                        'color': '#374151',
                                                        'lineHeight': '1.6',
                                                        'margin': '0'
                                                    }
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]),

                            # Parameters section
                            html.Div(className='chart-container', style={'background': '#f8fafc', 'marginTop': '32px'},
                                     children=[
                                         html.H3('Analysis Parameters', style={
                                             'fontSize': '20px',
                                             'fontWeight': '600',
                                             'color': '#1e293b',
                                             'marginBottom': '16px',
                                             'marginTop': '0'
                                         }),
                                         html.P(
                                             'You can adjust several parameters that act as multipliers to the components in the MVPF set-up. These include: i. the number of people detained, ii. the composition of cases, iii. the average length of stay, and iv. the assumption about detention’s effect on crime. These inputs scale the numerator and denominator components of the MVPF and let you test how sensitive the results are to policy or system changes. The defaults for each parameter capture the picture of Cook County Jail in 2018. The other options available are outer bounds for sensitivity analysis, and some alternatives based on our broad review of the literature.',
                                             style={
                                                 'fontSize': '15px',
                                                 'color': '#4b5563',
                                                 'marginBottom': '20px'
                                             }),

                                         html.Div(
                                             style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '16px'},
                                             children=[
                                                 # Felony Rate
                                                 html.Div(
                                                     id='parameter-felony-rate',
                                                     className='jumbotron',
                                                     style={'background': 'white', 'padding': '20px',
                                                            'borderRadius': '8px', 'borderLeft': '4px solid #3b82f6'},
                                                     children=[
                                                         html.H4(
                                                             content.get('parameters.felony_rate.title', 'Felony Rate'),
                                                             style={'fontSize': '16px', 'fontWeight': '600',
                                                                    'color': '#3b82f6', 'margin': '0 0 12px 0'}
                                                         ),
                                                         html.Div(children=[
                                                             html.Div(style={'marginBottom': '10px'}, children=[
                                                                 html.Div(
                                                                     sec.get('label', ''),
                                                                     style={'fontSize': '12px', 'fontWeight': '700',
                                                                            'color': '#374151',
                                                                            'textTransform': 'uppercase',
                                                                            'letterSpacing': '0.04em',
                                                                            'marginBottom': '4px'}
                                                                 ),
                                                                 html.P(
                                                                     sec.get('text', ''),
                                                                     style={'fontSize': '13px', 'color': '#374151',
                                                                            'lineHeight': '1.5', 'margin': '0'}
                                                                 )
                                                             ])
                                                             for sec in
                                                             content.get('parameters.felony_rate.sections', [])
                                                             if sec.get('text')
                                                         ])
                                                     ]
                                                 ),

                                                 # Detainee Population
                                                 html.Div(
                                                     id='parameter-detainee-population',
                                                     className='jumbotron',
                                                     style={'background': 'white', 'padding': '20px',
                                                            'borderRadius': '8px', 'borderLeft': '4px solid #10b981'},
                                                     children=[
                                                         html.H4(
                                                             content.get('parameters.detainee_population.title',
                                                                         'Detainee Population'),
                                                             style={'fontSize': '16px', 'fontWeight': '600',
                                                                    'color': '#10b981', 'margin': '0 0 12px 0'}
                                                         ),
                                                         html.Div(children=[
                                                             html.Div(style={'marginBottom': '10px'}, children=[
                                                                 html.Div(
                                                                     sec.get('label', ''),
                                                                     style={'fontSize': '12px', 'fontWeight': '700',
                                                                            'color': '#374151',
                                                                            'textTransform': 'uppercase',
                                                                            'letterSpacing': '0.04em',
                                                                            'marginBottom': '4px'}
                                                                 ),
                                                                 html.P(
                                                                     sec.get('text', ''),
                                                                     style={'fontSize': '13px', 'color': '#374151',
                                                                            'lineHeight': '1.5', 'margin': '0'}
                                                                 )
                                                             ])
                                                             for sec in
                                                             content.get('parameters.detainee_population.sections', [])
                                                             if sec.get('text')
                                                         ])
                                                     ]
                                                 ),

                                                 # Length of Stay
                                                 html.Div(
                                                     id='parameter-length-of-stay',
                                                     className='jumbotron',
                                                     style={'background': 'white', 'padding': '20px',
                                                            'borderRadius': '8px', 'borderLeft': '4px solid #f59e0b'},
                                                     children=[
                                                         html.H4(
                                                             content.get('parameters.length_of_stay.title',
                                                                         'Length of Stay'),
                                                             style={'fontSize': '16px', 'fontWeight': '600',
                                                                    'color': '#f59e0b', 'margin': '0 0 12px 0'}
                                                         ),
                                                         html.Div(children=[
                                                             html.Div(style={'marginBottom': '10px'}, children=[
                                                                 html.Div(
                                                                     sec.get('label', ''),
                                                                     style={'fontSize': '12px', 'fontWeight': '700',
                                                                            'color': '#374151',
                                                                            'textTransform': 'uppercase',
                                                                            'letterSpacing': '0.04em',
                                                                            'marginBottom': '4px'}
                                                                 ),
                                                                 html.P(
                                                                     sec.get('text', ''),
                                                                     style={'fontSize': '13px', 'color': '#374151',
                                                                            'lineHeight': '1.5', 'margin': '0'}
                                                                 )
                                                             ])
                                                             for sec in
                                                             content.get('parameters.length_of_stay.sections', [])
                                                             if sec.get('text')
                                                         ])
                                                     ]
                                                 ),

                                                 # Crime Effect
                                                 html.Div(
                                                     id='parameter-crime-effect',
                                                     className='jumbotron',
                                                     style={'background': 'white', 'padding': '20px',
                                                            'borderRadius': '8px', 'borderLeft': '4px solid #ef4444'},
                                                     children=[
                                                         html.H4(
                                                             content.get('parameters.crime_effect.title',
                                                                         'Crime Effect'),
                                                             style={'fontSize': '16px', 'fontWeight': '600',
                                                                    'color': '#ef4444', 'margin': '0 0 12px 0'}
                                                         ),
                                                         html.Div(children=[
                                                             html.Div(style={'marginBottom': '10px'}, children=[
                                                                 html.Div(
                                                                     sec.get('label', ''),
                                                                     style={'fontSize': '12px', 'fontWeight': '700',
                                                                            'color': '#374151',
                                                                            'textTransform': 'uppercase',
                                                                            'letterSpacing': '0.04em',
                                                                            'marginBottom': '4px'}
                                                                 ),
                                                                 html.P(
                                                                     sec.get('text', ''),
                                                                     style={'fontSize': '13px', 'color': '#374151',
                                                                            'lineHeight': '1.5', 'margin': '0'}
                                                                 )
                                                             ])
                                                             for sec in
                                                             content.get('parameters.crime_effect.sections', [])
                                                             if sec.get('text')
                                                         ])
                                                     ]
                                                 ),
                                             ]
                                         )
                                     ]),


                            # Limitations section
                                html.Div(style={'marginBottom': '0'}, children=[
                                    html.H3('Limitations and Considerations', style={
                                        'fontSize': '20px',
                                        'fontWeight': '600',
                                        'color': '#374151',
                                        'marginTop': '0',
                                        'marginBottom': '12px'
                                    }),
                                    html.P(
                                        'While this tool provides valuable insights, users should be aware of several important limitations:',
                                        style={
                                            'fontSize': '15px',
                                            'color': '#4b5563',
                                            'lineHeight': '1.8',
                                            'marginBottom': '12px'
                                        }
                                    ),
                                    html.Ul(style={'fontSize': '15px', 'color': '#4b5563', 'lineHeight': '1.8', 'marginBottom': '16px'}, children=[
                                        html.Li('Estimates rely on available research and may not capture all local context'),
                                        html.Li('Willingness-to-pay measures have inherent uncertainties and ethical considerations'),
                                        html.Li('Results should be interpreted as informative estimates rather than precise predictions'),
                                        html.Li('Policy decisions should consider multiple factors beyond MVPF analysis alone')
                                    ]),
                                    html.P(
                                        'This tool is designed to inform policy discussions and should be used alongside other evidence, '
                                        'stakeholder input, and contextual knowledge about Cook County Jail operations.',
                                        style={
                                            'fontSize': '15px',
                                            'color': '#4b5563',
                                            'lineHeight': '1.8',
                                            'margin': '0',
                                            'fontStyle': 'italic'
                                        }
                                    )
                                ])
                        ])
                    ]),

                    # Tab 5: About this Data Tool
                    dcc.Tab(label='About', value='tab-about', style={
                        'padding': '12px 24px',
                        'fontWeight': '500',
                        'fontSize': '14px'
                    }, selected_style={
                        'padding': '12px 24px',
                        'fontWeight': '600',
                        'fontSize': '14px',
                        'borderTop': '3px solid #3b82f6',
                        'backgroundColor': 'white'
                    }, children=[
                        html.Div(style={'padding': '24px 0', 'maxWidth': '900px', 'margin': '0 auto'}, children=[
                            html.Div(className='chart-container', children=[
                                html.H2('Data Sources', style={
                                    'fontSize': '28px',
                                    'fontWeight': 'bold',
                                    'color': '#1e293b',
                                    'marginTop': '0',
                                    'marginBottom': '24px'
                                }),
                                html.H2('About Cook County Jail', style={
                                    'fontSize': '28px',
                                    'fontWeight': 'bold',
                                    'color': '#1e293b',
                                    'marginTop': '0',
                                    'marginBottom': '24px'
                                }),
                                html.H2('Contact', style={
                                    'fontSize': '28px',
                                    'fontWeight': 'bold',
                                    'color': '#1e293b',
                                    'marginTop': '0',
                                    'marginBottom': '24px'
                                }),


                            ])
                        ])
                    ])
                ]),

                # Acknowledgements Section (Inside main-content, at bottom)
                html.Div(style={
                    'marginTop': '48px',
                    'paddingTop': '48px',
                    'borderTop': '2px solid #e5e7eb'
                }, children=[
            html.H2('Acknowledgements', style={
                'fontSize': '14px',
                'fontWeight': 'bold',
                'color': '#1e293b',
                'marginTop': '0',
                'marginBottom': '24px'
            }),

            # Development section
            html.Div(style={'marginBottom': '32px'}, children=[

                html.P(
                    'This data tool was developed by Adrienn Sinapis J. and Lara Pesce Ares, as part of the "Building Data Products for Public Impact" clinic led by Diag Davenport at the University of California, Berkeley. It is intended to support evidence-based policymaking and research on criminal justice reform.'
                    'We gratefully acknowledge the contributions of researchers, data scientists, and policy experts who made this work possible.',
                    style={
                        'fontSize': '12px',
                        'color': '#4b5563',
                        'lineHeight': '1.8',
                        'margin': '0'
                    }
                ),


                html.P(
                    'This tool builds upon the MVPF framework applies it to '
                    'the context of pretrial detention. We acknowledge the foundational research in criminal justice, '
                    'welfare economics, and public policy that informs our methodology.',
                    style={
                        'fontSize': '12px',
                        'color': '#4b5563',
                        'lineHeight': '1.8',
                        'margin': '0'
                    }
                ),


                html.P(
                    'We thank Cook County government agencies for providing access to administrative data and operational information. '
                    'This project also benefited from open-source software tools and libraries that enable interactive data visualization and analysis.',
                    style={
                        'fontSize': '12px',
                        'color': '#4b5563',
                        'lineHeight': '1.8',
                        'margin': '0'
                    }
                )
            ]),


            # Disclaimer section
            html.Div(style={
                'marginBottom': '0',
                'backgroundColor': '#f9fafb',
                'padding': '20px',
                'borderRadius': '8px',
                'borderLeft': '4px solid #3b82f6'
            }, children=[
                html.H3('Disclaimer', style={
                    'fontSize': '12px',
                    'fontWeight': '600',
                    'color': '#374151',
                    'marginTop': '0',
                    'marginBottom': '12px'
                }),
                html.P(
                    'The views and findings presented in this tool are those of the authors and do not necessarily reflect '
                    'the official positions or policies of Cook County government, funding organizations, or affiliated institutions. '
                    'All estimates should be interpreted as analytical tools to inform discussion rather than definitive policy prescriptions.',
                    style={
                        'fontSize': '12px',
                        'color': '#4b5563',
                        'lineHeight': '1.8',
                        'margin': '0',
                        'fontStyle': 'italic'
                    }
                )
            ])
        ])
    ])
])

# =============================================================================
# CALLBACKS MODULE
# All dashboard callbacks are registered via register_callbacks()
# =============================================================================


def _get_scenario_description(scenario):
    """Return the description for a given scenario."""
    descriptions = {
        'baseline': 'Represents current operations at Cook County Jail with standard parameters. This scenario serves as the reference point for comparison.',
        'most conservative': 'Uses conservative estimates for all parameters, minimizing potential benefits and maximizing costs. Provides a lower-bound estimate of MVPF.',
        'least conservative': 'Uses optimistic estimates that maximize potential benefits and minimize costs. Provides an upper-bound estimate of MVPF.'
    }
    return descriptions.get(scenario, 'No description available for this scenario.')


def _toggle_style(n_clicks, style):
    """Helper function to toggle visibility of collapsible sections."""
    if not n_clicks:
        return style or {'display': 'none'}
    if not style or style.get('display') == 'none':
        return {'display': 'block'}
    return {'display': 'none'}

def _convert_dropdown_to_params(fel_rate_sel, n_detainees_sel, n_society_sel, los_days_sel, n_detainees_base=None, crime_effect=0):
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
    baseline = n_detainees_base if n_detainees_base is not None else n_detainees_base_param.default_value

    # Sliders now return numeric values directly
    return {
        'fel_rate': fel_rate_sel,
        'los_days': los_days_sel,
        'n_detainees_mult': n_detainees_sel,
        'n_detainees_base': baseline,
        'n_society_mult': n_society_sel,
        'crime_weight_mult': 1.0,
        'crime_effect': crime_effect
    }


def _calculate_mvpf(scenario, detainee_param1, detainee_param2, society_param1, society_param2, detainee_baseline=None, crime_effect=0):
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
        crime_effect=crime_effect
    )

    result = calculator.calculate(scenario, params)

    # Extract breakdown values for backwards compatibility
    detainee_breakdown = list(result['detainee_breakdown'].values())
    society_breakdown = list(result['society_breakdown'].values())
    govt_breakdown = list(result['govt_breakdown'].values())

    def safe_get(lst, index, default=0):
        try:
            return lst[index]
        except IndexError:
            return default

    result['detainee_sub1'] = safe_get(detainee_breakdown, 0)
    result['detainee_sub2'] = safe_get(detainee_breakdown, 1)
    result['society_sub1'] = safe_get(society_breakdown, 0)
    result['society_sub2'] = safe_get(society_breakdown, 1)
    result['society_sub3'] = safe_get(society_breakdown, 2)
    result['govt_sub1'] = safe_get(govt_breakdown, 0)
    result['govt_sub2'] = safe_get(govt_breakdown, 1)
    result['govt_sub3'] = safe_get(govt_breakdown, 2)

    return result


def _build_kpi_card(result, mvpf, badge_color, badge_text_color, label, params):
    """Build the KPI card component with subcomponent details and parameters."""

    # Build subcomponent lists for each main component
    detainee_subs = []
    for name, value in result.get('detainee_breakdown', {}).items():
        detainee_subs.append(
            html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'fontSize': '12px', 'color': '#6b7280', 'marginTop': '4px'}, children=[
                html.Span(name, style={'maxWidth': '60%'}),
                html.Span(f"${int(value):,}", style={'fontWeight': '500', 'color': '#2563eb'})
            ])
        )

    society_subs = []
    for name, value in result.get('society_breakdown', {}).items():
        society_subs.append(
            html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'fontSize': '12px', 'color': '#6b7280', 'marginTop': '4px'}, children=[
                html.Span(name, style={'maxWidth': '60%'}),
                html.Span(f"${int(value):,}", style={'fontWeight': '500', 'color': '#16a34a'})
            ])
        )

    govt_subs = []
    for name, value in result.get('govt_breakdown', {}).items():
        govt_subs.append(
            html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'fontSize': '12px', 'color': '#6b7280', 'marginTop': '4px'}, children=[
                html.Span(name, style={'maxWidth': '60%'}),
                html.Span(f"${int(value):,}", style={'fontWeight': '500', 'color': '#dc2626'})
            ])
        )

    return html.Div(className='kpi-card', children=[
        html.Div(className='kpi-header', children=[
            html.H2('MVPF Score', className='kpi-title')
        ]),

        html.Div([
            html.Span(f"{mvpf:.4f}", className='kpi-value'),
            html.Span('ratio', className='kpi-ratio')
        ]),

        html.Div(className='kpi-interpretation', style={
            'marginTop': '24px',
            'padding': '20px',
            'background': '#f0f9ff',
            'borderRadius': '8px',
            'border': '1px solid #bfdbfe'
        }, children=[
            html.Div(style={'marginBottom': '12px'}, children=[
                html.Span(label, className='kpi-badge', style={
                    'backgroundColor': badge_color,
                    'color': badge_text_color,
                    'display': 'inline-block',
                    'padding': '6px 14px',
                    'borderRadius': '9999px',
                    'fontSize': '14px',
                    'fontWeight': '600'
                })
            ]),

            html.P(
                'This indicates the program delivers more value than its cost.' if mvpf > 1
                else 'Consider reviewing program efficiency.',
                style={
                    'marginTop': '0',
                    'marginBottom': '16px',
                    'color': '#1e3a8a',
                    'fontSize': '14px',
                    'lineHeight': '1.6',
                    'fontWeight': '500'
                }
            ),

            html.Div(style={'marginTop': '16px', 'paddingTop': '16px', 'borderTop': '1px solid #bfdbfe'}, children=[
                html.H4('How to Interpret', style={
                    'fontSize': '14px',
                    'fontWeight': '600',
                    'color': '#1e3a8a',
                    'marginTop': '0',
                    'marginBottom': '12px'
                }),
                html.Ul(
                    style={
                        'margin': '0',
                        'paddingLeft': '20px',
                        'color': '#1e40af',
                        'fontSize': '13px',
                        'lineHeight': '1.8'
                    },
                    children=[
                        html.Li([html.Strong('MVPF ≥ 2.5:'), ' Very high social return on investment']),
                        html.Li([html.Strong('MVPF > 1:'), ' Program delivers more value than it costs']),
                        html.Li([html.Strong('MVPF = 1:'), ' Program value equals its cost']),
                        html.Li([html.Strong('MVPF < 1:'), ' Program costs more than the value it provides']),
                        html.Li([html.Strong('MVPF < 0:'), ' Indicates program delivers net harm'])
                    ]
                )
            ])
        ]),

        # Calculation row -  above components
        html.Div(className='kpi-calculation', style={'marginTop': '12px', 'marginBottom': '24px', 'paddingTop': '0', 'borderTop': 'none'}, children=[
            html.P([
                html.Strong('Calculation: '),
                f"MVPF = (${int(result['detainee_values']):,} + ${int(result['society_values']):,}) / ${int(result['govt_cost']):,} = {mvpf:.4f}"
            ], style={'margin': '0',
                      'fontSize': '20px',})
        ]),

        # Component sections in 3-column grid
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr 1fr', 'gap': '16px'}, children=[
            # Detainee Values Component
            html.Div(className='kpi-component', children=[
                html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-start'}, children=[
                    html.Div(children=[
                        html.A(href='#detainee-values-section', className='kpi-component-link', children=[
                            html.H4('Values for Detainees')
                        ]),
                        html.P(f"${int(result['detainee_values']):,}", style={'color': '#2563eb', 'margin': '0'})
                    ]),
                    # Parameters on the right
                    html.Div(style={'textAlign': 'right', 'fontSize': '11px', 'color': '#6b7280'}, children=[
                        html.Div([html.Span('Felony Rate: ', style={'fontWeight': '500'}), f"{params['fel_rate']:.1%}"]),
                        html.Div([html.Span('Population Mult: ', style={'fontWeight': '500'}), f"{params['n_detainees_mult']:.0%}"])
                    ])
                ]),
                # Subcomponents list
                html.Div(style={'marginTop': '12px', 'paddingTop': '8px', 'borderTop': '1px solid #e5e7eb'}, children=[
                    html.Span('Subcomponents:', style={'fontSize': '11px', 'fontWeight': '600', 'color': '#374151', 'textTransform': 'uppercase'}),
                    html.Div(children=detainee_subs)
                ])
            ]),
            # Society Values Component
            html.Div(className='kpi-component', children=[
                html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-start'}, children=[
                    html.Div(children=[
                        html.A(href='#society-values-section', className='kpi-component-link', children=[
                            html.H4('Value for Society')
                        ]),
                        html.P(f"${int(result['society_values']):,}", style={'color': '#16a34a', 'margin': '0'})
                    ]),
                    # Parameters on the right
                    html.Div(style={'textAlign': 'right', 'fontSize': '11px', 'color': '#6b7280'}, children=[
                        html.Div([html.Span('Community Mult: ', style={'fontWeight': '500'}), f"{params['n_society_mult']:.0%}"]),
                        html.Div([html.Span('Length of Stay: ', style={'fontWeight': '500'}), f"{params['los_days']:.0f} days"])
                    ])
                ]),
                # Subcomponents list
                html.Div(style={'marginTop': '12px', 'paddingTop': '8px', 'borderTop': '1px solid #e5e7eb'}, children=[
                    html.Span('Subcomponents:', style={'fontSize': '11px', 'fontWeight': '600', 'color': '#374151', 'textTransform': 'uppercase'}),
                    html.Div(children=society_subs)
                ])
            ]),
            # Government Costs Component
            html.Div(className='kpi-component', children=[
                html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-start'}, children=[
                    html.Div(children=[
                        html.A(href='#government-cost-section', className='kpi-component-link', children=[
                            html.H4('Government Costs')
                        ]),
                        html.P(f"${int(result['govt_cost']):,}", style={'color': '#dc2626', 'margin': '0'})
                    ]),
                    # Parameters on the right
                    html.Div(style={'textAlign': 'right', 'fontSize': '11px', 'color': '#6b7280'}, children=[
                        html.Div([html.Span('Population Mult: ', style={'fontWeight': '500'}), f"{params['n_detainees_mult']:.0%}"]),
                        html.Div([html.Span('Length of Stay: ', style={'fontWeight': '500'}), f"{params['los_days']:.0f} days"])
                    ])
                ]),
                # Subcomponents list
                html.Div(style={'marginTop': '12px', 'paddingTop': '8px', 'borderTop': '1px solid #e5e7eb'}, children=[
                    html.Span('Subcomponents:', style={'fontSize': '11px', 'fontWeight': '600', 'color': '#374151', 'textTransform': 'uppercase'}),
                    html.Div(children=govt_subs)
                ])
            ])
        ])
    ])


def _build_interpretation_card():
    """Build the interpretation guide card component."""
    return html.Div(className='kpi-card', children=[
        html.H4('How to Interpret', style={
            'fontSize': '16px',
            'fontWeight': '600',
            'color': '#374151',
            'marginTop': '0',
            'marginBottom': '12px'
        }),
        html.Ul(
            style={
                'margin': '0',
                'paddingLeft': '20px',
                'color': '#4b5563',
                'fontSize': '14px',
                'lineHeight': '1.8'
            },
            children=[
                html.Li([html.Strong('MVPF ≥ 2.5:'), ' Very high social return on investment']),
                html.Li([html.Strong('MVPF > 1:'), ' Program delivers more value than it costs']),
                html.Li([html.Strong('MVPF = 1:'), ' Program value equals its cost']),
                html.Li([html.Strong('MVPF < 1:'), ' Program costs more than the value it provides']),
                html.Li([html.Strong('MVPF < 0:'), ' Indicates program delivers net harm'])
            ]
        )
    ])


def _build_benchmark_chart(current_mvpf, benchmarks):
    """Build the benchmark comparison bar chart."""
    # Prepare data: current MVPF first, then benchmarks
    names = ['Current MVPF for CCJ']
    values = [current_mvpf]
    colors = ['#2563eb']  # Blue for current

    for benchmark in benchmarks:
        bench_mvpf = float(benchmark['mvpf_value'])
        description = benchmark['Description']
        # Shorten long names for chart labels
        short_name = description if len(description) <= 25 else description[:22] + '...'
        names.append(short_name)
        values.append(bench_mvpf)
        # Color based on positive/negative
        colors.append('#16a34a' if bench_mvpf >= 0 else '#dc2626')

    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=names,
            y=values,
            marker_color=colors,
            text=[f"{v:.2f}" for v in values],
            textposition='outside',
            textfont=dict(size=11)
        )
    ])

    # Calculate y-axis range
    min_val = min(values)
    max_val = max(values)
    padding = max(abs(max_val), abs(min_val)) * 0.15
    y_range = [min(0, min_val - padding), max(0, max_val + padding)]

    fig.update_layout(
        title=None,
        xaxis_title='',
        yaxis_title='MVPF',
        yaxis_range=y_range,
        paper_bgcolor='white',
        plot_bgcolor='#f9fafb',
        font=dict(family='system-ui', size=11),
        margin=dict(t=20, b=80, l=50, r=20),
        showlegend=False,
        xaxis_tickangle=-35,
        height=280
    )

    # Add horizontal line at y=0
    fig.add_hline(y=0, line_dash="solid", line_color="#9ca3af", line_width=1)

    # Add horizontal line at y=1 (break-even point)
    fig.add_hline(y=1, line_dash="dash", line_color="#f59e0b", line_width=1,
                  annotation_text="Break-even", annotation_position="right")

    return fig


def _build_benchmark_card(current_mvpf):
    """Build the benchmark comparison card component with dynamic tiles and chart."""
    benchmarks = load_benchmarks()

    # Build comparison chart
    benchmark_chart = _build_benchmark_chart(current_mvpf, benchmarks)

    benchmark_tiles = []
    for benchmark in benchmarks:
        bench_mvpf = float(benchmark['mvpf_value'])
        description = benchmark['Description']
        source_link = benchmark['source_link']

        # Calculate comparison
        if current_mvpf != 0:
            if bench_mvpf >= 0 and current_mvpf >= 0:
                # Both positive: compare directly
                pct_diff = (abs(bench_mvpf)/ (current_mvpf ))  if bench_mvpf != 0 else 0
            elif bench_mvpf < 0 and current_mvpf >= 0:
                # Benchmark negative, current positive: CCJ is better
                pct_diff = abs (bench_mvpf) / abs(current_mvpf)
            elif bench_mvpf >= 0 and current_mvpf < 0:
                # Benchmark positive, current negative: CCJ is worse
                pct_diff = -abs(bench_mvpf)/ abs(current_mvpf)
            else:
                # Both negative: less negative is better
                pct_diff = (abs(bench_mvpf)/ (current_mvpf ))
        else:
            pct_diff = 0

        # Determine if CCJ is better or worse
        is_better = current_mvpf > bench_mvpf

        # Value styling
        value_class = 'positive' if bench_mvpf >= 0 else 'negative'
        comparison_class = 'better' if is_better else 'worse'

        # Format comparison text
        if is_better:
            comparison_text = f"-{abs(pct_diff):.0f}X" if pct_diff != 0 else "Same"
        else:
            comparison_text = f"+{abs(pct_diff):.0f}X" if pct_diff != 0 else "Same"

        # Get first source link if multiple
        first_link = source_link.split(',')[0].strip()

        tile = html.Div(className='benchmark-tile', children=[
            html.Div(className='benchmark-tile-header', children=[
                html.Span(f"{bench_mvpf:.2f}", className=f'benchmark-tile-value {value_class}'),
                html.Span(comparison_text, className=f'benchmark-tile-comparison {comparison_class}')
            ]),
            html.Div(className='benchmark-tile-name', children=description),
            html.A(
                'View Source',
                href=first_link,
                target='_blank',
                className='benchmark-tile-link'
            )
        ])
        benchmark_tiles.append(tile)

    return html.Div(className='kpi-card', children=[
        html.H3('Comparative Benchmarking', style={
            'fontSize': '20px',
            'fontWeight': '600',
            'color': '#1e293b',
            'marginBottom': '8px',
            'marginTop': '0'
        }),
        html.P([
            'Comparing the the actual MVPF values of selected government programs, interventions, and policy initiatives across different domains, and the impact of how 1 US dollar is spent on Cook County Jail comparing to spending on these initiatives.'
        ], style={
            'fontSize': '14px',
            'color': '#6b7280',
            'marginBottom': '16px',
            'fontWeight': '400'
        }),
        # Benchmark comparison chart
        dcc.Graph(
            figure=benchmark_chart,
            config={'displayModeBar': False}
        ),
        # Benchmark tiles grid
        html.Div(className='benchmark-grid', style={'marginTop': '16px'}, children=benchmark_tiles)
    ])


def _build_numerator_chart(result):
    """Build the numerator chart showing Detainee Values and Society Values."""
    det_val = result['detainee_values']
    soc_val = result['society_values']

    fig = go.Figure(data=[
        go.Bar(
            x=['Detainee Values', 'Society Values'],
            y=[det_val, soc_val],
            marker_color=['#3b82f6', '#10b981'],
            text=[
                f"${int(det_val):,}",
                f"${int(soc_val):,}"
            ],
            textposition='outside'
        )
    ])

    fig.update_layout(
        title='Willingness to Pay (MVPF numerator value)',
        xaxis_title='',
        yaxis_title='Value ($)',
        paper_bgcolor='#f8fafc',
        plot_bgcolor='#ffffff',
        font=dict(family='system-ui', size=12),
        margin=dict(t=50, b=80, l=80, r=40),
        showlegend=False
    )

    return fig


def _build_denominator_chart(result):
    """Build the denominator chart showing Government Cost vs Numerator (Detainee + Society)."""
    gov_val = result['govt_cost']
    det_val = result['detainee_values']
    soc_val = result['society_values']
    numerator = det_val + soc_val

    # Determine colors based on values (negative = red, positive = green/blue)
    numerator_color = '#10b981' if numerator >= 0 else '#ef4444'

    fig = go.Figure(data=[
        go.Bar(
            x=['Aggregated Value', 'Government Cost'],
            y=[numerator, gov_val],
            marker_color=[numerator_color, '#ef4444'],
            text=[f"${int(numerator):,}", f"${int(gov_val):,}"],
            textposition='outside'
        )
    ])

    fig.update_layout(
        title='Marginal Value to Government Costs Comparison',
        xaxis_title='',
        yaxis_title='Value ($)',
        paper_bgcolor='#f8fafc',
        plot_bgcolor='#ffffff',
        font=dict(family='system-ui', size=12),
        margin=dict(t=50, b=100, l=80, r=40),
        showlegend=False
    )

    return fig


def _build_parameter_comparison_chart(scenario, base_det_p1, base_det_p2, base_soc_p1, base_soc_p2, detainee_baseline=None, crime_effect=0):
    """Build the parameter comparison chart showing MVPF sensitivity to parameter changes."""
    # Calculate MVPFs for each parameter variation
    param_variations = {
        'Felony Rate': [],
        'Detainee Population': [],
        'Community Size': [],
        'Length of Stay': []
    }

    # Define parameter value mappings
    fel_rate_values = {
        'below': fel_rate_param.dropdown_map['below'],
        'average': fel_rate_param.dropdown_map['average'],
        'above': fel_rate_param.dropdown_map['above']
    }
    n_detainees_values = {
        'below': n_detainees_param.dropdown_map['below'],
        'average': n_detainees_param.dropdown_map['average'],
        'above': n_detainees_param.dropdown_map['above']
    }
    n_society_values = {
        'below': n_society_param.dropdown_map['below'],
        'average': n_society_param.dropdown_map['average'],
        'above': n_society_param.dropdown_map['above']
    }
    los_days_values = {
        'below': los_days_param.dropdown_map['below'],
        'average': los_days_param.dropdown_map['average'],
        'above': los_days_param.dropdown_map['above']
    }

    # Vary Felony Rate (detainee_param1)
    for variation in ['below', 'average', 'above']:
        result = _calculate_mvpf(scenario, fel_rate_values[variation], base_det_p2, base_soc_p1, base_soc_p2, detainee_baseline=detainee_baseline, crime_effect=crime_effect)
        param_variations['Felony Rate'].append(result['mvpf'])

    # Vary Detainee Population (detainee_param2)
    for variation in ['below', 'average', 'above']:
        result = _calculate_mvpf(scenario, base_det_p1, n_detainees_values[variation], base_soc_p1, base_soc_p2, detainee_baseline=detainee_baseline, crime_effect=crime_effect)
        param_variations['Detainee Population'].append(result['mvpf'])

    # Vary Community Size (society_param1)
    for variation in ['below', 'average', 'above']:
        result = _calculate_mvpf(scenario, base_det_p1, base_det_p2, n_society_values[variation], base_soc_p2, detainee_baseline=detainee_baseline, crime_effect=crime_effect)
        param_variations['Community Size'].append(result['mvpf'])

    # Vary Length of Stay (society_param2)
    for variation in ['below', 'average', 'above']:
        result = _calculate_mvpf(scenario, base_det_p1, base_det_p2, base_soc_p1, los_days_values[variation], detainee_baseline=detainee_baseline, crime_effect=crime_effect)
        param_variations['Length of Stay'].append(result['mvpf'])

    # Create grouped bar chart
    fig = go.Figure()

    colors = ['#93c5fd', '#3b82f6', '#1e40af']  # Light to dark blue for below, average, above
    labels = ['Below', 'Average', 'Above']

    for i, label in enumerate(labels):
        values = [param_variations[param][i] for param in param_variations.keys()]
        fig.add_trace(go.Bar(
            name=label,
            x=list(param_variations.keys()),
            y=values,
            marker_color=colors[i],
            text=[f"{v:.2f}" for v in values],
            textposition='outside',
            textfont=dict(size=10)
        ))

    fig.update_layout(
        title='MVPF Sensitivity to Parameter Changes',
        xaxis_title='Parameter',
        yaxis_title='MVPF',
        barmode='group',
        paper_bgcolor='#f8fafc',
        plot_bgcolor='#ffffff',
        font=dict(family='system-ui', size=11),
        margin=dict(t=50, b=100, l=60, r=40),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        height=400
    )

    # Add horizontal line at y=1 (break-even)
    fig.add_hline(y=1, line_dash="dash", line_color="#f59e0b", line_width=1,
                  annotation_text="Break-even", annotation_position="right")

    return fig


def _build_scenario_comparison_chart(det_p1, det_p2, soc_p1, soc_p2, detainee_baseline=None, crime_effect=0):
    """Build the scenario comparison chart showing MVPF for all scenarios on y-axis."""
    scenarios = [
        'baseline',
        'most conservative',
        'least conservative'
    ]

    scenario_labels = {
        'baseline': 'Baseline',
        'most conservative': 'Conservative',
        'least conservative': 'Least Conservative'
    }

    # Calculate MVPF for each scenario
    mvpf_values = []
    for scenario in scenarios:
        result = _calculate_mvpf(scenario, det_p1, det_p2, soc_p1, soc_p2, detainee_baseline=detainee_baseline, crime_effect=crime_effect)
        mvpf_values.append(result['mvpf'])

    # Color bars based on MVPF value (green for good, yellow for fair, red for poor)
    colors = []
    for mvpf in mvpf_values:
        if mvpf >= 2.5:
            colors.append('#16a34a')  # Green - Excellent
        elif mvpf >= 1.5:
            colors.append('#3b82f6')  # Blue - Good
        elif mvpf >= 1.0:
            colors.append('#f59e0b')  # Yellow - Fair
        else:
            colors.append('#dc2626')  # Red - Poor

    # Create horizontal bar chart with scenarios on y-axis
    labels = [scenario_labels[s] for s in scenarios]

    fig = go.Figure(data=[
        go.Bar(
            y=labels,
            x=mvpf_values,
            marker_color=colors,
            text=[f"{v:.2f}" for v in mvpf_values],
            textposition='outside',
            textfont=dict(size=11),
            orientation='h'
        )
    ])

    # Calculate x-axis range
    min_val = min(mvpf_values)
    max_val = max(mvpf_values)
    padding = max(abs(max_val), abs(min_val)) * 0.15
    x_range = [min(0, min_val - padding), max(0, max_val + padding)]

    fig.update_layout(
        title='MVPF Comparison Across Scenarios',
        xaxis_title='MVPF',
        yaxis_title='',
        xaxis_range=x_range,
        paper_bgcolor='#f8fafc',
        plot_bgcolor='#ffffff',
        font=dict(family='system-ui', size=11),
        margin=dict(t=50, b=60, l=180, r=100),
        showlegend=False,
        bargap=0.3,
        height=max(400, len(scenarios) * 50)
    )

    # Add vertical line at x=0
    fig.add_vline(x=0, line_dash="solid", line_color="#9ca3af", line_width=1)

    # Add vertical line at x=1 (break-even)
    fig.add_vline(x=1, line_dash="dash", line_color="#f59e0b", line_width=1,
                  annotation_text="Break-even", annotation_position="top")

    return fig


def _build_sensitivity_analysis_chart(parameter_name, param_values, base_det_p1, base_det_p2, base_soc_p1, base_soc_p2, crime_effect=0):
    """
    Build a sensitivity analysis chart showing how one parameter affects MVPF for baseline,
    least conservative, and most conservative scenarios.

    Parameters:
    -----------
    parameter_name : str
        Name of the parameter being varied ('Felony Rate', 'Detainee Population', 'Community Size', 'Length of Stay')
    param_values : dict
        Dictionary mapping 'below', 'average', 'above' to actual parameter values
    base_det_p1, base_det_p2, base_soc_p1, base_soc_p2 : float
        Base parameter values to use when not varying the parameter
    crime_effect : float, optional
        Crime effect multiplier (-4 to 14). Defaults to 0 (no effect).

    Returns:
    --------
    plotly.graph_objs.Figure
    """
    scenarios = ['baseline', 'most conservative', 'least conservative']
    scenario_labels = {
        'baseline': 'Baseline',
        'most conservative': 'Most Conservative',
        'least conservative': 'Least Conservative'
    }
    scenario_colors = {
        'baseline': '#2563eb',  # Blue
        'most conservative': '#d97706',  # Orange
        'least conservative': '#16a34a'  # Green
    }

    variations = ['below', 'average', 'above']

    fig = go.Figure()

    for scenario in scenarios:
        mvpf_values = []

        for variation in variations:
            # Determine which parameter to vary based on parameter_name
            if parameter_name == 'Felony Rate':
                result = _calculate_mvpf(scenario, param_values[variation], base_det_p2, base_soc_p1, base_soc_p2, crime_effect=crime_effect)
            elif parameter_name == 'Detainee Population':
                result = _calculate_mvpf(scenario, base_det_p1, param_values[variation], base_soc_p1, base_soc_p2, crime_effect=crime_effect)
            elif parameter_name == 'Community Size':
                result = _calculate_mvpf(scenario, base_det_p1, base_det_p2, param_values[variation], base_soc_p2, crime_effect=crime_effect)
            elif parameter_name == 'Length of Stay':
                result = _calculate_mvpf(scenario, base_det_p1, base_det_p2, base_soc_p1, param_values[variation], crime_effect=crime_effect)
            else:
                result = {'mvpf': 0}

            mvpf_values.append(result['mvpf'])

        fig.add_trace(go.Scatter(
            x=variations,
            y=mvpf_values,
            mode='lines+markers',
            name=scenario_labels[scenario],
            line=dict(color=scenario_colors[scenario], width=3),
            marker=dict(size=8, color=scenario_colors[scenario]),
            text=[f"{v:.2f}" for v in mvpf_values],
            textposition='top center',
            textfont=dict(size=10)
        ))

    fig.update_layout(
        title=f'Sensitivity to {parameter_name}',
        xaxis_title=parameter_name,
        yaxis_title='MVPF',
        paper_bgcolor='white',
        plot_bgcolor='#f9fafb',
        font=dict(family='system-ui', size=11),
        margin=dict(t=50, b=60, l=60, r=40),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            bgcolor='rgba(255,255,255,0.8)'
        ),
        height=300,
        hovermode='x unified'
    )

    # Add horizontal line at y=1 (break-even)
    fig.add_hline(y=1, line_dash="dash", line_color="#f59e0b", line_width=1,
                  annotation_text="Break-even", annotation_position="right")

    return fig


def _build_subcomponents_chart(result):
    """Build the subcomponents horizontal bar chart with variable names on y-axis."""
    # Collect all subcomponents with their variable names and values
    subcomponents = []
    colors = []

    # Detainee subcomponents (blue)
    for var_name, value in result.get('detainee_breakdown', {}).items():
        subcomponents.append({'name': var_name, 'value': value, 'category': 'Detainee'})
        colors.append('#3b82f6')

    # Society subcomponents (green)
    for var_name, value in result.get('society_breakdown', {}).items():
        subcomponents.append({'name': var_name, 'value': value, 'category': 'Society'})
        colors.append('#10b981')

    # Government subcomponents (red)
    for var_name, value in result.get('govt_breakdown', {}).items():
        subcomponents.append({'name': var_name, 'value': value, 'category': 'Govt'})
        colors.append('#ef4444')

    # Extract data for the chart
    names = [s['name'] for s in subcomponents]
    values = [s['value'] for s in subcomponents]
    text_labels = [f"${int(v):,}" for v in values]

    # Calculate x-axis range to ensure all bars are visible (horizontal bars use x-axis for values)
    if values:
        min_val = min(values)
        max_val = max(values)
        # Add padding (20%) to ensure text labels are visible
        padding = max(abs(max_val), abs(min_val)) * 0.2
        x_range = [min(0, min_val - padding), max(0, max_val + padding)]
    else:
        x_range = None

    fig = go.Figure(data=[
        go.Bar(
            y=names,  # Names on y-axis for horizontal bars
            x=values,  # Values on x-axis for horizontal bars
            marker_color=colors,
            text=text_labels,
            textposition='outside',
            textfont=dict(size=10),
            orientation='h'  # Horizontal orientation
        )
    ])

    fig.update_layout(
        title='Subcomponent Breakdown',
        xaxis_title='Value ($)',
        yaxis_title='',
        xaxis_range=x_range,
        paper_bgcolor='#f8fafc',
        plot_bgcolor='#ffffff',
        font=dict(family='system-ui', size=11),
        margin=dict(t=50, b=60, l=250, r=100),  # Increased left margin for labels
        showlegend=False,
        bargap=0.3,
        height=max(400, len(names) * 40)  # Dynamic height based on number of items
    )

    # Add a vertical line at x=0 for reference (vertical line for horizontal bars)
    fig.add_vline(x=0, line_dash="solid", line_color="#9ca3af", line_width=1)

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
        Output('detainee-wtp', 'style'),
        Input('detainee-wtp-btn', 'n_clicks'),
        State('detainee-wtp', 'style')
    )
    def toggle_detainee_wtp(n_clicks, style):
        return _toggle_style(n_clicks, style)

    @app.callback(
        Output('detainee-harm', 'style'),
        Input('detainee-harm-btn', 'n_clicks'),
        State('detainee-harm', 'style')
    )
    def toggle_detainee_harm(n_clicks, style):
        return _toggle_style(n_clicks, style)

    @app.callback(
        Output('society-crime', 'style'),
        Input('society-crime-btn', 'n_clicks'),
        State('society-crime', 'style')
    )
    def toggle_society_crime(n_clicks, style):
        return _toggle_style(n_clicks, style)

    @app.callback(
        Output('society-court', 'style'),
        Input('society-court-btn', 'n_clicks'),
        State('society-court', 'style')
    )
    def toggle_society_court(n_clicks, style):
        return _toggle_style(n_clicks, style)

    @app.callback(
        Output('society-spill', 'style'),
        Input('society-spill-btn', 'n_clicks'),
        State('society-spill', 'style')
    )
    def toggle_society_spill(n_clicks, style):
        return _toggle_style(n_clicks, style)

    @app.callback(
        Output('gov-op', 'style'),
        Input('gov-op-btn', 'n_clicks'),
        State('gov-op', 'style')
    )
    def toggle_gov_op(n_clicks, style):
        return _toggle_style(n_clicks, style)

    @app.callback(
        Output('gov-crime-increase', 'style'),
        Input('gov-crime-increase-btn', 'n_clicks'),
        State('gov-crime-increase', 'style')
    )
    def toggle_gov_crime_increase(n_clicks, style):
        return _toggle_style(n_clicks, style)

    @app.callback(
        Output('gov-crime-decrease', 'style'),
        Input('gov-crime-decrease-btn', 'n_clicks'),
        State('gov-crime-decrease', 'style')
    )
    def toggle_gov_crime_decrease(n_clicks, style):
        return _toggle_style(n_clicks, style)

    # -------------------------------------------------------------------------
    # Scenario Selection Callback (Jumbotron Buttons)
    # -------------------------------------------------------------------------

    @app.callback(
        [Output('scenario-selector', 'data'),
         Output('scenario-btn-baseline', 'style'),
         Output('scenario-btn-most-conservative', 'style'),
         Output('scenario-btn-least-conservative', 'style')],
        [Input('scenario-btn-baseline', 'n_clicks'),
         Input('scenario-btn-most-conservative', 'n_clicks'),
         Input('scenario-btn-least-conservative', 'n_clicks')],
        prevent_initial_call=True
    )
    def update_scenario_selection(baseline_clicks, conservative_clicks, least_clicks):
        """Handle scenario button clicks and update styling."""
        ctx = dash.callback_context

        if not ctx.triggered:
            return dash.no_update

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Determine selected scenario based on button clicked
        scenario_map = {
            'scenario-btn-baseline': 'baseline',
            'scenario-btn-most-conservative': 'most conservative',
            'scenario-btn-least-conservative': 'least conservative'
        }
        selected_scenario = scenario_map.get(button_id, 'baseline')

        # Define styles for selected and unselected states
        baseline_style = {'border': '3px solid #2563eb', 'cursor': 'pointer'} if button_id == 'scenario-btn-baseline' else {'border': '2px solid #e5e7eb', 'cursor': 'pointer'}
        conservative_style = {'border': '3px solid #d97706', 'cursor': 'pointer'} if button_id == 'scenario-btn-most-conservative' else {'border': '2px solid #e5e7eb', 'cursor': 'pointer'}
        least_style = {'border': '3px solid #16a34a', 'cursor': 'pointer'} if button_id == 'scenario-btn-least-conservative' else {'border': '2px solid #e5e7eb', 'cursor': 'pointer'}

        return selected_scenario, baseline_style, conservative_style, least_style

    # -------------------------------------------------------------------------
    # Slider Value Display Update Callbacks
    # -------------------------------------------------------------------------

    @app.callback(
        Output('felony-rate-value', 'children'),
        Input('detainee-param1', 'value')
    )
    def update_felony_rate_display(value):
        """Update displayed felony rate based on slider value."""
        return f"{value:.0%}"

    @app.callback(
        Output('detainee-population-value', 'children'),
        [Input('detainee-param2', 'value'),
         Input('detainee-baseline-input', 'value')]
    )
    def update_detainee_display(multiplier, baseline):
        """Update displayed detainee population based on baseline and multiplier."""
        baseline_value = baseline if baseline is not None else n_detainees_param.base_value
        calculated_value = baseline_value * multiplier
        return f"{calculated_value:,.0f}"

    @app.callback(
        Output('los-days-value', 'children'),
        Input('society-param2', 'value')
    )
    def update_los_days_display(value):
        """Update displayed length of stay based on slider value."""
        return f"{value:.0f} days"

    @app.callback(
        Output('crime-effect-value', 'children'),
        Input('crime-effect-slider', 'value')
    )
    def update_crime_effect_display(value):
        """Update displayed crime effect based on slider value."""
        if value is None:
            value = 0
        return f"{value}"

    # -------------------------------------------------------------------------
    # Main Dashboard Update Callback
    # -------------------------------------------------------------------------

    @app.callback(
        [Output('kpi-card', 'children'),
         Output('benchmark-card', 'children'),
         Output('numerator-chart', 'figure'),
         Output('denominator-chart', 'figure'),
         Output('parameter-comparison-chart', 'figure'),
         Output('scenario-comparison-chart', 'figure')],
        [Input('btn-calculate', 'n_clicks')],
        [State('scenario-selector', 'data'),
         State('detainee-param1', 'value'),
         State('detainee-param2', 'value'),
         State('detainee-baseline-input', 'value'),
         State('society-param2', 'value'),
         State('crime-effect-slider', 'value')]
    )
    def update_dashboard(n_clicks, scenario, det_p1, det_p2, det_baseline, soc_p2, crime_effect):
        """Main callback to update all dashboard components."""
        # Convert string parameters from State to floats
        det_p1 = float(det_p1) if det_p1 is not None else 0.7
        det_p2 = float(det_p2) if det_p2 is not None else 1.0
        det_baseline = float(det_baseline) if det_baseline is not None else n_detainees_base_param.default_value
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
            crime_effect=crime_effect
        )

        result = _calculate_mvpf(scenario, det_p1, det_p2, soc_p1, soc_p2, detainee_baseline=det_baseline, crime_effect=crime_effect)
        mvpf = result['mvpf']

        # Determine badge color and label
        if mvpf >= 2.5:
            badge_color, badge_text_color, label = '#dcfce7', '#16a34a', 'Excellent'
        elif mvpf >= 1.5:
            badge_color, badge_text_color, label = '#dbeafe', '#2563eb', 'Good'
        elif mvpf >= 1.0:
            badge_color, badge_text_color, label = '#fef3c7', '#ca8a04', 'Fair'
        else:
            badge_color, badge_text_color, label = '#fee2e2', '#dc2626', 'Poor'

        # Build components
        kpi_card = _build_kpi_card(result, mvpf, badge_color, badge_text_color, label, params)
        benchmark_card = _build_benchmark_card(mvpf)
        numerator_fig = _build_numerator_chart(result)
        denominator_fig = _build_denominator_chart(result)
        param_comparison_fig = _build_parameter_comparison_chart(scenario, det_p1, det_p2, soc_p1, soc_p2, det_baseline, crime_effect)
        scenario_comparison_fig = _build_scenario_comparison_chart(det_p1, det_p2, soc_p1, soc_p2, det_baseline, crime_effect)

        return kpi_card, benchmark_card, numerator_fig, denominator_fig, param_comparison_fig, scenario_comparison_fig

    # -------------------------------------------------------------------------
    # Sensitivity Analysis Callback for Tab 3
    # -------------------------------------------------------------------------

    @app.callback(
        [Output('sensitivity-felony-rate', 'figure'),
         Output('sensitivity-detainee-population', 'figure'),
         Output('sensitivity-crime-effect', 'figure'),
         Output('sensitivity-length-of-stay', 'figure')],
        [Input('btn-calculate', 'n_clicks')],
        [State('detainee-param1', 'value'),
         State('detainee-param2', 'value'),
         State('society-param2', 'value'),
         State('crime-effect-slider', 'value')]
    )
    def update_sensitivity_analysis(n_clicks, det_p1, det_p2, soc_p2, crime_effect):
        """Update sensitivity analysis graphs for baseline, most conservative, and least conservative scenarios."""
        # Convert string parameters from State to floats
        det_p1 = float(det_p1) if det_p1 is not None else 0.7
        det_p2 = float(det_p2) if det_p2 is not None else 1.0
        soc_p2 = float(soc_p2) if soc_p2 is not None else 70
        crime_effect = float(crime_effect) if crime_effect is not None else 0

        # Use default value for community size multiplier
        soc_p1 = 1.0

        # Define parameter value mappings for each parameter
        fel_rate_values = {
            'below': fel_rate_param.dropdown_map['below'],
            'average': fel_rate_param.dropdown_map['average'],
            'above': fel_rate_param.dropdown_map['above']
        }

        n_detainees_values = {
            'below': n_detainees_param.dropdown_map['below'],
            'average': n_detainees_param.dropdown_map['average'],
            'above': n_detainees_param.dropdown_map['above']
        }

        crime_effect_values = {
            'below': -4,
            'average': 0,
            'above': 14
        }

        los_days_values = {
            'below': los_days_param.dropdown_map['below'],
            'average': los_days_param.dropdown_map['average'],
            'above': los_days_param.dropdown_map['above']
        }

        # Build all 4 sensitivity analysis charts
        # For non-crime-effect charts, use the current crime_effect slider value
        felony_rate_fig = _build_sensitivity_analysis_chart(
            'Felony Rate', fel_rate_values, det_p1, det_p2, soc_p1, soc_p2, crime_effect=crime_effect
        )

        detainee_pop_fig = _build_sensitivity_analysis_chart(
            'Detainee Population', n_detainees_values, det_p1, det_p2, soc_p1, soc_p2, crime_effect=crime_effect
        )

        # For crime effect sensitivity, we vary crime_effect itself, so pass 0 as default
        crime_effect_fig = _build_sensitivity_analysis_chart(
            'Crime Effect', crime_effect_values, det_p1, det_p2, soc_p1, soc_p2, crime_effect=0
        )

        length_of_stay_fig = _build_sensitivity_analysis_chart(
            'Length of Stay', los_days_values, det_p1, det_p2, soc_p1, soc_p2, crime_effect=crime_effect
        )

        return felony_rate_fig, detainee_pop_fig, crime_effect_fig, length_of_stay_fig

    # -------------------------------------------------------------------------
    # Tab Navigation Callbacks (Combined landing page cards + sidebar)
    # -------------------------------------------------------------------------

    @app.callback(
        [Output('main-tabs', 'value'),
         Output('nav-home', 'className'),
         Output('nav-overview', 'className'),
         Output('nav-scenarios', 'className'),
         Output('nav-benchmarking', 'className'),
         Output('nav-descriptions', 'className'),
         Output('nav-about', 'className')],
        [Input('nav-home', 'n_clicks'),
         Input('nav-overview', 'n_clicks'),
         Input('nav-scenarios', 'n_clicks'),
         Input('nav-benchmarking', 'n_clicks'),
         Input('nav-descriptions', 'n_clicks'),
         Input('nav-about', 'n_clicks'),
         Input('link-to-overview', 'n_clicks'),
         Input('link-to-scenarios', 'n_clicks'),
         Input('link-to-benchmarking', 'n_clicks')],
        prevent_initial_call=True
    )
    def sidebar_navigation(home_clicks, overview_clicks, scenarios_clicks, benchmarking_clicks, descriptions_clicks, about_clicks,
                          overview_card_clicks, scenarios_card_clicks, benchmarking_card_clicks):
        """Handle navigation from left sidebar buttons and landing page cards."""
        ctx = dash.callback_context

        if not ctx.triggered:
            return dash.no_update

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Map button IDs to tab values (sidebar + landing page cards)
        button_to_tab = {
            'nav-home': 'tab-landing',
            'nav-overview': 'tab-overview',
            'nav-scenarios': 'tab-scenarios',
            'nav-benchmarking': 'tab-benchmarking',
            'nav-descriptions': 'tab-descriptions',
            'nav-about': 'tab-about',
            'link-to-overview': 'tab-overview',
            'link-to-scenarios': 'tab-scenarios',
            'link-to-benchmarking': 'tab-benchmarking'
        }

        # Get the tab value for the clicked button
        tab_value = button_to_tab.get(button_id, 'tab-landing')

        # Update button class names - add 'active' to the clicked button (only for sidebar)
        nav_classes = [
            'nav-button active' if button_id == 'nav-home' else 'nav-button',
            'nav-button active' if (button_id == 'nav-overview' or button_id == 'link-to-overview') else 'nav-button',
            'nav-button active' if (button_id == 'nav-scenarios' or button_id == 'link-to-scenarios') else 'nav-button',
            'nav-button active' if (button_id == 'nav-benchmarking' or button_id == 'link-to-benchmarking') else 'nav-button',
            'nav-button active' if button_id == 'nav-descriptions' else 'nav-button',
            'nav-button active' if button_id == 'nav-about' else 'nav-button'
        ]

        return tab_value, *nav_classes

    # -------------------------------------------------------------------------
    # Download CSV Callback
    # -------------------------------------------------------------------------

    @app.callback(
        Output('download-dataframe-csv', 'data'),
        Input('btn-download-csv', 'n_clicks'),
        [State('scenario-selector', 'data'),
         State('detainee-param1', 'value'),
         State('detainee-param2', 'value'),
         State('society-param2', 'value')],
        prevent_initial_call=True
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
            fel_rate_sel=det_p1,
            n_detainees_sel=det_p2,
            n_society_sel=soc_p1,
            los_days_sel=soc_p2
        )

        result = calculator.calculate(scenario, params)
        csv_string = calculator.export_to_string(result, include_metadata=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'mvpf_results_{scenario}_{timestamp}.csv'

        return dict(content=csv_string, filename=filename)


# Register all callbacks
register_callbacks(app)


if __name__ == '__main__':
    app.run(debug=True, port=8050)
