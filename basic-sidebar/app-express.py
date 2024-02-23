from pathlib import Path
import pandas as pd
import seaborn as sns
from shiny.express import input, render, ui

app_dir = Path(__file__).parent
dat = pd.read_csv(app_dir / "penguins.csv")

ui.page_opts(title="Hello sidebar!")

with ui.sidebar():
    ui.input_select(
        "var", "Select variable",
        choices=["bill_length_mm", "body_mass_g"]
    )
    ui.input_switch("show_kde", "Show KDE", value=True)
    ui.input_switch("show_rug", "Show Rug", value=True)


@render.plot
def hist():
    sns.histplot(dat, x=input.var(), kde=input.show_kde())
    if input.show_rug():
        sns.rugplot(dat[input.var()], alpha=0.25)
