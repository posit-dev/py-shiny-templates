from pathlib import Path

import polars as pl

app_dir = Path(__file__).parent
tips = pl.read_csv(app_dir / "tips.csv")
