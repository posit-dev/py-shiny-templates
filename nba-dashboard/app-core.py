import pandas as pd
from pathlib import Path

from shiny import App, reactive, render, req, ui

from shinywidgets import output_widget, render_plotly
import plotly.graph_objects as go


app_dir = Path(__file__).parent
players_df = pd.read_csv(app_dir / "players.csv")

# create dictionary where key is player id and value is name
players_dict = dict(zip(
    players_df["person_id"].astype(str),
    players_df["display_first_last"]
))

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_selectize(
            "players",
            "Select players",
            multiple=True,
            choices=players_dict,
            selected=["893"],
        ),
    ),
    ui.card(
        ui.card_header("Player comparison"),
        output_widget("all_stats"),
        full_screen=True,
    ),
    title="NBA Dashboard",
    fillable=True,
)


def server(input, output, session):
    
    # Career stats for each player
    # (gets read once the session starts so that this operation doesn't block the UI)
    careers = pd.read_csv(app_dir / "careers.csv")

    # One row per player (average over seasons)
    careers = careers.groupby("person_id").mean()

    @reactive.calc
    def player_stats():
        req(input.players())
        return careers[careers["person_id"].isin(input.players())]
    
    stats = [
        "PTS", "FG_PCT", "FG3_PCT", "FT_PCT", "REB", "AST", "STL", "BLK"
    ]

    # For each player, get the percentile of each stat
    @reactive.calc
    def percentiles():
        d = player_stats()
        # For each player stat, get the overall percentile of that stat
        for index, row in d.iterrows():
            for stat in stats:
                d.at[index, stat] = (d[stat] > row[stat]).mean()
        return d

    # radar chart of player stats
    @render_plotly
    def all_stats():
        #import plotly.express as px
        
        d = percentiles()
        fig = go.Figure()

        for index, row in d.iterrows():
            fig.add_trace(go.Scatter(
                r=[row[stat] for stat in stats],
                theta=stats,
                fill='toself',
                name=players_dict[index]
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True
        )

        return fig


app = App(app_ui, server)
