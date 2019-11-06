import copy
import logging

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from components import navbar as _navbar
from components import alert as _alert
from models import Schelling

logging.basicConfig()
logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

# This ugly global varible trick
# is to overcome some difficulties
# in dash
PRE_DEFINED_MAX_ITERATIONS = 30
PRE_DEFINED_WIDTH = 20
PRE_DEFINED_HEIGHT = 20
PRE_DEFINED_EMPTY_HOUSE_RATE = 0.2
PRE_DEFINED_THRESHOLD = 0.6
PRE_DEFINED_ETHICAL = 2

# Inithialize the model
SCHELLING_MODEL = Schelling(
    PRE_DEFINED_WIDTH, PRE_DEFINED_HEIGHT, PRE_DEFINED_EMPTY_HOUSE_RATE,
    PRE_DEFINED_THRESHOLD, PRE_DEFINED_MAX_ITERATIONS, PRE_DEFINED_ETHICAL
    )

SCHELLING_MODEL.initialize()
CURRENT_ITERATION = SCHELLING_MODEL.current_iteration
MAX_ITERATIONS = SCHELLING_MODEL.n_iterations
CURRENT_DATA = SCHELLING_MODEL.data.get(CURRENT_ITERATION)

logger.debug(
    "number of iteractions: {}".format(SCHELLING_MODEL.n_iterations)
)

logger.debug(
    "current step of iteractions: {}".format(SCHELLING_MODEL.current_iteration)
)
logger.debug("final agents: {}".format(SCHELLING_MODEL.agents))
logger.debug("final grid: {}".format(
    SCHELLING_MODEL.data.get(SCHELLING_MODEL.current_iteration)
))

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

SLIDER_MAX = CURRENT_ITERATION+1

param_controls = dbc.Form(
    [
        dbc.FormGroup(
            [
                dbc.Label("Grid Width", className="mr-2"),
                dbc.Input(
                    id="model-grid-width", type="number",
                    min="2", max="100", step="1",
                    placeholder=f"{PRE_DEFINED_WIDTH}",
                    className="mr-1"
                    ),
                dbc.Label("Grid Height", className="mr-2"),
                dbc.Input(
                    id="model-grid-height", type="number",
                    min="2", max="100", step="1",
                    placeholder=f"{PRE_DEFINED_HEIGHT}"
                    ),
            ],
            className="mr-4",
        ),
        html.Br(),
        html.Br(),
        dbc.FormGroup(
            [
                dbc.Label("Similarity Threshold", className="mr-2"),
                dbc.Input(
                    id="model-sim-threshold", type="number",
                    min="0", max="1", step="0.1",
                    placeholder=f"{PRE_DEFINED_THRESHOLD}"
                    ),
            ],
            className="mr-4",
        ),
        html.Br(),
        html.Br()
    ],
    inline=True
)



body = dbc.Container(
    [
        dbc.Row([
        dbc.Col(
            html.H1("Schelling's Segregation Model", style={'textAlign': "center"}),
            className="col", style={'textAlign': "center"})]
            ),
        dbc.Row([
            dbc.Col(
                _alert
            )
        ]),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id='graph-with-slider',
                            config={
                                'displayModeBar': False
                            }),
                    ],
                    md=8,
                ),
                dbc.Col(
                    [
                        dcc.Graph(
                            id="graph-changes",
                            config={
                                'displayModeBar': False
                            }
                        ),
                        html.P("Parameters"),
                        param_controls,
                        dbc.Button("Evolve One Step", id="model-calculate", color="primary"),
                    ]
                ),
            ], className="row", style={'textAlign': "center"}
        ),
        dbc.Row([
            dbc.Col(
                [dcc.Slider(
                    id='step-slider',
                    min=0,
                    max=SLIDER_MAX,
                    value=SLIDER_MAX,
                    marks={i: '{}'.format(i) if i == 1 else str(i)
                        for i in range(SLIDER_MAX+1)},
                    step=None
                )]
            )
        ],  style={'textAlign': "center", "marginBottom": "2em", "marginTop": "2em"}
        ),
    ],
    className="mt-4",
)

hidden_elem = html.P(id="hidden-div", style={"display":"none"})
hidden_elem_calculate = html.P(id="hidden-div-calculate", style={"display":"none"})


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.config.suppress_callback_exceptions = True

app.layout = html.Div([_navbar, body, hidden_elem, hidden_elem_calculate])
app.title = "Schelling's Segregation Model"


@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('step-slider', 'value')])
def update_figure(selected_step):
    logger.debug(selected_step)

    global SCHELLING_MODEL
    global CURRENT_DATA
    global CURRENT_ITERATION

    CURRENT_DATA = SCHELLING_MODEL.data.get(selected_step)
    trace = go.Heatmap(
        z=CURRENT_DATA,
        colorscale=[
            [0, "rgb(0,0,0)"],
            [0.5, "rgb(49,54,149)"],
            [1, "rgb(244,109,67)"]
            ],
        colorbar={
            "title": "ethical group",
            "tickvals": [0,1,2],
            "ticktext": [0,1,2]
            }, showscale=False
    )
    return {
        "data": [trace],
        "layout": go.Layout(
            width=650, height=650,
            title="Schelling's Model (Current Step: {})".format(selected_step),
            xaxis={"title": "x"},
            yaxis={"title": "y"}
        )
    }

