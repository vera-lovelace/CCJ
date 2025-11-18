import dash
from dash import html, dcc
import dash_bootstrap_components as dbc


def create_mvpf_benchmarks(current_value=2.45, benchmarks=None):
    """
    Create a MVPF Benchmarks component for Dash

    Parameters:
    -----------
    current_value : float
        The current MVPF score to highlight
    benchmarks : list of dict
        List of benchmark dictionaries with keys: 'name', 'value', 'category'
        If None, uses default benchmarks

    Returns:
    --------
    dash component
    """

    # Default benchmarks if none provided
    if benchmarks is None:
        benchmarks = [
            {"name": "Education Programs", "value": 2.8, "category": "high"},
            {"name": "Healthcare Subsidies", "value": 2.1, "category": "medium"},
            {"name": "Current Program", "value": current_value, "category": "high", "current": True},
            {"name": "Tax Credits", "value": 1.5, "category": "medium"},
            {"name": "Infrastructure", "value": 0.8, "category": "low"}
        ]

    def get_benchmark_color(category):
        if category == "high":
            return "#22c55e"  # green-500
        elif category == "medium":
            return "#3b82f6"  # blue-500
        return "#9ca3af"  # gray-400

    def create_benchmark_card(benchmark, index):
        is_current = benchmark.get('current', False)

        # Card style
        card_style = {
            'padding': '1rem',
            'borderRadius': '0.5rem',
            'border': '2px solid',
            'borderColor': '#3b82f6' if is_current else '#e5e7eb',
            'backgroundColor': '#eff6ff' if is_current else 'white',
            'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)' if is_current else 'none',
            'transition': 'all 0.3s',
            'marginBottom': '0.75rem'
        }

        # Color bar style
        bar_color = get_benchmark_color(benchmark['category'])
        color_bar_style = {
            'width': '0.5rem',
            'height': '3rem',
            'borderRadius': '0.25rem',
            'backgroundColor': bar_color
        }

        # Progress bar width (scale to 3.0 as max)
        progress_width = min((benchmark['value'] / 3.0) * 100, 100)

        return html.Div([
            # Main content row
            html.Div([
                # Left side with color bar and name
                html.Div([
                    html.Div(style=color_bar_style),
                    html.Div([
                        html.P(
                            [
                                benchmark['name'],
                                html.Span(
                                    'Current',
                                    style={
                                        'marginLeft': '0.5rem',
                                        'fontSize': '0.75rem',
                                        'backgroundColor': '#2563eb',
                                        'color': 'white',
                                        'padding': '0.25rem 0.5rem',
                                        'borderRadius': '0.25rem'
                                    }
                                ) if is_current else None
                            ],
                            style={
                                'fontWeight': '600',
                                'color': '#1e3a8a' if is_current else '#1f2937',
                                'margin': '0'
                            }
                        )
                    ], style={'marginLeft': '0.75rem'})
                ], style={'display': 'flex', 'alignItems': 'center', 'flex': '1'}),

                # Right side with value
                html.Div([
                    html.P(
                        f"{benchmark['value']:.2f}",
                        style={
                            'fontSize': '1.5rem',
                            'fontWeight': '700',
                            'color': '#1f2937',
                            'margin': '0'
                        }
                    )
                ], style={'textAlign': 'right'})
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),

            # Progress bar
            html.Div([
                html.Div(
                    style={
                        'height': '0.5rem',
                        'backgroundColor': bar_color,
                        'width': f'{progress_width}%',
                        'transition': 'width 0.3s',
                        'borderRadius': '9999px'
                    }
                )
            ], style={
                'marginTop': '0.75rem',
                'backgroundColor': '#e5e7eb',
                'height': '0.5rem',
                'borderRadius': '9999px',
                'overflow': 'hidden'
            })
        ], style=card_style)

    # Create all benchmark cards
    benchmark_cards = [create_benchmark_card(b, i) for i, b in enumerate(benchmarks)]

    # Legend
    legend = html.Div([
        html.P([
            html.Span('Legend: ', style={'fontWeight': '600'}),
            html.Span([
                html.Span(style={
                    'display': 'inline-block',
                    'width': '0.75rem',
                    'height': '0.75rem',
                    'backgroundColor': '#22c55e',
                    'borderRadius': '0.25rem',
                    'marginRight': '0.25rem'
                }),
                'High (>2.0)'
            ], style={'marginLeft': '0.5rem'}),
            html.Span([
                html.Span(style={
                    'display': 'inline-block',
                    'width': '0.75rem',
                    'height': '0.75rem',
                    'backgroundColor': '#3b82f6',
                    'borderRadius': '0.25rem',
                    'marginRight': '0.25rem'
                }),
                'Medium (1.0-2.0)'
            ], style={'marginLeft': '0.75rem'}),
            html.Span([
                html.Span(style={
                    'display': 'inline-block',
                    'width': '0.75rem',
                    'height': '0.75rem',
                    'backgroundColor': '#9ca3af',
                    'borderRadius': '0.25rem',
                    'marginRight': '0.25rem'
                }),
                'Low (<1.0)'
            ], style={'marginLeft': '0.75rem'})
        ], style={
            'fontSize': '0.75rem',
            'color': '#4b5563',
            'margin': '0'
        })
    ], style={
        'marginTop': '1rem',
        'padding': '0.75rem',
        'backgroundColor': '#f9fafb',
        'borderRadius': '0.5rem',
        'border': '1px solid #e5e7eb'
    })

    # Complete component
    return html.Div([
        # Header
        html.H3(
            'Comparative Benchmarks',
            style={
                'fontSize': '1.125rem',
                'fontWeight': '600',
                'color': '#1f2937',
                'marginBottom': '1rem'
            }
        ),

        # Benchmarks list
        html.Div(benchmark_cards),

        # Legend
        legend
    ], style={
        'backgroundColor': 'white',
        'borderRadius': '0.5rem',
        'boxShadow': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
        'padding': '1.5rem',
        'height': '100%'
    })