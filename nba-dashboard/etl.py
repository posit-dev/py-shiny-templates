import pandas as pd
from pathlib import Path
from nba_api.stats.endpoints import commonallplayers, playercareerstats
import time

players = commonallplayers.CommonAllPlayers().get_data_frames()[0]
players.columns = players.columns.str.lower().str.replace(" ", "_")
players["person_id"] = players["person_id"].astype(str)

f = Path(__file__).parent / "players.csv"
players.to_csv(f, index=False)

# Get career stats for each player, and store in one big dataframe
stat_columns = [
    "person_id", "PTS", "FG_PCT", "FG3_PCT", "FT_PCT", "REB", "AST", "STL", "BLK", #"TOV", "PF", "PLUS_MINUS"
]
careers = pd.DataFrame(columns=stat_columns)
for id in players["person_id"]:
    print("Getting stats for player", id)
    stats = playercareerstats.PlayerCareerStats(player_id=str(id))
    stats = stats.get_data_frames()[0]
    stats["person_id"] = id
    careers = pd.concat([careers, stats], axis=0)
    # Avoid getting rate-limited
    time.sleep(1)

f = Path(__file__).parent / "careers.csv"
careers.to_csv(f, index=False)
