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
    html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 3fr', 'gap': '24px', 'alignItems': 'start'}, children=[
        # Left Sidebar
        html.Div(style={'position': 'sticky', 'top': '24px', 'zIndex': '1000'}, children=[
            # Information Tile
            html.Div(className='info-tile', children=[
                html.H3('About MVPF'),
                html.P('The MVPF measures the ratio of beneficiaries\' willingness to pay to the net cost to the government.'),
                html.P([html.Strong('Components:')]),
                html.Ul([
                    html.Li('• Detainee Values: 2 subcomponents'),
                    html.Li('• Society Values: 3 subcomponents'),
                    html.Li('• Government Cost: 3 subcomponents')
                ]),
                html.P([html.Strong('Formula:'), html.Br(), 'MVPF = (Detainee + Society) / Government Cost'])
            ]),

            # Selection Options
            html.Div(className='sidebar control-section', children=[
                html.H3('Analysis Parameters'),

                html.Div(className='control-group', children=[
                    html.Div(className='label-with-info', children=[
                        html.Label('Detainee - Willingness to Pay for Freedom', className='control-label', style={'marginBottom': '0'}),
                        html.Span('i', className='info-icon', **{'data-tooltip': 'Placeholder explainer text - WTP Freedom'})
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
                        html.Label('Detainee - Relative Harm Valuation', className='control-label', style={'marginBottom': '0'}),
                        html.Span('i', className='info-icon', **{'data-tooltip': 'Placeholder explainer text - Relative Harm Valuation'})
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
                        html.Label('Community Impact', className='control-label', style={'marginBottom': '0'}),
                        html.Span('i', className='info-icon', **{'data-tooltip': 'Placeholder explainer text - Community Impact'})
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
                        html.Label('Length of Stay', className='control-label', style={'marginBottom': '0'}),
                        html.Span('i', className='info-icon', **{'data-tooltip': 'Placeholder explainer text - Length of Stay'})
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
                html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '24px'}, children=[
                    html.Div(children=[
                        html.H4('What is MVPF?', style={
                            'fontSize': '16px',
                            'fontWeight': '600',
                            'color': '#374151',
                            'marginTop': '0',
                            'marginBottom': '12px'
                        }),
                        html.P(
                            'The Marginal Value of Public Funds (MVPF) is a metric that measures the '
                            'social welfare benefit of a policy per dollar of government spending. '
                            'It represents how much value beneficiaries receive relative to what the policy costs.',
                            style={'color': '#4b5563', 'fontSize': '14px', 'lineHeight': '1.6', 'margin': '0'}
                        )
                    ]),
                    html.Div(children=[
                        html.H4('How to Interpret', style={
                            'fontSize': '16px',
                            'fontWeight': '600',
                            'color': '#374151',
                            'marginTop': '0',
                            'marginBottom': '12px'
                        }),
                        html.Ul(style={'margin': '0', 'paddingLeft': '20px', 'color': '#4b5563', 'fontSize': '14px', 'lineHeight': '1.8'}, children=[
                            html.Li([html.Strong('MVPF > 1:'), ' Program delivers more value than it costs']),
                            html.Li([html.Strong('MVPF = 1:'), ' Program value equals its cost']),
                            html.Li([html.Strong('MVPF < 1:'), ' Program costs more than the value it provides']),
                            html.Li([html.Strong('MVPF ≥ 2.5:'), ' Excellent - high social return on investment'])
                        ])
                    ])
                ]),
                html.Div(style={'marginTop': '24px', 'paddingTop': '24px', 'borderTop': '1px solid #e5e7eb'}, children=[
                    html.H4('Components Breakdown', style={
                        'fontSize': '16px',
                        'fontWeight': '600',
                        'color': '#374151',
                        'marginTop': '0',
                        'marginBottom': '16px'
                    }),
                    html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '16px'}, children=[
                        # Detainee Values
                        html.Div(style={'background': 'white', 'padding': '20px', 'borderRadius': '8px', 'borderLeft': '4px solid #2563eb'}, children=[
                            html.H5('Detainee Values', style={'fontSize': '15px', 'fontWeight': '600', 'color': '#2563eb', 'margin': '0 0 12px 0'}),
                            html.P('Measures the value detainees place on freedom and reduced harm from the intervention.',
                                   style={'fontSize': '14px', 'color': '#374151', 'margin': '0 0 8px 0', 'lineHeight': '1.6'}),
                            html.P('Add your detailed explanation here. This can include multiple paragraphs, formulas, methodology details, and any other information you need to convey about how detainee values are calculated and what they represent in the MVPF framework.',
                                   style={'fontSize': '13px', 'color': '#6b7280', 'margin': '0', 'lineHeight': '1.6'})
                        ]),
                        # Society Values
                        html.Div(style={'background': 'white', 'padding': '20px', 'borderRadius': '8px', 'borderLeft': '4px solid #16a34a'}, children=[
                            html.H5('Society Values', style={'fontSize': '15px', 'fontWeight': '600', 'color': '#16a34a', 'margin': '0 0 12px 0'}),
                            html.P('Captures broader community benefits including reduced crime costs and social stability.',
                                   style={'fontSize': '14px', 'color': '#374151', 'margin': '0 0 8px 0', 'lineHeight': '1.6'}),
                            html.P('Add your detailed explanation here. This can include multiple paragraphs, formulas, methodology details, and any other information you need to convey about how society values are calculated and what they represent in the MVPF framework.',
                                   style={'fontSize': '13px', 'color': '#6b7280', 'margin': '0', 'lineHeight': '1.6'})
                        ]),
                        # Government Cost
                        html.Div(style={'background': 'white', 'padding': '20px', 'borderRadius': '8px', 'borderLeft': '4px solid #dc2626'}, children=[
                            html.H5('Government Cost', style={'fontSize': '15px', 'fontWeight': '600', 'color': '#dc2626', 'margin': '0 0 12px 0'}),
                            html.P('Total expenditure including program operations, administrative overhead, and resource allocation.',
                                   style={'fontSize': '14px', 'color': '#374151', 'margin': '0 0 8px 0', 'lineHeight': '1.6'}),
                            html.P('Add your detailed explanation here. This can include multiple paragraphs, formulas, methodology details, and any other information you need to convey about how government costs are calculated and what they represent in the MVPF framework.',
                                   style={'fontSize': '13px', 'color': '#6b7280', 'margin': '0', 'lineHeight': '1.6'})
                        ])
                    ])
                ])
            ])
        ])
    ])
])


