from pathlib import Path
import pandas as pd
import seaborn as sns
from shiny.express import input, render, ui

app_dir = Path(__file__).parent
dat = pd.read_csv(app_dir / "penguins.csv")

ui.page_opts(title="Basic Shiny app")


@render.plot
def hist():
    return sns.histplot(dat, x=input.var()).set(xlabel=None)


ui.input_select(
    "var", "Select variable",
    choices=["bill_length_mm", "body_mass_g"]
)
