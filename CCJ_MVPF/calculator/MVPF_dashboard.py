#!pip install pandas

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import dash_daq as daq

# Load the CSV data

try:
    MVPF_table= pd.read_csv('CCJ_MVPF.csv')  # Update path if needed
except FileNotFoundError:
    raise FileNotFoundError("CSV file not found. Please ensure 'Data/CCJ_MVPF.csv' exists.")

# Define mappings for MVPF alternatives (same logic as R inputs)
alt_definitions = {
    1: {\
        "ST_detainee_rows": ["wtp_freedom", "lost_wages"],
        "LT_detainee_rows": ["income_reduced"],
        "ST_society_rows": ["crime_prev_measure"],
        "LT_society_rows": ["wrongful_death_wtp_life"],
        "ST_govt_rows": ["ccj_funding_2018"],
        "LT_govt_rows": ["inc_conv_len"]
    },
    2: {
        "ST_detainee_rows": ["wtp_rhv"],
        "LT_detainee_rows": ["income_reduced"],
        "ST_society_rows": ["crime_prev_measure"],
        "LT_society_rows": ["wrongful_death_wtp_life"],
        "ST_govt_rows": ["ccj_funding_2018"],
        "LT_govt_rows": ["inc_conv_len"]
    },
    3: {
        "ST_detainee_rows": ["wtp_freedom", "lost_wages"],
        "LT_detainee_rows": ["income_reduced"],
        "ST_society_rows": ["crime_prev_measure"],
        "LT_society_rows": ["wrongful_death_wtp_life"],
        "ST_govt_rows": ["mc_jail_day", "postrel_health_spike"],
        "LT_govt_rows": ["inc_conv_len"]
    },
    4: {
        "ST_detainee_rows": ["wtp_freedom", "lost_wages"],
        "LT_detainee_rows": ["income_reduced"],
        "ST_society_rows": ["crime_prev_measure"],
        "LT_society_rows": ["wrongful_death_wtp_life", "haven_cost_of_crime"],
        "ST_govt_rows": ["ccj_funding_2018"],
        "LT_govt_rows": ["inc_conv_len"]
    }
}

app = Dash(__name__)

