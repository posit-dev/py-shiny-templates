from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

import pandas as pd
import plotly.express as px
import scoredata
from shinywidgets import output_widget, render_widget
from faicons import icon_svg

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

THRESHOLD_MID = 0.85
THRESHOLD_MID_COLOR = "rgb(0, 137, 26)"
THRESHOLD_LOW = 0.5
THRESHOLD_LOW_COLOR = "rgb(193, 0, 0)"

# This starts a background process to add records to a database after a random intervale
# You should replace it with a connection to your actual database.
scoredata.begin()

con = sqlite3.connect(scoredata.SQLITE_DB_URI, uri=True)


def last_modified(con):
    """
    Fast-executing call to get the timestamp of the most recent row in the database.
    We will poll against this in absence of a way to receive a push notification when
    our SQLite database changes.
    """
    return con.execute("select max(timestamp) from accuracy_scores").fetchone()[0]


@reactive.poll(lambda: last_modified(con))
def df():
    """
    @reactive.poll calls a cheap query (`last_modified()`) every 1 second to check if
    the expensive query (`df()`) should be run and downstream calculations should be
    updated.

    By declaring this reactive object at the top-level of the script instead of in the
    server function, all sessions are sharing the same object, so the expensive query is
    only run once no matter how many users are connected.
    """
    tbl = pd.read_sql(
        "select * from accuracy_scores order by timestamp desc, model desc limit ?",
        con,
        params=[150],
    )
    # Convert timestamp to datetime object, which SQLite doesn't support natively
    tbl["timestamp"] = pd.to_datetime(tbl["timestamp"], utc=True)
    # Create a short label for readability
    tbl["time"] = tbl["timestamp"].dt.strftime("%H:%M:%S")
    # Reverse order of rows
    tbl = tbl.iloc[::-1]

    return tbl


model_names = ["model_1", "model_2", "model_3", "model_4"]
model_colors = {
    name: color
    for name, color in zip(model_names, px.colors.qualitative.D3[0 : len(model_names)])
}


def make_value_box(model, score):
    theme = "text-success"
    icon = icon_svg("check", width="50px")
    if score < THRESHOLD_MID:
        theme = "text-warning"
        icon = icon_svg("triangle-exclamation", width="50px")
    if score < THRESHOLD_LOW:
        theme = "bg-danger"
        icon = icon_svg("circle-exclamation", width="50px")

    return ui.value_box(model, ui.h2(score), theme=theme, showcase=icon)


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_checkbox_group("models", "Models", model_names, selected=model_names),
    ),
    ui.row(
        ui.h1("Model monitoring dashboard"),
        ui.output_ui("value_boxes"),
    ),
    ui.row(
        ui.card(output_widget("plot_timeseries")),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Calc
    def filtered_df():
        """
        Return the data frame that should be displayed in the app, based on the user's
        input. This will be either the latest rows, or a specific time range. Also
        filter out rows for models that the user has deselected.
        """
        data = df()

        # Filter the rows so we only include the desired models
        return data[data["model"].isin(input.models())]

    @reactive.Calc
    def filtered_model_names():
        return filtered_df()["model"].unique()

    @output
    @render.ui
    def value_boxes():
        data = filtered_df()
        models = data["model"].unique().tolist()
        scores_by_model = {
            x: data[data["model"] == x].iloc[-1]["score"] for x in models
        }
        # Round scores to 2 decimal places
        scores_by_model = {x: round(y, 2) for x, y in scores_by_model.items()}

        return ui.layout_columns(
            *[
                # For each model, return a value_box with the score, colored based on
                # how high the score is.
                make_value_box(model, score)
                for model, score in scores_by_model.items()
            ],
            width="135px",
        )

    @render_widget
    def plot_timeseries():
        """
        Returns a Plotly Figure visualization. Streams new data to the Plotly widget in
        the browser whenever filtered_df() updates, and completely recreates the figure
        when filtered_model_names() changes (see recreate_key=... above).
        """
        fig = px.line(
            filtered_df(),
            x="time",
            y="score",
            labels=dict(score="accuracy"),
            color="model",
            color_discrete_map=model_colors,
            template="simple_white",
        )

        return fig


app = App(app_ui, server)
