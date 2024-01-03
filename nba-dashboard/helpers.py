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


def plot_scorigami(player, df, var1="ast", var2="tov"):
    fig = px.density_heatmap(
        df, x="ast", y="tov", color_continuous_scale="reds", nbinsx=5, nbinsy=5
    )
    fig.update_layout(
        xaxis_title=var1,
        yaxis_title=var2,
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        xaxis_zeroline=False,
        yaxis_zeroline=False,
        xaxis_showticklabels=True,
        yaxis_showticklabels=True,
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
    )
    return fig
