"""
MVPF Dashboard Application
Main dashboard layout and callbacks
"""

# Import global components
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import pandas as pd

# Import local modules
from mvpf_calculator import MVPFCalculator
from graphs import create_main_components_chart, create_subcomponents_chart

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
                gap: 24px;
                padding-top: 24px;
                border-top: 1px solid #e5e7eb;
            }
            .kpi-component h4 {
                font-size: 14px;
                color: #6b7280;
                margin: 0 0 4px 0;
                font-weight: 400;
            }
            .kpi-component p {
                font-size: 24px;
                font-weight: 600;
                margin: 0 0 4px 0;
            }
            .kpi-component span {
                font-size: 12px;
                color: #9ca3af;
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
                    html.H3('About MVPF'),
                    html.P(
                        'The MVPF measures the ratio of beneficiaries\' willingness to pay to the net cost to the government.'
                    ),
                    html.P([html.Strong('Components:')]),
                    html.Ul([
                        html.Li('Detainee Values: 2 subcomponents'),
                        html.Li('Society Values: 3 subcomponents'),
                        html.Li('Government Cost: 3 subcomponents')
                    ]),
                    html.P([html.Strong('Formula:'), html.Br(), 'MVPF = (Detainee + Society) / Government Cost'])
                ]),

                # Selection Options
                html.Div(className='sidebar control-section', children=[
                    html.H3('Analysis Parameters'),

                    html.Div(className='control-group', children=[
                        html.Div(className='label-with-info', children=[
                            html.Label('Detainee - Willingness to Pay for Freedom',
                                       className='control-label', style={'marginBottom': '0'}),
                            html.Span('i', className='info-icon',
                                      **{'data-tooltip': 'Placeholder explainer text - WTP Freedom'})
                        ]),
                        dcc.Dropdown(
                            id='detainee-param1',
                            options=[
                                {'label': 'Low ', 'value': 'low'},
                                {'label': 'Medium ', 'value': 'medium'},
                                {'label': 'High ', 'value': 'high'}
                            ],
                            value='medium',
                            clearable=False
                        )
                    ]),

                    html.Div(className='control-group', children=[
                        html.Div(className='label-with-info', children=[
                            html.Label('Detainee - Relative Harm Valuation',
                                       className='control-label', style={'marginBottom': '0'}),
                            html.Span('i', className='info-icon',
                                      **{'data-tooltip': 'Placeholder explainer text - Relative Harm Valuation'})
                        ]),
                        dcc.Dropdown(
                            id='detainee-param2',
                            options=[
                                {'label': 'Basic', 'value': 'basic'},
                                {'label': 'Standard', 'value': 'standard'},
                                {'label': 'Enhanced', 'value': 'enhanced'}
                            ],
                            value='standard',
                            clearable=False
                        )
                    ]),

                    html.Div(className='control-group', children=[
                        html.Div(className='label-with-info', children=[
                            html.Label('Community Impact',
                                       className='control-label', style={'marginBottom': '0'}),
                            html.Span('i', className='info-icon',
                                      **{'data-tooltip': 'Placeholder explainer text - Community Impact'})
                        ]),
                        dcc.Dropdown(
                            id='society-param1',
                            options=[
                                {'label': 'Minimal', 'value': 'minimal'},
                                {'label': 'Moderate', 'value': 'moderate'},
                                {'label': 'Significant', 'value': 'significant'}
                            ],
                            value='moderate',
                            clearable=False
                        )
                    ]),

                    html.Div(className='control-group', children=[
                        html.Div(className='label-with-info', children=[
                            html.Label('Length of Stay',
                                       className='control-label', style={'marginBottom': '0'}),
                            html.Span('i', className='info-icon',
                                      **{'data-tooltip': 'Placeholder explainer text - Length of Stay'})
                        ]),
                        dcc.Dropdown(
                            id='society-param2',
                            options=[
                                {'label': 'Below Average', 'value': 'below'},
                                {'label': 'Average', 'value': 'average'},
                                {'label': 'Above Average', 'value': 'above'}
                            ],
                            value='average',
                            clearable=False
                        )
                    ])
                ])
            ]),

            # Main Content
            html.Div(children=[
                # Baseline Switch
                html.Div(className='baseline-switch', children=[
                    html.Span('Comparison', className='baseline-label'),
                    html.Div(className='button-group', children=[
                        html.Button(
                            'Baseline',
                            id='btn-historical',
                            n_clicks=0,
                            className='baseline-button baseline-button-active'
                        ),
                        html.Button(
                            'Experience-informed Calculation',
                            id='btn-optimal',
                            n_clicks=0,
                            className='baseline-button baseline-button-inactive'
                        )
                    ])
                ]),

                # Hidden div to store baseline state
                dcc.Store(id='baseline-type', data='historical'),

                # MVPF KPI Card
                html.Div(id='kpi-card'),

                # Main Components Chart
                html.Div(className='chart-container', children=[
                    dcc.Graph(id='main-components-chart')
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
                            ]),
                            # Right column
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
                                                                }
                                                            )
                                                        ]
                                                    ),

                                                 # Collapsible list
                                                 html.Div(children=[
                                                     # 1. Willingness to Pay for Freedom
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
                                                                     'Represents the monetary value detainees place on avoiding incarceration. '
                                                                     'Derived from economic and wellbeing tradeoffs and interpreted as a willingness-to-pay measure.',
                                                                     style={
                                                                         'fontSize': '13px',
                                                                         'color': '#6b7280',
                                                                         'margin': '6px 0'
                                                                     }
                                                                 )
                                                             ]
                                                         )
                                                     ]),

                                                     # 2. Harm During Detention
                                                     html.Div([
                                                         html.Button(
                                                             'Incarceration-Related Harm',
                                                             id='detainee-harm-btn',
                                                             n_clicks=0,
                                                             className='collapse-toggle'
                                                         ),
                                                         html.Div(
                                                             id='detainee-harm',
                                                             style={'display': 'none'},
                                                             children=[
                                                                 html.P(
                                                                     'Captures immediate harms of detention, including loss of autonomy, exposure to stressful '
                                                                     'conditions, disrupted routines, and consequences for mental and physical health.',
                                                                     style={
                                                                         'fontSize': '13px',
                                                                         'color': '#6b7280',
                                                                         'margin': '6px 0'
                                                                     }
                                                                 )
                                                             ]
                                                         )
                                                     ]),

                                                     # 3. Post-Release Effects
                                                     html.Div([
                                                         html.Button(
                                                             'Post-Release Effects',
                                                             id='detainee-post-btn',
                                                             n_clicks=0,
                                                             className='collapse-toggle'
                                                         ),
                                                         html.Div(
                                                             id='detainee-post',
                                                             style={'display': 'none'},
                                                             children=[
                                                                 html.P(
                                                                     'Reflects effects of detention that persist after release, including changes to employment, '
                                                                     'income, housing stability, and longer-run wellbeing.',
                                                                     style={
                                                                         'fontSize': '13px',
                                                                         'color': '#6b7280',
                                                                         'margin': '6px 0'
                                                                     }
                                                                 )
                                                             ]
                                                         )
                                                     ])
                                                 ])
                                             ]
                                         ),

                                         # Society Values
                                         html.Div(
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
                                                     'Society Values measure how detention affects public safety, victimization risk, and community wellbeing. '
                                                     'These values summarize spillovers felt by people outside the jail and convert those effects into a '
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
                                                     # 1. Crime Prevention or Displacement
                                                     html.Div([
                                                         html.Button(
                                                             'Crime Prevention / Displacement',
                                                             id='society-crime-btn',
                                                             n_clicks=0,
                                                             className='collapse-toggle'
                                                         ),
                                                         html.Div(
                                                             id='society-crime',
                                                             style={'display': 'none'},
                                                             children=[
                                                                 html.P(
                                                                     'Measures whether detention reduces or shifts crime, and monetizes the resulting changes '
                                                                     'in safety and risk.',
                                                                     style={
                                                                         'fontSize': '13px',
                                                                         'color': '#6b7280'
                                                                     }
                                                                 )
                                                             ]
                                                         )
                                                     ]),

                                                     # 2. Victimization Cost
                                                     html.Div([
                                                         html.Button(
                                                             'Victimization Costs',
                                                             id='society-victim-btn',
                                                             n_clicks=0,
                                                             className='collapse-toggle'
                                                         ),
                                                         html.Div(
                                                             id='society-victim',
                                                             style={'display': 'none'},
                                                             children=[
                                                                 html.P(
                                                                     'Represents monetized harm to potential victims or avoided victimization resulting from '
                                                                     'detention decisions.',
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
                                                                     'Captures broader economic and social ripple effects within households, neighborhoods, '
                                                                     'and local economies.',
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
                                                                     'Includes daily costs of running the jail: staffing, housing, food, medical care, and supplies.',
                                                                     style={
                                                                         'fontSize': '13px',
                                                                         'color': '#6b7280'
                                                                     }
                                                                 )
                                                             ]
                                                         )
                                                     ]),

                                                     # Court/Admin
                                                     html.Div([
                                                         html.Button(
                                                             'Court and Administrative Costs',
                                                             id='gov-admin-btn',
                                                             n_clicks=0,
                                                             className='collapse-toggle'
                                                         ),
                                                         html.Div(
                                                             id='gov-admin',
                                                             style={'display': 'none'},
                                                             children=[
                                                                 html.P(
                                                                     'Covers court processing, hearings, paperwork, supervision, and other administrative overhead.',
                                                                     style={
                                                                         'fontSize': '13px',
                                                                         'color': '#6b7280'
                                                                     }
                                                                 )
                                                             ]
                                                         )
                                                     ]),

                                                     # Long-term fiscal
                                                     html.Div([
                                                         html.Button(
                                                             'Long-Term Fiscal Effects',
                                                             id='gov-long-btn',
                                                             n_clicks=0,
                                                             className='collapse-toggle'
                                                         ),
                                                         html.Div(
                                                             id='gov-long',
                                                             style={'display': 'none'},
                                                             children=[
                                                                 html.P(
                                                                     'Reflects downstream public spending or savings associated with post-release outcomes, '
                                                                     'service needs, or recidivism.',
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
                                         )
                                     ]
                                 )
                             ])
                ])
            ])
        ]
    )
])

