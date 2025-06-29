# app.py
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, use_pages=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server          # Render / gunicorn needs this

navbar = dbc.NavbarSimple(
    brand="Gaza Casualty Tracker",
    children=[
        dbc.NavItem
        (dcc.Link("Overview", href=dash.page_registry["pages.overview"]["path"], className="nav-link")),
        (dcc.Link("Names",    href="/names", className="nav-link")),
        # future pages here …
    ],
    color="dark", dark=True, sticky="top",
)

app.layout = dbc.Container(
    [navbar, dash.page_container], fluid=True, className="p-0"
)

if __name__ == "__main__":
    # runs on http://127.0.0.1:8050/   (Ctrl-C to stop)
    app.run(debug=True)
