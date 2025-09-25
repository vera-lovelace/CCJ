import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_daq as daq

# Add Dataframe
mvpf_data = pd.read_csv('CCJ_MVPF.csv')

app = Dash(__name__)

app.layout = html.Div([
    html.H1('MVPF Calculator',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    html.Div([
        "Select scenario: ",
        dcc.Dropdown(id='alternative', options=[
            {'label': 'New York City', 'value': 'NYC'},
            {'label': 'Montréal', 'value': 'MTL'},
            {'label': 'San Francisco', 'value': 'SF'}
        ], value='NYC')
    ], style={'textAlign': 'left', 'fontSize': 28, 'border-style': 'outset'}),
    html.Div([
        "Output Year: ",
        dcc.Input(id='valuation-year', value='2025', type='number', style={'height': '50px', 'font-size': 35})
    ], style={'font-size': 40}),
    html.Div([
        "Component 1 selector: ",
        dcc.Input(id='input-year', value='2010', type='number', style={'height': '50px', 'font-size': 35})
    ], style={'font-size': 40}),
    daq.BooleanSwitch(id='switch-1', on=False, label="Option 1", labelPosition="top"),
    daq.BooleanSwitch(id='switch-2', on=False, label="Option 2", labelPosition="top"),
    daq.BooleanSwitch(id='switch-3', on=False, label="Option 3", labelPosition="top"),
    html.Div(id='Component 2'),
    html.Br(),
    html.Br(),
    html.Div(id='bar-plot'),
    html.Div(id='MVPF'),
])


# callbacks (update as needed)
import subprocess

@app.callback(
    Output('bar-plot', 'children'),
    Output('MVPF', 'children'),
    Input('switch-1', 'on'),
    Input('switch-2', 'on'),
    Input('switch-3', 'on'),
    Input('alternative', 'value'),
    Input('input-year', 'value'),
)
def update_output(switch1, switch2, switch3, scenario, year):
    # create a bar plot from mvpf_data
    fig = px.bar(mvpf_data, x=mvpf_data.columns[0], y=mvpf_data.columns[1])
    bar_plot = dcc.Graph(figure=fig)

    # MVPF calculation: load R script calculator if any switch is on
    if switch1 or switch2 or switch3:
        try:
            result = subprocess.run(
                ['Rscript', 'your_script.R', str(scenario), str(year), str(switch1), str(switch2), str(switch3)],
                capture_output=True, text=True, check=True
            )
            mvpf_text = f'MVPF (R): {result.stdout.strip()}'
        except Exception as e:
            mvpf_text = f'Error running R script: {e}'
    else:
        mvpf_text = f'MVPF (Python): {year}'

    comp2 = f'Switch states: Option 1: {switch1}, Option 2: {switch2}, Option 3: {switch3}, scenario: {scenario}'
    return bar_plot, mvpf_text, comp2

if __name__ == '__main__':
    app.run_server(debug=True)