# Baseline button switching callback
@app.callback(
    [Output('baseline-type', 'data'),
     Output('btn-historical', 'className'),
     Output('btn-optimal', 'className')],
    [Input('btn-historical', 'n_clicks'),
     Input('btn-optimal', 'n_clicks')],
    [State('baseline-type', 'data')]
)
def update_baseline(hist_clicks, opt_clicks, current_baseline):
    ctx = dash.callback_context
    if not ctx.triggered:
        return 'historical', 'baseline-button baseline-button-active', 'baseline-button baseline-button-inactive'

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'btn-historical':
        return 'historical', 'baseline-button baseline-button-active', 'baseline-button baseline-button-inactive'
    else:
        return 'optimal', 'baseline-button baseline-button-inactive', 'baseline-button baseline-button-active'


# Main dashboard update callback
@app.callback(
    [Output('kpi-card', 'children'),
     Output('main-components-chart', 'figure'),
     Output('subcomponents-chart', 'figure')],
    [Input('baseline-type', 'data'),
     Input('detainee-param1', 'value'),
     Input('detainee-param2', 'value'),
     Input('society-param1', 'value'),
     Input('society-param2', 'value')]
)
def update_dashboard(baseline_type, detainee_param1, detainee_param2, society_param1, society_param2):
    # Calculate MVPF
    calculator = MVPFCalculator(baseline_type)
    result = calculator.calculate_mvpf(detainee_param1, detainee_param2, society_param1, society_param2)
    
    mvpf = result['mvpf']
    label, text_color, bg_color = calculator.get_mvpf_interpretation(mvpf)

    # KPI Card
    kpi_card = html.Div(className='kpi-card', children=[
        html.Div(className='kpi-header', children=[
            html.H2('MVPF Score', className='kpi-title'),
            html.Span(label, className='kpi-badge', style={'backgroundColor': bg_color, 'color': text_color})
        ]),
        html.Div([
            html.Span(f"{mvpf:.2f}", className='kpi-value'),
            html.Span('ratio', className='kpi-ratio')
        ]),
        html.Div(className='kpi-components', children=[
            html.Div(className='kpi-component', children=[
                html.H4('Detainee Values'),
                html.P(f"${int(result['detainee_values']):,}", style={'color': '#2563eb'}),
                html.Span('2 subcomponents')
            ]),
            html.Div(className='kpi-component', children=[
                html.H4('Society Values'),
                html.P(f"${int(result['society_values']):,}", style={'color': '#16a34a'}),
                html.Span('3 subcomponents')
            ]),
            html.Div(className='kpi-component', children=[
                html.H4('Government Cost'),
                html.P(f"${int(result['govt_cost']):,}", style={'color': '#dc2626'}),
                html.Span('3 subcomponents')
            ])
        ]),
        html.Div(className='kpi-interpretation', children=[
            html.P([
                html.Strong('Calculation: '),
                f"MVPF = (${int(result['detainee_values']):,} + ${int(result['society_values']):,}) / ${int(result['govt_cost']):,} = {mvpf:.2f}"
            ]),
            html.P('This indicates the program delivers more value than its cost.' if mvpf > 1 else 'Consider reviewing program efficiency.', style={'marginTop': '8px'})
        ])
    ])

    # Create graphs
    main_fig = create_main_components_chart(result)
    sub_fig = create_subcomponents_chart(result)

    return kpi_card, main_fig, sub_fig


if __name__ == '__main__':
    app.run(debug=True, port=8050)