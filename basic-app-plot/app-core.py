from pathlib import Path
import pandas as pd
import seaborn as sns
from shiny import App, render, ui

app_dir = Path(__file__).parent
dat = pd.read_csv(app_dir / "penguins.csv")

app_ui = ui.page_fixed(
    ui.panel_title("Basic Shiny app"),
    ui.output_plot("hist"),
    ui.input_select(
        "var", "Select variable",
        choices=["bill_length_mm", "body_mass_g"]
    )
)


def server(input, output, session):
    @render.plot
    def hist():
        return sns.histplot(dat, x=input.var()).set(xlabel=None)


app = App(app_ui, server)
