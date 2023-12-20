from nba_api.stats.endpoints import playergamelog, commonallplayers, shotchartdetail
from nba_api.stats.static import players, teams
import pandas as pd
import plotly.express as px


def list_players() -> pd.DataFrame:
    all_players = commonallplayers.CommonAllPlayers().get_data_frames()[0]
    all_players = all_players[all_players["TO_YEAR"] == "2023"]
    all_players.columns = all_players.columns.str.lower().str.replace(" ", "_")
    return all_players[
        ["person_id", "display_first_last", "from_year", "to_year", "team_name"]
    ]


def get_player_stats(player_name):
    all_players = players.get_players()
    all_players = pd.DataFrame(all_players)
    player_id = all_players[all_players["full_name"] == player_name]["id"]

    # Query for player's game log
    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season="2023")

    # Get DataFrame from gamelog
    df = gamelog.get_data_frames()[0]

    # Make the df columns lower snake case
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    # Parse the game_date column to datetime format
    df["game_date"] = pd.to_datetime(df["game_date"], format="%b %d, %Y")

    return df


def plot_fga_vs_fgm(game_log_df):
    fig = px.scatter(
        game_log_df,
        x="fga",
        y="fgm",
        labels={"fga": "Field goals attempted", "fgm": "Field goals made"},
    )
    return fig


def plot_rebounds(game_log_df):
    fig = px.scatter(
        game_log_df,
        x="oreb",
        y="dreb",
        labels={"dreb": "Defensive rebounds", "oreb": "Offensive rebounds"},
    )
    return fig
