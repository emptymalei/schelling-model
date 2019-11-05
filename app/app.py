import logging

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from models import Schelling

logging.basicConfig()
logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

schelling_model = Schelling(50, 50, 0.3, 0.8, 100, 2)
schelling_model.initialize()
logger.debug(
    "number of iteractions: {}".format(schelling_model.n_iterations)
)
schelling_model.evolve()
logger.debug(
    "current step of iteractions: {}".format(schelling_model.current_iteration)
)
logger.debug("final agents: {}".format(schelling_model.agents))
logger.debug("final grid: {}".format(
    schelling_model.data.get(schelling_model.current_iteration)
    ))

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Graph(id='graph-with-slider'),
    dcc.Slider(
        id='step-slider',
        min=0,
        max=schelling_model.current_iteration,
        value=schelling_model.current_iteration,
        step=None
    )
])


@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('step-slider', 'value')])
def update_figure(selected_step):
    current_step_data = schelling_model.data.get(selected_step)
    trace = go.Heatmap(
        z=current_step_data, colorscale='Electric',
        colorbar={"title": "ethical group"}, showscale=True
        )
    return {
        "data": [trace],
        "layout": go.Layout(
            width=800, height=750,
            title="Schelling's Model (step: {})".format(selected_step),
            xaxis={"title": "x"},
            yaxis={"title": "y"}
            )
        }



if __name__ == '__main__':
    app.run_server(debug=True)
