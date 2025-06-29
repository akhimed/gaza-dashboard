# pages/names.py
import datetime as dt
import pandas as pd
import dash
from dash import html, dcc, Input, Output
import dash.dash_table as dash_table
import plotly.express as px

from fetch_data import get_names_df

dash.register_page(__name__, path="/names", name="Names")

# ────────────────────────────────────────────────────────────────────────────
# Load once into memory (refresh when the server restarts)
# ────────────────────────────────────────────────────────────────────────────
names_df: pd.DataFrame = get_names_df()

# Last-refresh time (for the little caption)
_LAST_REFRESH = dt.datetime.utcfromtimestamp(
    names_df.attrs.get("file_mtime", dt.datetime.utcnow()).timestamp()
).strftime("%b %d %Y %H:%M UTC")


# ────────────────────────────────────────────────────────────────────────────
# Layout
# ────────────────────────────────────────────────────────────────────────────
def layout() -> html.Div:
    total = len(names_df)

    first_names_df = (
        names_df["english_name"].str.split().str[0].str.title()
        .value_counts().nlargest(10)
        .rename_axis("first_name").reset_index(name="count")
    )
    bar_fig = _make_bar(first_names_df)
    age_fig = _make_age_hist(names_df)

    return html.Div(
        [
            html.H2("Recorded Victims – Names Dataset", style={"textAlign": "center"}),
            html.P(
                f"{total:,} individual records "
                f"(data cache refreshed {_LAST_REFRESH}).",
                style={"textAlign": "center"},
            ),

            # --------------- Filters ---------------- #
            html.Div(
                [
                    dcc.Dropdown(
                        id="gender-filter",
                        options=[
                            {"label": "All genders", "value": "all"},
                            {"label": "Male only",   "value": "m"},
                            {"label": "Female only", "value": "f"},
                        ],
                        value="all",
                        clearable=False,
                        style={"width": "180px"},
                    ),
                    dcc.Input(
                        id="name-search",
                        type="text",
                        placeholder="Search name…",
                        style={"marginLeft": "12px", "width": "200px"},
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "gap": "12px",
                    "margin": "14px 0 26px",
                },
            ),

            dcc.Graph(id="bar-names", figure=bar_fig),
            dcc.Graph(id="age-hist",  figure=age_fig),

            html.H4("Browse full table (filtered)"),
            dash_table.DataTable(
                id="names-table",
                columns=[
                    {"name": "ID",            "id": "id",            "type": "numeric"},
                    {"name": "English name",  "id": "english_name"},
                    {"name": "Age",           "id": "age",           "type": "numeric"},
                    {"name": "Gender",        "id": "sex"},
                    {"name": "Date of birth", "id": "dob"},
                    {"name": "Source",        "id": "source"},
                ],
                page_size=15,
                sort_action="native",
                style_table={"overflowX": "auto"},
            ),
        ],
        style={"maxWidth": "1150px", "margin": "0 auto"},
    )


# ────────────────────────────────────────────────────────────────────────────
# Callbacks
# ────────────────────────────────────────────────────────────────────────────
@dash.callback(
    Output("bar-names",  "figure"),
    Output("age-hist",   "figure"),
    Output("names-table","data"),
    Input("gender-filter","value"),
    Input("name-search",  "value"),
)
def update_visuals(gender_val: str, search_text: str):
    df = names_df.copy()

    # gender filter
    if gender_val in ("m", "f"):
        df = df[df["sex"] == gender_val]

    # name search (case-insensitive English only)
    if search_text:
        term = search_text.lower()
        df = df[df["english_name"].str.lower().str.contains(term, na=False)]

    # rebuild bar + hist
    first_names = (
        df["english_name"].str.split().str[0].str.title()
        .value_counts().nlargest(10)
        .rename_axis("first_name").reset_index(name="count")
    )
    bar_fig = _make_bar(first_names)
    age_fig = _make_age_hist(df)

    return bar_fig, age_fig, df.to_dict("records")


# ────────────────────────────────────────────────────────────────────────────
# Helper chart builders
# ────────────────────────────────────────────────────────────────────────────
def _make_bar(df_names: pd.DataFrame):
    fig = px.bar(
        df_names, x="first_name", y="count",
        color="count", text="count", color_continuous_scale="agsunset",
        title="Top 10 most common first names"
    )
    fig.update_layout(yaxis_title="", xaxis_title="")
    return fig


def _make_age_hist(df: pd.DataFrame):
    fig = px.histogram(
        df.dropna(subset=["age"]),
        x="age", nbins=30,
        color_discrete_sequence=["#d62828"],
        title="Age distribution of recorded victims"
    )
    fig.update_layout(yaxis_title="Number of people", xaxis_title="Age")
    return fig
