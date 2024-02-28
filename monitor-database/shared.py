import sqlite3

import faicons as fa
import pandas as pd
import plotly.express as px

# This starts a background process to add records to a database after a random interval
# You should replace it with a connection to your actual database.
import scoredata
from shiny import module, reactive, render, ui

scoredata.begin()
con = sqlite3.connect(scoredata.SQLITE_DB_URI, uri=True)


def last_modified():
    """
    Fast-executing call to get the timestamp of the most recent row in the
    database. We will poll against this in absence of a way to receive a push
    notification when our SQLite database changes.
    """
    res = con.execute("select max(timestamp) from accuracy_scores")
    return res.fetchone()[0]


@reactive.poll(last_modified)
def df():
    """
    @reactive.poll calls a cheap query (`last_modified()`) every 1 second to
    check if the expensive query (`df()`) should be run and downstream
    calculations should be updated.

    By declaring this reactive object at the top-level of the script instead of
    in the server function, all sessions are sharing the same object, so the
    expensive query is only run once no matter how many users are connected.
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


# ---------------------------------------------------------------
# Plot and value box logic
# ---------------------------------------------------------------

THRESHOLD_MID = 0.85
THRESHOLD_MID_COLOR = "#f9b928"
THRESHOLD_LOW = 0.5
THRESHOLD_LOW_COLOR = "#c10000"


@module.ui
def value_box_ui(title):
    return ui.value_box(
        title,
        ui.output_text("value"),
        showcase=ui.output_ui("icon"),
    )


@module.server
def value_box_server(input, output, session, df, model: str):
    @reactive.calc
    def score():
        d = df()
        return d[d["model"] == model].iloc[-1]["score"]

    @render.text
    def value():
        return f"{score():.2f}"

    @render.ui
    def icon():
        if score() > THRESHOLD_MID:
            return fa.icon_svg("circle-check").add_class("text-success")
        if score() > THRESHOLD_LOW:
            return fa.icon_svg("triangle-exclamation").add_class("text-warning")
        return fa.icon_svg("circle-exclamation").add_class("text-danger")


def plot_timeseries(d):
    fig = px.line(
        d,
        x="time",
        y="score",
        labels=dict(score="accuracy"),
        color="model",
        color_discrete_sequence=px.colors.qualitative.Set2,
        template="simple_white",
    )

    fig.add_hline(
        THRESHOLD_LOW,
        line_dash="dot",
        line=dict(color=THRESHOLD_LOW_COLOR, width=2),
        opacity=0.3,
        annotation=dict(text="Warning Zone", xref="paper", x=1, y=THRESHOLD_MID),
        annotation_position="bottom right",
    )
    fig.add_hline(
        THRESHOLD_MID,
        line_dash="dot",
        line=dict(color=THRESHOLD_MID_COLOR, width=2),
        opacity=0.3,
        annotation=dict(text="Danger Zone", xref="paper", x=1, y=THRESHOLD_LOW),
        annotation_position="bottom right",
    )

    fig.update_yaxes(range=[0, 1], fixedrange=True)
    fig.update_xaxes(fixedrange=True, tickangle=60)
    fig.update_layout(hovermode="x unified")

    return fig
