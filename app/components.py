import dash_bootstrap_components as dbc

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Statistical Physics", href="https://statisticalphysics.openmetric.org")),
        dbc.DropdownMenu(
            nav=True,
            in_navbar=True,
            label="More",
            children=[
                dbc.DropdownMenuItem("Source Code"),
                dbc.DropdownMenuItem(divider=True)
            ],
        ),
    ],
    brand="Schelling's Model",
    brand_href="#",
    sticky="top",
)