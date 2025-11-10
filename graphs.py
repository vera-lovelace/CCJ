"""
Graph Generation Module
Contains all Plotly graph/chart creation functions for MVPF dashboard
"""

import plotly.graph_objs as go
import pandas as pd

def update_dashboard(baseline_type, detainee_param1, detainee_param2, society_param1, society_param2):
    # Calculate MVPF
    result = calculate_mvpf(baseline_type, detainee_param1, detainee_param2, society_param1, society_param2)

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

    # Main Components Chart
    main_fig = go.Figure(data=[
        go.Bar(
            x=['Detainee Values', 'Society Values', 'Government Cost'],
            y=[result['detainee_values'], result['society_values'], result['govt_cost']],
            marker_color=['#3b82f6', '#10b981', '#ef4444'],
            text=[f"${int(result['detainee_values']):,}",
                  f"${int(result['society_values']):,}",
                  f"${int(result['govt_cost']):,}"],
            textposition='outside'
        )
    ])

    main_fig.update_layout(
        title='MVPF Main Components',
        xaxis_title='',
        yaxis_title='Value ($)',
        paper_bgcolor='#f8fafc',
        plot_bgcolor='#ffffff',
        font=dict(family='system-ui', size=12),
        margin=dict(t=50, b=80, l=80, r=40),
        showlegend=False
    )

    # Subcomponents Chart - grouped by component
    sub_fig = go.Figure(data=[
        go.Bar(
            name='Subcomp 1',
            x=['Detainee Values', 'Society Values', 'Govt Cost'],
            y=[result['detainee_sub1'], result['society_sub1'], result['govt_sub1']],
            marker_color='#93c5fd',
            text=[f"${int(result['detainee_sub1']):,}",
                  f"${int(result['society_sub1']):,}",
                  f"${int(result['govt_sub1']):,}"],
            textposition='outside'
        ),
        go.Bar(
            name='Subcomp 2',
            x=['Detainee Values', 'Society Values', 'Govt Cost'],
            y=[result['detainee_sub2'], result['society_sub2'], result['govt_sub2']],
            marker_color='#3b82f6',
            text=[f"${int(result['detainee_sub2']):,}",
                  f"${int(result['society_sub2']):,}",
                  f"${int(result['govt_sub2']):,}"],
            textposition='outside'
        ),
        go.Bar(
            name='Subcomp 3',
            x=['Detainee Values', 'Society Values', 'Govt Cost'],
            y=[0, result['society_sub3'], result['govt_sub3']],
            marker_color='#1e40af',
            text=['',
                  f"${int(result['society_sub3']):,}",
                  f"${int(result['govt_sub3']):,}"],
            textposition='outside'
        )
    ])

    sub_fig.update_layout(
        title='Component Breakdown',
        xaxis_title='Main Components',
        yaxis_title='Value ($)',
        barmode='group',
        paper_bgcolor='#f8fafc',
        plot_bgcolor='#ffffff',
        font=dict(family='system-ui', size=12),
        margin=dict(t=50, b=80, l=80, r=40)
    )


    return kpi_card, main_fig, sub_fig