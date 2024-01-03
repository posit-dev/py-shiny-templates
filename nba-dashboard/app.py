from shiny import Inputs, Outputs, Session, App, reactive, render, req, ui
from helpers import get_player_stats, list_players, plot_scorigami, teams
import pandas as pd
from value_boxes import stat_box_ui, stat_box_server
from shinywidgets import output_widget, render_widget

teams = pd.DataFrame(teams.get_teams())

stats = ["pts", "ast", "reb", "plus_minus"]

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_selectize(
            "team",
            "Team",
            choices=sorted(teams["nickname"].to_list()),
            selected="Warriors",
        ),
        ui.output_ui("player_select"),
    ),
    ui.layout_columns(
        [
            ui.card(ui.card_header("Assist to Turnover", output_widget("ast_tov"))),
            ui.card(ui.card_header("Rebounds", output_widget("dreb_oreb"))),
        ],
        [stat_box_ui(stat, stat) for stat in stats],
        col_widths=[7, 5],
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    players = list_players()

    @render.ui
    def player_select():
        filtered_players = players[players["team_name"] == input.team()].sort_values(
            "display_first_last"
        )
        choice_dict = filtered_players["display_first_last"].to_list()
        return ui.input_selectize(
            "player",
            "Player",
            choices=choice_dict,
        )
        return

    @reactive.Calc
    def game_logs():
        return get_player_stats(req(input.player()))

    @render_widget
    def ast_tov():
        return plot_scorigami(input.player(), game_logs())

    @render_widget
    def dreb_oreb():
        return plot_scorigami(input.player(), game_logs(), "dreb", "oreb")

    [stat_box_server(stat, stat, game_logs=game_logs) for stat in stats]


app = App(app_ui, server)
