from pathlib import Path

import polars as pl
from plots import plot_auc_curve, plot_precision_recall_curve, plot_score_distribution
from shiny import reactive, render
from shiny.express import input, ui

app_dir = Path(__file__).parent
scores = pl.scan_csv(app_dir / "scores.csv")


@reactive.calc()
def dat():
    return scores.filter(pl.col("account") == input.account()).collect()


ui.page_opts(title="Model scoring dashboard", fillable=True)

ui.nav_spacer()

with ui.nav_panel("Training Dashboard"):
    with ui.navset_card_underline(
        title="Model Metrics",
    ):
        with ui.nav_panel("ROC Curve"):

            @render.plot
            def roc_curve():
                return plot_auc_curve(dat(), "is_electronics", "training_score")

        with ui.nav_panel("Precision/Recall"):

            @render.plot
            def precision_recall():
                return plot_precision_recall_curve(
                    dat(), "is_electronics", "training_score"
                )

    with ui.card():
        ui.card_header("Training Scores")

        @render.plot
        def score_dist():
            return plot_score_distribution(dat())


with ui.nav_panel("View Data"):
    with ui.layout_columns():
        with ui.value_box():
            "Row count"

            @render.text
            def row_count():
                return dat().shape[0]

        with ui.value_box():
            "Mean training score"

            @render.text
            def mean_score():
                return round(dat()["training_score"].mean(), 2)

    with ui.card():

        @render.data_frame
        def data():
            return dat()


with ui.sidebar():
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
