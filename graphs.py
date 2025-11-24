"""
Graph Generation Module
Contains all Plotly graph/chart creation functions for MVPF dashboard
"""

import plotly.graph_objs as go
import pandas as pd

def create_main_components_chart(result):
    """
    Create bar chart showing main MVPF components.

    Args:
        result (dict): MVPF calculation results

    Returns:
        plotly.graph_objs.Figure: Main components bar chart
    """
    fig = go.Figure(data=[
        go.Bar(
            x=['Detainee Values', 'Society Values', 'Government Cost'],
            y=[result['detainee_values'], result['society_values'], result['govt_cost']],
            marker_color=['#3b82f6', '#10b981', '#ef4444'],
            text=[
                f"${int(result['detainee_values']):,}",
                f"${int(result['society_values']):,}",
                f"${int(result['govt_cost']):,}"
            ],
            textposition='outside'
        )
    ])

    fig.update_layout(
        title='MVPF Main Components',
        xaxis_title='',
        yaxis_title='Value ($)',
        paper_bgcolor='#f8fafc',
        plot_bgcolor='#ffffff',
        font=dict(family='system-ui', size=12),
        margin=dict(t=50, b=80, l=80, r=40),
        showlegend=False
    )
    return fig

def create_subcomponents_chart(result):
    """
    Create grouped bar chart showing component breakdown.

    Args:
        result (dict): MVPF calculation results

    Returns:
        plotly.graph_objs.Figure: Subcomponents breakdown chart
    """
    fig = go.Figure(data=[
        go.Bar(
            name='Subcomp 1',
            x=['Detainee Values', 'Society Values', 'Govt Cost'],
            y=[result['detainee_sub1'], result['society_sub1'], result['govt_sub1']],
            marker_color='#93c5fd',
            text=[
                f"${int(result['detainee_sub1']):,}",
                f"${int(result['society_sub1']):,}",
                f"${int(result['govt_sub1']):,}"
            ],
            textposition='outside'
        ),
        go.Bar(
            name='Subcomp 2',
            x=['Detainee Values', 'Society Values', 'Govt Cost'],
            y=[result['detainee_sub2'], result['society_sub2'], result['govt_sub2']],
            marker_color='#3b82f6',
            text=[
                f"${int(result['detainee_sub2']):,}",
                f"${int(result['society_sub2']):,}",
                f"${int(result['govt_sub2']):,}"
            ],
            textposition='outside'
        ),
        go.Bar(
            name='Subcomp 3',
            x=['Detainee Values', 'Society Values', 'Govt Cost'],
            y=[0, result['society_sub3'], result['govt_sub3']],
            marker_color='#1e40af',
            text=[
                '',
                f"${int(result['society_sub3']):,}",
                f"${int(result['govt_sub3']):,}"
            ],
            textposition='outside'
        )
    ])

    fig.update_layout(
        title='Component Breakdown',
        xaxis_title='Main Components',
        yaxis_title='Value ($)',
        barmode='group',
        paper_bgcolor='#f8fafc',
        plot_bgcolor='#ffffff',
        font=dict(family='system-ui', size=12),
        margin=dict(t=50, b=80, l=80, r=40)
    )

    return fig

def create_comparison_chart(policies_data):
    """
    Create comparison chart for multiple policies

    Args:
        policies_data (list): List of dicts with 'policy_name' and 'mvpf' keys

    Returns:
        plotly.graph_objs.Figure: Comparison bar chart
    """
    policy_names = [p['policy_name'] for p in policies_data]
    mvpfs = [p['mvpf'] for p in policies_data]

    colors = ['#16a34a' if m >= 2.5 else '#3b82f6' if m >= 1.5
    else '#ca8a04' if m >= 1.0 else '#dc2626' for m in mvpfs]

    fig = go.Figure(data=[
        go.Bar(
            x=policy_names,
            y=mvpfs,
            marker_color=colors,
            text=[f"{m:.2f}" for m in mvpfs],
            textposition='outside'
        )
    ])

    fig.update_layout(
        title='Policy Comparison',
        xaxis_title='Policy',
        yaxis_title='MVPF Ratio',
        paper_bgcolor='#f8fafc',
        plot_bgcolor='#ffffff',
        font=dict(family='system-ui', size=12),
        margin=dict(t=50, b=100, l=80, r=40),
        showlegend=False
    )

    return fig

def create_denominator_chart(result):
    """
    Create bar chart showing main MVPF components in the denominator.

    Args:
        result (dict): MVPF calculation results

    Returns:
        plotly.graph_objs.Figure: Main components bar chart
    """
    fig = go.Figure(data=[
        go.Bar(
            x=['Government Cost'],
            y=[result['govt_cost']],
            marker_color=['#3b82f6', '#10b981', '#ef4444'],
            text=[
                f"${int(result['govt_cost']):,}"
            ],
            textposition='outside'
        )
    ])

    fig.update_layout(
        title='MVPF Government costs',
        xaxis_title='',
        yaxis_title='Value ($)',
        paper_bgcolor='#f8fafc',
        plot_bgcolor='#ffffff',
        font=dict(family='system-ui', size=12),
        margin=dict(t=50, b=80, l=80, r=40),
        showlegend=False
    )
    return fig

def create_numerator_chart(result):
    """
    Create bar chart showing main MVPF components for willingness to pay

    Args:
        result (dict): MVPF calculation results

    Returns:
        plotly.graph_objs.Figure: Main components bar chart
    """
    fig = go.Figure(data=[
        go.Bar(
            x=['Detainee Values', 'Society Values'],
            y=[result['detainee_values'], result['society_values']],
            marker_color=['#3b82f6', '#10b981', '#ef4444'],
            text=[
                f"${int(result['detainee_values']):,}",
                f"${int(result['society_values']):,}"
            ],
            textposition='outside'
        )
    ])

    fig.update_layout(
        title='MVPF Main Components',
        xaxis_title='',
        yaxis_title='Value ($)',
        paper_bgcolor='#f8fafc',
        plot_bgcolor='#ffffff',
        font=dict(family='system-ui', size=12),
        margin=dict(t=50, b=80, l=80, r=40),
        showlegend=False
    )
    return fig
