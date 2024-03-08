from __future__ import annotations

from shared import df, plot_timeseries, value_box_server, value_box_ui
from shiny import App, Inputs, Outputs, Session, reactive, ui
from shinywidgets import output_widget, render_plotly

all_models = ["model_1", "model_2", "model_3", "model_4"]

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_checkbox_group("models", "Models", all_models, selected=all_models)
    ),
    ui.layout_columns(
        value_box_ui("model_1", "Model 1"),
        value_box_ui("model_2", "Model 2"),
        value_box_ui("model_3", "Model 3"),
        value_box_ui("model_4", "Model 4"),
        fill=False,
        id="value-boxes",
    ),
    ui.card(
        ui.card_header(
            "Model accuracy over time",
            ui.input_switch("pause", "Pause updates", value=False, width="auto"),
            class_="d-flex justify-content-between",
        ),
        output_widget("plot", height=500),
        full_screen=True,
    ),
    title="Model monitoring dashboard",
    class_="bslib-page-dashboard",
)


def server(input: Inputs, output: Outputs, session: Session):
    # Note that df from shared.py is a reactive calc that gets
    # invalidated (approximately) when the database updates
    # We can choose to ignore the invalidation by doing an isolated read
    @reactive.calc
    def maybe_paused_df():
        if not input.pause():
            return df()
        with reactive.isolate():
            return df()

    # Source the value box module server code for each model
    for model in all_models:
        value_box_server(model, maybe_paused_df, model)

    @render_plotly
    def plot():
        d = maybe_paused_df()
        d = d[d["model"].isin(input.models())]
        return plot_timeseries(d)

    # Hacky way to hide/show model value boxes. This is currently the only real
    # option you want the value box UI to be statically rendered (thus, reducing
    # flicker on update), but also want to hide/show them based on user input.
    @reactive.effect
    @reactive.event(input.models)
    def _():
        ui.remove_ui("#value-box-hide")  # Remove any previously added style tag

        # Construct CSS to hide the value boxes that the user has deselected
        css = ""
        missing_models = list(set(all_models) - set(input.models()))
        for model in missing_models:
            i = all_models.index(model) + 1
            css += f"#value-boxes > *:nth-child({i}) {{ display: none; }}"

        # Add the CSS to the head of the document
        if css:
            style = ui.tags.style(css, id="value-box-hide")
            ui.insert_ui(style, selector="head")


app = App(app_ui, server)
