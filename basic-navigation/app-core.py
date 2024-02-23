from pathlib import Path
import pandas as pd
import seaborn as sns
from shiny import App, render, ui

app_dir = Path(__file__).parent
dat = pd.read_csv(app_dir / "penguins.csv")

# The contents of the first 'page' is a navset with two 'panels'.
page1 = ui.navset_card_underline(
    ui.nav_panel("Plot", ui.output_plot("hist")),
    ui.nav_panel("Table", ui.output_data_frame("data")),
    footer=ui.input_select(
        "var", "Select variable",
        choices=["bill_length_mm", "body_mass_g"]
    ),
    title="Penguins data"
)

app_ui = ui.page_navbar(
    ui.nav_spacer(),  # Push the navbar items to the right
    ui.nav_panel("Page 1", page1),
    ui.nav_panel("Page 2", "This is the second 'page'."),
    title="Shiny navigation components",
)


def server(input, output, session):
    @render.plot
    def hist():
        return sns.histplot(dat, x=input.var()).set(xlabel=None)
    
    @render.data_frame
    def data():
        return dat[["species", "island", input.var()]]


app = App(app_ui, server)