app.layout = html.Div([
    html.H1('MVPF Calculator',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # Dropdown Selector (Full Width at the Very Top)
    html.Div([
        html.Label("Select MVPF Alternative:"),
        dcc.Dropdown(
            id='alternative',
            options=[ {'label': f'Alternative {i}', 'value': i}
                for i in sorted(MVPF_table['alternative'].unique())
            ],  # Your options list
            value=1
        )
    ], style={'fontSize': 24, 'marginBottom': '20px'}),

    # --- START TOP ROW: Side-by-Side (Waterall & Final Value) ---
    html.Div(style={'display': 'flex', 'flexDirection': 'row', 'gap': '20px', 'marginBottom': '20px'}, children=[

        # COLUMN 1: Waterfall Chart (Takes about 75-80% of the width)
        html.Div(id='bar-plot', style={'flex': '3'}),  # flex: 3 means it takes 3 parts of 4 total

        # COLUMN 2: Final MVPF Value (Takes about 20-25% of the width)
        html.Div(id='mvpf-output',
                 style={'flex': '1',  # flex: 1 means it takes 1 part of 4 total
                        'fontSize': 24,
                        'fontWeight': 'bold',
                        'color': 'darkgreen',
                        'textAlign': 'center',
                        'paddingTop': '50px',  # Vertically center the text a bit

                        }),
    ]),
    # --- END TOP ROW ---

    # Input Variables/Rows (Full Width at the Bottom)
    html.Div(id='alt-variables',
             style={'whiteSpace': 'pre-wrap',
                    'fontFamily': 'monospace',
                    'fontSize': 16,
                    'borderTop': '1px solid #ccc',
                    'paddingTop': '15px'
                    })
])

#+ selector between alternatives,
#then print out the content of the selected rows



@app.callback(
    [
     Output('bar-plot', 'children'),
     Output('mvpf-output', 'children'),
     Output('alt-variables', 'children'),
     ],
    [Input('alternative', 'value'),
     ]
)


def update_output(alt_id):
    # 1. Filter the pre-calculated MVPF table by the selected Alternative ID
    # Use the 'alternative' column for filtering
    filtered_df = MVPF_table[MVPF_table['alternative'] == alt_id]

    if filtered_df.empty:
        return (
            f"Alternative {alt_id} definitions:",
            html.Div("No data found for this alternative in the MVPF_table.", style={'color': 'red'}),
            "Final MVPF: N/A"
        )

    # 2. Extract Variables and MVPF Value
    # Get the row definitions for display (assuming alt_definitions is loaded)
    alt_vars = alt_definitions.get(alt_id, {})

    var_display = "\n".join([
        f"--- Alternative {alt_id} Component Rows ---",
        f"ST_detainee_rows: {alt_vars.get('ST_detainee_rows', ['N/A'])}",
        f"LT_detainee_rows: {alt_vars.get('LT_detainee_rows', ['N/A'])}",
        f"ST_society_rows:  {alt_vars.get('ST_society_rows', ['N/A'])}",
        f"LT_society_rows:  {alt_vars.get('LT_society_rows', ['N/A'])}",
        f"ST_govt_rows:     {alt_vars.get('ST_govt_rows', ['N/A'])}",
        f"LT_govt_rows:     {alt_vars.get('LT_govt_rows', ['N/A'])}"
    ])

    # The mvpf_value is repeated in all rows, so we grab the first one
    mvpf_val = filtered_df['mvpf_value'].iloc[0]
    mvpf_output = f"Final MVPF for Alternative {alt_id}: **{mvpf_val:,.2f}**"

    # 3. CREATE WATERFALL CHART

    # --- Data Preparation for Waterfall ---
    final_total = filtered_df['value'].sum()

    # --- Create Plotly Waterfall Figure ---
    fig = go.Figure(go.Waterfall(
        # X-axis labels: The specific components (e.g., det_values_lt)
        x=filtered_df['components'],
        # All bars represent a change from the previous step (relative)
        measure=["relative"] * len(filtered_df),
        # Y-axis values: The dollar amount
        y=filtered_df['value'],

        # Define colors for positive/negative change
        increasing={"marker": {"color": "green"}},
        decreasing={"marker": {"color": "red"}},

        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))

    # Add the final cumulative bar (TOTAL)
    fig.add_trace(go.Waterfall(
        x=['TOTAL (Cumulative)'],
        measure=['total'],
        y=[final_total],
        name='TOTAL (Cumulative)',
        connector={"line": {"color": "rgb(63, 63, 63)"}}
    ))

    fig.update_layout(
        title=f"MVPF Component Breakdown (Alternative {alt_id})",
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_tickangle=-45,
        yaxis_title="Value (2025$)"
    )

    bar_plot = dcc.Graph(figure=fig)

    # Return the three required outputs
    return var_display, bar_plot, mvpf_output


"Simulated MVPF value: {mvpf_value:.2f}"


# Run app
if __name__ == '__main__':
    app.run(debug=True)

    # MVPF calculation: load R script calculator if any switch is on
    #if switch1 or switch2 or switch3:
     #   try:
      #      result = subprocess.run(
       #         ['Rscript', 'your_script.R', str(scenario), str(year), str(switch1), str(switch2), str(switch3)],
        #        capture_output=True, text=True, check=True
         #   )
          #  mvpf_text = f'MVPF (R): {result.stdout.strip()}'
       # except Exception as e:

        #    mvpf_text = f'Error running R script: {e}'
   # else:
    #    mvpf_text = f'MVPF (Python): {year}'

    #comp2 = f'Switch states: Option 1: {switch1}, Option 2: {switch2}, Option 3: {switch3}, scenario: {scenario}'
    #return bar_plot, mvpf_text, comp2





