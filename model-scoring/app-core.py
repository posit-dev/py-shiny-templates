from pathlib import Path

import polars as pl
from plots import plot_auc_curve, plot_precision_recall_curve, plot_score_distribution
from shared import scores
from shiny import App, Inputs, reactive, render, ui

# TODO: borrow some ideas from
# https://github.com/evidentlyai/evidently
# https://medium.com/@dasulaakshat/model-monitoring-dashboard-for-models-in-production-d69f17b96f2c
app_ui = ui.page_navbar(
    ui.nav_spacer(),
    ui.nav_panel(
        "Training Dashboard",
        ui.navset_card_underline(
            ui.nav_panel("ROC Curve", ui.output_plot("roc_curve")),
            ui.nav_panel("Precision/Recall", ui.output_plot("precision_recall")),
            title="Model Metrics",
        ),
        ui.card(
            ui.card_header("Training Scores"),
            ui.output_plot("score_dist"),
        ),
    ),
    ui.nav_panel(
        "View Data",
        ui.layout_columns(
            ui.value_box(title="Row count", value=ui.output_text("row_count")),
            ui.value_box(
                title="Mean training score", value=ui.output_text("mean_score")
            ),
            fill=False,
        ),
        ui.card(ui.output_data_frame("data")),
    ),
    sidebar=ui.sidebar(
        ui.input_select(
            "account",
            "Account",
            choices=[
                "Berge & Berge",
                "Fritsch & Fritsch",
                "Hintz & Hintz",
                "Mosciski and Sons",
                "Wolff Ltd",
            ],
        )
    ),
    id="tabs",
    title="Model scoring dashboard",
    fillable=True,
)


def server(input: Inputs):
    @reactive.calc()
    def dat() -> pl.DataFrame:
        return scores.filter(pl.col("account") == input.account())

    @render.plot
    def score_dist():
        return plot_score_distribution(dat())

    @render.plot
    def roc_curve():
        return plot_auc_curve(dat(), "is_electronics", "training_score")

    @render.plot
    def precision_recall():
        return plot_precision_recall_curve(dat(), "is_electronics", "training_score")

    @render.text
    def row_count():
        return dat().shape[0]

    @render.text
    def mean_score():
        return round(dat()["training_score"].mean(), 2)

    @render.data_frame
    def data():
        return dat()


app = App(app_ui, server)
