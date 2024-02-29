import time
from pathlib import Path

import pandas as pd
from nba_api.stats.endpoints import commonallplayers, playercareerstats

players = commonallplayers.CommonAllPlayers().get_data_frames()[0]
players.columns = players.columns.str.lower().str.replace(" ", "_")
players["person_id"] = players["person_id"].astype(str)

f = Path("nba-dashboard") / "players.csv"
players.to_csv(f, index=False)

# Get career stats for each player (one row per player per season)
careers = pd.DataFrame()
for id in players["person_id"]:
    print("Getting stats for player", id)
    stats = playercareerstats.PlayerCareerStats(player_id=str(id))
    stats = stats.get_data_frames()[0]
    stats["person_id"] = id
    careers = pd.concat([careers, stats], axis=0)
    # Avoid getting rate-limited
    time.sleep(1)

f = Path(__file__).parent / "careers_all.csv"
careers.to_csv(f, index=False)

# Columns to use for the visualizations
stat_cols = ["PTS", "FG_PCT", "FG3_PCT", "FT_PCT", "REB", "AST", "STL", "BLK"]
cols = ["person_id", "GP"] + stat_cols

# Divide each non-pct stat by the number of games played (to get per-game averages)
careers["PTS"] = careers["PTS"] / careers["GP"]
careers["REB"] = careers["REB"] / careers["GP"]
careers["AST"] = careers["AST"] / careers["GP"]
careers["STL"] = careers["STL"] / careers["GP"]
careers["BLK"] = careers["BLK"] / careers["GP"]


# Get the average of each stat for each player (but sum the number of games played)
def apply_func(x):
    res = x.mean()
    res["GP"] = x["GP"].sum()
    return res


careers = careers[cols].groupby("person_id").apply(apply_func).reset_index()

# Merge with players to get from_year and to_year
careers = careers.merge(players[["person_id", "from_year", "to_year"]], on="person_id")

f = Path(__file__).parent / "careers.csv"
careers.to_csv(f, index=False)
