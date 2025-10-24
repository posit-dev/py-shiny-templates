from pathlib import Path

import polars as pl

app_dir = Path(__file__).parent
scores = pl.read_csv(app_dir / "scores.csv")
