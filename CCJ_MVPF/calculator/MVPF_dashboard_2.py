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

# Style settings for active/inactive buttons (for visual feedback)
BUTTON_STYLE = {'marginRight': '10px', 'padding': '10px 15px', 'borderRadius': '8px', 'border': '1px solid #ccc', 'cursor': 'pointer'}
ACTIVE_STYLE = {**BUTTON_STYLE, 'backgroundColor': '#007bff', 'color': 'white', 'fontWeight': 'bold', 'border': '1px solid #007bff'}
INACTIVE_STYLE = {**BUTTON_STYLE, 'backgroundColor': '#f0f0f0', 'color': '#333'}


app.layout = html.Div([
    html.H1('MVPF Calculator',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # 1. Alternative Selection (Dropdown)
    html.Div([
        html.Label("Select MVPF Alternative:", style={'marginRight': '20px', 'fontSize': 20}),
        html.Button('Alternative 1', id='btn-alt-1', n_clicks=0, style={'marginRight': '10px'}),
        html.Button('Alternative 2', id='btn-alt-2', n_clicks=0, style={'marginRight': '10px'}),
        html.Button('Alternative 3', id='btn-alt-3', n_clicks=0, style={'marginRight': '10px'}),
        html.Button('Alternative 4', id='btn-alt-4', n_clicks=0, style={'marginRight': '10px'}),
    ], style={'fontSize': 24, 'marginBottom': '20px'}),

    # Hides the selected value, used to feed the main callback
    dcc.Store(id='alternative-store', data=1), # Initialize with Alternative 1

    # 2. Final MVPF Value (mvpf-output)
    html.Div(id='mvpf-output',
             style={'fontSize': 24,
                    'color': 'darkblue',
                    'marginTop': '10px',
                    'marginBottom': '20px'
                    }),

    # 3. Input Variables/Rows (alt-variables)
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


# Callback to update button styles for visual feedback
@app.callback(
    [Output('btn-alt-1', 'style'),
     Output('btn-alt-2', 'style'),
     Output('btn-alt-3', 'style'),
     Output('btn-alt-4', 'style')],
    [Input('alternative-store', 'data')]
)
def update_button_styles(alt_id):
    styles = [INACTIVE_STYLE] * 4
    if alt_id is not None and 1 <= alt_id <= 4:
        styles[alt_id - 1] = ACTIVE_STYLE
    return styles

@app.callback(
    [Output('mvpf-output', 'children'),
     Output('bar-plot', 'children'),
     Output('alt-variables', 'children'),
     Output('alternative-store', 'data')], # Update the store with the newly selected ID
    [Input('btn-alt-1', 'n_clicks'),
     Input('btn-alt-2', 'n_clicks'),
     Input('btn-alt-3', 'n_clicks'),
     Input('btn-alt-4', 'n_clicks')]
)

def update_output(alt_id) :
    ctx = callback_context

    # --- 1. Determine the selected alternative ID (alt_id) ---
    # Check if any input was triggered by a user click
    if not ctx.triggered or ctx.triggered[0]['value'] == 0:
        # Initial load or no actual button click yet (use default from store: 1)
        alt_id = 1
    else:
        # Determine which button triggered the callback
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'btn-alt-1':
            alt_id = 1
        elif button_id == 'btn-alt-2':
            alt_id = 2
        elif button_id == 'btn-alt-3':
            alt_id = 3
        elif button_id == 'btn-alt-4':
            alt_id = 4
        else:
            # Should not happen, but fallback to 1
            alt_id = 1

    # --- 2. Filter data based on selected alt_id ---

    # 1. Filter the pre-calculated MVPF table by the selected Alternative ID
    # Use the 'alternative' column for filtering
    filtered_df = MVPF_table[MVPF_table['alternative'] == alt_id]

    if filtered_df.empty:
        return (
            "Final MVPF: N/A",
            html.Div(f"No data found for Alternative {alt_id}.", style={'color': 'red'}),
            "Alternative Definitions: N/A",
            alt_id  # Return the ID to the store even if data is missing
        )

    # 2. Extract Variables and MVPF Value
    # Get the row definitions for display (assuming alt_definitions is loaded)
    # The mvpf_value is repeated in all rows, so we grab the first one
    mvpf_val = filtered_df['mvpf_value'].iloc[0]
    mvpf_output = f"MVPF (Alternative {alt_id}): ${mvpf_val:,.2f}"

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


    # 3. CREATE BAR PLOT (Switched from go.Figure/go.Waterfall)

    html.Div(id='bar-plot', style={'marginBottom': '30px'}),

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

        # Adjust layout
        fig.update_layout(
            barmode='stack',
            xaxis_title="Population/Cost Group",
            yaxis_title="Value (USD)",
            legend_title="Component",
            plot_bgcolor='white',
            paper_bgcolor='#F9FAFB',
            uniformtext_minsize=8,
            uniformtext_mode='show'
        )
        # Draw a horizontal line at y=0


        bar_plot = dcc.Graph(figure=fig)

    # Return the three required outputs
    return mvpf_output, bar_plot, var_display, alt_id


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