# Collapse toggles for Components Breakdown
def _toggle_style(n_clicks, style):
    if not n_clicks:
        return style or {'display': 'none'}
    if not style or style.get('display') == 'none':
        return {'display': 'block'}
    return {'display': 'none'}


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
    Output('detainee-post', 'style'),
    Input('detainee-post-btn', 'n_clicks'),
    State('detainee-post', 'style')
)
def toggle_detainee_post(n_clicks, style):
    return _toggle_style(n_clicks, style)


@app.callback(
    Output('society-crime', 'style'),
    Input('society-crime-btn', 'n_clicks'),
    State('society-crime', 'style')
)
def toggle_society_crime(n_clicks, style):
    return _toggle_style(n_clicks, style)


@app.callback(
    Output('society-victim', 'style'),
    Input('society-victim-btn', 'n_clicks'),
    State('society-victim', 'style')
)
def toggle_society_victim(n_clicks, style):
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
    Output('gov-admin', 'style'),
    Input('gov-admin-btn', 'n_clicks'),
    State('gov-admin', 'style')
)
def toggle_gov_admin(n_clicks, style):
    return _toggle_style(n_clicks, style)


@app.callback(
    Output('gov-long', 'style'),
    Input('gov-long-btn', 'n_clicks'),
    State('gov-long', 'style')
)
def toggle_gov_long(n_clicks, style):
    return _toggle_style(n_clicks, style)

if __name__ == '__main__':
    app.run(debug=True, port=8050)
