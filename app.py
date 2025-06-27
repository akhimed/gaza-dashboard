# app.py
import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
from fetch_data import get_data
from dash.dependencies import Input, Output 
df = get_data()
WINDOW = 7    
import plotly.graph_objects as go
import io 
# 1️⃣  Build the empty placeholder figure
empty_fig = go.Figure()
empty_fig.update_layout(
    title="Loading...",
    xaxis_title="Date",
    yaxis_title="Value",
    plot_bgcolor="white"
)
empty_fig.add_annotation(
    text="Loading data...",
    xref="paper", yref="paper",
    showarrow=False,
    font=dict(size=20),
    x=0.5, y=0.5, align="center"
)

# --- Dash boilerplate ---
app = dash.Dash(__name__)          # initialize the app

# expose Flask server for WSGI (Render / gunicorn)
server = app.server

latest = df.iloc[-1]
prev   = df.iloc[-(WINDOW + 1)]    # roughly 7 days earlier


# 7-day deltas
delta_killed  = latest["killed_cum"]          - prev["killed_cum"]
delta_injured = latest["injured_cum"]         - prev["injured_cum"]
delta_child   = latest["ext_killed_children_cum"] - prev["ext_killed_children_cum"]
delta_women   = latest["ext_killed_women_cum"]    - prev["ext_killed_women_cum"]


KPI_VALUES = {
    "Total Killed":    int(latest["killed_cum"]),
    "Total Injured":   int(latest["injured_cum"]),
    "Children Killed": int(latest["ext_killed_children_cum"]),
    "Women Killed":    int(latest["ext_killed_women_cum"]),
}

KPI_DELTA_DATA = [
    ("Total Killed",    int(latest["killed_cum"]),          delta_killed),
    ("Total Injured",   int(latest["injured_cum"]),         delta_injured),
    ("Children Killed", int(latest["ext_killed_children_cum"]), delta_child),
    ("Women Killed",    int(latest["ext_killed_women_cum"]),    delta_women),
]

def format_delta(value):
    if value > 0:
        return "▲", "#dc2626", abs(int(value))   # red - up
    elif value < 0:
        return "▼", "#16a34a", abs(int(value))   # green - down
    else:
        return "—", "#6b7280", 0                 # gray

def kpi_card(label, value, delta, last_updated=None):
    arrow, color, abs_delta = format_delta(delta)

    if abs_delta:                      # normal behaviour
        footer = html.Span(
            f"{arrow} {abs_delta:,} / {WINDOW}d",
            style={"color": color, "fontSize": "0.75rem"},
        )
    else:                              # no movement → show last update
        footer = html.Span(
            f"last update: {last_updated}",
            style={"color": "#6b7280", "fontSize": "0.75rem", "fontStyle": "italic"},
        )

    return html.Div(
        [html.H3(f"{value:,}"), html.P(label), footer],
        className="kpi-card",
        style={"flex": "1"},
    )



def styled_dropdown(id, options, value):
    return dcc.Dropdown(
        id=id,
        options=options,
        value=value,
        clearable=False,
        className="dropdown-menu",  # 🔗 hook to CSS
    )



def last_change_date(series):
    """Return the most-recent date where the value changed."""
    # reverse-scan until value differs from the latest one
    latest_val = series.iloc[-1]
    mask = series != latest_val
    if mask.any():
        # index of last True → the row *before* repeats started
        last_row = mask[::-1].idxmax()
        return df.loc[last_row, "report_date"].strftime("%b %d %Y")
    else:
        return None          # never changed (edge-case)



