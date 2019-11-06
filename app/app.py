import logging

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from components import navbar as _navbar
from models import Schelling

logging.basicConfig()
logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

schelling_model = Schelling(10, 10, 0.3, 0.8, 10, 2)
schelling_model.initialize()
logger.debug(
    "number of iteractions: {}".format(schelling_model.n_iterations)
)

logger.debug(
    "current step of iteractions: {}".format(schelling_model.current_iteration)
)
logger.debug("final agents: {}".format(schelling_model.agents))
logger.debug("final grid: {}".format(
    schelling_model.data.get(schelling_model.current_iteration)
))

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']



param_controls = dbc.Form(
    [
        dbc.FormGroup(
            [
                dbc.Label("Grid Width", className="mr-2"),
                dbc.Input(id="model-grid-width", type="number", placeholder="20"),
            ],
            className="mr-4",
        ),
        dbc.FormGroup(
            [
                dbc.Label("Grid Height", className="mr-2"),
                dbc.Input(id="model-grid-height", type="number", placeholder="20"),
            ],
            className="mr-4",
        ),
        dbc.FormGroup(
            [
                dbc.Label("Max Iteractions", className="mr-2"),
                dbc.Input(id="model-grid-max-iter", type="number", placeholder="20"),
            ],
            className="mr-4",
        )
    ],
    inline=True
)



body = dbc.Container(
    [
        dbc.Row([
        dbc.Col(
            html.H1("Schelling's Model", style={'textAlign': "center"}),
            className="col", style={'textAlign': "center"})]
            ),
        dbc.Row([
            dbc.Col(
                [dcc.Slider(
                    id='step-slider',
                    min=0,
                    max=schelling_model.current_iteration,
                    value=schelling_model.current_iteration,
                    marks={i: '{}'.format(i) if i == 1 else str(i)
                        for i in range(schelling_model.current_iteration+1)},
                    step=None
                )]
            )
        ],  style={'textAlign': "center", "marginBottom": "2em", "marginTop": "2em"}
    ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(id='graph-with-slider'),
                    ],
                    md=8,
                ),
                dbc.Col(
                    [
                        html.H2("Parameters"),
                        param_controls,
                        dbc.Button("Calculate", id="model-calculate", color="primary"),
                    ]
                ),
            ], className="row", style={'textAlign': "center"}
        )
    ],
    className="mt-4",
)

hidden_elem = html.P(id="hidden-div", style={"display":"none"})
hidden_elem_calculate = html.P(id="hidden-div-calculate", style={"display":"none"})


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.config.suppress_callback_exceptions = True

app.layout = html.Div([_navbar, body, hidden_elem, hidden_elem_calculate])

@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('step-slider', 'value'),
    Input('model-grid-width', 'value'),
    Input('model-grid-height', 'value'),
    Input('model-grid-max-iter', 'value')])
def update_figure(selected_step, width, height, max_iterations):
    logger.debug(selected_step)
    logger.debug(f"width: {width}, height: {height}")
    if width is None:
        width = 20
    if height is None:
        height = 20
    if max_iterations is None:
        max_iterations = 20
    logger.debug(f"width: {width}, height: {height}; adjusted")
    schelling_model = Schelling(width, height, 0.3, 0.8, max_iterations, 2)
    schelling_model.initialize()
    schelling_model.evolve()
    current_step_data = schelling_model.data.get(selected_step)
    trace = go.Heatmap(
        z=current_step_data, colorscale='Electric',
        colorbar={"title": "ethical group"}, showscale=True
    )
    return {
        "data": [trace],
        "layout": go.Layout(
            width=600, height=600,
            title="Schelling's Model (Current Step: {})".format(selected_step),
            xaxis={"title": "x"},
            yaxis={"title": "y"}
        )
    }

@app.callback(
    Output('hidden-div', 'children'),
    [Input('model-grid-width', 'value'),
    Input('model-grid-height', 'value')])
def update_model(width, height):
    logger.debug(f"width: {width}, height: {height}")
    if width is None:
        width = 20
    if height is None:
        height = 20
    logger.debug(f"width: {width}, height: {height}; adjusted")
    schelling_model = Schelling(width, height, 0.3, 0.8, 10, 2)
    schelling_model.initialize()
    return "hidden"


@app.callback(
    Output('step-slider', 'value'),
    [Input('model-grid-max-iter', 'value')])
def calculate_model(max_iterations):
    if max_iterations is None:
        max_iterations = 10
    return max_iterations



if __name__ == '__main__':
    app.run_server(debug=True)
