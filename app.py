# app.py
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, use_pages=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server          # Render / gunicorn needs this


def make_footer():
    return html.Footer(
        dbc.Container([
            html.Div("Made with 💚 by Ahmad Hamed", className="text-center"),
            html.Div(
                "Data source: Tech For Palestine Collective",
                className="text-center text-muted",
                style={"fontSize": "0.8rem"},
            ),
        ]),
        style={
            "padding": "20px 0",
            "marginTop": "30px",
            "backgroundColor": "#212529",   # same as Bootstrap “dark”
            "color": "#ffffff",             # white text
            "borderTop": "1px solid #343a40"
        },
    )


navbar = dbc.NavbarSimple(
    brand=(dcc.Link("Gaza Casualty Tracker",href=dash.page_registry["pages.overview"]["path"], className="nav-link", style={"color": "#ffffff"})),
    children=[
        dbc.NavItem
        (dcc.Link("Overview", href=dash.page_registry["pages.overview"]["path"], className="nav-link", style={"color": "#ffffff"})),
        (dcc.Link("Names", href="/names", className="nav-link", style={"color": "#ffffff"})),
        # future pages here …
    ],
    color="dark", dark=True, sticky="top",
)


app.layout = dbc.Container(
    [navbar, dash.page_container, make_footer()], fluid=True, className="p-0"
)

if __name__ == "__main__":
    # runs on http://127.0.0.1:8050/   (Ctrl-C to stop)
    app.run(debug=True)
