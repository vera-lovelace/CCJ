"""
Graph Generation Module
Contains all Plotly graph/chart creation functions for MVPF dashboard
"""

import plotly.graph_objs as go
import pandas as pd
from formatting import Colors
from content_loader import ContentManager
from constants import (
    MVPF_THRESHOLD_EXCELLENT,
    MVPF_THRESHOLD_GOOD,
    MVPF_THRESHOLD_FAIR,
    MAX_DESCRIPTION_LENGTH,
    MAX_DESCRIPTION_DISPLAY,
    ZERO
)

# Initialize content manager
content = ContentManager()


def build_benchmark_chart(current_mvpf, benchmarks):
    """Build the benchmark comparison bar chart (vertical orientation)."""
    # Prepare data: current MVPF first, then benchmarks
    names = ["Current MVPF for CCJ"]
    values = [current_mvpf]
    colors_list = [Colors.NAVY_MEDIUM]  # Blue for current

    for benchmark in benchmarks:
        bench_mvpf = float(benchmark["mvpf_value"])
        description = benchmark["Description"]
        # Shorten long names for chart labels
        short_name = description if len(description) <= MAX_DESCRIPTION_LENGTH else description[:MAX_DESCRIPTION_DISPLAY] + "..."
        names.append(short_name)
        values.append(bench_mvpf)
        # Color based on positive/negative
        colors_list.append(Colors.SUCCESS_GREEN if bench_mvpf >= ZERO else Colors.ERROR_RED)

    # Create horizontal bar chart (vertical orientation)
    fig = go.Figure(
        data=[
            go.Bar(
                y=names,
                x=values,
                orientation="h",
                marker_color=colors_list,
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
        bargap=0.2,  # 2025 best practice: elegant spacing for horizontal bars
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


def build_numerator_chart(result):
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
        bargap=0.4,  # 2025 best practice: elegant spacing for 2 vertical bars
    )

    # Update bar width for more elegant appearance
    fig.update_traces(width=0.5)

    return fig


def build_denominator_chart(result):
    """Build the denominator chart showing Government Cost vs Numerator (Detainee + Society)."""
    gov_val = result["govt_cost"]
    det_val = result["detainee_values"]
    soc_val = result["society_values"]
    numerator = det_val + soc_val

    # Determine colors based on values (negative = red, positive = green/blue)
    numerator_color = "#10b981" if numerator >= ZERO else "#ef4444"

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
        bargap=0.4,  # 2025 best practice: elegant spacing for 2 vertical bars
    )

    # Update bar width for more elegant appearance
    fig.update_traces(width=0.5)

    return fig


def build_parameter_comparison_chart(
    scenario,
    base_det_p1,
    base_det_p2,
    base_soc_p1,
    base_soc_p2,
    detainee_baseline=None,
    crime_effect=0,
    fel_rate_param=None,
    n_detainees_param=None,
    n_society_param=None,
    los_days_param=None,
    calculate_mvpf_func=None
):
    """Build the parameter comparison chart showing MVPF sensitivity to parameter changes.

    Args:
        scenario: Scenario name
        base_det_p1: Base detainee parameter 1 (felony rate)
        base_det_p2: Base detainee parameter 2 (population multiplier)
        base_soc_p1: Base society parameter 1 (community size)
        base_soc_p2: Base society parameter 2 (length of stay)
        detainee_baseline: Baseline detainee population
        crime_effect: Crime effect multiplier
        fel_rate_param: ParameterDefinition for felony rate
        n_detainees_param: ParameterDefinition for detainee population
        n_society_param: ParameterDefinition for society multiplier
        los_days_param: ParameterDefinition for length of stay
        calculate_mvpf_func: Function to calculate MVPF (should be helpers.calculate_mvpf_for_dashboard)
    """
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
        result = calculate_mvpf_func(
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
        result = calculate_mvpf_func(
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
        result = calculate_mvpf_func(
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
        result = calculate_mvpf_func(
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

    chart_colors = [
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
                marker_color=chart_colors[i],
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
        bargap=0.15,  # 2025 best practice: tighter spacing for grouped bars
        bargroupgap=0.1,  # Space between groups
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


def build_scenario_comparison_chart(
    det_p1, det_p2, soc_p1, soc_p2, detainee_baseline=None, crime_effect=0, calculate_mvpf_func=None
):
    """Build the scenario comparison chart showing MVPF for all scenarios on y-axis.

    Args:
        det_p1: Detainee parameter 1 (felony rate)
        det_p2: Detainee parameter 2 (population multiplier)
        soc_p1: Society parameter 1 (community size)
        soc_p2: Society parameter 2 (length of stay)
        detainee_baseline: Baseline detainee population
        crime_effect: Crime effect multiplier
        calculate_mvpf_func: Function to calculate MVPF (should be helpers.calculate_mvpf_for_dashboard)
    """
    scenarios = ["baseline", "most conservative", "least conservative"]

    scenario_labels = {
        "baseline": "Baseline",
        "most conservative": "Lower bound",
        "least conservative": "Upper bound",
    }

    # Calculate MVPF for each scenario
    mvpf_values = []
    for scenario in scenarios:
        result = calculate_mvpf_func(
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
    chart_colors = []
    for mvpf in mvpf_values:
        if mvpf >= MVPF_THRESHOLD_EXCELLENT:
            chart_colors.append(Colors.SUCCESS_GREEN)  # Green - Excellent
        elif mvpf >= MVPF_THRESHOLD_GOOD:
            chart_colors.append(Colors.NAVY_MEDIUM)  # Blue - Good
        elif mvpf >= MVPF_THRESHOLD_FAIR:
            chart_colors.append("#f59e0b")  # Yellow - Fair
        else:
            chart_colors.append(Colors.ERROR_RED)  # Red - Poor

    # Create horizontal bar chart with scenarios on y-axis
    labels = [scenario_labels[s] for s in scenarios]

    fig = go.Figure(
        data=[
            go.Bar(
                y=labels,
                x=mvpf_values,
                marker_color=chart_colors,
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


def build_sensitivity_analysis_chart(
    parameter_name, param_values, base_det_p1, base_det_p2, base_soc_p1, base_soc_p2, crime_effect=0, calculate_mvpf_func=None
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
    calculate_mvpf_func: Function to calculate MVPF (should be helpers.calculate_mvpf_for_dashboard)

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
                result = calculate_mvpf_func(
                    scenario,
                    value,
                    base_det_p2,
                    base_soc_p1,
                    base_soc_p2,
                    crime_effect=crime_effect,
                )
            elif parameter_name == "Detainee Population":
                result = calculate_mvpf_func(
                    scenario,
                    base_det_p1,
                    value,
                    base_soc_p1,
                    base_soc_p2,
                    crime_effect=crime_effect,
                )
            elif parameter_name == "Community Size":
                result = calculate_mvpf_func(
                    scenario,
                    base_det_p1,
                    base_det_p2,
                    value,
                    base_soc_p2,
                    crime_effect=crime_effect,
                )
            elif parameter_name == "Length of Stay":
                result = calculate_mvpf_func(
                    scenario,
                    base_det_p1,
                    base_det_p2,
                    base_soc_p1,
                    value,
                    crime_effect=crime_effect,
                )
            elif parameter_name == "Crime Effect":
                result = calculate_mvpf_func(
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


def build_subcomponents_chart(result):
    """Build the subcomponents horizontal bar chart with variable names on y-axis."""
    # Collect all subcomponents with their variable names and values
    subcomponents = []
    chart_colors = []

    # Detainee subcomponents (blue)
    for var_name, value in result.get("detainee_breakdown", {}).items():
        subcomponents.append({"name": var_name, "value": value, "category": "Detainee"})
        chart_colors.append(Colors.NAVY_MEDIUM)

    # Society subcomponents (green)
    for var_name, value in result.get("society_breakdown", {}).items():
        subcomponents.append({"name": var_name, "value": value, "category": "Society"})
        chart_colors.append("#10b981")

    # Government subcomponents (red)
    for var_name, value in result.get("govt_breakdown", {}).items():
        subcomponents.append({"name": var_name, "value": value, "category": "Govt"})
        chart_colors.append("#ef4444")

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
                marker_color=chart_colors,
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
    fig.add_vline(x=0, line_dash="solid", line_color=Colors.GRAY_500, line_width=1)

    return fig
