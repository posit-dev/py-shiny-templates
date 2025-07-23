import numpy as np

# Import helpers for plotting logic
from plots import color_palette, density_plot, radar_chart

# Import some pre-downloaded data on player careers
from shared import app_dir, careers_df, from_start, gp_max, players_dict, stats, to_end
from shiny import App, reactive, req, ui
from shinywidgets import output_widget, render_plotly

# Define the app UI
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_selectize(
            "players",
            "Search for players",
            multiple=True,
            choices=players_dict,
            selected=["893", "2544", "201939"],
            width="100%",
        ),
        ui.input_slider(
            "games",
            "Career games played",
            value=[300, gp_max],
            min=0,
            max=gp_max,
            step=1,
            sep="",
        ),
        ui.input_slider(
            "seasons",
            "Career within years",
            value=[from_start, to_end],
            min=from_start,
            max=to_end,
            step=1,
            sep="",
        ),
    ),
    ui.layout_columns(
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
                    "stat", None, choices=stats, selected="PTS", width="auto"
                ),
                " vs the rest of the league",
                class_="d-flex align-items-center gap-1",
            ),
            output_widget("stat_compare"),
            ui.card_footer("Click on a player's name to add them to the comparison."),
            full_screen=True,
        ),
        col_widths=[4, 8],
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
            (careers_df["GP"] >= games[0])
            & (careers_df["GP"] <= games[1])
            & (careers_df["from_year"] >= seasons[0])
            & (careers_df["to_year"] <= seasons[1])
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
        res["color"] = np.resize(color_palette, len(players))
        return res

    # For each player, get the percentile of each stat
    @reactive.calc
    def percentiles():
        d = player_stats()

        def apply_func(x):
            for col in stats:
                x[col] = (x[col].values > careers()[col].values).mean()
            return x

        return d.groupby("person_id")[
            ["person_id", "player_name", "color", *stats]
        ].apply(apply_func, include_groups=False)

    # radar chart of player stats
    @render_plotly
    def career_compare():
        return radar_chart(percentiles(), player_stats(), stats)

    # 1D density plot of player stats
    @render_plotly
    def stat_compare():
        return density_plot(
            careers(), player_stats(), input.stat(), players_dict, on_rug_click
        )

    # When a player is clicked on the rug plot, add them to the selected players
    def on_rug_click(trace, points, state):
        player_id = trace.customdata[points.point_inds[0]]
        selected = list(input.players()) + [player_id]
        ui.update_selectize("players", selected=selected)


app = App(app_ui, server)
