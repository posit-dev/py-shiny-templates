from pathlib import Path
import pandas as pd
import seaborn as sns
from shiny import App, render, ui

app_dir = Path(__file__).parent
dat = pd.read_csv(app_dir / "penguins.csv")

app_ui = ui.page_sidebar(
    ui.sidebar(
      ui.input_select(
          "var", "Select variable",
          choices=["bill_length_mm", "body_mass_g"]
      ),
      ui.input_switch("show_kde", "Show KDE", value=True),
      ui.input_switch("show_rug", "Show Rug", value=True),
    ),
    ui.output_plot("hist"),
    title="Hello sidebar!",
)


def server(input, output, session):
    @render.plot
    def hist():
        sns.histplot(dat, x=input.var(), kde=input.show_kde())
        if input.show_rug():
            sns.rugplot(dat[input.var()], alpha=0.25)


app = App(app_ui, server)
