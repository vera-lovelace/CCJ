"""
MVPF Dashboard Application
Main dashboard layout and callbacks
"""

# Import global components
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
from datetime import datetime

from content_loader import ContentManager
from mvpf_calculator import MVPFCalculator
from parameters import ParameterRegistry


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
        html.H1('MVPF Analysis Dashboard'),
        html.P('Marginal Value of Public Funds Calculation')
    ]),

    # Main grid
    html.Div(
        style={'display': 'grid', 'gridTemplateColumns': '1fr 3fr', 'gap': '24px', 'alignItems': 'start'},
        children=[
            # Left Sidebar
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

                # Selection Options
                html.Div(className='sidebar control-section', children=[
                    html.H3('Analysis Parameters'),

                    html.Div(className='control-group', children=[
                        html.Div(className='label-with-info', children=[
                            html.Label(f"Felony Rate (base: {fel_rate_param.default_value:.0%})",
                                       className='control-label', style={'marginBottom': '0'}),
                            html.Span('i', className='info-icon',
                                      **{'data-tooltip': fel_rate_param.description})
                        ]),
                        dcc.Dropdown(
                            id='detainee-param1',
                            options=FEL_RATE_OPTIONS,
                            value='average',
                            clearable=False
                        )
                    ]),

                    html.Div(className='control-group', children=[
                        html.Div(className='label-with-info', children=[
                            html.Label(f"Detainee Population (base: {n_detainees_param.base_value:,.0f})",
                                       className='control-label', style={'marginBottom': '0'}),
                            html.Span('i', className='info-icon',
                                      **{'data-tooltip': n_detainees_param.description})
                        ]),
                        dcc.Dropdown(
                            id='detainee-param2',
                            options=N_DETAINEES_OPTIONS,
                            value='average',
                            clearable=False
                        )
                    ]),

                    html.Div(className='control-group', children=[
                        html.Div(className='label-with-info', children=[
                            html.Label(f"Community Size (base: {n_society_param.base_value:,.0f})",
                                       className='control-label', style={'marginBottom': '0'}),
                            html.Span('i', className='info-icon',
                                      **{'data-tooltip': n_society_param.description})
                        ]),
                        dcc.Dropdown(
                            id='society-param1',
                            options=N_SOCIETY_OPTIONS,
                            value='average',
                            clearable=False
                        )
                    ]),

                    html.Div(className='control-group', children=[
                        html.Div(className='label-with-info', children=[
                            html.Label(f"Length of Stay (base: {los_days_param.default_value:.0f} days)",
                                       className='control-label', style={'marginBottom': '0'}),
                            html.Span('i', className='info-icon',
                                      **{'data-tooltip': los_days_param.description})
                        ]),
                        dcc.Dropdown(
                            id='society-param2',
                            options=LOS_DAYS_OPTIONS,
                            value='average',
                            clearable=False
                        )
                    ])
                ])
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
                        '📥 Download Results (CSV)',
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

                # 2-Column Layout: Left (KPI) | Right (Chart + Benchmark)
                html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '24px', 'marginBottom': '24px'}, children=[
                    # Left Column
                    html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '24px'}, children=[
                        # KPI Card
                        html.Div(id='kpi-card'),

                        # Scenario Selection Section
                        html.Div(style={'marginTop': '24px', 'paddingTop': '24px', 'borderTop': '1px solid #e5e7eb'}, children=[
                            html.H4('Scenario Selection', style={
                                'fontSize': '16px',
                                'fontWeight': '600',
                                'color': '#374151',
                                'marginTop': '0',
                                'marginBottom': '12px'
                            }),
                            html.Label('Select Scenario:', style={
                                'fontSize': '14px',
                                'fontWeight': '500',
                                'color': '#6b7280',
                                'marginBottom': '8px',
                                'display': 'block'
                            }),
                            dcc.Dropdown(
                                id='scenario-selector',
                                options=[
                                    {'label': 'Baseline - Current Operations', 'value': 'baseline'},
                                    {'label': 'Conservative Approach', 'value': 'most conservative'},
                                    {'label': 'Least Conservative Approach', 'value': 'least conservative'},
                                    {'label': 'Reduced Crime Scenario', 'value': 'reduced_crime'},
                                    {'label': 'Increased Crime Scenario', 'value': 'increased_crime'},
                                    {'label': 'Pre-Trial Diversion Program', 'value': 'diversion_program'},
                                    {'label': 'Bail Reform Scenario', 'value': 'bail_reform'},
                                    {'label': 'Facility Capacity Expansion', 'value': 'capacity_expansion'}
                                ],
                                value='baseline',
                                clearable=False
                            )

                        ])

                    ]),

                    # Right Column
                    html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '24px'}, children=[
                        # Main Components Chart
                        html.Div(className='chart-container', children=[
                            dcc.Graph(id='main-components-chart')
                        ]),

                        # Benchmark Card (populated by callback)
                        html.Div(id='benchmark-card')
                    ])
                ]),

                # Subcomponents Chart
                html.Div(className='chart-container', children=[
                    dcc.Graph(id='subcomponents-chart')
                ]),

                # MVPF Explainer Section
                html.Div(className='chart-container', style={'background': '#f8fafc'}, children=[
                    html.H3('Understanding MVPF', style={
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
                                    'What is MVPF?',
                                    style={
                                        'fontSize': '16px',
                                        'fontWeight': '600',
                                        'color': '#374151',
                                        'marginTop': '0',
                                        'marginBottom': '12px'
                                    }
                                ),
                                html.P(
                                    'The Marginal Value of Public Funds (MVPF) is a metric that measures the '
                                    'social welfare benefit of a policy per dollar of government spending. '
                                    'It represents how much value beneficiaries receive relative to what the policy costs.',
                                    style={
                                        'color': '#4b5563',
                                        'fontSize': '14px',
                                        'lineHeight': '1.6',
                                        'margin': '0'
                                    }
                                ),
                                html.Div(children=[
                                    html.H4(
                                        "Applying MVPF to detention",
                                        style={
                                            'fontSize': '16px',
                                            'fontWeight': '600',
                                            'color': '#374151',
                                            'marginTop': '1',
                                            'marginBottom': '12px'
                                        }
                                    ),
                                    html.P(
                                        'Most MVPF work looks at policies where the person subject to the policy is also the main '
                                        'beneficiary, such as cash transfers. Detention is different. Jail is imposed on detainees '
                                        'but is justified as benefiting the general public. That is why this tool tracks both '
                                        'Detainee effects and broader Society effects when calculating the MVPF of detention.',
                                        style={
                                            'color': '#4b5563',
                                            'fontSize': '14px',
                                            'lineHeight': '1.6',
                                            'margin': '0'
                                        }
                                    ),
                                    html.P(
                                        'Most studies on detention focus on marginal changes, like one extra day in jail or one '
                                        'additional person detained. This tool instead looks at the overall or infra-marginal picture '
                                        'for a facility, using Cook County Jail as the baseline case. It uses the full annual costs of '
                                        'operating the jail and the full set of impacts on people who are detained to summarize those '
                                        'tradeoffs in an MVPF-style framework.',

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
                                                             'Willingness to Pay derived from Relative Harm Valuation',
                                                             id='detainee-harm-btn',
                                                             n_clicks=0,
                                                             className='collapse-toggle'
                                                         ),
                                                         html.Div(
                                                             id='detainee-harm',
                                                             style={'display': 'none'},
                                                             children=[
                                                                 html.P(
                                                                     'Text from content.json',
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
                                                             'Willingness to Pay for Freedom',
                                                             id='detainee-wtp-btn',
                                                             n_clicks=0,
                                                             className='collapse-toggle'
                                                         ),
                                                         html.Div(
                                                             id='detainee-wtp',
                                                             style={'display': 'none'},
                                                             children=[
                                                                 html.P(
                                                                     'Text from content.json',
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
                                                             'Crime Prevention',
                                                             id='society-crime-btn',
                                                             n_clicks=0,
                                                             className='collapse-toggle'
                                                         ),
                                                         html.Div(
                                                             id='society-crime',
                                                             style={'display': 'none'},
                                                             children=[
                                                                 html.P(
                                                                     'text from content.json',
                                                                     style={
                                                                         'fontSize': '13px',
                                                                         'color': '#6b7280'
                                                                     }
                                                                 )
                                                             ]
                                                         )
                                                     ]),
# 1. Crime Prevention
                                                     html.Div([
                                                         html.Button(
                                                             'Court Appearance Effects',
                                                             id='society-court-btn',
                                                             n_clicks=0,
                                                             className='collapse-toggle'
                                                         ),
                                                         html.Div(
                                                             id='society-court',
                                                             style={'display': 'none'},
                                                             children=[
                                                                 html.P(
                                                                     'text from content.json',
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
                                                             'Community and Economic Spillovers',
                                                             id='society-spill-btn',
                                                             n_clicks=0,
                                                             className='collapse-toggle'
                                                         ),
                                                         html.Div(
                                                             id='society-spill',
                                                             style={'display': 'none'},
                                                             children=[
                                                                 html.P(
                                                                     'text from content.json',
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
                                                             'Operational Costs',
                                                             id='gov-op-btn',
                                                             n_clicks=0,
                                                             className='collapse-toggle'
                                                         ),
                                                         html.Div(
                                                             id='gov-op',
                                                             style={'display': 'none'},
                                                             children=[
                                                                 html.P(
                                                                     'text from content.json',
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
                                                             'Costs associated with Crime Effect: Increase',
                                                             id='gov-crime-increase-btn',
                                                             n_clicks=0,
                                                             className='collapse-toggle'
                                                         ),
                                                         html.Div(
                                                             id='gov-crime-increase',
                                                             style={'display': 'none'},
                                                             children=[
                                                                 html.P(
                                                                     'text from content.json',
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
                                                             'Costs associated with Crime Effect: Decrease',
                                                             id='gov-crime-decrease-btn',
                                                             n_clicks=0,
                                                             className='collapse-toggle'
                                                         ),
                                                         html.Div(
                                                             id='gov-crime-decrease',
                                                             style={'display': 'none'},
                                                             children=[
                                                                 html.P(
                                                                     'text from content.json',
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

# --- Toggle Callbacks ---


def _toggle_style(n_clicks, style):
    if not n_clicks:
        return style or {'display': 'none'}
    if not style or style.get('display') == 'none':
        return {'display': 'block'}
    return {'display': 'none'}


# --- Detainee Values subcomponents ---

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


# --- Society Values subcomponents ---

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


# --- Government Cost subcomponents ---

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

"""
Dashboard Callbacks
"""

def convert_dropdown_to_params(fel_rate_sel, n_detainees_sel, n_society_sel, los_days_sel):
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
    # Get values from registry dropdown maps
    fel_rate_val = fel_rate_param.dropdown_map.get(fel_rate_sel, fel_rate_param.default_value)
    los_days_val = los_days_param.dropdown_map.get(los_days_sel, los_days_param.default_value)
    n_det_mult = n_detainees_param.dropdown_map.get(n_detainees_sel, 1.0)
    n_soc_mult = n_society_param.dropdown_map.get(n_society_sel, 1.0)

    return {
        'fel_rate': fel_rate_val,  # Direct value (0.5, 0.7, 1.0)
        'los_days': los_days_val,  # Direct value in days (60, 70, 203)
        'n_detainees_mult': n_det_mult,  # Multiplier (0.8, 1.0, 1.2)
        'n_society_mult': n_soc_mult,  # Multiplier (0.8, 1.0, 1.2)
        'crime_weight_mult': 1.0,
        'recidivism_mult': 1.0
    }


def calculate_mvpf(scenario, detainee_param1, detainee_param2, society_param1, society_param2):
    """
    Calculate MVPF using the modular MVPFCalculator class

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
    # Convert dashboard parameters to calculator format using registry
    params = convert_dropdown_to_params(
        fel_rate_sel=detainee_param1,
        n_detainees_sel=detainee_param2,
        n_society_sel=society_param1,
        los_days_sel=society_param2
    )

    # Calculate MVPF
    result = calculator.calculate(scenario, params)
    print("Debug - Result structure:")
    print(f"Detainee breakdown: {result['detainee_breakdown']}")
    print(f"Society breakdown: {result['society_breakdown']}")
    print(f"Govt breakdown: {result['govt_breakdown']}")

    # Extract breakdown values for backwards compatibility
    detainee_breakdown = list(result['detainee_breakdown'].values())
    society_breakdown = list(result['society_breakdown'].values())
    govt_breakdown = list(result['govt_breakdown'].values())

    def safe_get(lst, index, default=0):
        try:
            return lst[index]
        except IndexError:
            return default
    # Add breakdown values to the result
    result['detainee_sub1'] = safe_get(detainee_breakdown, 0)
    result['detainee_sub2'] = safe_get(detainee_breakdown, 1)
    result['society_sub1'] = safe_get(society_breakdown, 0)
    result['society_sub2'] = safe_get(society_breakdown, 1)
    result['society_sub3'] = safe_get(society_breakdown, 2)
    result['govt_sub1'] = safe_get(govt_breakdown, 0)
    result['govt_sub2'] = safe_get(govt_breakdown, 1)
    result['govt_sub3'] = safe_get(govt_breakdown, 2)

    return result


# Main callback for updating all components
@app.callback(
    [Output('kpi-card', 'children'),
     Output('benchmark-card', 'children'),
     Output('main-components-chart', 'figure'),
     Output('subcomponents-chart', 'figure')],
    [Input('scenario-selector', 'value'),
     Input('detainee-param1', 'value'),
     Input('detainee-param2', 'value'),
     Input('society-param1', 'value'),
     Input('society-param2', 'value')]
)
def update_dashboard(scenario, det_p1, det_p2, soc_p1, soc_p2):
    # Calculate MVPF
    result = calculate_mvpf(scenario, det_p1, det_p2, soc_p1, soc_p2)


    mvpf = result['mvpf']

    # Determine badge color and label
    if mvpf >= 2.5:
        badge_color = '#dcfce7'
        badge_text_color = '#16a34a'
        label = 'Excellent'
    elif mvpf >= 1.5:
        badge_color = '#dbeafe'
        badge_text_color = '#2563eb'
        label = 'Good'
    elif mvpf >= 1.0:
        badge_color = '#fef3c7'
        badge_text_color = '#ca8a04'
        label = 'Fair'
    else:
        badge_color = '#fee2e2'
        badge_text_color = '#dc2626'
        label = 'Poor'


    # KPI Card
    kpi_card = html.Div(className='kpi-card', children=[
        html.Div(className='kpi-header', children=[
            html.H2('MVPF Score', className='kpi-title')
        ]),

        html.Div([
            html.Span(f"{mvpf:.4f}", className='kpi-value'),
            html.Span('ratio', className='kpi-ratio')
        ]),

        # Interpretation section
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

            # Interpretation guide
            html.Div(children=[
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
                        html.Li(
                            [html.Strong('MVPF ≥ 2.5:'), ' Very high social return on investment']
                        ),
                        html.Li(
                            [html.Strong('MVPF > 1:'), ' Program delivers more value than it costs']
                        ),
                        html.Li(
                            [html.Strong('MVPF = 1:'), ' Program value equals its cost']
                        ),
                        html.Li(
                            [html.Strong('MVPF < 1:'), ' Program costs more than the value it provides']
                        ),
                        html.Li(
                            [html.Strong('MVPF < 0:'), ' Indicates program delivers net harm']
                        )
                    ]
                )
            ])
        ]),

        # Component Tiles with clickable links
        html.Div(className='kpi-components', children=[
            # Detainee Values Tile
            html.Div(className='kpi-component', children=[
                html.A(href='#detainee-values-section', className='kpi-component-link', children=[
                    html.H4('Values for Detainees')
                ]),
                html.P(f"${int(result['detainee_values']):,}", style={'color': '#2563eb'}),
                html.Span('2 subcomponents')
            ]),

            # Society Values Tile
            html.Div(className='kpi-component', children=[
                html.A(href='#society-values-section', className='kpi-component-link', children=[
                    html.H4('Value for Society')
                ]),
                html.P(f"${int(result['society_values']):,}", style={'color': '#16a34a'}),
                html.Span('3 subcomponents')
            ]),

            # Government Cost Tile
            html.Div(className='kpi-component', children=[
                html.A(href='#government-cost-section', className='kpi-component-link', children=[
                    html.H4('Government Costs')
                ]),
                html.P(f"${int(result['govt_cost']):,}", style={'color': '#dc2626'}),
                html.Span('3 subcomponents'),

            ])
        ]),

        # Calculation at the bottom
        html.Div(className='kpi-calculation', children=[
            html.P([
                html.Strong('Calculation: '),
                f"MVPF = (${int(result['detainee_values']):,} + ${int(result['society_values']):,}) / ${int(result['govt_cost']):,} = {mvpf:.4f}"
            ], style={'margin': '0'})
        ])

    ])

    # Benchmark Card
    benchmark_card = html.Div(className='kpi-card', children=[
        html.H3('Comparative Benchmarking', style={
            'fontSize': '20px',
            'fontWeight': '600',
            'color': '#1e293b',
            'marginBottom': '16px',
            'marginTop': '0'
        }),
        html.P('CCJ program relative to federal programs:', style={
            'fontSize': '14px',
            'color': '#6b7280',
            'marginBottom': '16px',
            'fontWeight': '500'
        }),
        html.Ul(
            style={
                'margin': '0',
                'paddingLeft': '20px',
                'color': '#374151',
                'fontSize': '14px',
                'lineHeight': '1.8'
            },
            children=[
                html.Li([
                    html.Strong('23×'),
                    ' more cost-effective: Supplemental Security Income (SSI)'
                ]),
                html.Li([
                    html.Strong('6.1×'),
                    ' more cost-effective: Food Stamps (SNAP)'
                ]),
                html.Li([
                    html.Strong('1.2×'),
                    ' more cost-effective: Mandated Mental Health Treatment in the Criminal Justice System'
                ]),
                html.Li([
                    html.Strong('3.7×'),
                    ' less harmful: American Opportunity Tax Credit (AOTC)'
                ])
            ]
        ),
        html.P('Source: Policy benchmarks based on comparative MVPF analysis', style={
            'fontSize': '11px',
            'color': '#9ca3af',
            'marginTop': '16px',
            'marginBottom': '0',
            'fontStyle': 'italic'
        })
    ])

    # Main Components Chart
    # Use logarithmic scale with absolute values to handle vastly different magnitudes
    # Negative values are shown as absolute with visual indicators
    det_val = result['detainee_values']
    soc_val = result['society_values']
    gov_val = result['govt_cost']

    # Use absolute values for log scale, add small offset to avoid log(0)
    y_values = [abs(det_val) + 1, abs(soc_val) + 1, abs(gov_val) + 1]

    # Color code: red for negative, blue/green for positive
    colors = ['#ef4444' if det_val < 0 else '#3b82f6',
              '#10b981' if soc_val >= 0 else '#ef4444',
              '#22c55e' if gov_val < 0 else '#ef4444']

    main_fig = go.Figure(data=[
        go.Bar(
            x=['Value for Detainees', 'Value for Society', 'Government Cost'],
            y=y_values,
            marker_color=colors,
            text=[f"${int(det_val):,}",
                  f"${int(soc_val):,}",
                  f"${int(gov_val):,}"],
            textposition='outside'
        )
    ])

    main_fig.update_layout(
        title='MVPF Main Components (Absolute values)',
        xaxis_title='',
        yaxis_title='Absolute Value ($) - Log Scale',
        yaxis_type='log',
        paper_bgcolor='#f8fafc',
        plot_bgcolor='#ffffff',
        font=dict(family='system-ui', size=12),
        margin=dict(t=50, b=80, l=80, r=40),
        showlegend=False
    )


    # Subcomponents Chart - grouped by component
    # Use logarithmic scale with absolute values for vastly different magnitudes
    sub_fig = go.Figure(data=[
        go.Bar(
            name='Subcomp 1',
            x=['Detainee Values', 'Society Values', 'Govt Cost'],
            y=[abs(result['detainee_sub1']) + 1, abs(result['society_sub1']) + 1, abs(result['govt_sub1']) + 1],
            marker_color='#93c5fd',
            text=[f"${int(result['detainee_sub1']):,}",
                  f"${int(result['society_sub1']):,}",
                  f"${int(result['govt_sub1']):,}"],
            textposition='outside'
        ),
        go.Bar(
            name='Subcomp 2',
            x=['Detainee Values', 'Society Values', 'Govt Cost'],
            y=[abs(result['detainee_sub2']) + 1, abs(result['society_sub2']) + 1, abs(result['govt_sub2']) + 1],
            marker_color='#3b82f6',
            text=[f"${int(result['detainee_sub2']):,}",
                  f"${int(result['society_sub2']):,}",
                  f"${int(result['govt_sub2']):,}"],
            textposition='outside'
        ),
        go.Bar(
            name='Subcomp 3',
            x=['Detainee Values', 'Society Values', 'Govt Cost'],
            y=[1, abs(result['society_sub3']) + 1, abs(result['govt_sub3']) + 1],
            marker_color='#1e40af',
            text=['',
                  f"${int(result['society_sub3']):,}",
                  f"${int(result['govt_sub3']):,}"],
            textposition='outside'
        )
    ])

    sub_fig.update_layout(
        title='Component Breakdown (Log Scale)',
        xaxis_title='Main Components',
        yaxis_title='Absolute Value ($) - Log Scale',
        yaxis_type='log',
        barmode='group',
        paper_bgcolor='#f8fafc',
        plot_bgcolor='#ffffff',
        font=dict(family='system-ui', size=12),
        margin=dict(t=50, b=80, l=80, r=40)
    )

    return kpi_card, benchmark_card, main_fig, sub_fig


# Download CSV callback
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

    # Convert dashboard parameters to calculator format using registry
    params = convert_dropdown_to_params(
        fel_rate_sel=det_p1,
        n_detainees_sel=det_p2,
        n_society_sel=soc_p1,
        los_days_sel=soc_p2
    )

    # Calculate MVPF
    result = calculator.calculate(scenario, params)

    # Export to CSV string
    csv_string = calculator.export_to_string(result, include_metadata=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'mvpf_results_{scenario}_{timestamp}.csv'

    return dict(content=csv_string, filename=filename)


if __name__ == '__main__':
    app.run(debug=True, port=8050)
