import dash_bootstrap_components as dbc
import dash_html_components as html

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("About Schelling's Model", href="https://ytliu0.github.io/schelling/")),
        dbc.DropdownMenu(
            nav=True,
            in_navbar=True,
            label="More",
            children=[
                dbc.DropdownMenuItem(
                    dbc.NavLink("Source Code", href="https://github.com/emptymalei/schelling-model")
                ),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem(
                    dbc.NavLink("Statistical Physics", href="https://statisticalphysics.openmetric.org")
                )
            ],
        ),
    ],
    brand="Schelling's Model",
    brand_href="#",
    sticky="top",
)

alert = dbc.Alert(
    [
        html.H4("", className="info-heading"),
        html.P(
            "The heatmap shows how each ethical group is located on the 2D grid of the available houses. "
            "The black pixels, blue pixels and red pixels represent empty houses, houses occupied by ethical group 1, and houses occupied by ethical group 2, respectively."
        ),
        html.Hr(),
        html.P(
            "Type in your desired parameters and press the button to initialize and calculate. Each click of the button only calculates one step of the model. (I made it this way because I am running this on a potato server.) ",
            className="mb-0",
        ),
        html.P(
            "The calculation history can be reviewed by clicking on the slider at the bottom of the page.",
            className="mb-0",
        ),
    ], color="info"
)
