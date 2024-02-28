from pathlib import Path

import pandas as pd

# Load data
app_dir = Path(__file__).parent
players_df = pd.read_csv(app_dir / "players.csv", dtype={"person_id": str})
careers_df = pd.read_csv(app_dir / "careers.csv", dtype={"person_id": str})

# Define the stats to compare
stats = ["PTS", "FG_PCT", "FG3_PCT", "FT_PCT", "REB", "AST", "STL", "BLK"]

# create dictionary where key is player id and value is name
players_dict = dict(zip(players_df["person_id"], players_df["display_first_last"]))

careers_df["player_name"] = careers_df["person_id"].map(players_dict)

from_start = players_df["from_year"].min()
to_end = players_df["to_year"].max()
gp_max = careers_df["GP"].max()
