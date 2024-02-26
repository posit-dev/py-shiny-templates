import pandas as pd
import numpy as np
from pathlib import Path

from shiny import App, reactive, req, ui

from shinywidgets import output_widget, render_plotly
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff

# Load data
app_dir = Path(__file__).parent
players_df = pd.read_csv(app_dir / "players.csv", dtype={"person_id": str})
careers_df = pd.read_csv(app_dir / "careers.csv", dtype={"person_id": str})

# Define the stats to compare
stats = ["PTS", "FG_PCT", "FG3_PCT", "FT_PCT", "REB", "AST", "STL", "BLK"]

# create dictionary where key is player id and value is name
players_dict = dict(zip(
    players_df["person_id"],
    players_df["display_first_last"]
))

careers_df["player_name"] = careers_df["person_id"].map(players_dict)

from_start = players_df["from_year"].min()
to_end = players_df["to_year"].max()
gp_max = careers_df["GP"].max()

# Define the app UI
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_selectize(
            "players",
            "Search for players",
            multiple=True,
            choices=players_dict,
            selected=["893", "2544", "201939"],
            width="100%"
        ),
        ui.input_slider(
            "games", "Career games played",
            value=[300, gp_max],
            min=0, max=gp_max,
            step=1, sep=""
        ),
        ui.input_slider(
            "seasons", "Career within years",
            value=[from_start, to_end],
            min=from_start, max=to_end,
            step=1, sep=""
        )
    ),
    # TODO: add filters for:
    # * position
    # * team
    # * various stats
    ui.card(
        ui.card_header("Player career comparison"),
        output_widget("career_compare"),
        ui.card_footer("Percentiles are based on career per game averages."),
        full_screen=True,
    ),
    ui.card(
        ui.card_header(
            "Player career ",
            ui.input_select(
                "stat", None,
                choices=stats,
                selected="PTS",
                width="auto"
            ),
            " vs the rest of the league",
            class_="d-flex align-items-center gap-1",
        ),
        output_widget("stat_compare"),
        ui.card_footer("Click on a player's name to add them to the comparison."),
        full_screen=True,
    ),
    ui.include_css(app_dir / "styles.css"),
    title="NBA Dashboard",
    fillable=True,
)


def server(input, output, session):
    
    # Filter the careers data based on the selected games and seasons
    @reactive.calc
    def careers():
        games = input.games()
        seasons = input.seasons()
        idx = (
            (careers_df["GP"] >= games[0]) &
            (careers_df["GP"] <= games[1]) &
            (careers_df["from_year"] >= seasons[0]) &
            (careers_df["to_year"] <= seasons[1])
        )
        return careers_df[idx]

    # Update available players when careers data changes
    @reactive.effect
    def _():
        players = dict(zip(careers()["person_id"], careers()["player_name"]))
        ui.update_selectize("players", choices=players, selected=input.players())

    # Get the stats for the selected players
    @reactive.calc
    def player_stats():
        players = req(input.players())
        res = careers()
        res = res[res["person_id"].isin(players)]
        res["color"] = np.resize(px.colors.qualitative.D3, len(players))
        return res

    # For each player, get the percentile of each stat
    @reactive.calc
    def percentiles():
        d = player_stats()

        def apply_func(x):
            for col in stats:
                x[col] = (x[col].values > careers()[col].values).mean()
            return x

        return d.groupby("person_id").apply(apply_func)

    # radar chart of player stats
    @render_plotly
    def career_compare():
        percs = percentiles()
        stats_df = player_stats()

        fig = go.Figure()

        for _, row in percs.iterrows():
            id = row["person_id"]
            r = [row[x] for x in stats]
            vals = stats_df[stats_df["person_id"] == id][stats].values[0]
            text = np.round(vals, 2).astype(str).tolist()
            fig.add_trace(go.Scatterpolar(
                r=r + r[:1],
                theta=stats + stats[:1],
                text=text + text[:1],
                name=row["player_name"],
                hoverinfo="text+name",
                line=dict(width=1, color=row["color"]),
            ))

        fig.update_layout(
            margin=dict(l=30, r=30, t=30, b=30),
            polar=dict(radialaxis=dict(range=[0, 1])),
            showlegend=True,
            legend=dict(
                orientation="h",
                y=-0.1, yanchor="top",
                x=0.5, xanchor="center"
            )
        )

        return fig
    
    # 1D density plot of player stats
    @render_plotly
    def stat_compare():
        vals = careers()[input.stat()]
        vals = vals[~vals.isnull()]
        fig = ff.create_distplot(
            [vals], ["Overall"],
            rug_text=[careers()["player_name"]],
            colors=["black"], show_hist=False,
        )
        # Clean up some defaults (1st trace is the density plot, 2nd is the rug plot)
        fig.data[0].hoverinfo = "none"
        fig.data[0].showlegend = False
        fig.data[1].hoverinfo = "text+x"
        fig.data[1].customdata = careers()["person_id"]
        # Use height of the density plot to inform the vertical lines
        ymax = fig.data[0].y.max()
        # Arrange rows from highest to lowest value so that legend order is correct
        stats_df = player_stats().sort_values(input.stat(), ascending=False)
        # Add vertical lines for each player
        for _, row in stats_df.iterrows():
            x = row[input.stat()]
            fig.add_scatter(
                x=[x, x], y=[0, ymax],
                mode="lines", name=players_dict[row["person_id"]],
                line=dict(color=row["color"], width=1),
                hoverinfo="x+name"
            )

        fig.update_layout(
            hovermode="x",
            xaxis=dict(
                title=input.stat() + " per game (career average)",
                hoverformat=".1f"
            ),
            legend=dict(
                orientation="h",
                y=1.03, yanchor="bottom",
                x=0.5, xanchor="center"
            )
        )

        # Convert Figure to FigureWidget so we can add click events
        fig = go.FigureWidget(fig.data, fig.layout)
        fig.data[1].on_click(on_rug_click)
        return fig

    # When a player is clicked on the rug plot, add them to the selected players
    def on_rug_click(trace, points, state):
        player_id = trace.customdata[points.point_inds[0]]
        selected = list(input.players()) + [player_id]
        ui.update_selectize("players", selected=selected)


app = App(app_ui, server)
