import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_daq as daq

# Load the CSV data
mvpf_data = pd.read_csv('Data/CCJ_MVPF.csv')  # Update path if needed

# Define mappings for MVPF alternatives (same logic as R inputs)
alt_definitions = {
    1: {
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
    html.Div([
        html.Label("Select MVPF Alternative:"),
        dcc.Dropdown(
            id='alternative',
            options=[{'label': f'Alternative {i}', 'value': i} for i in alt_definitions],
            value=1
        )
    ], style={'fontSize': 24, 'marginBottom': '20px'}),
    html.Div(id='alt-variables', style={'whiteSpace': 'pre-wrap', 'fontFamily': 'monospace', 'fontSize': 16}),
    html.Div(id='bar-plot'),
    html.Div(id='mvpf-output', style={'fontSize': 24, 'marginTop': '20px', 'color': 'darkgreen'})
    html.Br(),
    html.Br(),
    html.Div(id='bar-plot'),
    html.Div(id='MVPF'),
])

#selector between alternatives,
#then print out the content of the selected rows

# callbacks (update as needed)
import subprocess

@app.callback(
    Output('alt-variables', 'children'),
    Output('bar-plot', 'children'),
    Output('mvpf-output', 'children'),
    Input('alternative', 'value')
    Input('input-year', 'value'),
)
def update_output(switch1, switch2, switch3, scenario, year):
    # Get variable definitions
    alt_vars = alt_definitions.get(alt_id, {})
    used_rows = sum(alt_vars.values(), [])  # Flatten to a single list
    filtered_df = mvpf_data[mvpf_data['name'].isin(used_rows)]

    var_display = "\n".join([
        f"ST_detainee_rows: {alt_vars.get('ST_detainee_rows', [])}",
        f"LT_detainee_rows: {alt_vars.get('LT_detainee_rows', [])}",
        f"ST_society_rows:  {alt_vars.get('ST_society_rows', [])}",
        f"LT_society_rows:  {alt_vars.get('LT_society_rows', [])}",
        f"ST_govt_rows:     {alt_vars.get('ST_govt_rows', [])}",
        f"LT_govt_rows:     {alt_vars.get('LT_govt_rows', [])}"
    ])

    # create a bar plot from mvpf_data
    fig = px.bar(mvpf_data, x=mvpf_data.columns[0], y=mvpf_data.columns[1])
    bar_plot = dcc.Graph(figure=fig)

    # Calculate MVPF (simulated): just sum values (replace with real formula if needed)
    mvpf_value = filtered_df['value'].sum()
    mvpf_text = f"Simulated MVPF value: {mvpf_value:.2f}"

    return var_display, bar_plot, mvpf_text


# Run app
if __name__ == '__main__':
    app.run_server(debug=True)



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