@app.callback(
    Output('hidden-div', 'children'),
    [Input('model-grid-width', 'value'),
    Input('model-grid-height', 'value'),
    Input('model-sim-threshold', 'value')])
def update_model(width, height, sim_th):
    logger.debug(f"width: {width}, height: {height}")
    if width is None:
        width = PRE_DEFINED_WIDTH
    if height is None:
        height = PRE_DEFINED_HEIGHT
    if sim_th is None:
        sim_th = PRE_DEFINED_THRESHOLD

    logger.debug(f"width: {width}, height: {height}; adjusted")

    global SCHELLING_MODEL
    global CURRENT_DATA
    global CURRENT_ITERATION

    SCHELLING_MODEL = Schelling(
        width, height, PRE_DEFINED_EMPTY_HOUSE_RATE,
        sim_th, PRE_DEFINED_MAX_ITERATIONS, PRE_DEFINED_ETHICAL
        )
    SCHELLING_MODEL.initialize()
    CURRENT_ITERATION = SCHELLING_MODEL.current_iteration
    CURRENT_DATA = SCHELLING_MODEL.data.get(CURRENT_ITERATION)

    return "hidden"

@app.callback(
    Output('model-calculate', 'children'),
    [Input('model-calculate', 'n_clicks')])
def update_button(n):
    if n is None:
        n = 0
    if n == 0:
        return "Initialize"
    else:
        return "Next Iteraction"

@app.callback(
    Output('hidden-div-calculate', 'children'),
    [Input('model-calculate', 'n_clicks')])
def update_model(n):
    logger.debug(f"{n} clicks")
    if n is None:
        max_iter = 0

    global SCHELLING_MODEL
    global CURRENT_DATA
    global CURRENT_ITERATION

    SCHELLING_MODEL_COPY = copy.deepcopy(SCHELLING_MODEL)
    SCHELLING_MODEL_COPY.evove_one()
    SCHELLING_MODEL = copy.deepcopy(SCHELLING_MODEL_COPY)

    logger.debug("evolved one step")
    CURRENT_ITERATION = SCHELLING_MODEL.current_iteration
    logger.debug("current iteraction: {}".format(CURRENT_ITERATION))
    CURRENT_DATA = SCHELLING_MODEL.data.get(CURRENT_ITERATION)
    logger.debug("current data: {}".format(CURRENT_DATA))
    return "hidden"

@app.callback(
    Output('step-slider', 'value'),
    [Input('model-calculate', 'n_clicks')])
def update_step_slider_value(n):
    if n is None:
        n = 0

    global SCHELLING_MODEL
    global CURRENT_DATA
    global CURRENT_ITERATION

    logger.debug(
        "update slider value 0: current_iteraction: {}".format(CURRENT_ITERATION)
        )
    CURRENT_ITERATION = SCHELLING_MODEL.current_iteration
    logger.debug(
        "update slider value 1: current_iteraction: {}".format(CURRENT_ITERATION)
        )
    return CURRENT_ITERATION

@app.callback(
    Output('step-slider', 'max'),
    [Input('model-calculate', 'n_clicks')])
def update_step_slider_max(n):
    if n is None:
        n = 0

    global SCHELLING_MODEL
    global CURRENT_DATA
    global CURRENT_ITERATION

    return CURRENT_ITERATION

@app.callback(
    Output('step-slider', 'marks'),
    [Input('model-calculate', 'n_clicks')])
def update_step_slider_marks(n):
    if n is None:
        n = 0

    global SCHELLING_MODEL
    global CURRENT_DATA
    global CURRENT_ITERATION

    return {
        i: '{}'.format(i) if i == 1 else str(i)
                        for i in range(CURRENT_ITERATION+1)
                        }

@app.callback(
    Output('graph-changes', 'figure'),
    [Input('model-calculate', 'n_clicks')])
def update_graph_changes(n):
    if n is None:
        n = 0

    global SCHELLING_MODEL
    global CURRENT_DATA
    global CURRENT_ITERATION

    return {
        "data": [
            go.Scatter(
                x=[idx for idx, _ in enumerate(SCHELLING_MODEL.changes)],
                y=SCHELLING_MODEL.changes,
                mode='lines',
                marker={'size': 10, "opacity": 0.6, "line": {'width': 0.5}},
            )
        ],
        "layout": go.Layout(
            height=300,
            title="Number of Changes at Each Iteraction",
            colorway=['#fdae61', '#abd9e9', '#2c7bb6'],
            yaxis={"title": "Number of Changes"},
            xaxis={"title": "Iteractions"})
        }



if __name__ == '__main__':
    app.run_server(debug=False)
