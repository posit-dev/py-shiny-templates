import seaborn as sns

# Import data from shared.py
from shared import df
from shiny import App, render, ui

# User interface (UI) definition
app_ui = ui.page_fixed(
    # Add a title to the page with some top padding
    ui.panel_title(ui.h2("Basic Shiny app", class_="pt-5")),
    # A container for plot output
    ui.output_plot("hist"),
    # A select input for choosing the variable to plot
    ui.input_select(
        "var", "Select variable", choices=["bill_length_mm", "body_mass_g"]
    ),
)


# Server function provides access to client-side input values
def server(input):
    @render.plot
    def hist():
        # Histogram of the selected variable (input.var())
        p = sns.histplot(df, x=input.var(), color="#007bc2", edgecolor="white")
        return p.set(xlabel=None)


app = App(app_ui, server)