app.layout = html.Div(
    [
        html.H1("Loss of Life in Gaza", style={"textAlign": "center"}),
        html.H2("Since October 7, 2023 (These metrics do not fully reflect the loss of human life in Palestine", 
                style={"textAlign": "center"}),
        # KPI ROW (cards now include 7-day delta)
        html.Div(id="kpi-row"),

        # metric selector
        styled_dropdown(
            id="metric-dropdown",
            options=[
                {"label": "Total Killed",    "value": "killed_cum"},
                {"label": "Total Injured",   "value": "injured_cum"},
                {"label": "Children Killed", "value": "ext_killed_children_cum"},
                {"label": "Women Killed",    "value": "ext_killed_women_cum"},
            ],
            value="killed_cum"
        ),


        # date-range slider (labels = first day of each month)
        html.Div(
            [
                dcc.RangeSlider(
                    id="date-range-slider",
                    min=0,
                    max=len(df) - 1,
                    value=[0, len(df) - 1],
                    marks={
                        i: d.strftime("%b\n%Y")
                        for i, d in enumerate(df["report_date"])
                        if d.day == 1
                    },
                    step=1,
                    tooltip={"placement": "bottom", "always_visible": False},
                    updatemode="mouseup",
                    allowCross=False,
                ),
            ],
            style={"margin": "30px 20px"},
        ),

        # main figure
        dcc.Graph(id="main-graph"),

        html.H3("Interactive Tableau View of Data:", 
            style={"textAlign": "center"}),
        # --- Tableau iframe  ---------------------------------------
        html.Div(
                html.Iframe(
            src=(
                "https://public.tableau.com/views/"
                "Book2_17509844206740/Dashboard1"
                "?:showVizHome=no&:embed=true&publish=yes"
            ),
            style={
                "width": "90%",     # adjust as needed
                "height": "900px",
                "border": "none",
            },
        ),

        style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "margin": "20px 0"
        },
    ),



        html.Div(  # 1️⃣ hidden JSON store
            dcc.Store(id="data-store", data=df.to_json(date_format="iso", orient="split"))
        ),

        dcc.Interval(  # 2️⃣ timer fires every 24 h (in-app, per user session)
            id="data-refresh",
            interval=24 * 60 * 60 * 1000,   # milliseconds
            n_intervals=0,                  # start at zero
        ),

    ]
)


@app.callback(
    Output("data-store", "data"),
    Input("data-refresh", "n_intervals"),
    prevent_initial_call=False   # run once when the page first loads
)
def refresh_data(_):
    fresh_df = get_data(refresh=True)        # hit the remote CSV / JSON
    return fresh_df.to_json(date_format="iso", orient="split")



@app.callback(
    Output("main-graph", "figure"),
    Input("metric-dropdown", "value"),
    Input("date-range-slider", "value"),
    Input("data-store", "data"),          #  <-- NEW
)
def update_graph(metric, date_range, json_df):
    # ---- fresh dataframe coming from the store ----
    df = pd.read_json(io.StringIO(json_df), orient="split")

    # keep your slider filtering logic
    start_idx, end_idx = date_range
    filtered_df = df.iloc[start_idx : end_idx + 1]

    # same label-cleaning + plotting as before
    clean = metric
    if clean.endswith("_cum"):
        clean = clean[:-4].lower()
    if "ext_" in clean:
        clean = clean.replace("ext_", "")
    clean = clean.replace("_", " ").title()

    fig = px.line(
        filtered_df,
        x="report_date",
        y=metric,
        title=f"Gaza – Total {clean} Over Time",
        labels={"report_date": "Date", metric: clean},
        color_discrete_sequence=["#d62828"],
    )

    fig.update_layout(
        plot_bgcolor="#d9fae3",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(0,0,0,0.05)"),
        yaxis=dict(gridcolor="rgba(0,0,0,0.05)"),
    )
    return fig

@app.callback(
    Output("kpi-row", "children"),
    Input("data-store", "data"),
)
def update_kpis(json_df):
    df = pd.read_json(io.StringIO(json_df), orient="split")
    latest = df.iloc[-1]
    prev   = df.iloc[-8]

    # deltas
    delta_killed  = latest["killed_cum"]             - prev["killed_cum"]
    delta_injured = latest["injured_cum"]            - prev["injured_cum"]
    delta_child   = latest["ext_killed_children_cum"] - prev["ext_killed_children_cum"]
    delta_women   = latest["ext_killed_women_cum"]    - prev["ext_killed_women_cum"]

    # last-updated stamps for static series
    child_last  = last_change_date(df["ext_killed_children_cum"])
    women_last  = last_change_date(df["ext_killed_women_cum"])

    cards = [
        kpi_card("Total Killed",    int(latest["killed_cum"]),          delta_killed),
        kpi_card("Total Injured",   int(latest["injured_cum"]),         delta_injured),
        kpi_card("Children Killed", int(latest["ext_killed_children_cum"]),
                 delta_child, last_updated=child_last),
        kpi_card("Women Killed",    int(latest["ext_killed_women_cum"]),
                 delta_women, last_updated=women_last),
    ]

    return html.Div(
        cards,
        style={
            "display": "flex",
            "flexWrap": "wrap",
            "gap": "10px",
            "margin": "15px 0",
        }
    )



if __name__ == "__main__":
    # runs on http://127.0.0.1:8050/   (Ctrl-C to stop)
    app.run(debug=True)
