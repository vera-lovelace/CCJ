"""
MVPF Dashboard Application
Main dashboard layout and callbacks
"""

#import global components
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import pandas as pd

# Import local modules
from mvpf_calculator import MVPFCalculator
from graphs import create_main_components_chart, create_subcomponents_chart

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Custom CSS for styling (similar to Tailwind)
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
    html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 3fr', 'gap': '24px'}, children=[
        # Left Sidebar
        html.Div(children=[
            # Information Tile
            html.Div(className='info-tile', children=[
                html.H3('About MVPF'),
                html.P(
                    'The MVPF measures the ratio of beneficiaries\' willingness to pay to the net cost to the government.'),
                html.P([html.Strong('Components:')]),
                html.Ul([
                    html.Li('• Detainee Values: 2 subcomponents'),
                    html.Li('• Society Values: 3 subcomponents'),
                    html.Li('• Government Cost: 3 subcomponents')
                ]),
                html.P([
                    html.Strong('Formula:'), html.Br(),
                    'MVPF = (Detainee + Society) / Government Cost'
                ])
            ]),

            # Selection Options
            html.Div(className='sidebar control-section', children=[
                html.H3('Analysis Parameters'),

                html.Div(className='control-group', children=[
                    html.Label('Detainee - Willingness to Pay for Freedom', className='control-label'),
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
                    html.Label('Detainee - Relative Harm Valuation', className='control-label'),
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
                    html.Label('Community Impact', className='control-label'),
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
                    html.Label('Length of Stay', className='control-label'),
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
            ])
        ])
    ])
])


# Callback for baseline button switching
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



# Main callback for updating all components
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
    # Calculate MVPF using calculator module
    calculator = MVPFCalculator(baseline_type)
    result = calculator.calculate_mvpf(
        detainee_param1, detainee_param2,
        society_param1, society_param2
    )
    mvpf = result['mvpf']
    label, text_color, bg_color = calculator.get_mvpf_interpretation(mvpf)

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
            html.H2('MVPF Score', className='kpi-title'),
            html.Span(label, className='kpi-badge', style={
                'backgroundColor': badge_color,
                'color': badge_text_color
            })
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
            html.P(
                'This indicates the program delivers more value than its cost.' if mvpf > 1
                else 'Consider reviewing program efficiency.',
                style={'marginTop': '8px'}
            )
        ])
    ])

    # Create graphs using graphs module
    main_fig = create_main_components_chart(result)
    sub_fig = create_subcomponents_chart(result)

    return kpi_card, main_fig, sub_fig

# Server for deployment
#server = app.server

if __name__ == '__main__':
    app.run(debug=True, port=8050)