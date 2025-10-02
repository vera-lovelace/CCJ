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

    # 1. Alternative Selection (Dropdown)
    html.Div([
        html.Label("Select MVPF Alternative:"),
        dcc.Dropdown(
            id='alternative',
            options=[
                {'label': f'Alternative {i}', 'value': i}
                for i in sorted(MVPF_table['alternative'].unique())
            ],  # Your options list generation goes here
            value=1
        )
    ], style={'fontSize': 24, 'marginBottom': '20px'}),

    # 2. Final MVPF Value (mvpf-output)
    html.Div(id='mvpf-output',
             style={'fontSize': 24,
                    'color': 'darkblue',
                    'marginTop': '10px',
                    'marginBottom': '20px'
                    }),

    # 3. Waterfall Plot (bar-plot)
    html.Div(id='bar-plot', style={'marginBottom': '30px'}),

    # 4. Input Variables/Rows (alt-variables)
    html.Div(id='alt-variables',
             style={'whiteSpace': 'pre-wrap',
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': 18,
                    'fontWeight': 'bold',
                    'color': 'darkblue',
                    'marginTop': '10px',
                    'marginBottom': '20px',
                    'borderTop': '1px solid #ccc',
                    'paddingTop': '15px',
                    })
])

#+ selector between alternatives,
#then print out the content of the selected rows



@app.callback(
    [Output('mvpf-output', 'children'),   # 1. Final Value (First Output)
     Output('bar-plot', 'children'),      # 2. Plot
     Output('alt-variables', 'children')], # 3. Input Variables (Last Output)
    [Input('alternative', 'value')]
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
    mvpf_output = f"MVPF: {mvpf_val:,.2f} USD"

    # 3. CREATE BAR PLOT (Switched from go.Figure/go.Waterfall)

    if filtered_df.empty:
        # If no data is available after filtering, return a placeholder
        bar_plot = html.Div("No data available for the plot.", style={'color': 'orange'})
    else:
        # Use Plotly Express Bar for component visualization
        fig = px.bar(
            filtered_df,
            x='levels',  # Group bars by the main category (Detainee, Society, Gov)
            y='value',  # The amount for each component
            color='components',  # Use the detailed component name for stacking/coloring
            text_auto=True,
            title=f"MVPF Component Breakdown (Alternative {alt_id})",
            labels={
                'levels': 'Population/Cost Group',
                'value': 'Value (2025$)'
            },
            # Use a facet to separate positive/negative impacts if desired, or just stack:
            # text='value' # Optional: Display value on top of bars
        )
        # 2. Update traces for text formatting
        fig.update_traces(
            texttemplate='%{y:$,.0f}',
            textposition='outside'
        )

        # Adjust layout for better readability
        fig.update_layout(
            barmode='stack',
            xaxis_title="Population/Cost Group",
            yaxis_title="Value (2025$)",
            uniformtext_minsize=8,  # Helps ensure text labels fit
            uniformtext_mode='show'
        )

        # Draw a horizontal line at y=0


        bar_plot = dcc.Graph(figure=fig)

    # Return the three required outputs
    return mvpf_output, bar_plot, var_display


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





