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
            .header {
                margin-bottom: 24px;
            }
            .header h1 {
                font-size: 30px;
                font-weight: bold;
                color: #1e293b;
                margin: 0 0 8px 0;
            }
            .header p {
                color: #64748b;
                margin: 0;
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
app.layout = html.Div(className='main-container', children=[
    # Header
    html.Div(className='header', children=[
        html.H1(content.get('header.title', 'MVPF Analysis Dashboard')),
        html.P(content.get('header.subtitle', 'Marginal Value of Public Funds Calculation'))
    ]),

    html.Div(style={'position': 'sticky', 'top': '24px', 'zIndex': '1000'}, children=[
                # Information Tile
                html.Div(className='info-tile', children=[
                    html.H3(content.get('info_tile.heading', 'About MVPF')),
                    html.P(content.get('info_tile.description', 'The MVPF measures the ratio of beneficiaries willingness to pay to the net cost to the government')),
                    html.P([
                        html.Strong(content.get('info_tile.formula_label', 'Formula:')),
                        html.Br(),
                        content.get('info_tile.formula', 'MVPF = (Detainee + Society) / Government Cost')
                    ])
                ]),


    # Analysis Parameters - Four Jumbotrons
    html.Div(className='jumbotron-grid', children=[
        # Jumbotron 1: Felony Rate
        html.Div(className='jumbotron', children=[
            html.Div(className='jumbotron-icon', style={'background': '#dbeafe'}, children=[
                html.Span('%%', style={'color': '#2563eb'})
            ]),
            html.H4(content.get('controls.felony_rate.title', 'Felony Rate'), className='jumbotron-title'),
            html.P(f"{fel_rate_param.default_value:.0%}", className='jumbotron-value'),
            html.P(content.get('controls.felony_rate.tooltip', fel_rate_param.description), className='jumbotron-description'),
            dcc.Dropdown(
                id='detainee-param1',
                options=FEL_RATE_OPTIONS,
                value='average',
                clearable=False
            )
        ]),

        # Jumbotron 2: Detainee Population
        html.Div(className='jumbotron', children=[
            html.Div(className='jumbotron-icon', style={'background': '#fef3c7'}, children=[
                html.Span('#', style={'color': '#d97706', 'fontWeight': '700'})
            ]),
            html.H4(content.get('controls.detainee_population.title', 'Detainee Population'), className='jumbotron-title'),
            html.P(f"{n_detainees_param.base_value:,.0f}", className='jumbotron-value'),
            html.P(content.get('controls.detainee_population.tooltip', n_detainees_param.description), className='jumbotron-description'),
            dcc.Dropdown(
                id='detainee-param2',
                options=N_DETAINEES_OPTIONS,
                value='average',
                clearable=False
            )
        ]),

        # Jumbotron 3: Community Size
        html.Div(className='jumbotron', children=[
            html.Div(className='jumbotron-icon', style={'background': '#dcfce7'}, children=[
                html.Span('#', style={'color': '#16a34a', 'fontWeight': '700'})
            ]),
            html.H4(content.get('controls.community_size.title', 'Community Size'), className='jumbotron-title'),
            html.P(f"{n_society_param.base_value:,.0f}", className='jumbotron-value'),
            html.P(content.get('controls.community_size.tooltip', n_society_param.description), className='jumbotron-description'),
            dcc.Dropdown(
                id='society-param1',
                options=N_SOCIETY_OPTIONS,
                value='average',
                clearable=False
            )
        ]),

        # Jumbotron 4: Length of Stay
        html.Div(className='jumbotron', children=[
            html.Div(className='jumbotron-icon', style={'background': '#fee2e2'}, children=[
                html.Span('D', style={'color': '#dc2626', 'fontWeight': '700'})
            ]),
            html.H4(content.get('controls.length_of_stay.title', 'Length of Stay'), className='jumbotron-title'),
            html.P(f"{los_days_param.default_value:.0f} days", className='jumbotron-value'),
            html.P(content.get('controls.length_of_stay.tooltip', los_days_param.description), className='jumbotron-description'),
            dcc.Dropdown(
                id='society-param2',
                options=LOS_DAYS_OPTIONS,
                value='average',
                clearable=False
            )
        ])
    ]),

    # Calculate Button Section
    html.Div(className='calculate-section', style={
        'display': 'flex',
        'justifyContent': 'center',
        'marginBottom': '24px'
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

    # Main Content
    html.Div(children=[
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

                # Tabs Container
                dcc.Tabs(id='main-tabs', value='tab-overview', children=[
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
                            # 2-Column Layout: Left (KPI + Chart) | Right (Interpretation + Benchmark)
                            html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '24px'}, children=[
                                # Left Column
                                html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '24px'}, children=[
                                    # KPI Card
                                    html.Div(id='kpi-card'),

                                    # Charts Row: Numerator and Denominator side by side
                                    html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '16px'}, children=[
                                        # Numerator Chart (Detainee + Society Values)
                                        html.Div(className='chart-container', children=[
                                            dcc.Graph(id='numerator-chart')
                                        ]),

                                        # Denominator Chart (Government Cost vs Numerator)
                                        html.Div(className='chart-container', children=[
                                            dcc.Graph(id='denominator-chart')
                                        ])
                                    ])
                                ]),

                                # Right Column
                                html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '24px'}, children=[
                                    # Interpretation Card (populated by callback)
                                    html.Div(id='interpretation-card'),

                                    # Benchmark Card (populated by callback)
                                    html.Div(id='benchmark-card')
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
                            # Scenario Selection Section
                            html.Div(className='chart-container', style={'marginBottom': '24px'}, children=[
                                html.H4(content.get('scenarios.section_title', 'Scenario Selection'), style={
                                    'fontSize': '18px',
                                    'fontWeight': '600',
                                    'color': '#374151',
                                    'marginTop': '0',
                                    'marginBottom': '16px'
                                }),
                                html.P(content.get('scenarios.description', 'Compare different policy scenarios and their impact on MVPF calculations.'), style={
                                    'fontSize': '14px',
                                    'color': '#6b7280',
                                    'marginBottom': '16px'
                                }),
                                html.Label(content.get('scenarios.label', 'Select Scenario:'), style={
                                    'fontSize': '14px',
                                    'fontWeight': '500',
                                    'color': '#374151',
                                    'marginBottom': '8px',
                                    'display': 'block'
                                }),
                                dcc.Dropdown(
                                    id='scenario-selector',
                                    options=[
                                        {'label': content.get('scenarios.options.baseline', 'Baseline - Current Operations'), 'value': 'baseline'},
                                        {'label': content.get('scenarios.options.most_conservative', 'Conservative Approach'), 'value': 'most conservative'},
                                        {'label': content.get('scenarios.options.least_conservative', 'Least Conservative Approach'), 'value': 'least conservative'},
                                        {'label': content.get('scenarios.options.reduced_crime', 'Reduced Crime Scenario'), 'value': 'reduced_crime'},
                                        {'label': content.get('scenarios.options.increased_crime', 'Increased Crime Scenario'), 'value': 'increased_crime'},
                                        {'label': content.get('scenarios.options.diversion_program', 'Pre-Trial Diversion Program'), 'value': 'diversion_program'},
                                        {'label': content.get('scenarios.options.bail_reform', 'Bail Reform Scenario'), 'value': 'bail_reform'},
                                        {'label': content.get('scenarios.options.capacity_expansion', 'Facility Capacity Expansion'), 'value': 'capacity_expansion'}
                                    ],
                                    value='baseline',
                                    clearable=False,
                                    style={'maxWidth': '400px'}
                                )
                            ]),

                            # Subcomponents Chart
                            html.Div(className='chart-container', children=[
                                dcc.Graph(id='subcomponents-chart')
                            ])
                        ])
                    ])
                ]),

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
                                            'margin': '0'
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
                                    )
                                ])
                            ])
                        ]
                    ),

                    # Components breakdown
                    html.Div(style={'marginTop': '24px', 'paddingTop': '24px', 'borderTop': '1px solid #e5e7eb'},
                             children=[
                                 html.H4('Components Breakdown', style={
                                     'fontSize': '16px',
                                     'fontWeight': '600',
                                     'color': '#374151',
                                     'marginTop': '0',
                                     'marginBottom': '16px'
                                 }),
                                 html.Div(
                                     style={'display': 'flex', 'flexDirection': 'column', 'gap': '16px'},
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
                                                 html.H5('Detainee Values', style={
                                                     'fontSize': '15px',
                                                     'fontWeight': '600',
                                                     'color': '#2563eb',
                                                     'margin': '0 0 12px 0'
                                                 }),

                                                 html.P(
                                                     'Detainee Values capture the total harm detention imposes on people who are jailed. '
                                                     'We measure this using a willingness-to-pay lens, estimating how much a person would trade '
                                                     'to avoid being detained. This reflects short-term harms, disruptions to work and family life, '
                                                     'and long-term effects on health, income, and stability.',
                                                     style={
                                                         'fontSize': '14px',
                                                         'color': '#374151',
                                                         'margin': '0 0 12px 0',
                                                         'lineHeight': '1.6'
                                                     }
                                                 ),

                                                 # Subcomponents header
                                                 html.Div(className='label-with-info', children=[
                                                     html.Span('Subcomponents', style={
                                                         'fontWeight': '500',
                                                         'fontSize': '14px'
                                                        })

                                                    ]),
                                                 html.Div(children=[
                                                    # RHV
                                                     html.Div([
                                                         html.Button(
                                                             content.get('components_breakdown.detainee_values.subcomponents.harm_valuation.button_text', 'Willingness to Pay derived from Relative Harm Valuation'),
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
                                                             content.get('components_breakdown.detainee_values.subcomponents.wtp_freedom.button_text', 'Willingness to Pay for Freedom'),
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
                                                 html.H5('Society Values', style={
                                                     'fontSize': '15px',
                                                     'fontWeight': '600',
                                                     'color': '#16a34a',
                                                     'margin': '0 0 12px 0'
                                                 }),

                                                 html.P(
                                                     'Society Values measure how detention affects external factors like public safety, victimization risk, and community wellbeing. '
                                                     'These values summarize the effects felt by people outside the jail and convert those effects into a '
                                                     'common dollar scale for comparison.',
                                                     style={
                                                         'fontSize': '14px',
                                                         'color': '#374151',
                                                         'margin': '0 0 12px 0',
                                                         'lineHeight': '1.6'
                                                     }
                                                 ),

                                                 html.Div(className='label-with-info', children=[
                                                     html.Span('Subcomponents', style={
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
                                                 html.H5('Government Cost', style={
                                                     'fontSize': '15px',
                                                     'fontWeight': '600',
                                                     'color': '#dc2626',
                                                     'margin': '0 0 12px 0'
                                                 }),

                                                 html.P(
                                                     'Government Cost reflects all public spending required to run the detention system. This includes daily '
                                                     'operations, staffing, healthcare, facilities, court processing, and administrative overhead. It represents '
                                                     'the fiscal cost taxpayers bear to support the current level of detention.',
                                                     style={
                                                         'fontSize': '14px',
                                                         'color': '#374151',
                                                         'margin': '0 0 12px 0',
                                                         'lineHeight': '1.6'
                                                     }
                                                 ),

                                                 html.Div(className='label-with-info', children=[
                                                     html.Span('Subcomponents', style={
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

                                                     # Crime Increase Costs
                                                     html.Div([
                                                         html.Button(
                                                             content.get('components_breakdown.government_cost.subcomponents.crime_increase.button_text', 'Costs associated with Crime Effect: Increase'),
                                                             id='gov-crime-increase-btn',
                                                             n_clicks=0,
                                                             className='collapse-toggle'
                                                         ),
                                                         html.Div(
                                                             id='gov-crime-increase',
                                                             style={'display': 'none'},
                                                             children=[
                                                                 html.P(
                                                                     content.get('components_breakdown.government_cost.subcomponents.crime_increase.explanation', ''),
                                                                     style={
                                                                         'fontSize': '13px',
                                                                         'color': '#6b7280'
                                                                     }
                                                                 )
                                                             ]
                                                         )
                                                     ]),

                                                     # Crime Decrease Costs
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
                                             ]
                                         )
                                     ]
                                 )
                             ])
                ])
             ])
        ]
    )
])

# =============================================================================
# CALLBACKS MODULE
# All dashboard callbacks are registered via register_callbacks()
# =============================================================================


def _toggle_style(n_clicks, style):
    """Helper function to toggle visibility of collapsible sections."""
    if not n_clicks:
        return style or {'display': 'none'}
    if not style or style.get('display') == 'none':
        return {'display': 'block'}
    return {'display': 'none'}


def _convert_dropdown_to_params(fel_rate_sel, n_detainees_sel, n_society_sel, los_days_sel):
    """
    Convert dashboard dropdown selections to parameter values using the registry.

    Parameters:
    -----------
    fel_rate_sel : str
        Felony rate selection ('below', 'average', 'above')
    n_detainees_sel : str
        Detainee population selection ('below', 'average', 'above')
    n_society_sel : str
        Community size selection ('below', 'average', 'above')
    los_days_sel : str
        Length of stay selection ('below', 'average', 'above')

    Returns:
    --------
    dict : Parameter values for calculator
    """
    fel_rate_val = fel_rate_param.dropdown_map.get(fel_rate_sel, fel_rate_param.default_value)
    los_days_val = los_days_param.dropdown_map.get(los_days_sel, los_days_param.default_value)
    n_det_mult = n_detainees_param.dropdown_map.get(n_detainees_sel, 1.0)
    n_soc_mult = n_society_param.dropdown_map.get(n_society_sel, 1.0)

    return {
        'fel_rate': fel_rate_val,
        'los_days': los_days_val,
        'n_detainees_mult': n_det_mult,
        'n_society_mult': n_soc_mult,
        'crime_weight_mult': 1.0,
        'recidivism_mult': 1.0
    }


def _calculate_mvpf(scenario, detainee_param1, detainee_param2, society_param1, society_param2):
    """
    Calculate MVPF using the modular MVPFCalculator class.

    Parameters:
    -----------
    scenario : str
        Scenario name (e.g., 'baseline', 'most conservative', etc.)
    detainee_param1 : str
        Felony rate selection ('below', 'average', 'above')
    detainee_param2 : str
        Detainee population selection ('below', 'average', 'above')
    society_param1 : str
        Community size selection ('below', 'average', 'above')
    society_param2 : str
        Length of stay selection ('below', 'average', 'above')

    Returns:
    --------
    dict : MVPF results with all breakdowns
    """
    params = _convert_dropdown_to_params(
        fel_rate_sel=detainee_param1,
        n_detainees_sel=detainee_param2,
        n_society_sel=society_param1,
        los_days_sel=society_param2
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

        html.Div(className='kpi-interpretation', children=[
            html.Span(label, className='kpi-badge', style={
                'backgroundColor': badge_color,
                'color': badge_text_color,
                'display': 'inline-block',
                'marginBottom': '12px'
            }),

            html.P(
                'This indicates the program delivers more value than its cost.' if mvpf > 1
                else 'Consider reviewing program efficiency.',
                style={'marginTop': '8px', 'marginBottom': '16px'}
            ),
        ]),

        # Calculation row - moved above components
        html.Div(className='kpi-calculation', style={'marginTop': '0', 'marginBottom': '24px', 'paddingTop': '0', 'borderTop': 'none'}, children=[
            html.P([
                html.Strong('Calculation: '),
                f"MVPF = (${int(result['detainee_values']):,} + ${int(result['society_values']):,}) / ${int(result['govt_cost']):,} = {mvpf:.4f}"
            ], style={'margin': '0'})
        ]),

        # Vertical component sections
        html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '16px'}, children=[
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
    names = ['Current MVPF']
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

        # Calculate percentage comparison
        if current_mvpf != 0:
            if bench_mvpf >= 0 and current_mvpf >= 0:
                # Both positive: compare directly
                pct_diff = ((current_mvpf - bench_mvpf) / abs(bench_mvpf)) * 100 if bench_mvpf != 0 else 0
            elif bench_mvpf < 0 and current_mvpf >= 0:
                # Benchmark negative, current positive: CCJ is better
                pct_diff = abs(current_mvpf - bench_mvpf) / abs(bench_mvpf) * 100
            elif bench_mvpf >= 0 and current_mvpf < 0:
                # Benchmark positive, current negative: CCJ is worse
                pct_diff = -abs(current_mvpf - bench_mvpf) / abs(bench_mvpf) * 100
            else:
                # Both negative: less negative is better
                pct_diff = ((bench_mvpf - current_mvpf) / abs(bench_mvpf)) * 100
        else:
            pct_diff = 0

        # Determine if CCJ is better or worse
        is_better = current_mvpf > bench_mvpf

        # Value styling
        value_class = 'positive' if bench_mvpf >= 0 else 'negative'
        comparison_class = 'better' if is_better else 'worse'

        # Format comparison text
        if is_better:
            comparison_text = f"+{abs(pct_diff):.0f}%" if pct_diff != 0 else "Same"
        else:
            comparison_text = f"-{abs(pct_diff):.0f}%" if pct_diff != 0 else "Same"

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
            'Your MVPF: ',
            html.Strong(f'{current_mvpf:.2f}'),
            ' compared to other programs'
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
        title='MVPF Numerator: Willingness to Pay',
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
            x=['Numerator\n(Det + Soc)', 'Government Cost'],
            y=[numerator, gov_val],
            marker_color=[numerator_color, '#ef4444'],
            text=[f"${int(numerator):,}", f"${int(gov_val):,}"],
            textposition='outside'
        )
    ])

    fig.update_layout(
        title='MVPF: Numerator vs Denominator',
        xaxis_title='',
        yaxis_title='Value ($)',
        paper_bgcolor='#f8fafc',
        plot_bgcolor='#ffffff',
        font=dict(family='system-ui', size=12),
        margin=dict(t=50, b=100, l=80, r=40),
        showlegend=False
    )

    return fig


