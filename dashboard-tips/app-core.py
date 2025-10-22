import faicons as fa
import plotly.express as px
import polars as pl

# Load data and compute static values
from shared import app_dir, tips
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_plotly

# Collect once for initial bill range
bill_rng = (
    tips.select("total_bill").min().collect().item(),
    tips.select("total_bill").max().collect().item(),
)

ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "wallet": fa.icon_svg("wallet"),
    "currency-dollar": fa.icon_svg("dollar-sign"),
    "ellipsis": fa.icon_svg("ellipsis"),
}

# Add page title and sidebar
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider(
            "total_bill",
            "Bill amount",
            min=bill_rng[0],
            max=bill_rng[1],
            value=bill_rng,
            pre="$",
        ),
        ui.input_checkbox_group(
            "time",
            "Food service",
            ["Lunch", "Dinner"],
            selected=["Lunch", "Dinner"],
            inline=True,
        ),
        ui.input_action_button("reset", "Reset filter"),
        open="desktop",
    ),
    ui.layout_columns(
        ui.value_box(
            "Total tippers", ui.output_ui("total_tippers"), showcase=ICONS["user"]
        ),
        ui.value_box(
            "Average tip", ui.output_ui("average_tip"), showcase=ICONS["wallet"]
        ),
        ui.value_box(
            "Average bill",
            ui.output_ui("average_bill"),
            showcase=ICONS["currency-dollar"],
        ),
        fill=False,
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Tips data"), ui.output_data_frame("table"), full_screen=True
        ),
        ui.card(
            ui.card_header(
                "Total bill vs tip",
                ui.popover(
                    ICONS["ellipsis"],
                    ui.input_radio_buttons(
                        "scatter_color",
                        None,
                        ["none", "sex", "smoker", "day", "time"],
                        inline=True,
                    ),
                    title="Add a color variable",
                    placement="top",
                ),
                class_="d-flex justify-content-between align-items-center",
            ),
            output_widget("scatterplot"),
            full_screen=True,
        ),
        ui.card(
            ui.card_header(
                "Tip percentages",
                ui.popover(
                    ICONS["ellipsis"],
                    ui.input_radio_buttons(
                        "tip_perc_y",
                        "Split by:",
                        ["sex", "smoker", "day", "time"],
                        selected="day",
                        inline=True,
                    ),
                    title="Add a color variable",
                ),
                class_="d-flex justify-content-between align-items-center",
            ),
            output_widget("tip_perc"),
            full_screen=True,
        ),
        col_widths=[6, 6, 12],
    ),
    ui.include_css(app_dir / "styles.css"),
    title="Restaurant tipping",
    fillable=True,
)


def server(input, output, session):
    @reactive.calc
    def tips_data():
        bill = input.total_bill()
        idx1 = tips.filter(pl.col("total_bill").is_between(bill[0], bill[1]))
        idx2 = idx1.filter(pl.col("time").is_in(input.time()))
        return idx2

    @render.ui
    def total_tippers():
        return tips_data().select(pl.len()).collect().item()

    @render.ui
    def average_tip():
        d = (
            tips_data()
            .select((pl.col("tip") / pl.col("total_bill")).mean().alias("avg_tip_pct"))
            .collect()
        )
        if d.shape[0] > 0:
            return f"{d.select('avg_tip_pct').item():.1%}"

    @render.ui
    def average_bill():
        d = tips_data().select(pl.col("total_bill").mean().alias("avg_bill")).collect()
        if d.shape[0] > 0:
            return f"${d.select('avg_bill').item():.2f}"

    @render.data_frame
    def table():
        return render.DataGrid(tips_data().collect())

    @render_plotly
    def scatterplot():
        color = input.scatter_color()
        return px.scatter(
            tips_data().collect(),
            x="total_bill",
            y="tip",
            color=None if color == "none" else color,
            trendline="lowess",
        )

    @render_plotly
    def tip_perc():
        from ridgeplot import ridgeplot

        dat = (
            tips_data()
            .with_columns((pl.col("tip") / pl.col("total_bill")).alias("percent"))
            .unique()
            .filter(pl.col("day").is_in(input.tip_perc_y()))
            .group_by("day")
            .agg(pl.col("percent").alias("grouped_percent"))
            .sort(pl.col("day").cast(pl.Enum(["Sun", "Sat", "Thur", "Fri"])))
            .collect()
        )
        samples = dat.select("grouped_percent").to_series().to_list()
        labels = dat.select("day").to_series().to_list()

        plt = ridgeplot(
            samples=samples,
            labels=labels,
            bandwidth=0.01,
            colorscale="viridis",
            colormode="row-index",
        )

        plt.update_layout(
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
            )
        )

        return plt

    @reactive.effect
    @reactive.event(input.reset)
    def _():
        ui.update_slider("total_bill", value=bill_rng)
        ui.update_checkbox_group("time", selected=["Lunch", "Dinner"])


app = App(app_ui, server)
