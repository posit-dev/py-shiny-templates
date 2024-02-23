from pathlib import Path
import pandas as pd
import seaborn as sns
from shiny.express import input, render, ui

app_dir = Path(__file__).parent
dat = pd.read_csv(app_dir / "penguins.csv")

ui.page_opts(title="Shiny navigation components")

ui.nav_spacer()  # Push the navbar items to the right

footer = ui.input_select(
    "var", "Select variable",
    choices=["bill_length_mm", "body_mass_g"]
)

with ui.nav_panel("Page 1"):

    with ui.navset_card_underline(title="Penguins data", footer=footer):
        with ui.nav_panel("Plot"):
            @render.plot
            def hist():
                return sns.histplot(dat, x=input.var()).set(xlabel=None)

        with ui.nav_panel("Table"):
            @render.data_frame
            def data():
                return dat[["species", "island", input.var()]]

with ui.nav_panel("Page 2"):
    "This is the second 'page'."