def _build_subcomponents_chart(result):
    """Build the subcomponents bar chart with variable names and auto-scaling."""
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

    # Calculate y-axis range to ensure all bars are visible
    if values:
        min_val = min(values)
        max_val = max(values)
        # Add padding (20%) to ensure text labels are visible
        padding = max(abs(max_val), abs(min_val)) * 0.2
        y_range = [min(0, min_val - padding), max(0, max_val + padding)]
    else:
        y_range = None

    fig = go.Figure(data=[
        go.Bar(
            x=names,
            y=values,
            marker_color=colors,
            text=text_labels,
            textposition='outside',
            textfont=dict(size=10)
        )
    ])

    fig.update_layout(
        title='Subcomponent Breakdown',
        xaxis_title='',
        yaxis_title='Value ($)',
        yaxis_range=y_range,
        paper_bgcolor='#f8fafc',
        plot_bgcolor='#ffffff',
        font=dict(family='system-ui', size=11),
        margin=dict(t=50, b=100, l=100, r=40),
        showlegend=False,
        xaxis_tickangle=-45,
        bargap=0.3
    )

    # Add a horizontal line at y=0 for reference
    fig.add_hline(y=0, line_dash="solid", line_color="#9ca3af", line_width=1)

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
    # Main Dashboard Update Callback
    # -------------------------------------------------------------------------

    @app.callback(
        [Output('kpi-card', 'children'),
         Output('benchmark-card', 'children'),
         Output('interpretation-card', 'children'),
         Output('numerator-chart', 'figure'),
         Output('denominator-chart', 'figure'),
         Output('subcomponents-chart', 'figure')],
        [Input('btn-calculate', 'n_clicks')],
        [State('scenario-selector', 'value'),
         State('detainee-param1', 'value'),
         State('detainee-param2', 'value'),
         State('society-param1', 'value'),
         State('society-param2', 'value')]
    )
    def update_dashboard(n_clicks, scenario, det_p1, det_p2, soc_p1, soc_p2):
        """Main callback to update all dashboard components."""
        # Get params for display in KPI card
        params = _convert_dropdown_to_params(
            fel_rate_sel=det_p1,
            n_detainees_sel=det_p2,
            n_society_sel=soc_p1,
            los_days_sel=soc_p2
        )

        result = _calculate_mvpf(scenario, det_p1, det_p2, soc_p1, soc_p2)
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
        interpretation_card = _build_interpretation_card()
        benchmark_card = _build_benchmark_card(mvpf)
        numerator_fig = _build_numerator_chart(result)
        denominator_fig = _build_denominator_chart(result)
        sub_fig = _build_subcomponents_chart(result)

        return kpi_card, benchmark_card, interpretation_card, numerator_fig, denominator_fig, sub_fig

    # -------------------------------------------------------------------------
    # Download CSV Callback
    # -------------------------------------------------------------------------

    @app.callback(
        Output('download-dataframe-csv', 'data'),
        Input('btn-download-csv', 'n_clicks'),
        [State('scenario-selector', 'value'),
         State('detainee-param1', 'value'),
         State('detainee-param2', 'value'),
         State('society-param1', 'value'),
         State('society-param2', 'value')],
        prevent_initial_call=True
    )
    def download_csv(n_clicks, scenario, det_p1, det_p2, soc_p1, soc_p2):
        """Generate and download CSV file with current MVPF results."""
        if n_clicks is None or n_clicks == 0:
            return None

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
